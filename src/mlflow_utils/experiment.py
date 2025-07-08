import os
import yaml
from datetime import datetime

from src.mlflow_utils.model import Models
from src.mlflow_utils.trace import Trace


class Experiment:
    def __init__(self, folder_path):
        self.folder_path = folder_path
        self.experiment_id = os.path.basename(folder_path)
        self.meta = self.load_meta()
        self.traces = self.load_traces()

    def load_meta(self):
        meta_path = os.path.join(self.folder_path, "meta.yaml")
        if os.path.isfile(meta_path):
            with open(meta_path) as f:
                return yaml.safe_load(f)
        return {}

    def load_traces(self):
        traces = []
        traces_dir = os.path.join(self.folder_path, "traces")
        if not os.path.isdir(traces_dir):
            return traces

        for trace_id in os.listdir(traces_dir):
            trace_folder = os.path.join(traces_dir, trace_id)
            if os.path.isdir(trace_folder):
                traces.append(Trace(trace_folder, experiment_id = self.experiment_id))
        return traces

    @property
    def metadata(self):
        creation_time = self.meta.get("creation_time")
        readable_time = self._format_time(creation_time)
        return {
            "experiment_id": self.experiment_id,
            "name": self.meta.get("name"),
            "creation_time": creation_time,
            "creation_time_str": readable_time,
            "trace_count": len(self.traces)
        }

    def _format_time(self, timestamp_ms):
        if not timestamp_ms:
            return "Unknown"
        dt = datetime.utcfromtimestamp(int(timestamp_ms) / 1000)
        return dt.strftime("%Y-%m-%d %H:%M:%S UTC")

    def __repr__(self):
        return (f"Experiment(id='{self.metadata['experiment_id']}', "
                f"traces={self.metadata['trace_count']}, "
                f"created='{self.metadata['creation_time_str']}')")
