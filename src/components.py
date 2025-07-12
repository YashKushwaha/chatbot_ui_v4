import chromadb
from pymongo import MongoClient

from llama_index.llms.ollama import Ollama

CHROMA_DB_PORT = 8010
IMAGE_SERVER_PORT = 8040

def get_ollama_llm():
    model = "qwen3:14b"
    context_window = 1000

    llm = Ollama(
        model=model,
        request_timeout=120.0,
        thinking=True,
        context_window=context_window,
    )
    return llm

def get_chroma_db_client():
    client = chromadb.HttpClient(
        host="localhost",
        port=int(CHROMA_DB_PORT))
    return client

def get_mongo_db_client():
    mongo_db_client = MongoClient("mongodb://localhost:27017/")
    return mongo_db_client