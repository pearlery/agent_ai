#from contexts.Recommendation_From_Log import call_recommendation_agent_from_script
from agents.agent_factory import call_recommendation_agent_from_script
from NatsFunction.Nats_Pub import publish_Js_message 
import json
from config.Config import cfg
subscribed_subject = None

async def send_to_next_agent_json(data_str):
    try:
        data_dict = json.loads(data_str)

        # Step 1: Call the recommendation agent
        result_wrapper = await call_recommendation_agent_from_script(data_dict)

        # Step 2: Convert outer wrapper if it's a JSON string
        if isinstance(result_wrapper, str):
            try:
                result_wrapper = json.loads(result_wrapper)
            except json.JSONDecodeError as e:
                error_msg = f"Invalid top-level JSON string returned by agent: {e}"
                print(f"❌ {error_msg}")
                error_payload = {
                    "status": "error",
                    "message": error_msg,
                    "raw": result_wrapper
                }
                await publish_Js_message(cfg.OUTPUT_SUBJECT, error_payload)
                return error_payload

        # Step 3: Validate it's a dict
        if not isinstance(result_wrapper, dict):
            error_msg = f"Agent output is not a dict. Got: {type(result_wrapper)}"
            print(f"❌ {error_msg}")
            error_payload = {
                "status": "error",
                "message": error_msg,
                "raw": str(result_wrapper)
            }
            await publish_Js_message(cfg.OUTPUT_SUBJECT, error_payload)
            return error_payload

        # Step 4: Decode the 'result' field if it is a string
        result_field = result_wrapper.get("result")
        if isinstance(result_field, str):
            try:
                result_wrapper["result"] = json.loads(result_field)
                print("✅ Decoded stringified result field into real JSON.")
            except json.JSONDecodeError as e:
                error_msg = f"'result' field is not valid JSON: {e}"
                print(f"❌ {error_msg}")
                error_payload = {
                    "status": "error",
                    "message": error_msg,
                    "raw": result_wrapper
                }
                await publish_Js_message(cfg.OUTPUT_SUBJECT, error_payload)
                return error_payload

        # ✅ Step 5: Publish and return the full structure
        await publish_Js_message(cfg.OUTPUT_SUBJECT, result_wrapper)
        print("✅ Published full agent response to OUTPUT_SUBJECT.")
        return result_wrapper

    except Exception as e:
        error_msg = f"Exception during processing: {e}"
        print(f"❌ {error_msg}")
        error_payload = {
            "status": "error",
            "message": error_msg,
            "raw": data_str
        }
        await publish_Js_message(cfg.OUTPUT_SUBJECT, error_payload)
        return error_payload



"""
async def send_to_next_agent_json(data_str):
    try:
        data_dict = json.loads(data_str)

        # Run the model
        result_wrapper = await call_recommendation_agent_from_script(data_dict)  #temp_clean

        # Strip markdown formatting if present mostly clear out by prompt but might presist in some long prompt (not enough token)
        cleaned = result_wrapper.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]  # remove leading ```json
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]  # remove trailing ```

        # Final strip & parse
        result_json = json.loads(cleaned.strip())
        await publish_js_message(cfg.OUTPUT_SUBJECT, result_json)
        return result_json
    
    except Exception as e:
        error_json_package = {
        "status": "error", 
        "result": { 
            "errorMessage" : e
            }
        }
        await publish_js_message(cfg.OUTPUT_SUBJECT, error_json_package)
        return error_json_package

async def send_to_next_agent(data_str):
    #Log the received message
    
    data_dict = json.loads(data_str)
    with open("log.txt", "a", encoding="utf-8") as f:
        f.write(data_str)
    try:    
        #Run The Model and Publish the result
        result = await call_recommendation_agent_from_script(data_dict)
        Pub_Out = await publish_js_message(cfg.OUTPUT_SUBJECT, result)
        #print(f"Data Sucessfully Pub : {Pub_Out}")
        return None
        
    except Exception as e:
        data_str = f"<decode-error: {e}>"
        with open("log.txt", "a", encoding="utf-8") as f:
            f.write(data_str)

temp_clean = {
  "status": "success", 
  "result": {
    "agent.overview.updated": {
      "data": {
        "description": "The security log indicates a 'HTTP Unauthorized Brute Force Attack' detected by PAN NGFW involving user 'bdms\\kunnika.le' and source IP '10.166.4.30'. The alert was closed as a false positive. The task is to recommend how to investigate or detect this security log using the client's available tools and configurations."
      }
    },
    "agent.tools.updated": {
      "data": [
        { "name": "Palo Alto", "status": "active" },
        { "name": "TrendMicro", "status": "active" }
      ]
    }
  }
}
"""
