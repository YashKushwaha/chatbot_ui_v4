from fastapi import Form, File, UploadFile
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi import APIRouter, Request
from llama_index.core.vector_stores import VectorStoreQuery

from src.templates import image_evaluator_template
from src.tools import prepare_images_for_prompt

import asyncio
import base64

router = APIRouter()

async def stream_llm_response(llm, prompt: str):
    response = llm.stream_complete(prompt)
    for chunk in response:
        yield chunk.delta
        await asyncio.sleep(0.1)

async def stream_response(response):
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
    llm = request.app.state.llm
    if image:
        image.file.seek(0)
        image_bytes = image.file.read()
        image_for_llm = base64.b64encode(image_bytes).decode("utf-8")
        response_stream = llm.stream_complete(message, image_for_llm)
    else:
        #pass
        response_stream = llm.stream_complete(message)
    return StreamingResponse(stream_response(response_stream), media_type="text/plain")

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

@router.post("/multi_modal_rag")
def multi_modal_rag(request: Request, message: str = Form(...), image: UploadFile = File(None)):
    retriever =  request.app.state.retriever
    results = retriever.retrieve(message) 
    response_stream = '\n\n'.join(
        f"![image](/get_image?filename={node.text})"
        for node in results
    )
    image_list = [node.text for node in results]
    print(image_list)
    image_string, base64_images = prepare_images_for_prompt(image_list)

    print(image_string)
    prompt = image_evaluator_template.render(user_query = message, images = image_string)
    response_gen = request.app.state.llm.stream_complete(prompt=prompt, image_source=base64_images)
    return StreamingResponse(stream_response(response_gen), media_type="text/plain")

