from llama_index.core.base.embeddings.base import BaseEmbedding
from pydantic import PrivateAttr
import requests
import aiohttp

class RemoteEmbedding(BaseEmbedding):

    _server_url: str = PrivateAttr()

    def __init__(self, server_url: str):
        super().__init__()
        self._server_url = server_url.rstrip('/')

    def _get_query_embedding(self, query: str):
        response = requests.post(f"{self._server_url}/embed", json={"text": query})
        response.raise_for_status()
        return response.json()["embedding"]

    def get_query_embedding(self, query: str):
        return self._get_query_embedding(query)
    
    def _get_text_embedding(self, text: str):
        # Some methods in llama-index call this for general embeddings
        return self._get_query_embedding(text)

    async def _aget_query_embedding(self, query: str):
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self._server_url}/embed", json={"text": query}) as resp:
                resp.raise_for_status()
                result = await resp.json()
                return result["embedding"]

    def _get_text_embeddings(self, texts: list[str]):
        response = requests.post(f"{self._server_url}/batch_embed", json={"texts": texts})
        response.raise_for_status()
        return response.json()["embeddings"]
    