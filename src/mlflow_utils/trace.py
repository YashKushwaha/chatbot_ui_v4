import os
import json
from datetime import datetime

from src.mlflow_utils.trace_analyzer import TraceAnalyzer

def list_of_dicts_to_string(data):
    """
    Convert a list of dictionaries to a clean, readable string.
    """
    if not isinstance(data, list):
        return "Invalid input: Expected a list."
    
    output_lines = []
    for idx, item in enumerate(data, start=1):
        if isinstance(item, dict):
            lines = [f"{key}: {value}" for key, value in item.items()]
            output_lines.append(f"[{idx}] " + ", ".join(lines))
        else:
            output_lines.append(f"[{idx}] {str(item)}")

    return "\n".join(output_lines)

class Trace:
    def __init__(self, trace_folder, experiment_id):
        self.trace_folder = trace_folder
        self.trace_id = os.path.basename(trace_folder)
        self.data = self.load_trace()
        self.experiment_id = experiment_id

    def load_trace(self):
        trace_file = os.path.join(self.trace_folder, "artifacts", "traces.json")
        if os.path.isfile(trace_file):
            with open(trace_file) as f:
                return json.load(f)
        return {}

    def get_spans_summary(self):
        analyzer = TraceAnalyzer(self.data)
        # Get flat summary for listing
        flat_summary = analyzer.get_flat_summary()

        # Get hierarchy summary for nested display
        hierarchy = analyzer.get_hierarchy_summary()

        # Get details for a specific span
        details = analyzer.get_span_details("desired_span_id")

        #return dict(flat_summary=flat_summary, hierarchy=hierarchy, details=details)
        return [f"```json\n{flat_summary}```"]
    
    @property
    def metadata(self):
        spans = self.data.get("spans", [])
        start_time_ns = spans[0].get("start_time_unix_nano", 0) if spans else 0
        readable_time = self._format_time(start_time_ns)

        return {
            "trace_id": self.trace_id,
            "span_count": len(spans),
            "start_time_unix_nano": start_time_ns,
            "start_time_str": readable_time,
            "experiment_id": self.experiment_id
        }

    def _format_time(self, timestamp_ns):
        if not timestamp_ns:
            return "Unknown"
        dt = datetime.utcfromtimestamp(int(timestamp_ns) / 1e9)
        return dt.strftime("%Y-%m-%d %H:%M:%S UTC")

    def __repr__(self):
        return (f"Trace(id='{self.metadata['trace_id']}', "
                f"spans={self.metadata['span_count']}, "
                f"start='{self.metadata['start_time_str']}')")

