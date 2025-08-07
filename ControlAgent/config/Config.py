import os
from dotenv import load_dotenv

class Config:
    def __init__(self):
        load_dotenv()  # โหลดตัวแปรจาก .env
        # LLM Configuration
        self.LLM_MODEL = os.getenv('LLM_MODEL')
        self.LLM_TEMPERATURE = float(os.getenv('LLM_TEMPERATURE', 0.05))
        self.LOCAL_LLM_URL = os.getenv('LOCAL_LLM_URL')
        
        #LangSmith
        os.environ["LANGCHAIN_TRACING_V2"] = os.getenv("LANGCHAIN_TRACING_V2")
        os.environ["LANGCHAIN_ENDPOINT"] = os.getenv("LANGCHAIN_ENDPOINT")
        os.environ["LANGCHAIN_API_KEY"] = os.getenv('LANGSMITH_API_KEY')
        os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGCHAIN_PROJECT")
        
        self.NAT_SERVER_URL = os.getenv("NAT_SERVER_URL")
        self.AUTO_OPEN_CONNECTION = os.getenv("AUTO_OPEN_CONNECTION", "true").lower() == "true"
        self.STREAM_NAME = os.getenv("STREAM_NAME", "model_server_stream")
        self.STREAM_PREFIX = os.getenv("STREAM_PREFIX", "agent-test")
        self.DURABLE_NAME1 = os.getenv("DURABLE_NAME1", "model_server_durable_context_agent")
        self.DURABLE_NAME2 = os.getenv("DURABLE_NAME2", "model_server_durable_context_agent")
        self.DURABLE_NAME3 = os.getenv("DURABLE_NAME3", "model_server_durable_context_agent")
        self.INPUT_SUBJECT1 = self.STREAM_PREFIX + os.getenv("INPUT_SUBJECT_SUFFIX1", ".Type")
        self.INPUT_SUBJECT2 = self.STREAM_PREFIX + os.getenv("INPUT_SUBJECT_SUFFIX2", ".Context")
        self.INPUT_SUBJECT3 = self.STREAM_PREFIX + os.getenv("INPUT_SUBJECT_SUFFIX3", ".Output")
        self.OUTPUT_SUBJECT = self.STREAM_PREFIX + os.getenv("OUTPUT_SUBJECT_SUFFIX", ".Ending")
        #Buged it is not reading from .env file fix later
        self.QUEUE_NAME = os.getenv("QUEUE_NAME", "model_server_queue_context_agent")
cfg = Config()