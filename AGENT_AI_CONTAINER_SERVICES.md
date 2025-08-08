# 🚀 Agent AI App Container - Services Overview

## 📦 Agent AI App Container รวมอะไรบ้าง

เมื่อรัน Docker, **Agent AI App container** จะเรียกใช้ `agntics_ai.cli.run_all --docker` ซึ่งจะเริ่มทำงานหลาย services พร้อมกัน:

### 🎛️ **1. Control Agent API Server** (Port 9004)
- **Framework**: FastAPI  
- **Purpose**: API สำหรับควบคุมและติดตาม timeline
- **Thread**: Background daemon thread
- **Endpoints**:
  - `GET /` - API info
  - `POST /start` - เริ่ม processing
  - `POST /control/type/finished` - Type Agent stage complete
  - `POST /control/flow/finished` - Final stage complete
  - `GET /control/status/{session_id}` - ดู timeline status
  - `GET /control/sessions` - ดูทุก sessions
  - `GET /health` - Health check

### 🌐 **2. Web Application** (Port 5000)  
- **Framework**: Flask
- **Purpose**: Dashboard และ UI สำหรับแสดงผล
- **Thread**: Background daemon thread
- **Features**:
  - Real-time dashboard
  - Incident reports display
  - Server-sent events สำหรับ live updates
  - API endpoints สำหรับ data

### 🤖 **3. Analysis Agent** (Background Processing)
- **Purpose**: วิเคราะห์ cybersecurity threats ด้วย MITRE ATT&CK framework
- **Mode**: Continuous processing จาก NATS stream
- **LLM Integration**: ใช้ Ollama หรือ external API
- **Timeline**: อัพเดท "Type Agent" stage

### 💡 **4. Recommendation Agent** (Background Processing)
- **Purpose**: สร้างข้อเสนอแนะเชิงกลยุทธ์และปฏิบัติการ
- **Mode**: Continuous processing จาก NATS stream  
- **LLM Integration**: ใช้ Ollama หรือ external API
- **Timeline**: อัพเดท "Recommendation" stage

### 📥 **5. Input Agent** (Background Processing)
- **Purpose**: รับและประมวลผล alert จาก input sources
- **Mode**: One-time execution ตอน startup
- **Timeline**: อัพเดท "Received Alert" stage

## 🏗️ Architecture ใน Container

```
┌─────────────────────────────────────────────────────────┐
│                Agent AI App Container                    │
│                                                         │
│  ┌─────────────────┐    ┌─────────────────────────────┐ │
│  │   Main Thread   │    │      Background Threads     │ │
│  │                 │    │                             │ │
│  │  🎯 Orchestrator │    │  🎛️ Control Agent API     │ │
│  │     (run_all)   │    │     (FastAPI:9004)         │ │
│  │                 │    │                             │ │
│  │  📊 Timeline    │    │  🌐 Web Application        │ │
│  │     Tracker     │    │     (Flask:5000)           │ │ │
│  │                 │    │                             │ │
│  │  ⚙️ Config &    │    │                             │ │
│  │     NATS        │    └─────────────────────────────┘ │
│  └─────────────────┘                                    │
│                                                         │
│  ┌─────────────────────────────────────────────────────┐ │
│  │            Processing Agents (Async)                │ │
│  │                                                     │ │
│  │  🤖 Analysis Agent    💡 Recommendation Agent      │ │
│  │  📥 Input Agent                                     │ │
│  └─────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

## 🔄 Startup Sequence ใน Docker Mode

1. **Configuration Loading** - โหลด config จาก YAML
2. **NATS Connection** - เชื่อมต่อ NATS server (หรือ skip ถ้าไม่มี)  
3. **Control Agent Start** - เริ่ม FastAPI server (port 9004)
4. **Web App Start** - เริ่ม Flask server (port 5000)
5. **Input Phase** - รัน Input Agent (ถ้ามี NATS)
6. **Processing Agents** - รัน Analysis + Recommendation agents (ถ้ามี NATS)

## ⚡ Service States

### ✅ เมื่อมี NATS Server:
- **Control Agent API**: ✅ รัน (port 9004)
- **Web Application**: ✅ รัน (port 5000)  
- **Analysis Agent**: ✅ รัน (background processing)
- **Recommendation Agent**: ✅ รัน (background processing)
- **Input Agent**: ✅ รัน (one-time)
- **Timeline Tracking**: ✅ ทั้ง 7 stages

### ⚠️ เมื่อไม่มี NATS Server:
- **Control Agent API**: ✅ รัน (port 9004) - Manual mode
- **Web Application**: ✅ รัน (port 5000) - Display mode
- **Analysis Agent**: ❌ Skip
- **Recommendation Agent**: ❌ Skip  
- **Input Agent**: ❌ Skip
- **Timeline Tracking**: ✅ ผ่าน Control Agent API เท่านั้น

## 🎯 Timeline Stages ที่ Support

ระบบติดตาม 7 stages ตามที่คุณกำหนด:

1. **"Received Alert"** - เมื่อรับ alert
2. **"Type Agent"** - Analysis Agent ประมวลผล  
3. **"Analyze Root Cause"** - วิเคราะห์สาเหตุ
4. **"Triage Status"** - จัดลำดับความรุนแรง
5. **"Action Taken"** - ดำเนินการ
6. **"Tool Status"** - สถานะเครื่องมือ
7. **"Recommendation"** - Recommendation Agent ให้คำแนะนำ

## 🔗 Inter-Service Communication

- **Control Agent ↔ Timeline Tracker** - อัพเดท stages
- **Web App ↔ Output Handler** - แสดงผลรายงาน
- **Agents ↔ NATS** - Message passing (ถ้ามี)
- **Control Agent ↔ Session Manager** - จัดการ sessions
- **All Services ↔ Config** - การตั้งค่าส่วนกลาง

## 📊 Resource Usage

- **Threads**: 3+ (Main + Control Agent + Web App + อื่นๆ)
- **Ports**: 2 (5000, 9004)
- **Memory**: Moderate (ขึ้นกับ LLM usage)
- **Disk**: Config files, logs, output files

---

**สรุป: Agent AI App container นี้เป็น "All-in-One" service ที่รวมทุกอย่างเอาไว้แล้ว รวมทั้ง Control Agent ที่คุณเพิ่งเพิ่มเข้ามาด้วย!** ✨