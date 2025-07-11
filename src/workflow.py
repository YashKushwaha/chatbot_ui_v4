from src.tools import ImageRetrieverTool, prepare_images_for_prompt
from src.image_retriever import ImageRetriever

from jinja2 import Template
from llama_index.core.workflow import (
    Event,
    StartEvent,
    StopEvent,
    Workflow,
    step,
)

from src.ollama_vision import  OllamaVisionLLM    


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


class RetrieveImageListEvent(Event):
    image_list: list


class ImageRetrievalWorkfow(Workflow):
    def __init__(self, image_retriever_tool, vision_llm):
        super().__init__()
        self.image_retriever_tool = image_retriever_tool
        self.template = Template(QUERY_TEMPLATE)
        self.vision_llm = vision_llm
    @step
    async def retrieve_image_ids(self, ev: StartEvent) -> RetrieveImageListEvent:
        query = ev.query
        results = self.image_retriever_tool(query) 
        images = [node.text for node in results]
        return RetrieveImageListEvent(image_list=images, query = query)
    
    @step
    async def evaluate_images(self, ev: RetrieveImageListEvent) -> StopEvent:
        image_string, base64_images = prepare_images_for_prompt(ev.image_list)
        prompt = self.template.render(user_query = ev.query, images = image_string)    
        response_gen = self.vision_llm.stream_complete(prompt=prompt, image_source=base64_images)
        final_response = ""
        for chunk in response_gen:
            print(chunk.delta, end="", flush=True)  # Print tokens as they stream
            final_response += chunk.delta
        return StopEvent(final_response=final_response)


async def main(image_retriever_tool, vision_llm):
    
    w = ImageRetrievalWorkfow(image_retriever_tool, vision_llm)
    result = await w.run(query='A typical busy day in a big metro city')
    print(result)

if __name__ == '__main__':
    from src.embedding_client import RemoteEmbedding
    embed_model = RemoteEmbedding(f"http://localhost:8020")
    from src.components import get_chroma_db_client
    vec_db_client = get_chroma_db_client()

    chroma_collection = vec_db_client.get_collection('images')
    from llama_index.vector_stores.chroma import ChromaVectorStore
    vec_store = ChromaVectorStore(chroma_collection = chroma_collection)
    
    image_retriever = ImageRetriever(embed_model=embed_model, vec_store=vec_store, similarity_top_k=4)
    image_retriever_tool = ImageRetrieverTool(image_retriever=image_retriever)
    import asyncio
    vision_llm = OllamaVisionLLM(model_name = 'gemma3:12b')
    asyncio.run(main(image_retriever_tool, vision_llm))
    


