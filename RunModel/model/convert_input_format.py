def convert_input_format(wrapped_input: dict) -> dict:
    """
    Takes a dictionary with key 'node' and extracts fields for prediction.

    Args:
        wrapped_input (dict): JSON object with 'node' key.

    Returns:
        dict: Flattened input for prediction, aligned with model DataFrame format.
    """
    try:
        node = wrapped_input.get("node", {})

        # Extract contexts
        contexts = node.get("contexts", {})
        hostname = contexts.get("hostname")
        endpoint_type = contexts.get("endpoint_type")
        os_type = contexts.get("os")
        src_ip_raw = contexts.get("src_ip", [])
        src_ip = ";".join(src_ip_raw) if isinstance(src_ip_raw, list) else str(src_ip_raw)

        # Extract sla
        sla = node.get("sla", {})
        sla_mttv = sla.get("mttv")

        # Extract objectMarking definition
        object_marking = node.get("objectMarking", [])
        object_marking_def = (
            object_marking[0]["definition"] if object_marking and "definition" in object_marking[0] else None
        )

        return {
            'severity': [node.get("severity")],
            'alert_status': [node.get("alert_status")],
            'log_source': [node.get("log_source")],
            'tags': [node.get("tags")],
            'objectMarking': [object_marking_def],
            'alert_name': [node.get("alert_name")],
            'sla_mttv': [sla_mttv],
            'hostname': [hostname],
            'endpoint_type': [endpoint_type],
            'os': [os_type],
            'src_ip': [src_ip]
        }

    except Exception as e:
        print("Error during input conversion:", e)
        raise
