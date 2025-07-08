import subprocess
import time
import json
import os
import chromadb


CHROMA_DB_PORT = "8010"
EMBEDDING_SERVER_PORT = "8020"
MLFLOW_PORT = "8030"
MONGO_DB_PORT = "27017"

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
db_location =  os.path.join(PROJECT_ROOT, 'local_only', 'chroma_db')
os.makedirs(db_location, exist_ok=True)

def get_chroma_db_commands():
    commands = [
        "chroma",
        "run",
        "--path", db_location,
        "--host", "localhost",
        "--port", CHROMA_DB_PORT
    ]
    return commands

def get_embedding_server_commands():
    commands = [
    "uvicorn",
    "scripts.embeddings_server:app",
    "--host", "127.0.0.1",
    "--port", f"{EMBEDDING_SERVER_PORT}"
    ]
    return commands

def get_mlflow_server_commands():
    commands = [
        "mlflow",
        "server",
        "--backend-store-uri", "./mlflow_logs",
        "--host", "localhost",
        "--port", MLFLOW_PORT
    ]
    return commands

if __name__ == '__main__':

    embed_proc = subprocess.Popen(get_embedding_server_commands())    
    chroma_proc = subprocess.Popen(get_chroma_db_commands())
    mlflow_proc = subprocess.Popen(get_mlflow_server_commands())

    # Keep main script alive
    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        print("Shutting down servers...")
        embed_proc.terminate()
        chroma_proc.terminate()
        mlflow_proc.terminate()