"""
Enhanced configuration module for Agent AI system.
Supports both YAML and environment variable configuration.
"""
import os
import yaml
from typing import Dict, Any, Optional
from dotenv import load_dotenv


class Config:
    """Enhanced configuration class with support for environment variables and YAML."""
    
    def __init__(self, config_path: Optional[str] = None):
        # Load environment variables
        load_dotenv()
        
        # Load YAML config if provided
        self.yaml_config = {}
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as file:
                self.yaml_config = yaml.safe_load(file) or {}
        
        # Initialize configuration
        self._init_llm_config()
        self._init_nats_config()
        self._init_webapp_config()
        self._init_logging_config()
    
    def _init_llm_config(self):
        """Initialize LLM configuration for Ollama only."""
        yaml_llm = self.yaml_config.get('llm', {})
        
        # Ollama configuration
        self.LLM_MODEL = os.getenv('LLM_MODEL', yaml_llm.get('local_model', 'llama4:128x17b'))
        self.LLM_TEMPERATURE = float(os.getenv('LLM_TEMPERATURE', yaml_llm.get('temperature', 0.05)))
        self.LOCAL_LLM_URL = os.getenv('LOCAL_LLM_URL', yaml_llm.get('local_url', 'http://localhost:11434/api/generate'))
        self.LLM_MAX_TOKENS = int(os.getenv('LLM_MAX_TOKENS', yaml_llm.get('max_tokens', 2048)))
    
    def _init_nats_config(self):
        """Initialize NATS configuration."""
        yaml_nats = self.yaml_config.get('nats', {})
        yaml_subjects = yaml_nats.get('subjects', {})
        
        self.NATS_SERVER_URL = os.getenv('NATS_SERVER_URL', yaml_nats.get('server_url', 'nats://localhost:4222'))
        self.AUTO_OPEN_CONNECTION = os.getenv('AUTO_OPEN_CONNECTION', 'true').lower() == 'true'
        
        # Stream configuration
        self.NATS_STREAM_NAME = os.getenv('NATS_STREAM_NAME', yaml_nats.get('stream_name', 'AGENT_AI_PIPELINE'))
        self.NATS_STREAM_PREFIX = os.getenv('NATS_STREAM_PREFIX', 'agentAI')
        self.DURABLE_NAME = os.getenv('DURABLE_NAME', 'agent_ai_durable')
        self.QUEUE_NAME = os.getenv('QUEUE_NAME', 'agent_ai_queue')
        
        # Subject configuration
        input_suffix = os.getenv('INPUT_SUBJECT_SUFFIX', '.input')
        analysis_suffix = os.getenv('ANALYSIS_SUBJECT_SUFFIX', '.analysis')
        output_suffix = os.getenv('OUTPUT_SUBJECT_SUFFIX', '.output')
        
        self.INPUT_SUBJECT = yaml_subjects.get('input', f"{self.NATS_STREAM_PREFIX}{input_suffix}")
        self.ANALYSIS_SUBJECT = yaml_subjects.get('analysis', f"{self.NATS_STREAM_PREFIX}{analysis_suffix}")
        self.OUTPUT_SUBJECT = yaml_subjects.get('output', f"{self.NATS_STREAM_PREFIX}{output_suffix}")
    
    def _init_webapp_config(self):
        """Initialize web app configuration."""
        yaml_webapp = self.yaml_config.get('webapp', {})
        
        self.WEBAPP_HOST = os.getenv('WEBAPP_HOST', yaml_webapp.get('host', '0.0.0.0'))
        self.WEBAPP_PORT = int(os.getenv('WEBAPP_PORT', yaml_webapp.get('port', 5000)))
        self.WEBAPP_DEBUG = os.getenv('WEBAPP_DEBUG', str(yaml_webapp.get('debug', True))).lower() == 'true'
    
    def _init_logging_config(self):
        """Initialize logging configuration."""
        yaml_logging = self.yaml_config.get('logging', {})
        
        self.LOG_LEVEL = os.getenv('LOG_LEVEL', yaml_logging.get('level', 'INFO'))
        self.LOG_FORMAT = os.getenv('LOG_FORMAT', yaml_logging.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    
    
    def get_llm_config(self) -> Dict[str, Any]:
        """Get LLM configuration as dictionary for Ollama."""
        return {
            'local_model': self.LLM_MODEL,
            'temperature': self.LLM_TEMPERATURE,
            'max_tokens': self.LLM_MAX_TOKENS,
            'local_url': self.LOCAL_LLM_URL,
            'use_local_ollama': True
        }
    
    def get_nats_config(self) -> Dict[str, Any]:
        """Get NATS configuration as dictionary."""
        return {
            'server_url': self.NATS_SERVER_URL,
            'stream_name': self.NATS_STREAM_NAME,
            'auto_open_connection': self.AUTO_OPEN_CONNECTION,
            'durable_name': self.DURABLE_NAME,
            'queue_name': self.QUEUE_NAME,
            'subjects': {
                'input': self.INPUT_SUBJECT,
                'analysis': self.ANALYSIS_SUBJECT,
                'output': self.OUTPUT_SUBJECT
            }
        }
    
    def get_webapp_config(self) -> Dict[str, Any]:
        """Get web app configuration as dictionary."""
        return {
            'host': self.WEBAPP_HOST,
            'port': self.WEBAPP_PORT,
            'debug': self.WEBAPP_DEBUG
        }


# Global configuration instance
def get_config(config_path: Optional[str] = None) -> Config:
    """Get global configuration instance."""
    config_file = config_path or os.path.join(os.path.dirname(__file__), 'config.yaml')
    return Config(config_file)


# Default configuration instance
cfg = get_config()