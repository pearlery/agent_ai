from control.record_alert import append_json
from pathlib import Path
import json
from NatsFunction.Nats_Pub import publish_Js_message as publish_js_message
from control.timeline import build_timeline_payload

from pathlib import Path

async def startFlow(data_str: str) -> str:
    try:
        json_data = json.loads(data_str)
        append_json(file_path=Path("database/start_log.json"), new_entry=json_data)
        await publish_js_message(subject="agentAI.websoc", message=build_timeline_payload(1,alertid="not_included_yet"))
        return "success"
    except json.JSONDecodeError:
        return "error: invalid JSON"
    except Exception as e:
        return f"error: {str(e)}"

async def finishedType(data_str: str) -> str:
    try:
        data = json.loads(data_str)  

        append_json(file_path=Path("database/type_log.json"), new_entry=data)
        await publish_js_message(subject="agentAI.websoc", message=build_timeline_payload(5,alertid="not_included_yet"))
        return "success"
    except json.JSONDecodeError as e:
        return f"error: invalid JSON - {str(e)}"
    except Exception as e:
        return f"error: {str(e)}"

async def finishedFlow(data_str: str) -> str:
    try:
        data = json.loads(data_str)

        # Case: Upstream agent returned a structured error
        if data.get("status") == "error":
            err_msg = str(data.get("message", "Unknown error from agent"))
            await publish_js_message(
                subject="agentAI.websoc",
                message=build_timeline_payload(7, error=err_msg, alertid="not_included_yet")
            )
            return f"error: {err_msg}"

        # Case: Normal success flow
        append_json(file_path=Path("database/context_log.json"), new_entry=data)
        await publish_js_message(
            subject="agentAI.websoc",
            message=build_timeline_payload(7, alertid="not_included_yet")
        )
        return "success"

    except json.JSONDecodeError as e:
        err_msg = f"Invalid JSON - {str(e)}"
        await publish_js_message(
            subject="agentAI.websoc",
            message=build_timeline_payload(7, error=err_msg, alertid="not_included_yet")
        )
        return f"error: {err_msg}"

    except Exception as e:
        err_msg = str(e)
        await publish_js_message(
            subject="agentAI.websoc",
            message=build_timeline_payload(7, error=err_msg, alertid="not_included_yet")
        )
        return f"error: {err_msg}"
# async def finishedFlow(data_str: str) -> str:
#     try:
#         data = json.loads(data_str)  

#         append_json(file_path=Path("database/context_log.json"), new_entry=data)
#         await publish_js_message(subject="agentAI", message=build_timeline_payload(7,alertid="not_included_yet"))
#         return "success"
#     except json.JSONDecodeError as e:
#         await publish_js_message(subject="agentAI", message=build_timeline_payload(7,error=e,alertid="not_included_yet"))
#         return f"error: invalid JSON - {str(e)}"
#     except Exception as e:
#         await publish_js_message(subject="agentAI", message=build_timeline_payload(7,error=e,alertid="not_included_yet"))
#         return f"error: {str(e)}"

# async def send_status(status: int, error: str = None):
#     match status:
#         case 0:
#             await publish_js_message(subject="agentAI", message=build_timeline_payload(0))
#         case 1:
#             await publish_js_message(subject="agentAI", message=build_timeline_payload(1))
#         case 2:
#             await publish_js_message(subject="agentAI", message="status 2")
#         case 3:
#             await publish_js_message(subject="agentAI", message="status 3")
#         case _:
#             print(f"[] Impossible status: {status}")
    
