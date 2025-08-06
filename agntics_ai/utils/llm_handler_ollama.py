"""
Simplified LLM handler for Ollama only.
"""
import logging
from typing import List, Dict, Any
import aiohttp
import json

logger = logging.getLogger(__name__)


async def get_llm_completion(messages: List[Dict[str, str]], llm_config: Dict[str, Any], max_retries: int = 3) -> str:
    """
    Get completion from Ollama local API with retry logic.
    
    Args:
        messages: List of message dictionaries with 'role' and 'content' keys
        llm_config: LLM configuration containing local_url, local_model, etc.
        max_retries: Maximum number of retry attempts
        
    Returns:
        str: The content of the LLM response
        
    Raises:
        Exception: If API call fails after all retries
    """
    last_exception = None
    
    for attempt in range(max_retries + 1):
        try:
            # Convert messages to Ollama format
            prompt = _convert_messages_to_prompt(messages)
            
            # Prepare Ollama request
            ollama_data = {
                "model": llm_config.get('local_model', 'qwen3:235b'),
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": llm_config.get('temperature', 0.05),
                    "num_predict": llm_config.get('max_tokens', 2048)
                }
            }
            
            # Make request to Ollama
            local_url = llm_config.get('local_url', 'http://localhost:11434/api/generate')
            
            # Set timeout based on attempt (progressive timeout)
            timeout = aiohttp.ClientTimeout(total=30 + (attempt * 10))
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(local_url, json=ollama_data) as response:
                    if response.status == 200:
                        result = await response.json()
                        content = result.get('response', '')
                        if attempt > 0:
                            logger.info(f"Ollama completion successful on attempt {attempt + 1}, response length: {len(content)}")
                        else:
                            logger.debug(f"Ollama completion successful, response length: {len(content)}")
                        return content
                    else:
                        error_text = await response.text()
                        logger.warning(f"Ollama API error on attempt {attempt + 1}: {response.status} - {error_text}")
                        last_exception = Exception(f"Ollama API error: {response.status}")
                        
                        # Don't retry on client errors (4xx)
                        if 400 <= response.status < 500:
                            break
                        
        except aiohttp.ClientError as e:
            logger.warning(f"Ollama connection error on attempt {attempt + 1}: {e}")
            last_exception = Exception(f"Ollama connection error: {e}")
        except asyncio.TimeoutError as e:
            logger.warning(f"Ollama timeout on attempt {attempt + 1}: {e}")
            last_exception = Exception(f"Ollama timeout error: {e}")
        except Exception as e:
            logger.warning(f"Unexpected error on attempt {attempt + 1}: {e}")
            last_exception = Exception(f"Ollama completion failed: {e}")
        
        # Wait before retrying (exponential backoff)
        if attempt < max_retries:
            wait_time = min(2 ** attempt, 10)  # Cap at 10 seconds
            logger.info(f"Retrying in {wait_time} seconds... (attempt {attempt + 2}/{max_retries + 1})")
            await asyncio.sleep(wait_time)
    
    # All retries failed
    logger.error(f"Ollama completion failed after {max_retries + 1} attempts")
    raise last_exception or Exception("Ollama completion failed after all retries")


def _convert_messages_to_prompt(messages: List[Dict[str, str]]) -> str:
    """Convert OpenAI-style messages to a single prompt string for Ollama."""
    prompt_parts = []
    
    for message in messages:
        role = message.get('role', '')
        content = message.get('content', '')
        
        if role == 'system':
            prompt_parts.append(f"System: {content}")
        elif role == 'user':
            prompt_parts.append(f"User: {content}")
        elif role == 'assistant':
            prompt_parts.append(f"Assistant: {content}")
        else:
            prompt_parts.append(content)
    
    prompt_parts.append("Assistant:")  # Add final prompt for response
    return "\n\n".join(prompt_parts)


def create_analysis_prompt(log_data: Dict[str, Any], external_context: Dict[str, Any] = None) -> List[Dict[str, str]]:
    """
    Create a prompt for the Analysis Agent to map log data to MITRE ATT&CK framework.
    
    Args:
        log_data: Raw log data dictionary
        external_context: Additional context information
        
    Returns:
        List of message dictionaries for LLM API
    """
    system_prompt = """You are a meticulous cybersecurity analyst specializing in mapping raw log data to the MITRE ATT&CK framework. Your analysis must be evidence-based and precise. Your task is to analyze the provided JSON log object and the supplementary context, then identify the single most relevant MITRE ATT&CK Tactic and Technique (including sub-technique ID if applicable). You MUST respond with a single, valid JSON object and nothing else.

### INSTRUCTIONS:
1. Analyze the `log_data` and `external_context`.
2. Identify the most likely MITRE ATT&CK Tactic and Technique.
3. Provide a step-by-step reasoning for your conclusion, citing specific evidence from the input.
4. Provide a confidence score from 0.0 to 1.0.
5. Format your entire output as a single JSON object matching the schema in the examples.

### EXAMPLE OUTPUT FORMAT:
{
  "technique_id": "T1059.001",
  "technique_name": "PowerShell",
  "tactic": "Execution",
  "confidence_score": 0.95,
  "reasoning": "The log shows the execution of 'powershell.exe' with a base64 encoded command ('-enc'). This is a classic indicator of the PowerShell technique (T1059.001) being used for execution, as adversaries often use encoding to obfuscate their commands."
}"""
    
    input_data = {
        "log_data": log_data,
        "external_context": external_context or {}
    }
    
    user_prompt = f"""**INPUT:**
{input_data}

**OUTPUT:**"""
    
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]


def create_recommendation_prompt(analysis_data: Dict[str, Any]) -> List[Dict[str, str]]:
    """
    Create a prompt for the Recommendation Agent to generate incident response report.
    
    Args:
        analysis_data: Analysis results from the Analysis Agent
        
    Returns:
        List of message dictionaries for LLM API
    """
    system_prompt = """### ROLE ###
You are a world-class Tier-3 Security Operations Center (SOC) Analyst and Threat Intelligence Expert. You are calm, precise, and an expert communicator. You are writing a report for a technical security team at a mid-sized financial institution. Your analysis must be grounded strictly in the data provided.

### CONTEXT ###
- **Client Security Stack**: The client uses CrowdStrike Falcon (EDR), Splunk (SIEM), and Zscaler (Web Gateway).
- **Sector Threat Landscape**: The financial sector is currently being targeted by ransomware groups like LockBit and financially motivated actors like FIN7.

### TASK ###
Your task is to generate a comprehensive, actionable incident report in Markdown format. The report must be clear, concise, and targeted at a technical security audience. It must help them understand the incident and take immediate, effective action.

### OUTPUT FORMAT & CONSTRAINTS ###
The report MUST strictly follow this Markdown structure:

# Executive Summary
(Provide a brief, 3-sentence summary of the event, its severity based on the tactic, and the primary finding.)

# Alert Details
- **Timestamp**: {{timestamp}}
- **Hostname**: {{hostname}}
- **Key Indicators**: (List key indicators from the log)

# In-Depth Technical Analysis
(Provide a step-by-step narrative of what happened based on the analysis data.)

# MITRE ATT&CK Framework Mapping
- **Tactic**: {{tactic}}
- **Technique**: {{technique_id}} - {{technique_name}}

# Recommended Mitigation & Response Steps

## 1. Immediate Containment (Short-Term)
**Step 1.1 - Isolate Host:**
- **Action**: Immediately isolate the host from the network
- **Tool**: Use CrowdStrike Falcon console "Network Contain" feature

**Step 1.2 - Investigate with SIEM:**
- **Action**: Run Splunk query to search for similar activity
- **Tool**: Splunk query example provided

## 2. Strategic Hardening (Long-Term)
(Provide strategic recommendations based on the identified technique)"""
    
    user_prompt = f"""### INPUT DATA ###
Here is the complete analysis data in JSON format. Base your entire report ONLY on this information:

```json
{analysis_data}
```

Generate the incident report following the exact Markdown structure specified above."""
    
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]