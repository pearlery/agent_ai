# 🐳 Docker Services Overview

## Services ที่จะรันเมื่อใช้ Docker Compose

### 1. **NATS JetStream Server** (`nats-server`)
- **Image**: `nats:2.10-alpine`
- **Container**: `agent-ai-nats-server`
- **Port**: `8222` (HTTP monitoring)
- **Internal Port**: `4222` (NATS protocol)
- **Purpose**: Message streaming สำหรับการสื่อสารระหว่าง agents
- **Health Check**: ✅ Port 4222
- **Status**: **พร้อมใช้งาน**

### 2. **Agent AI Application** (`agent-ai`)
- **Image**: Built from local Dockerfile
- **Container**: `agent-ai-app`
- **Ports**:
  - `5000:5000` - **Web Interface**
  - `9004:9004` - **Control Agent API** (ใหม่!)
- **Services ที่รัน**:
  - 🌐 **Web App** (Flask) - Dashboard และ UI
  - 🎛️ **Control Agent API** (FastAPI) - Timeline และ control endpoints
  - 🤖 **Analysis Agent** - MITRE ATT&CK analysis
  - 💡 **Recommendation Agent** - Security recommendations
  - 📥 **Input Agent** - Alert processing
- **Dependencies**: NATS Server
- **Health Check**: ✅ ทั้ง Web App และ Control Agent API
- **Status**: **อัพเดทแล้ว - รวม Control Agent**

### 3. **Ollama LLM** (`ollama`) - Optional
- **Image**: `ollama/ollama:latest`
- **Container**: `agent-ai-ollama`
- **Port**: `11434:11434`
- **Purpose**: Local LLM สำหรับการวิเคราะห์
- **Profile**: `ollama` (รันเมื่อต้องการ)
- **Status**: **พร้อมใช้งาน**

## 🚀 วิธีการรัน

### รันทั้งหมด (ไม่มี Ollama):
```bash
docker-compose up -d
```

### รันพร้อม Ollama:
```bash
docker-compose --profile ollama up -d
```

### ตรวจสอบ status:
```bash
docker-compose ps
```

## 🔌 Endpoints ที่สามารถเข้าถึงได้

| Service | URL | Description |
|---------|-----|-------------|
| **Web Dashboard** | http://localhost:5000 | หน้า UI หลัก |
| **Control Agent API** | http://localhost:9004 | API สำหรับควบคุมระบบ |
| **API Documentation** | http://localhost:9004/docs | FastAPI Swagger docs |
| **NATS Monitoring** | http://localhost:8222 | NATS server status |
| **Ollama API** | http://localhost:11434 | LLM API (ถ้าเปิด) |

## 🎯 Timeline API Endpoints

จาก Control Agent API (port 9004):

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/start` | เริ่ม processing (Received Alert) |
| POST | `/control/type/finished` | Type Agent เสร็จ |
| POST | `/control/flow/finished` | Workflow เสร็จสิ้น |
| GET | `/control/status/{session_id}` | ดู timeline status |
| GET | `/control/sessions` | ดูทุก sessions |

## 📊 Timeline Stages

ระบบจะติดตาม 7 stages:
1. **Received Alert** - รับ alert เข้าระบบ
2. **Type Agent** - วิเคราะห์ประเภท threat
3. **Analyze Root Cause** - วิเคราะห์สาเหตุ
4. **Triage Status** - จัดลำดับความสำคัญ
5. **Action Taken** - ดำเนินการ
6. **Tool Status** - สถานะเครื่องมือ
7. **Recommendation** - ข้อเสนอแนะ

## 🔧 Environment Variables

สำหรับ Docker Compose:
```yaml
# NATS
NATS_SERVER_URL=nats://nats-server:4222
AUTO_OPEN_CONNECTION=true

# LLM (ใช้ Ollama หรือ external API)
LLM_MODEL=Qwen/Qwen3-32B
LLM_TEMPERATURE=0.05

# Web App
WEBAPP_HOST=0.0.0.0
WEBAPP_PORT=5000

# Logging
LOG_LEVEL=INFO
```

## ✅ สิ่งที่แก้ไขแล้ว

1. ✅ **เพิ่ม Control Agent port 9004**
2. ✅ **อัพเดท health checks สำหรับทั้ง 2 services**
3. ✅ **แก้ Dockerfile ให้รัน orchestrator แทน webapp เท่านั้น**
4. ✅ **เพิ่ม Docker mode ที่รัน Web App + Control Agent พร้อมกัน**
5. ✅ **Timeline stages ตามที่กำหนด**

## 🎉 ผลลัพธ์

เมื่อรัน `docker-compose up -d` จะได้:

- **NATS Server** - Message streaming
- **Web Dashboard** (port 5000) - UI
- **Control Agent API** (port 9004) - Timeline API
- **Analysis & Recommendation Agents** - Background processing
- **Timeline tracking ทั้ง 7 stages**
- **Health monitoring สำหรับทุก services**

ระบบพร้อมใช้งานครบถ้วน! 🚀