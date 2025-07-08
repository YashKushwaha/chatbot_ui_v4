import os
from src.mlflow_utils.model import Models
from src.mlflow_utils.experiment import Experiment

class MLflowLogs:
    def __init__(self, logs_dir):
        self.logs_dir = logs_dir
        self.experiments = []
        self.models = None
        self.load()

    def load(self):
        for folder in os.listdir(self.logs_dir):
            folder_path = os.path.join(self.logs_dir, folder)
            if self.is_experiment_folder(folder_path):
                self.experiments.append(Experiment(folder_path))
            elif folder == "models" and os.path.isdir(folder_path):
                self.models = Models(folder_path)

    def is_experiment_folder(self, folder_path):
        return (
            os.path.isdir(folder_path) and
            os.path.isfile(os.path.join(folder_path, "meta.yaml"))
        )

    def list_experiments(self):
        return [exp.experiment_id for exp in self.experiments]

    def get_experiment_by_id(self, exp_id):
        for exp in self.experiments:
            if exp.experiment_id == exp_id:
                return exp
        return None
