# Agent AI Control Agent

## Overview

The Control Agent is an orchestrator component that manages the entire Agent AI workflow, similar to the original ControlAgent in your previous project. It provides:

- **Workflow Orchestration**: Manages the flow from alert reception to final recommendations
- **Timeline Tracking**: Tracks processing stages and handles errors
- **Data Persistence**: Records workflow data in database files
- **API Interface**: REST API endpoints for external integration
- **Status Management**: Real-time status updates via NATS

## Features

### Workflow Stages
1. **Received Alert** - Initial alert processing
2. **Type Agent** - Classification and analysis
3. **Analyze Root Cause** - Deep analysis
4. **Triage Status** - Prioritization
5. **Action Taken** - Response actions
6. **Tool Status** - Security tool monitoring
7. **Recommendation** - Final recommendations

### API Endpoints

#### Control Endpoints
- `POST /control/start` - Start processing a new alert
- `POST /control/type/finished` - Mark type classification complete
- `POST /control/flow/finished` - Mark entire workflow complete
- `GET /control/status/{session_id}` - Get session status
- `GET /control/sessions` - List all sessions
- `DELETE /control/session/{session_id}` - Delete session
- `GET /control/health` - Health check

#### Usage Examples

**Start a new workflow:**
```bash
curl -X POST "http://localhost:9002/control/start" \
  -H "Content-Type: application/json" \
  -d '{
    "alert_id": "alert-001",
    "data": {
      "alert_name": "Suspicious PowerShell Activity",
      "severity": "High",
      "events": [...]
    }
  }'
```

**Complete type classification:**
```bash
curl -X POST "http://localhost:9002/control/type/finished" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "session-uuid",
    "data": {
      "technique_id": "T1059.001",
      "technique_name": "PowerShell",
      "tactic": "Execution",
      "confidence_score": 0.95
    }
  }'
```

**Complete entire workflow:**
```bash
curl -X POST "http://localhost:9002/control/flow/finished" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "session-uuid",
    "data": {
      "status": "success",
      "report": "# Incident Report\n...",
      "recommendations": [...]
    }
  }'
```

## Integration

### With Existing Agents
The Control Agent works alongside your existing agents:
- **Input Agent** → publishes alerts
- **Analysis Agent** → performs MITRE ATT&CK analysis  
- **Recommendation Agent** → generates reports
- **Control Agent** → orchestrates the entire flow

### Database Files
Creates the following database files in `database/` directory:
- `start_log.json` - Initial alert records
- `type_log.json` - Classification results
- `context_log.json` - Final workflow results

### Output Format
Maintains compatibility with your existing `output.json` format:
```json
{
  "agent.overview.updated": [...],
  "agent.tools.updated": [...],
  "agent.recommendation.updated": [...],
  "agent.checklist.updated": [...],
  "agent.executive.updated": [...],
  "agent.attack.updated": [...],
  "agent.timeline.updated": [...]
}
```

## Running

### Start Control Agent
```bash
python start_control_agent.py
```

### With Docker
```bash
docker build -t agent-ai-control .
docker run -p 9002:9002 agent-ai-control
```

### Configuration
Uses the same configuration system as other agents:
- Environment variables from `.env`
- YAML configuration from `config/config.yaml`
- NATS connection settings
- Ollama LLM settings

## Monitoring

- **Health Check**: `GET /control/health`
- **Session List**: `GET /control/sessions`
- **Timeline Updates**: Published to `agentAI.websoc` NATS subject
- **Logs**: Standard Python logging to console

## Error Handling

The Control Agent handles errors at each stage:
- Invalid JSON in requests
- Agent processing failures
- NATS communication errors
- Timeline tracking errors

Errors are recorded in:
- Timeline with error status
- Executive summary updates
- Database logs
- NATS error publications

This maintains the same error handling behavior as your original ControlAgent.