from llama_index.core.retrievers import BaseRetriever
from llama_index.core.schema import QueryBundle, NodeWithScore, TextNode

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
            embedding = self.embed_model.embed_image(query)  # query should be image path or tensor

        results = self.vec_store.query(embedding, similarity_top_k=self.similarity_top_k) 

        return results
