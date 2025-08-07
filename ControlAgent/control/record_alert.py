import json
from pathlib import Path
from datetime import datetime


def load_json(file_path):
    if not file_path.exists():
        return {}
    with open(file_path, "r") as f:
        return json.load(f)

def save_json(file_path, data):
    with open(file_path, "w") as f:
        json.dump(data, f, indent=2)



def append_json(file_path: Path, new_entry: dict):
    # Step 1: Ensure file exists
    if not file_path.exists():
        with open(file_path, 'w') as f:
            json.dump([], f)

    # Step 2: Load existing data
    with open(file_path, 'r+') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            data = []

        # Step 3: Append new entry
        data.append(new_entry)

        # Step 4: Write back
        f.seek(0)
        json.dump(data, f, indent=2)
        f.truncate()
        
        
        
        
"""
    #unused function
    def process_alert_file():
    # Load the main input JSON
    with open(INPUT_FILE, "r") as f:
        data = json.load(f)

    node = data.get("node", {})
    alert_id = node.get("alert_id")

    if not alert_id:
        raise ValueError("Missing alert_id in input")

    # Save individual alert file
    alert_file = LOG_DIR / f"{alert_id}.json"
    save_json(alert_file, node)

    # Update index
    index = load_json(INDEX_FILE)
    index[alert_id] = {
        "path": str(alert_file),
        "timestamp": datetime.utcnow().isoformat(),
        "alert_name": node.get("alert_name"),
        "severity": node.get("severity"),
        "status": node.get("alert_status"),
        "log_source": node.get("log_source")
    }

    save_json(INDEX_FILE, index)
    print(f"[✓] Saved alert {alert_id} to {alert_file}")
"""