from src.tools import ImageRetrieverTool
from src.image_retriever import ImageRetriever

from llama_index.core.workflow import (
    Event,
    StartEvent,
    StopEvent,
    Workflow,
    step,
)

class RetrieveImageListEvent(Event):
    image_list: list


class ImageRetrievalWorkfow(Workflow):
    def __init__(self, image_retriever_tool):
        super().__init__()
        self.image_retriever_tool = image_retriever_tool

    @step
    async def retrieve_image_ids(self, ev: StartEvent) -> RetrieveImageListEvent:
        query = ev.query
        results = self.image_retriever_tool(query) 
        images = [node.text for node in results]
        return RetrieveImageListEvent(image_list=images)
    
    @step
    async def show_image_ids(self, ev: RetrieveImageListEvent) -> StopEvent:
        for i in ev.image_list:
            print(i)
        return StopEvent()

async def main(image_retriever_tool):
    w = ImageRetrievalWorkfow(image_retriever_tool)
    result = await w.run(query='Hello, World !')
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

    asyncio.run(main(image_retriever_tool))
    


