

class TraceAnalyzer:
    def __init__(self, trace_data):
        self.spans = trace_data.get("spans", [])
        self.span_lookup = {span['span_id']: span for span in self.spans}

    def get_flat_summary(self):
        """
        Return a flat list of spans with essential details.
        """
        summary = []
        for span in self.spans:
            summary.append({
                "span_id": span["span_id"],
                "name": span["name"],
                "span_type": span.get("attributes", {}).get("mlflow.spanType", "UNKNOWN"),
                "parent_span_id": span.get("parent_span_id"),
            })
        return summary

    def get_hierarchy_summary(self):
        """
        Return hierarchical structure based on parent-child relationships.
        """
        tree = self._build_hierarchy()
        return self._build_nested_tree(tree, parent_id=None)

    def get_span_details(self, span_id):
        """
        Return detailed information for a specific span.
        """
        from datetime import datetime
        span = self.span_lookup.get(span_id)
        if not span:
            return {"error": "Span not found"}

        return {
            "span_id": span["span_id"],
            "trace_id": span["trace_id"],
            "name": span["name"],
            "span_type": span.get("attributes", {}).get("mlflow.spanType", "UNKNOWN"),
            "start_time": datetime.fromtimestamp(int(span["start_time_unix_nano"]) / 1e9).isoformat(),
            "end_time": datetime.fromtimestamp(int(span["end_time_unix_nano"]) / 1e9).isoformat(),
            "attributes": span.get("attributes", {}),
            "status": span.get("status", {}),
        }

    def _build_hierarchy(self):
        tree = {}
        for span in self.spans:
            tree.setdefault(span.get("parent_span_id"), []).append(span)
        return tree

    def _build_nested_tree(self, tree, parent_id, depth=0):
        """
        Recursively builds nested tree for hierarchy display.
        """
        nodes = []
        for span in tree.get(parent_id, []):
            node = {
                "span_id": span["span_id"],
                "name": span["name"],
                "span_type": span.get("attributes", {}).get("mlflow.spanType", "UNKNOWN"),
                "depth": depth,
                "children": self._build_nested_tree(tree, span["span_id"], depth + 1)
            }
            nodes.append(node)
        return nodes
