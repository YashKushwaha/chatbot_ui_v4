import os

from back_end.config_settings import PROJECT_ROOT 

EXPERIMENT_NAME = "agent testing"
MLFLOW_LOGS_FOLDER = os.path.join(PROJECT_ROOT, 'mlflow_logs')
os.makedirs(MLFLOW_LOGS_FOLDER, exist_ok=True)
