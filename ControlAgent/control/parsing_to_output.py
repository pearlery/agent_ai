import json
from NatsFunction.Nats_Pub import publish_js_message
from config.Config import cfg
async def strip_status(input):
    try:
        data_dict = json.loads(input)

        # Strip markdown formatting if present mostly clear out by prompt but might presist in some long prompt (not enough token)
        cleaned = data_dict.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]  # remove leading ```json
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]  # remove trailing ```

        # Final strip & parse
        result_json = json.loads(cleaned.strip())
        await publish_js_message(cfg.OUTPUT_SUBJECT, result_json)
        return result_json
    except Exception as e :
        print(f"error as {e}")
        return None