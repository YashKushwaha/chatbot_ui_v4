from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from llama_index.vector_stores.chroma import ChromaVectorStore

from llama_index.core import Settings
from llama_index.utils.workflow import (
    draw_all_possible_flows,
    draw_most_recent_execution,
)

import os
import asyncio

from pathlib import Path

from back_end.config_settings import PROJECT_ROOT, STATIC_DIR, IMAGES_DIR
from constants import MLFLOW_LOGS_FOLDER

from back_end.routes import ui_routes, debug_routes, api_routes, db_routes, vec_db_routes, mlflow_routes
'''
from src.agent_list import get_function_agent
from src.react_agent import get_react_agent
'''
from src.components import get_ollama_llm, get_mongo_db_client, get_chroma_db_client
from src.embedding_client import RemoteEmbedding
from src.image_retriever import ImageRetriever
from src.image_store import ImageStore
from src.mlflow_utils import MLflowLogs
from src.aws_bedrock import get_bedrock_llm
from src.ollama_vision import OllamaVisionLLM
import mlflow

EXPERIMENT_NAME = 'Multimodal Retrieval'
IMAGES_FOLDER = os.path.join(PROJECT_ROOT, 'local_only', 'data', 'images')

mlflow.set_tracking_uri(MLFLOW_LOGS_FOLDER)
mlflow.set_experiment(EXPERIMENT_NAME)
mlflow.llama_index.autolog()  # Enable mlflow tracing

app = FastAPI()

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
app.mount("/images", StaticFiles(directory=IMAGES_DIR), name="images")


#llm = get_ollama_llm()

#llm = get_bedrock_llm()
model_name = 'gemma3:12b'
llm = OllamaVisionLLM(model_name=model_name)
embed_model = RemoteEmbedding(f"http://localhost:8020")

Settings.llm = llm
Settings.embed_model = embed_model

mongo_db_client = get_mongo_db_client()
vec_db_client = get_chroma_db_client()

chroma_collection = vec_db_client.get_collection('images')
vec_store = ChromaVectorStore(chroma_collection = chroma_collection)
retriever = ImageRetriever(embed_model, vec_store, 3,'text')

mlflow_handler = MLflowLogs(MLFLOW_LOGS_FOLDER)
#app.state.agent = agent
app.state.settings = Settings
app.state.embed_model = embed_model
app.state.retriever = retriever
app.state.vec_store = vec_store
app.state.mongo_db_client = mongo_db_client
app.state.vec_db_client = vec_db_client
app.state.experiment_name = EXPERIMENT_NAME
app.state.mlflow_handler = mlflow_handler
app.state.llm = llm
app.state.image_manager = ImageStore(IMAGES_FOLDER)

app.include_router(ui_routes.router)
app.include_router(debug_routes.router) 
app.include_router(api_routes.router) 
app.include_router(db_routes.router) 
app.include_router(vec_db_routes.router) 
app.include_router(mlflow_routes.router) 

if __name__ == "__main__":
    import uvicorn
    app_path = Path(__file__).resolve().with_suffix('').name  # gets filename without .py
    uvicorn.run(f"{app_path}:app", host="localhost", port=8000, reload=True)