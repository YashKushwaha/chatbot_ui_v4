from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
import json
#from back_end.config_settings import templates

router = APIRouter()

@router.get("/vecdb/list-collections", response_class=JSONResponse)
def db_stats(request: Request):
    client = request.app.state.vec_db_client
    collection_list = [i.name for i in client.list_collections()]
    return JSONResponse({'collections': collection_list})

@router.get("/vecdb/num-records-in-collection", response_class=JSONResponse)
def db_stats(request: Request, collection:str):
    client = request.app.state.vec_db_client
    collection_list = [i.name for i in client.list_collections()]
    if collection in collection_list:
        col = client.get_collection(collection)
        num_records = col.count()
    else:
        num_records = -1
    return JSONResponse({'num_records': num_records})

@router.get("/vecdb/first-n-records-in-collection", response_class=JSONResponse)
def list_collections(request: Request, collection):
    client = request.app.state.vec_db_client
    collection_list = [i.name for i in client.list_collections()]
    if collection in collection_list:
        record = client.get_collection(collection).peek(1)
        record = dict(record)
        record.pop('embeddings')
        record.pop('included')
        records = [record]
    else:
        records = []
    return JSONResponse({"records": records if isinstance(records, list) else []})
