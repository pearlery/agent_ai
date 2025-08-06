
# NATS and project configuration
NATS_URL = 'nats://192.168.55.158:31653'

# JetStream Subjects
INPUT_SUBJECT = 'agentAI.Input'
TYPE_SUBJECT = 'agentAI.Type'
CONTEXT_SUBJECT = 'agentAI.Context'
RECOMMEND_SUBJECT = 'agentAI.Recommendation'
OUTPUT_SUBJECT = 'agentAI.Output'

# Local LLM Configuration (Qwen3 via Ollama or compatible endpoint)
LLM_MODEL = 'qwen3:235b'
LLM_TEMPERATURE = 0.05
LOCAL_LLM_URL = 'http://192.168.123.110:11434/'
