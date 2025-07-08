from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core import VectorStoreIndex
from llama_index.core.retrievers import BaseRetriever
from llama_index.core.vector_stores.types import VectorStoreQuery
from llama_index.core.schema import QueryBundle


class FlickrImageVectorStore:
    def __init__(self, chroma_collection, embed_model, similarity_top_k=3):
        self.vec_store = ChromaVectorStore(chroma_collection = chroma_collection)
        self.index = VectorStoreIndex.from_vector_store(self.vec_store, embed_model=embed_model)
        self.retriever = VectorIndexRetriever(index=self.index, similarity_top_k=self.similarity_top_k)

    def _retrieve(self, query_bundle: QueryBundle):
        nodes = self.retriever.retrieve(query_bundle)

        
        return all_nodes