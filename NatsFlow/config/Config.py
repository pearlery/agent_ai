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
cfg = Config()