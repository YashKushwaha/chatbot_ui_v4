from llama_index.core.retrievers import BaseRetriever
from llama_index.core.schema import QueryBundle, NodeWithScore, TextNode
from llama_index.core.tools import FunctionTool
from llama_index.core.vector_stores import VectorStoreQuery
from llama_index.core.schema import NodeWithScore
from llama_index.core.postprocessor.types import BaseNodePostprocessor

class ImageRetriever(BaseRetriever):
    def __init__(self, embed_model, vec_store, similarity_top_k=5, mode="text"):
        self.embed_model = embed_model
        self.vec_store = vec_store
        self.similarity_top_k = similarity_top_k
        self.mode = mode  # "text" or "image"

    def _retrieve(self, query_bundle: QueryBundle):
        query = query_bundle.query_str

        if self.mode == "text":
            embedding = self.embed_model.get_query_embedding(query)
        else:
            embedding = self.embed_model.embed_image(query)

        vec_store_query = VectorStoreQuery(query_embedding = embedding[0], similarity_top_k = 5)
        results = self.vec_store.query(vec_store_query) 
        print(results.__dict__)

        return [
        NodeWithScore(node=n, score=s)
        for n, s in zip(results.nodes, results.similarities)
    ]

def retrieve_images(query: str, retriever):
    results = retriever.retrieve(query)    
    return [node.text for node in results.nodes]
"""
image_retriever_tool = FunctionTool.from_defaults(
    fn=retrieve_images,
    name="image_retrieval_tool",
    description="Retrieves relevant images for a given text query. Returns a list of image filenames or URLs."
)
"""

if __name__ == '__main__':
    from src.embedding_client import RemoteEmbedding
    embed_model = RemoteEmbedding(f"http://localhost:8020")
    from src.components import get_chroma_db_client
    vec_db_client = get_chroma_db_client()

    chroma_collection = vec_db_client.get_collection('images')
    from llama_index.vector_stores.chroma import ChromaVectorStore
    vec_store = ChromaVectorStore(chroma_collection = chroma_collection)
    
    retriever = ImageRetriever(embed_model=embed_model, vec_store=vec_store, similarity_top_k=4)

    results = retriever.retrieve('man walking in park') 