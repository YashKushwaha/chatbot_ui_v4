from fastapi import FastAPI
from sentence_transformers import SentenceTransformer
from pydantic import BaseModel
from typing import List
from pathlib import Path

from src.embedding_model import OpenCLIPEmbedder

class EmbedRequest(BaseModel):
    text: str

class BatchEmbedRequest(BaseModel):
    texts: List[str]

app = FastAPI()
#model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
model = OpenCLIPEmbedder()


@app.post("/embed")
async def embed(request: EmbedRequest):
    embedding = model.encode_text(request.text).tolist()
    return {"embedding": embedding}

@app.post("/batch_embed")
async def batch_embed(request: BatchEmbedRequest):
    embeddings = model.encode_text(request.texts).tolist()
    return {"embeddings": embeddings}

@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    app_path = Path(__file__).resolve().with_suffix('').name  # gets filename without .py
    uvicorn.run(f"{app_path}:app", host="localhost", port=8020, reload=True)