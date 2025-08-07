from typing import Dict, Any


def extract_info_from_single_log(log: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract 'definition' and 'src_ip' from a single log dict.
    
    Expected structure:
    {
        "node": {
            "objectMarking": [{"definition": "..."}, ...],
            "contexts": {"src_ip": ["..."]}
        }
    }

    Returns:
    {
        "definition": "N-Health",
        "src_ips": ["10.x.x.x"]
    }
    """
    node = log.get("node", {})

    # Extract first definition
    object_marking = node.get("objectMarking", [])
    definition = (
        object_marking[0]["definition"]
        if object_marking and "definition" in object_marking[0]
        else None
    )

    # Extract src_ip (always list)
    contexts = node.get("contexts", {})
    src_ips = contexts.get("src_ip", [])
    if isinstance(src_ips, str):
        src_ips = [src_ips]

    return {
        "definition": definition,
        "src_ips": src_ips
    }

# --- Main test entry ---

def extract_info_from_single_log(log: Dict[str, Any]) -> Dict[str, Any]:
    node = log.get("node", {})

    object_marking = node.get("objectMarking", [])
    definition = (
        object_marking[0]["definition"]
        if object_marking and "definition" in object_marking[0]
        else None
    )

    contexts = node.get("contexts", {})
    src_ips = contexts.get("src_ip", [])
    if isinstance(src_ips, str):
        src_ips = [src_ips]

    return {
        "definition": definition,
        "src_ips": src_ips
    }

# if __name__ == "__main__":
#     sample_log = {
#         "node": {
#             "objectMarking": [{"definition": "N-Health"}],
#             "contexts": {
#                 "src_ip": ["10.1.2.3", "192.168.0.5"]
#             }
#         }
#     }
#     from tools.Example_Log_Keeper import example_log_body2 as sample_log


#     extracted = extract_info_from_single_log(sample_log)
#     print("Extracted:", extracted)
