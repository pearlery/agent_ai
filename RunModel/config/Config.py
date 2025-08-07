# config.py
from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    def __init__(self):
        self.NAT_SERVER_URL = os.getenv("NAT_SERVER_URL")
        self.AUTO_OPEN_CONNECTION = os.getenv("AUTO_OPEN_CONNECTION", "false").lower() == "true"
        self.STREAM_NAME = os.getenv("STREAM_NAME", "model_server_stream")
        self.STREAM_PREFIX = os.getenv("STREAM_PREFIX", "agent-test")
        self.DURABLE_NAME = os.getenv("DURABLE_NAME", "model_server_durable_type_agent")
        self.INPUT_SUBJECT = self.STREAM_PREFIX + os.getenv("INPUT_SUBJECT_SUFFIX", ".Type")
        self.OUTPUT_SUBJECT = self.STREAM_PREFIX + os.getenv("OUTPUT_SUBJECT_SUFFIX", ".Context")
        self.QUEUE_NAME = os.getenv("QUEUE_NAME", "model_server_queue_type_agent")
cfg = Config()