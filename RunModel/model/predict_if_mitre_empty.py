from typing import Dict, Any
from model.runModel import clean_run_prediction

def predict_check_package(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Input format:
    {
      "node": { ... }
    }

    Returns:
    {
      "log": { "node": ... },
      "type": {
        "prediction": { ... },
        "Mitre_Match": [ ... ]
      }
    }
    """
    try:
        node = data.get("node", {})

        if isinstance(node.get("mitre"), list) and len(node["mitre"]) == 0:
            prediction_result = clean_run_prediction(data)  # run on full data, not just node

            return {
                "log": { "node": data["node"] },
                "type": {
                    "prediction": prediction_result.get("prediction", {
                        "tactic": [],
                        "technique": [],
                        "subtechnique": []
                    }),
                    "Mitre_Match": prediction_result.get("Mitre_Match", [])
                }
            }

        else:
            return {
                "log": { "node": data["node"] },
                "type": {
                    "prediction": {
                        "tactic": [],
                        "technique": [],
                        "subtechnique": []
                    },
                    "Mitre_Match": []
                }
            }

    except Exception as e:
        return {"error": str(e)}

def predict_with_mitre_check(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Input format:
    {
      "node": { ... }
    }

    Returns:
    {
      "prediction": { ... },
      "Mitre_Match": [ ... ]
    }
    """
    try:
        node = data.get("node", {})

        if isinstance(node.get("mitre"), list) and len(node["mitre"]) == 0:
            return clean_run_prediction(data)  # input is full {node: ...}

        else:
            return {
                "prediction": {
                    "tactic": [],
                    "technique": [],
                    "subtechnique": []
                },
                "Mitre_Match": []
            }

    except Exception as e:
        return {"error": str(e)}
