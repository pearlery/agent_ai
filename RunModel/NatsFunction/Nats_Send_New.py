from model.predict_if_mitre_empty import predict_check_package
from NatsFunction.Nats_Pub import publish_Js_message as publish_js_message
import json
from config.Config import cfg
from pydantic import BaseModel
subscribed_subject = None

async def send_to_next_agent(data_str):
    #Log the received message
        
    data_dict = json.loads(data_str)
    print(f"log received data: {data_dict}")
    try:    
        #Run The Model and Publish the result
        result = predict_check_package(data_dict)
        Pub_Out = await publish_js_message(cfg.OUTPUT_SUBJECT, result)
        #print(f"Data Sucessfully Pub : {Pub_Out}")
        with open("log.txt", "a", encoding="utf-8") as f:
            f.write({Pub_Out})
        
    except Exception as e:
        data_str = f"<decode-error: {e}>"
        with open("log.txt", "a", encoding="utf-8") as f:
            f.write(data_str)