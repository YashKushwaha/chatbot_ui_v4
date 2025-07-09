from fastapi import Form, File, UploadFile
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi import APIRouter, Request
from llama_index.core.vector_stores import VectorStoreQuery
import asyncio

router = APIRouter()

async def stream_llm_response(llm, prompt: str):
    response = llm.stream_complete(prompt)
    for chunk in response:
        yield chunk.delta
        await asyncio.sleep(0.1)

'''
@router.post("/chat_bot")
async def chat_bot(request: Request, message: str = Form(...), image: UploadFile = File(None)):
    response_stream = stream_agent_response(request.app.state.agent, message)
    return StreamingResponse(response_stream, media_type="text/plain")
'''
@router.post("/chat")
async def chat_bot(request: Request, message: str = Form(...), image: UploadFile = File(None)):
    response_stream = stream_llm_response(request.app.state.llm, message)
    return StreamingResponse(response_stream, media_type="text/plain")

@router.post("/vision")
async def vision(request: Request, message: str = Form(...), image: UploadFile = File(None)):
    response_stream = message
    if image:
        print('image -> ', image)
    #response_stream = stream_llm_response(request.app.state.llm, message)
    return StreamingResponse(response_stream, media_type="text/plain")


@router.post("/retriever")
async def retriever(request: Request, message: str = Form(...), image: UploadFile = File(None)):
    vec_store = request.app.state.vec_store
    embed_model = request.app.state.settings.embed_model
    embeddings = embed_model.get_query_embedding(message)
    vec_store_query = VectorStoreQuery(query_embedding = embeddings[0], similarity_top_k = 5)
    results = vec_store.query(query = vec_store_query)

    response_stream = '\n\n'.join(
        f"![image](/get_image?filename={node.text})"
        for node in results.nodes
    )
    return StreamingResponse(response_stream, media_type="text/plain")
