from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
import json
import os
#from back_end.config_settings import templates
import yaml
import datetime
from src.mlflow_utils import Experiment

router = APIRouter()

@router.get("/mlflow/list-experiments", response_class=JSONResponse)
def list_experiments(request: Request):
    mlflow_handler = request.app.state.mlflow_handler
    experiments = [dict(name = i.metadata['name'], experiment_id=i.metadata['experiment_id']) for i in mlflow_handler.experiments]
    return JSONResponse({'experiments': experiments})

@router.get("/mlflow/list-traces", response_class=JSONResponse)
def list_traces(request: Request, experiment_id:str):
    mlflow_handler = request.app.state.mlflow_handler
    logs_dir = mlflow_handler.logs_dir
    experiment = Experiment(os.path.join(logs_dir, experiment_id ))
    traces = [i.metadata for i in experiment.load_traces()]
    sorted_traces = sorted(traces, key=lambda x: x["start_time_unix_nano"], reverse=True)
    return JSONResponse({'traces': sorted_traces})

@router.get("/mlflow/list-trace-summary", response_class=JSONResponse)
def list_traces(request: Request, experiment_id:str, trace_id:str):
    mlflow_handler = request.app.state.mlflow_handler
    logs_dir = mlflow_handler.logs_dir
    experiment = Experiment(os.path.join(logs_dir, experiment_id ))
    relevant_traces = [i for i in experiment.load_traces() if i.metadata.get('trace_id') == trace_id]
    if len(relevant_traces) > 0:
        trace = relevant_traces[0]
        span_summary = trace.get_spans_summary()
    else:
        span_summary=[]

    return JSONResponse({'span_summary': span_summary})
