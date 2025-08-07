import json
import os
from typing import Dict, Any


def load_onboarding_context_from_log(log_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Given a single log with a 'node', load the corresponding onboarding context file.
    """
    node = log_data.get("node", log_data)
    object_marking = node.get("objectMarking", [])
    definition = object_marking[0].get("definition") if object_marking else None

    if not definition:
        raise ValueError("Missing 'definition' in log")

    filename = f"{definition}_Context.json"
    path = f"contexts/clientInfo/{filename}"

    if not os.path.exists(path):
        raise FileNotFoundError(f"Context file not found: {path}")

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
