from llama_index.core.tools.types import BaseTool, ToolMetadata, ToolOutput
from pydantic import BaseModel

from src.ollama_vision import get_image
from src.image_retriever import ImageRetriever
from src.embedding_client import RemoteEmbedding
from src.components import get_chroma_db_client
from llama_index.core.vector_stores import VectorStoreQuery

from jinja2 import Template

from llama_index.vector_stores.chroma import ChromaVectorStore
import requests
import json
from jinja2 import Template


QUERY_TEMPLATE = """
You are a helpful assistant. Your job is to evaluate the relevance of a list of images to the user query.

Images are going to be in the format <image_num> : <image_id> e.g.
<image_1> : 123.jpg
<image_2> : 456.jpg
<image_3> : abc.jpg

Identify the most relevant image and also write a short description of the image.
Output in json format only using the format:
{"best_image":"456.jpg",
 "description": "Description of the image"
}

USER QUERY:
{{user_query}}

IMAGES:
{{images}}

"""
template = Template(QUERY_TEMPLATE)

class QueryInput(BaseModel):
    query: str

class ImageList(BaseModel):
    image_list: list

class ImageRetrieverTool(BaseTool):
    args_schema = QueryInput
    
    def __init__(self, image_retriever=None):
        self.image_retriever = image_retriever 

    @property
    def metadata(self) -> ToolMetadata:
        tool_metadata = ToolMetadata(
        description = ('This tool takes user query, creates embedding and searches in vector database '
                       'returns the name of file in image database'
                       ),
        name = 'Image Retriever' ,
        return_direct = False
        )
        return tool_metadata

    def __call__(self, query: QueryInput) -> str:
        return self.image_retriever.retrieve(query)

class ImageListEvaluatorTool(BaseTool):
    args_schema = ImageList
    
    def __init__(self, vision_llm=None, template=None):
        #self.image_retriever_fn = image_retriever_fn 
        self.vision_llm = vision_llm 
        self.template = template

    @property
    def metadata(self) -> ToolMetadata:
        tool_metadata = ToolMetadata(
        description = ('This tool receives a list of ids of images in the image database.'
                       'Makes call to the database & retrieves the image. It evaluates the images against user query'
                       'And returns the id of image most aligned with user query'
                       ),
        name = 'Image List Evaluator' ,
        return_direct = False
        )
        return tool_metadata

    def __call__(self, query:QueryInput, image_list: ImageList) -> str:
        image_string, base64_images = prepare_images_for_prompt(image_list)
        prompt = self.template.render(user_query = query, images = image_string)    
        response_gen = self.vision_llm.stream_complete(prompt=prompt, image_source=base64_images)
        return response_gen

def prepare_images_for_prompt(images):
    url_list = []
    image_string = []
    for num, image_name in enumerate(images, start=1):
        to_add = f'<image_{num}> : {image_name}'
        image_string.append(to_add)
        url = f'http://localhost:8040/get_image?filename={image_name}'
        url_list.append(url)

    image_string = '\n'.join(image_string)
    base64_images = [get_image(url) for url in url_list]
    #return dict(image_string=image_string, base64_images=base64_images)
    return image_string, base64_images

if __name__ == '__main__':
    #query = QueryInput(query = 'Hello, World ! Howare you ?')

    from src.embedding_client import RemoteEmbedding
    embed_model = RemoteEmbedding(f"http://localhost:8020")
    from src.components import get_chroma_db_client
    vec_db_client = get_chroma_db_client()

    chroma_collection = vec_db_client.get_collection('images')
    from llama_index.vector_stores.chroma import ChromaVectorStore
    vec_store = ChromaVectorStore(chroma_collection = chroma_collection)
    
    image_retriever = ImageRetriever(embed_model=embed_model, vec_store=vec_store, similarity_top_k=4)
    tool = ImageRetrieverTool(image_retriever = image_retriever)
    
    query = "Poeple praying in church"

    results = tool(query) 
    images = [node.text for node in results]
    print(images)

    from src.ollama_vision import  OllamaVisionLLM    
    vision_llm = OllamaVisionLLM(model_name = 'gemma3:12b')

    evaluator = ImageListEvaluatorTool(vision_llm=vision_llm, template = template)

    response = evaluator(query=query, image_list=images)
    
    final_response = ""
    for chunk in response:
        print(chunk.delta, end="", flush=True)  # Print tokens as they stream
        final_response += chunk.delta
