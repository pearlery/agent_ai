# Agent AI Test Suite

## การทดสอบระบบ Agent AI

### ไฟล์ทดสอบ

#### 1. `test_graphql_integration.py`
- **วัตถุประสงค์**: ทดสอบการเชื่อมต่อระหว่าง Agent AI และ GraphQL ผ่าน NATS
- **การทดสอบ**: 
  - การส่งข้อมูลผ่าน NATS topic `agentAI.graphql.mutation`
  - การทำงานของ GraphQL Publisher
  - การอัพเดทข้อมูลแบบ real-time
- **การรัน**: `python test_graphql_integration.py`

#### 2. `test_system_integration.py`
- **วัตถุประสงค์**: ทดสอบระบบทั้งหมดรวมกัน (End-to-End)
- **การทดสอบ**:
  - Complete workflow จาก alert → analysis → recommendation
  - Control Agent และ session management
  - Error handling และ graceful degradation
- **การรัน**: `python test_system_integration.py`

## การเตรียมสำหรับการทดสอบ

### 1. เริ่ม NATS Server
```bash
nats-server -js
```

### 2. เริ่ม Frontend GraphQL Server
```bash
cd C:\Users\p\Desktop\Agentic\Frontend_AIAgent
npm start
```

### 3. รันการทดสอบ
```bash
cd C:\Users\p\Desktop\Agentic\agent_ai\tests

# ทดสอบ GraphQL integration
python test_graphql_integration.py

# ทดสอบระบบทั้งหมด
python test_system_integration.py
```

## ผลลัพธ์ที่คาดหวัง

### ✅ การทดสอบที่สำเร็จควรแสดง:
- ✅ NATS connection established
- ✅ GraphQL Publisher initialized
- ✅ Data published to GraphQL mutations
- ✅ Timeline updates working
- ✅ Session management working
- ✅ Frontend receives real-time updates

### ❌ สัญญาณที่บ่งบอกปัญหา:
- ❌ NATS connection timeout
- ❌ GraphQL Publisher not initialized
- ❌ Frontend not receiving updates
- ❌ Session data not persisted

## การ Debug

### 1. ตรวจสอบ NATS
```bash
# ตรวจสอบ streams
nats stream list

# ตรวจสอบ subjects
nats sub "agentAI.>"
```

### 2. ตรวจสอบ GraphQL
- เช็ค Frontend GraphQL Server console
- ดู network tab ใน browser DevTools
- ตรวจสอบ WebSocket connections

### 3. ตรวจสอบ Logs
- ดู console output จากการรัน test scripts
- ตรวจสอบไฟล์ output.json และ test_output.json

## การเพิ่ม Test ใหม่

1. สร้างไฟล์ test ใหม่ในโฟลเดอร์ `tests/`
2. ใช้ naming convention: `test_[component_name].py`
3. เพิ่มการอธิบายใน README นี้

## หมายเหตุ

- การทดสอบต้องการ NATS Server ทำงานอยู่
- Frontend GraphQL Server ต้องรันเพื่อรับข้อมูลจาก NATS
- บางการทดสอบอาจใช้เวลานานเนื่องจากการรอ async operations