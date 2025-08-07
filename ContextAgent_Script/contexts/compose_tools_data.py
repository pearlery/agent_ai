# contexts/clientInfo/compose_tools_data.py
import json
from typing import Dict, Any
from contexts.extract_ip_and_definition import extract_info_from_single_log
from contexts.get_ip_info import search_multiple_ip_contexts
from contexts.load_onboarding_context import load_onboarding_context_from_log

def validate_client_exists(definition: str, registry_path: str = "contexts/clientInfo/client_registry.json") -> bool:
    try:
        with open(registry_path, "r", encoding="utf-8") as f:
            registry_data = json.load(f)
        client_list = registry_data.get("client", [])
        for client in client_list:
            if client.get("name") == definition and client.get("onBoarding", False):
                return True
        return False
    except Exception as e:
        raise ValueError(f"Error reading client registry: {e}")


async def compose_full_tools_data_from_log(log_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Compose a full tools_data JSON with:
    - currentTechnologies (always included)
    - ip (based on longest-prefix match for all found IPs)
    """
    # Step 1: Extract client name and IPs
    context_input = extract_info_from_single_log(log_data)
    definition = context_input.get("definition")
    src_ips = context_input.get("src_ips", [])

    if not definition:
        raise ValueError("Missing objectMarking 'definition' in log data.")

    # Step 2: Validate client existence
    if not validate_client_exists(definition):
        return {
            "message": "No client onboarding data available for this definition."
        }

    # Step 3: Load onboarding context and extract data
    onboarding_context = load_onboarding_context_from_log(log_data)
    onboarding_data = (
        onboarding_context[0]["data"]["onBoarding"]
        if isinstance(onboarding_context, list)
        else onboarding_context["data"]["onBoarding"]
    )

    # Optional: Debug write
    with open("debug_log_data.json", "w", encoding="utf-8") as f:
        json.dump(log_data, f, indent=2)

    if not src_ips:
        raise ValueError("Missing src_ips in log contexts.")

    ip_data_list = await search_multiple_ip_contexts(src_ips, onboarding_data)

    return {
        "currentTechnologies": onboarding_data.get("currentTechnologies", []),
        "ip": ip_data_list
    }
