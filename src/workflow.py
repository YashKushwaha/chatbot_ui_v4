from src.ollama_vision import get_image
from src.image_retriever import ImageRetriever
from src.embedding_client import RemoteEmbedding
from src.components import get_chroma_db_client
from llama_index.core.vector_stores import VectorStoreQuery

from jinja2 import Template

from llama_index.vector_stores.chroma import ChromaVectorStore
import requests
import json

def make_llm_call(model_name, prompt, encoded_image_list):
    ollama_url = "http://localhost:11434/api/generate"
    payload = {
        "model": model_name,
        "prompt": prompt,
        "images": encoded_image_list
    }

    headers = {
        "Content-Type": "application/json"
    }

    response = requests.post(ollama_url, headers=headers, data=json.dumps(payload), stream=True)

    output = ""
    for line in response.iter_lines():
        if line:
            chunk = json.loads(line.decode("utf-8"))
            output += chunk.get("response", "")

            print(chunk.get("response", ""), end='')

    print()
prompt_template = """
You are a helpful assistant. Users may ask you to generate images based on a text description.
You will be provided with images retrieved from the knowledge base and you have to decide which image best aligns with user query.

Images will be provided in the follwoing format:
<image_1> : name of the file e.g. 12345.jpg
<image_2> : 67891011.jpg
....

Respond in **json** format e.g {'best_image': 12345.jpg}

USER QUERY:

{{user_query}}

IMAGES:
{{images}}
"""
template = Template(prompt_template)

query = 'Going to office in New York'
embed_model = RemoteEmbedding(f"http://localhost:8020")

vec_db_client = get_chroma_db_client()

chroma_collection = vec_db_client.get_collection('images')
vec_store = ChromaVectorStore(chroma_collection = chroma_collection)

#retriever = ImageRetriever(embed_model, vec_store)
embeddings = embed_model.get_query_embedding(query)
vec_store_query = VectorStoreQuery(query_embedding = embeddings[0], similarity_top_k = 5)
results = vec_store.query(query = vec_store_query)
#results = retriever.retrieve(query)
images = [node.text for node in results.nodes][:3]


url_list = []
image_string = []
for num, image_name in enumerate(images, start=1):
    to_add = f'<image_{num}> : {image_name}'
    image_string.append(to_add)
    url = f'http://localhost:8000/get_image?filename={image_name}'
    url_list.append(url)

image_string = '\n'.join(image_string)

print(image_string)

base64_images = [get_image(url) for url in url_list]
rendered_prompt = template.render(user_query = query, images = image_string)

model_name = 'gemma3:12b'

make_llm_call(model_name, prompt=rendered_prompt, encoded_image_list=base64_images)