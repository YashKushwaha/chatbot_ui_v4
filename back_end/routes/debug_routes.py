from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi import Form, File, UploadFile

import json
import asyncio
from back_end.config_settings import templates

router = APIRouter()

async  def dummy_llm_call(response):
    for word in response:
        yield word
        await asyncio.sleep(0.05)  # simulate delay

@router.post("/echo")
async def chat(message: str = Form(...), image: UploadFile = File(None)):
    message = message.replace('\n', '<br>')
    #return JSONResponse({"response": message})
    return StreamingResponse(dummy_llm_call(message), media_type="text/plain")

