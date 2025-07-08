from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
import json
from back_end.config_settings import templates

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
def root(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "chat_endpoint": "/echo"
    })

@router.get("/chat_bot", response_class=HTMLResponse)
def root(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "chat_endpoint": "/chat_bot"
    })

@router.get("/retriever", response_class=HTMLResponse)
def root(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "chat_endpoint": "/retriever"
    })

@router.get("/mongo", response_class=HTMLResponse)
def root(request: Request):
    return templates.TemplateResponse("mongo_db.html", {
        "request": request,
    })

@router.get("/vecdb", response_class=HTMLResponse)
def root(request: Request):
    return templates.TemplateResponse("vec_db.html", {
        "request": request,
    })

@router.get("/mlflow", response_class=HTMLResponse)
def root(request: Request):
    return templates.TemplateResponse("mlflow.html", {
        "request": request,
    })


@router.get("/chat_history", response_class=HTMLResponse)
def chat_history(request: Request):
    chat_history = request.app.state.chat_engine.chat_history

    return templates.TemplateResponse("chat_history_template.html", {
        "request": request,
        "chat_history": chat_history
    })

@router.get("/buffer_memory", response_class=HTMLResponse)
def chat_history(request: Request):
    chat_history = request.app.state.chat_engine._memory.get()

    return templates.TemplateResponse("chat_history_template.html", {
        "request": request,
        "chat_history": chat_history
    })

@router.get("/chat_history_raw", response_class=HTMLResponse)
def root(request: Request):
    chat_history = request.app.state.chat_engine.chat_history
    return json.dumps([msg.dict() for msg in chat_history], indent=2)

@router.get("/echo", response_class=HTMLResponse)
def root(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "chat_endpoint": "/echo"
    })


