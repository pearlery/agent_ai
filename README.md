# Agent AI System - Intelligent Security Analysis Platform

## 📋 สารบัญ (Table of Contents)
- [ภาพรวมระบบ](#ภาพรวมระบบ-overview)
- [หลักการทำงานและสถาปัตยกรรม](#หลักการทำงานและสถาปัตยกรรม-principles--architecture)
- [คุณสมบัติหลัก](#คุณสมบัติหลัก-key-features)
- [การเริ่มต้นใช้งาน](#การเริ่มต้นใช้งาน-getting-started)
- [การตั้งค่าและการกำหนดค่า](#การตั้งค่าและการกำหนดค่า-configuration)
- [คู่มือการใช้งาน](#คู่มือการใช้งาน-usage-guide)
- [Web Interface และ Real-time Monitoring](#web-interface-และ-real-time-monitoring)
- [API Documentation](#api-documentation)
- [การพัฒนาและขยายระบบ](#การพัฒนาและขยายระบบ-development--extension)
- [Troubleshooting](#troubleshooting)

## 🎯 ภาพรวมระบบ (Overview)

Agent AI System เป็นแพลตฟอร์มวิเคราะห์ความปลอดภัยแบบอัจฉริยะที่ขับเคลื่อนด้วย **Large Language Models (LLMs)** และสถาปัตยกรรมแบบ **Event-Driven Microservices** ระบบนี้ได้รับการออกแบบมาเพื่อประมวลผลและวิเคราะห์แจ้งเตือนความปลอดภัย (Security Alerts) จากระบบต่างๆ โดยอัตโนมัติ

### 🚀 วัตถุประสงค์หลัก
- **วิเคราะห์อัตโนมัติ**: ระบุเทคนิคการโจมตีตาม MITRE ATT&CK Framework
- **ให้คำแนะนำเชิงปฏิบัติ**: สร้างรายงานและขั้นตอนการแก้ไขปัญหา
- **รองรับ Real-time**: ประมวลผลแบบเรียลไทม์ผ่าน Message Queue
- **ปรับแต่งได้**: รองรับเครื่องมือและระบบหลากหลายของลูกค้า

## 🏗️ หลักการทำงานและสถาปัตยกรรม (Principles & Architecture)

### หลักการออกแบบ (Design Principles)

#### 1. **LLM-First Approach**
- **หลักการ**: ใช้ LLM เป็นหลักในการตัดสินใจ หลีกเลี่ยง rule-based logic
- **ประโยชน์**: ระบบมีความยืดหยุ่นสูง สามารถเรียนรู้และปรับตัวได้
- **การใช้งาน**: 
  - Analysis Agent ใช้ LLM วิเคราะห์ log และ map กับ MITRE ATT&CK
  - Recommendation Agent ใช้ LLM สร้างรายงานและคำแนะนำ

#### 2. **Event-Driven Architecture**
- **หลักการ**: ส่วนประกอบต่างๆ สื่อสารผ่าน Message Events
- **ประโยชน์**: Decoupling, Scalability, และ Resilience สูง
- **การใช้งาน**: NATS JetStream เป็น Message Broker กลาง

#### 3. **Microservices Pattern**
- **หลักการ**: แบ่งระบบเป็น Services เล็กๆ ที่มีหน้าที่เฉพาะ
- **ประโยชน์**: พัฒนา, deploy, และ scale แยกกันได้
- **Services**:
  - **Control Agent**: API Gateway และ Process Controller
  - **Analysis Agent**: MITRE ATT&CK Analysis
  - **Recommendation Agent**: Report Generation
  - **Web App**: Real-time Monitoring Interface

#### 4. **Tool-Agnostic Integration**
- **หลักการ**: รองรับเครื่องมือหลากหลายผ่านการกำหนดค่า
- **ประโยชน์**: ใช้ได้กับ Security Stack ของลูกค้าต่างๆ
- **การใช้งาน**: อ่านข้อมูล tool จาก JSON configuration files

### สถาปัตยกรรมระบบ (System Architecture)

```
┌─────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│   Web Client    │    │   External API   │    │   Demo Scripts   │
└─────────┬───────┘    └─────────┬────────┘    └─────────┬────────┘
          │                      │                       │
          ▼                      ▼                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Control Agent (FastAPI:9004)                 │
│                    - Timeline API (7 Stages)                    │
│                    - Session Management                         │
│                    - Process Orchestration                      │
│                    - Manual Workflow Control                    │
└─────────────────────────┬───────────────────────────────────────┘
                          │
          ┌───────────────┼───────────────┐
          ▼               ▼               ▼
┌─────────────────────────────────────────────────────────────────┐
│                  NATS JetStream Message Broker                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │agentAI.Input│  │agentAI.     │  │agentAI.Output           │  │
│  │             │  │Analysis     │  │                         │  │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘  │
└─────┬───────────────────┬───────────────────┬───────────────────┘
      │                   │                   │
      ▼                   ▼                   ▼
┌─────────────┐  ┌─────────────────┐  ┌─────────────────────────┐
│ Analysis    │  │ Recommendation  │  │     Web App (5000)      │
│ Agent       │  │ Agent           │  │  - Real-time Dashboard  │
│ - LLM       │  │ - LLM           │  │  - Timeline Tracking    │
│ - MITRE     │  │ - Tool          │  │  - Output Visualization │
│   ATT&CK    │  │   Integration   │  │  - SSE Updates          │
└─────────────┘  └─────────────────┘  └─────────────────────────┘
```

### Data Flow (การไหลของข้อมูล)

#### Phase 1: Alert Ingestion
```
External System → Control Agent → NATS (agentAI.Input)
```
- รับ Alert ผ่าน REST API
- สร้าง Session ID และ Timeline tracking
- เผยแพร่ไปยัง Message Queue

#### Phase 2: MITRE Analysis  
```
NATS (agentAI.Input) → Analysis Agent → LLM → NATS (agentAI.Analysis)
```
- ดึง Alert จาก Queue
- ใช้ LLM วิเคราะห์และ map กับ MITRE ATT&CK
- เผยแพร่ผลการวิเคราะห์ต่อ

#### Phase 3: Report Generation
```
NATS (agentAI.Analysis) → Recommendation Agent → Tool Loader → LLM → NATS (agentAI.Output)
```
- ดึงผลการวิเคราะห์จาก Queue
- โหลดข้อมูล Security Tools ของลูกค้า
- ใช้ LLM สร้างรายงานและคำแนะนำ
- เผยแพร่ผลลัพธ์สุดท้าย

### 📊 Timeline Stages (7 Stages Tracking)

ระบบติดตามขั้นตอนการประมวลผลแบบ real-time ผ่าน **Control Agent Timeline API**:

1. **"Received Alert"** - รับ security alert เข้าระบบ
2. **"Type Agent"** - วิเคราะห์ประเภทของ threat ด้วย Analysis Agent
3. **"Analyze Root Cause"** - วิเคราะห์สาเหตุรากของเหตุการณ์
4. **"Triage Status"** - จัดลำดับความรุนแรงและความสำคัญ
5. **"Action Taken"** - ดำเนินการตอบสนองและแก้ไข
6. **"Tool Status"** - ตรวจสอบสถานะเครื่องมือความปลอดภัย
7. **"Recommendation"** - สร้างคำแนะนำและรายงานด้วย Recommendation Agent

## ⚡ คุณสมบัติหลัก (Key Features)

### 🤖 AI-Powered Analysis
- **LLM Integration**: รองรับ Ollama (Local LLM) พร้อมระบบ retry และ timeout
- **MITRE ATT&CK Mapping**: ระบุเทคนิคการโจมตีแบบอัตโนมัติ
- **Contextual Analysis**: วิเคราะห์ log พร้อม context ที่เกี่ยวข้อง

### 🔄 Event-Driven Processing
- **NATS JetStream**: Message broker ที่เสถียรและ scalable
- **Async Processing**: ประมวลผลแบบ asynchronous ทั้งระบบ
- **Durable Subscriptions**: รองรับการ recovery และ replay messages

### 📊 Real-Time Monitoring
- **Web Dashboard**: ติดตามสถานะการประมวลผลแบบ real-time
- **Progress Tracking**: แสดงความคืบหน้าของแต่ละขั้นตอน
- **Timeline Visualization**: แสดง timeline การประมวลผล

### 🛠️ Tool Integration
- **Customer-Specific Tools**: รองรับเครื่องมือของลูกค้าแต่ละราย
- **Dynamic Tool Loading**: อ่านข้อมูล tool แบบ dynamic
- **Intelligent Recommendations**: แนะนำการใช้เครื่องมือตามสถานการณ์

### 🎛️ Control Agent API (NEW!)
- **Timeline API**: RESTful API สำหรับติดตาม 7 stages แบบ real-time
- **Session Management**: จัดการ session และ workflow ด้วย API
- **Manual Control**: สามารถควบคุมขั้นตอนการประมวลผลแบบ manual
- **FastAPI Integration**: Auto-generated API docs ที่ `/docs`
- **Health Monitoring**: API endpoints สำหรับตรวจสอบสุขภาพระบบ

### 🌐 RESTful API
- **Control Agent API**: FastAPI-based API สำหรับรับ alerts (Port 9004)
- **Process Control**: API สำหรับควบคุมและติดตามกระบวนการ
- **Status Monitoring**: API สำหรับตรวจสอบสถานะระบบ
- **Web Dashboard API**: Flask-based API สำหรับ UI (Port 5000)

## 🚀 การเริ่มต้นใช้งาน (Getting Started)

### Prerequisites (ข้อกำหนดเบื้องต้น)

#### สำหรับ Docker Deployment:
- [Docker](https://www.docker.com/get-started) v20.10+
- [Docker Compose](https://docs.docker.com/compose/install/) v2.0+
- RAM อย่างน้อย 4GB (สำหรับ LLM processing)

#### สำหรับ Local Development:
- Python 3.10+
- [NATS Server](https://docs.nats.io/running-a-nats-service/introduction/installation)
- [Ollama](https://ollama.ai/) (สำหรับ Local LLM)

### 🐳 วิธีที่ 1: Docker Compose (แนะนำ)

#### 1. Clone และ Setup Project
```bash
git clone <repository-url>
cd agent_ai/agent_ai

# คัดลอกไฟล์ environment
cp .env.example .env
```

#### 2. การกำหนดค่า Environment Variables
แก้ไขไฟล์ `.env`:
```env
# NATS Configuration
NATS_URL=nats://192.168.55.158:31653

# API Configuration  
CONTROL_AGENT_URL=http://localhost:9004

# LLM Configuration (Optional)
OLLAMA_MODEL=llama4:128x17b
LLM_TIMEOUT=60
```

#### 3. เริ่มระบบ
```bash
# Build และ start ทุก services
docker-compose up --build

# หรือเริ่มแบบ background
docker-compose up --build -d
```

#### 4. ตรวจสอบการทำงาน
- **Control Agent API**: http://localhost:9004  
- **Web Dashboard**: http://localhost:5000
- **API Documentation**: http://localhost:9004/docs
- **NATS Monitoring**: http://localhost:8222

### 💻 วิธีที่ 2: Local Development

#### 1. Setup Python Environment
```bash
# สร้าง Virtual Environment
python -m venv venv

# Activate (Linux/Mac)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r agntics_ai/requirements.txt
```

#### 2. Setup External Services

**Start NATS Server:**
```bash
# Install NATS Server
# https://docs.nats.io/running-a-nats-service/introduction/installation

# Start NATS with JetStream enabled
nats-server -js
```

**Start Ollama (สำหรับ LLM):**
```bash
# Install Ollama
# https://ollama.ai/download

# Pull model
ollama pull llama3

# Ollama จะรันอัตโนมัติบน localhost:11434
```

#### 3. กำหนดค่า Configuration
แก้ไขไฟล์ `agntics_ai/config/config.yaml`:
```yaml
nats:
  server_url: "nats://localhost:4222"
  
llm:
  local_url: "http://localhost:11434/api/generate"
  local_model: "llama3"
  timeout: 60
```

#### 4. เริ่ม Services

**วิธีที่ 1 - All-in-One (แนะนำ):**
```bash
# รันทุก services รวมกัน (Control Agent + Web App + Processing Agents)
python -m agntics_ai.cli.run_all

# หรือโหมด demo
python -m agntics_ai.cli.run_all --demo
```

**วิธีที่ 2 - แยก Terminal:**

**Terminal 1 - Control Agent:**
```bash
python start_control_agent.py
```

**Terminal 2 - Analysis Agent:**
```bash
python -m agntics_ai.agents.analysis_agent
```

**Terminal 3 - Recommendation Agent:**
```bash
python -m agntics_ai.agents.recommendation_agent
```

**Terminal 4 - Web App:**
```bash
python -m agntics_ai.webapp.app
```

## ⚙️ การตั้งค่าและการกำหนดค่า (Configuration)

### Environment Variables (.env)
```env
# NATS Message Broker
NATS_URL=nats://192.168.55.158:31653

# Control Agent 
CONTROL_AGENT_URL=http://localhost:9004
CONTROL_AGENT_HOST=0.0.0.0
CONTROL_AGENT_PORT=9004

# Web Application
WEBAPP_HOST=0.0.0.0
WEBAPP_PORT=5000

# LLM Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama4:128x17b
LLM_TIMEOUT=60

# Logging
LOG_LEVEL=INFO
```

### Application Configuration (config.yaml)
```yaml
nats:
  server_url: "nats://192.168.55.158:31653"
  stream_name: "agentAI_stream" 
  subjects:
    input: "agentAI.Input"
    analysis: "agentAI.Analysis"
    output: "agentAI.Output"

llm:
  local_url: "http://localhost:11434/api/generate"
  local_model: "llama4:128x17b"
  temperature: 0.05
  max_tokens: 2048
  timeout: 60

webapp:
  host: "0.0.0.0"
  port: 5000
  debug: false

logging:
  level: "INFO"
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
```

### Customer Tool Configuration
ไฟล์ JSON ใน `agntics_ai/data/tool/` สำหรับข้อมูลเครื่องมือของลูกค้า:

```json
[{
  "data": {
    "onBoarding": {
      "currentTechnologies": [
        {
          "technology": "EDR",
          "product": "CrowdStrike Falcon"
        },
        {
          "technology": "SIEM", 
          "product": "Splunk Enterprise"
        }
      ],
      "objectMarking": [{
        "customer_info": {
          "name": "Customer Name",
          "type": "Customer"
        }
      }]
    }
  }
}]
```

## 📚 คู่มือการใช้งาน (Usage Guide)

### 🎮 การทดสอบระบบ

#### 1. Quick System Test
```bash
# ทดสอบการเชื่อมต่อและ configuration
python system_test.py
```

#### 2. Full Demo Run  
```bash
# รันด้วยข้อมูลตัวอย่าง
python run_demo.py
```

#### 3. การส่ง Alert ผ่าน API
```bash
# ส่ง Alert โดยตรง
curl -X POST "http://localhost:9004/start" \
  -H "Content-Type: application/json" \
  -d '{
    "alert_id": "TEST-2024-001",
    "alert_name": "Suspicious Process Execution",
    "rawAlert": "...",
    "events": [...]
  }'
```

### 📊 การติดตามและตรวจสอบ

#### 1. Web Dashboard
เปิด http://localhost:5000 เพื่อดู:
- **Timeline**: ความคืบหน้าของการประมวลผล
- **Output**: ผลลัพธ์แบบ real-time
- **System Status**: สถานะของ agents และ services

#### 2. ไฟล์ Output
- **output.json**: ผลลัพธ์หลักในรูปแบบ JSON
- **data/alerts/**: ข้อมูล alert เริ่มต้น
- **data/analyses/**: ผลการวิเคราะห์ MITRE
- **data/reports/**: รายงานฉบับสมบูรณ์

#### 3. Log Files  
ตรวจสอบ logs สำหรับ debugging:
```bash
# Container logs (Docker)
docker-compose logs -f control_agent
docker-compose logs -f webapp

# Local development logs
# ดูใน console ของแต่ละ Terminal
```

### 🎛️ การใช้งาน Control Agent Timeline API

#### Start Processing Flow (Received Alert)
```bash
# เริ่มกระบวนการประมวลผล - stage 1
curl -X POST "http://localhost:9004/start" \
  -H "Content-Type: application/json" \
  -d '{"input_file": "test.json"}'
```

#### Type Agent Complete (Stage 2)
```bash
# แจ้งว่า Type Agent เสร็จแล้ว
curl -X POST "http://localhost:9004/control/type/finished" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "your-session-id",
    "data": {
      "technique_name": "T1055 Process Injection",
      "confidence": 0.85,
      "analysis": "Analysis results..."
    }
  }'
```

#### Workflow Complete (Final Stage)
```bash
# แจ้งว่า workflow เสร็จสิ้น - stage 7
curl -X POST "http://localhost:9004/control/flow/finished" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "your-session-id",
    "data": {
      "status": "completed",
      "report": "Final incident report...",
      "recommendations": "Security recommendations..."
    }
  }'
```

#### Get Session Status
```bash
# ตรวจสอบ timeline และสถานะ session
curl "http://localhost:9004/control/status/your-session-id"
```

#### List All Sessions  
```bash
# ดู sessions ทั้งหมด
curl "http://localhost:9004/control/sessions"
```

#### System Health Check
```bash  
# ตรวจสอบสุขภาพระบบ
curl "http://localhost:9004/health"
```

## 🌐 Web Interface และ Real-time Monitoring

### Dashboard Features

#### 1. **Real-time Timeline**
- แสดงขั้นตอนการประมวลผล
- อัพเดทสถานะแบบ real-time
- แสดงเวลาที่ใช้ในแต่ละขั้นตอน

#### 2. **Output Visualization**
- แสดงผลการวิเคราะห์ MITRE ATT&CK
- รายงานและคำแนะนำ
- ข้อมูลเครื่องมือที่เกี่ยวข้อง

#### 3. **System Monitoring**
- สถานะของ Agent แต่ละตัว
- การเชื่อมต่อ NATS
- สถิติการประมวลผล

### Technical Implementation
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Backend**: Flask with Server-Sent Events (SSE)
- **Real-time Communication**: EventSource API
- **Auto-refresh**: 2-second polling interval

## 📖 API Documentation

### 🎛️ Control Agent Timeline API (Port 9004)

**Base URL**: `http://localhost:9004`
**API Docs**: `http://localhost:9004/docs` (Auto-generated Swagger UI)

#### POST /start
เริ่มกระบวนการประมวลผล (Stage 1: Received Alert)

**Request Body:**
```json
{
  "input_file": "test.json"
}
```

**Response:**
```json
{
  "status": "success",
  "session_id": "uuid-session-id",
  "message": "Flow started successfully"
}
```

#### POST /control/type/finished  
แจ้งว่า Type Agent เสร็จแล้ว (Stage 2: Type Agent)

**Request Body:**
```json
{
  "session_id": "uuid-session-id",
  "data": {
    "technique_name": "T1055 Process Injection",
    "confidence": 0.85,
    "analysis": "Detailed analysis results..."
  }
}
```

#### POST /control/flow/finished
แจ้งว่า workflow เสร็จสิ้น (Stage 7: Recommendation)

**Request Body:**
```json
{
  "session_id": "uuid-session-id", 
  "data": {
    "status": "completed",
    "report": "Final incident report...",
    "recommendations": "Security recommendations..."
  }
}
```

#### GET /control/status/{session_id}
ดู timeline และสถานะของ session

**Response:**
```json
{
  "session_id": "uuid-session-id",
  "status": "completed",
  "timeline": [
    {"stage": "Received Alert", "status": "success", "errorMessage": ""},
    {"stage": "Type Agent", "status": "success", "errorMessage": ""},
    {"stage": "Analyze Root Cause", "status": "success", "errorMessage": ""},
    {"stage": "Triage Status", "status": "success", "errorMessage": ""},
    {"stage": "Action Taken", "status": "success", "errorMessage": ""},
    {"stage": "Tool Status", "status": "success", "errorMessage": ""},
    {"stage": "Recommendation", "status": "success", "errorMessage": ""}
  ],
  "last_updated": "2025-08-07T16:30:00Z"
}
```

#### GET /control/sessions
ดูรายการ sessions ทั้งหมด

**Response:**
```json
{
  "sessions": [
    {
      "session_id": "uuid-1",
      "created_at": "2025-08-07T16:25:00Z", 
      "status": "completed"
    },
    {
      "session_id": "uuid-2",
      "created_at": "2025-08-07T16:28:00Z",
      "status": "in_progress"
    }
  ],
  "total": 2
}
```

#### GET /health
Health check endpoint

**Response:**
```json
{
  "status": "healthy",
  "service": "Control Agent API",
  "active_sessions": 3,
  "active_connections": 1,
  "nats_connected": true
}
```

### 🌐 Web Dashboard API (Port 5000)

#### GET /api/reports
ดูรายงานทั้งหมด

#### GET /api/latest  
ดูรายงานล่าสุด

#### GET /api/output
ดู output.json ปัจจุบัน

### Output Format Specification

ระบบสร้าง output ในรูปแบบ flat JSON structure:

```json
{
  "agentAI.overview.updated": {
    "id": "session-uuid",
    "data": {
      "description": "Security incident summary..."
    }
  },
  "agentAI.attack.updated": {
    "id": "session-uuid", 
    "data": [{
      "tacticID": "TA0001",
      "tacticName": "Initial Access",
      "confidence": 0.85
    }]
  },
  "agentAI.recommendation.updated": {
    "id": "session-uuid",
    "data": [{
      "description": "Investigation Path",
      "content": "Detailed recommendations..."
    }]
  },
  "agentAI.timeline.updated": {
    "alert_id": "session-uuid",
    "data": [
      {"stage": "Received Alert", "status": "success", "errorMessage": ""},
      {"stage": "Type Agent", "status": "success", "errorMessage": ""},
      {"stage": "Analyze Root Cause", "status": "success", "errorMessage": ""},
      {"stage": "Triage Status", "status": "success", "errorMessage": ""},
      {"stage": "Action Taken", "status": "success", "errorMessage": ""},
      {"stage": "Tool Status", "status": "success", "errorMessage": ""},
      {"stage": "Recommendation", "status": "success", "errorMessage": ""}
    ]
  }
}
```

## 🔧 การพัฒนาและขยายระบบ (Development & Extension)

### การเพิ่ม Agent ใหม่

#### 1. สร้าง Agent Class
```python
# agntics_ai/agents/new_agent.py
import asyncio
from ..utils.nats_handler import NATSHandler

class NewAgent:
    def __init__(self, nats_handler: NATSHandler):
        self.nats_handler = nats_handler
        self.running = False
    
    async def run(self):
        psub = await self.nats_handler.subscribe_pull(
            subject="agentAI.NewSubject",
            durable_name="new_agent"
        )
        
        self.running = True
        while self.running:
            try:
                msgs = await psub.fetch(batch=1, timeout=5.0)
                for msg in msgs:
                    # Process message
                    await self._process_message(msg)
                    await msg.ack()
            except asyncio.TimeoutError:
                continue
```

#### 2. เพิ่ม Subject ใน Configuration
```yaml
# config.yaml
nats:
  subjects:
    input: "agentAI.Input"
    analysis: "agentAI.Analysis" 
    new_subject: "agentAI.NewSubject"
    output: "agentAI.Output"
```

### การปรับแต่ง LLM Prompts

#### Analysis Agent Prompt
ใน `agntics_ai/utils/llm_handler_ollama.py`:
```python
def create_analysis_prompt(log_data, external_context=None):
    system_prompt = """คุณเป็นนักวิเคราะห์ความปลอดภัยเชี่ยวชาญ...
    
    ### INSTRUCTIONS:
    1. วิเคราะห์ log_data และ external_context
    2. ระบุ MITRE ATT&CK Tactic และ Technique ที่เกี่ยวข้อง
    3. ให้คะแนนความเชื่อมั่น 0.0-1.0
    
    ### OUTPUT FORMAT:
    {
      "technique_id": "T1059.001",
      "technique_name": "PowerShell", 
      "tactic": "Execution",
      "tactic_id": "TA0002",
      "confidence_score": 0.95,
      "reasoning": "..."
    }"""
    
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"INPUT: {log_data}"}
    ]
```

### การเพิ่มเครื่องมือลูกค้า

#### 1. สร้างไฟล์ Tool Configuration
```json
// agntics_ai/data/tool/Customer_Tools.json
[{
  "data": {
    "onBoarding": {
      "currentTechnologies": [
        {
          "technology": "EDR",
          "product": "Microsoft Defender"
        },
        {
          "technology": "SIEM",
          "product": "Azure Sentinel" 
        }
      ],
      "monitorAssets": [
        {
          "purpose": "Domain Controller",
          "productName": "Windows Server",
          "ipAddress": "192.168.1.10"
        }
      ],
      "objectMarking": [{
        "customer_info": {
          "name": "Customer ABC",
          "type": "Customer"
        }  
      }]
    }
  }
}]
```

#### 2. ปรับแต่ง Tool Loading Logic
ใน `agntics_ai/utils/tool_loader.py`:
```python
def find_relevant_tools(self, attack_technique: str, customer_name: str):
    """แก้ไข logic ตามต้องการ"""
    current_tech = self.get_current_technologies(customer_name)
    
    # ส่งข้อมูลทั้งหมดให้ LLM ตัดสินใจ
    relevant_tools = []
    for tech in current_tech:
        relevant_tools.append({
            'type': 'security_technology',
            'technology': tech.get('technology'),
            'product': tech.get('product'),
            'purpose': f'Available for {attack_technique} analysis'
        })
    
    return relevant_tools
```

### การขยาย Web Interface

#### เพิ่ม Real-time Features
```javascript
// webapp/templates/index.html
function initializeRealTimeUpdates() {
    const eventSource = new EventSource('/events');
    
    eventSource.onmessage = function(event) {
        const data = JSON.parse(event.data);
        updateDashboard(data);
    };
    
    // Custom event handlers
    eventSource.addEventListener('progress', function(event) {
        updateProgressBar(JSON.parse(event.data));
    });
}
```

## 🔍 Troubleshooting

### การแก้ไขปัญหาทั่วไป

#### 1. NATS Connection Issues
```bash
# ตรวจสอบ NATS Server
curl http://localhost:8222/varz

# ตรวจสอบ Streams
nats stream list

# ตรวจสอบ Consumers  
nats consumer list agentAI_stream
```

#### 2. LLM Timeout Problems
```yaml
# เพิ่ม timeout ใน config.yaml
llm:
  timeout: 120  # เพิ่มจาก 60 เป็น 120 วินาที
```

#### 3. Agent Not Processing
```bash
# ตรวจสอบ logs
docker-compose logs -f analysis_agent

# ตรวจสอบ message queue
curl "http://localhost:9004/health"
```

#### 4. Web App Not Loading
```bash
# ตรวจสอบ port conflicts
netstat -tulpn | grep :5000

# Restart web app
docker-compose restart webapp
```

### Performance Tuning

#### 1. LLM Optimization  
- ปรับ `temperature` ต่ำลง (0.01-0.05) สำหรับผลลัพธ์ที่สม่ำเสมอ
- เพิ่ม `max_tokens` สำหรับรายงานที่ยาวขึ้น
- ใช้ model ที่เล็กกว่าสำหรับ development

#### 2. NATS Configuration
```yaml
# docker-compose.yaml
nats-server:
  command: [
    "nats-server", 
    "--jetstream",
    "--store_dir=/data",
    "--max_memory_store=1GB",
    "--max_file_store=10GB"
  ]
```

#### 3. Resource Allocation
```yaml  
# docker-compose.yaml - เพิ่ม resource limits
services:
  control_agent:
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '0.5'
```

### Debug Mode
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG

# Run with verbose output
python -u start_control_agent.py

# Monitor all NATS messages
nats sub "agentAI.>"
```

---

## 📞 การสนับสนุน (Support)

### การรายงานปัญหา
- สร้าง Issue ใน repository
- แนบ logs และ configuration files  
- ระบุ environment (Docker/Local) และ OS

### การร่วมพัฒนา
- Fork repository และสร้าง branch ใหม่
- ทำการแก้ไขและ test ให้เรียบร้อย
- สร้าง Pull Request พร้อม description ที่ชัดเจน

### License
ระบุ license ของโปรเจค (MIT, Apache 2.0, etc.)

---

## 🎉 Latest Updates

### v2.0 - Control Agent Integration (Current)
- ✅ **Control Agent API** - FastAPI server พร้อม Timeline API
- ✅ **7 Stages Timeline** - ติดตามขั้นตอนการประมวลผลแบบ real-time
- ✅ **Docker Integration** - รวม Control Agent ใน Docker Compose
- ✅ **Session Management** - จัดการ workflow sessions ด้วย API
- ✅ **Manual Control Mode** - สามารถควบคุมขั้นตอนแบบ manual
- ✅ **Auto-generated API Docs** - Swagger UI ที่ `/docs`
- ✅ **Health Monitoring** - ตรวจสอบสุขภาพระบบแบบ real-time

### v1.0 - Core Agent System
- ✅ **LLM-Powered Analysis** - MITRE ATT&CK mapping
- ✅ **Event-Driven Architecture** - NATS JetStream
- ✅ **Real-time Web Dashboard** - Flask + SSE
- ✅ **Tool Integration** - Customer-specific tools support

---

**สร้างด้วย ❤️ โดย Agent AI Team**

**🚀 Ready for Production with Control Agent Timeline API!**