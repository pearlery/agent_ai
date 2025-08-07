# Agent AI System

## 1. ภาพรวม (Overview)

Agent AI System คือแพลตฟอร์มอัจฉริยะที่ขับเคลื่อนด้วยอีเวนต์ (event-driven) ซึ่งออกแบบมาเพื่อวิเคราะห์แจ้งเตือน (alerts) จากระบบต่างๆ โดยอัตโนมัติ แพลตฟอร์มนี้จะรับแจ้งเตือน, ทำการวิเคราะห์เชิงลึกโดยใช้ Agent ที่ขับเคลื่อนด้วย AI, และให้คำแนะนำที่สามารถนำไปปฏิบัติได้จริง ระบบถูกสร้างขึ้นด้วยสถาปัตยกรรมแบบ Microservices และใช้ Message Broker สำหรับการสื่อสารแบบ Asynchronous ระหว่างส่วนประกอบต่างๆ

## 2. คุณสมบัติหลัก (Features)

-   **Asynchronous Processing:** สร้างขึ้นบน NATS Message Broker เพื่อการสื่อสารที่มีเสถียรภาพและขยายขนาดได้
-   **AI-Powered Analysis:** ใช้ประโยชน์จาก Large Language Models (LLMs) เพื่อวิเคราะห์แจ้งเตือนและข้อมูลที่ซับซ้อน
-   **Automated Recommendations:** สร้างขั้นตอนที่นำไปปฏิบัติได้จริงเพื่อแก้ไขปัญหาที่ตรวจพบ
-   **RESTful API Control:** มี `Control Agent` กลางสำหรับจัดการกระบวนการทำงานผ่าน FastAPI
-   **Web Interface:** มี Web Application ที่พัฒนาด้วย Flask สำหรับแสดงสถานะของระบบ
-   **Containerized Deployment:** สามารถติดตั้งและรันผ่าน Docker และ Docker Compose ได้อย่างสมบูรณ์
-   **Extensible Tooling:** Agent สามารถติดตั้งเครื่องมือต่างๆ เพิ่มเติมเพื่อเชื่อมต่อกับระบบภายนอกและแหล่งข้อมูลอื่นๆ ได้

## 3. สถาปัตยกรรมและโฟลว์การทำงาน (Architecture & Data Flow)

ระบบประกอบด้วย Service หลัก 3 ส่วนที่ทำงานแยกกันและสื่อสารผ่าน NATS Message Broker ซึ่งเป็นหัวใจของสถาปัตยกรรม

### ส่วนประกอบหลัก (Core Components)

1.  **Control Agent (`control_app.py`):**
    -   **หน้าที่:** เป็นประตูหลัก (Gateway) ของระบบ สร้างด้วย FastAPI
    -   รับแจ้งเตือนผ่าน REST API (`/alert` endpoint)
    -   สร้าง Session ID ที่ไม่ซ้ำกันสำหรับแต่ละแจ้งเตือน
    -   จัดเก็บแจ้งเตือนเริ่มต้นไว้ใน `data/alerts/`
    -   เผยแพร่ (Publish) ข้อความแรกไปยัง NATS เพื่อเริ่มต้นกระบวนการ

2.  **Analysis Agent (`analysis_agent.py`):**
    -   **หน้าที่:** Worker ที่วิเคราะห์แจ้งเตือนเพื่อระบุเทคนิคการโจมตี
    -   ดึง (Pull) ข้อความจาก NATS ที่ Control Agent ส่งมา
    -   ใช้ LLM เพื่อวิเคราะห์ข้อมูลแจ้งเตือนและจับคู่กับ **MITRE ATT&CK Framework**
    -   จัดเก็บผลการวิเคราะห์ (เช่น `T1059.001`) ไว้ใน `data/analyses/`
    -   เผยแพร่ผลการวิเคราะห์ต่อไปยัง NATS

3.  **Recommendation Agent (`recommendation_agent.py`):**
    -   **หน้าที่:** Worker ที่สร้างรายงานและคำแนะนำในการรับมือ
    -   ดึงผลการวิเคราะห์จาก NATS
    -   ค้นหาเครื่องมือ (Tools) ที่เกี่ยวข้องกับเทคนิคการโจมตีที่พบจาก `agntics_ai/data/tool/`
    -   ใช้ LLM เพื่อสร้างรายงานฉบับสมบูรณ์ในรูปแบบ Markdown ซึ่งประกอบด้วย: สรุปสำหรับผู้บริหาร, รายละเอียดทางเทคนิค, และคำแนะนำในการรับมือ (โดยอ้างอิงเครื่องมือที่ค้นพบ)
    -   จัดเก็บรายงานไว้ใน `data/reports/`
    -   เผยแพร่ผลลัพธ์สุดท้ายไปยัง NATS และอัปเดตไฟล์ `output.json`

### โฟลว์การทำงานผ่าน NATS (NATS Data Flow)

การสื่อสารทั้งหมดเกิดขึ้นผ่าน NATS stream ชื่อ `agentAI_stream` โดยใช้ Subject ที่แตกต่างกันในแต่ละขั้นตอน:

1.  **`agentAI.Input`**:
    -   **Publisher:** `Control Agent`
    -   **Consumer:** `Analysis Agent`
    -   **Payload:** ข้อมูลแจ้งเตือนเริ่มต้นพร้อม `session_id`

2.  **`agentAI.Analysis`**:
    -   **Publisher:** `Analysis Agent`
    -   **Consumer:** `Recommendation Agent`
    -   **Payload:** ข้อมูลแจ้งเตือนเดิมที่เสริมด้วยผลการวิเคราะห์จาก MITRE ATT&CK

3.  **`agentAI.Output`**:
    -   **Publisher:** `Recommendation Agent`
    -   **Consumer:** (ไม่มีในปัจจุบัน, แต่สามารถต่อยอดเพื่อส่ง Notification ได้)
    -   **Payload:** ผลลัพธ์สุดท้ายที่ประกอบด้วยข้อมูลทั้งหมดและรายงานฉบับสมบูรณ์

## 4. การเริ่มต้นใช้งาน (Getting Started)

คุณสามารถรันโปรเจกต์ได้ 2 วิธี:

### วิธีที่ 1: Docker Compose (แนะนำ)

วิธีนี้ง่ายที่สุดและเหมาะสำหรับ Production หรือการทดสอบทั่วไป

1.  **Prerequisites:** ติดตั้ง [Docker](https://www.docker.com/get-started) และ [Docker Compose](https://docs.docker.com/compose/install/)

2.  **Configuration:**
    -   คัดลอกไฟล์ `.env.example` ไปเป็น `.env`: `cp .env.example .env`
    -   ในไฟล์ `.env`, ค่า `NATS_URL` และ `CONTROL_AGENT_URL` ถูกตั้งค่าให้ชี้ไปที่ชื่อ Service ภายใน Docker network อยู่แล้ว (`nats` และ `control_agent`) คุณไม่จำเป็นต้องแก้ไข

3.  **Run the System:**
    ```bash
    docker-compose up --build
    ```
    คำสั่งนี้จะสร้างและรัน Container ทั้งหมด: `control_agent`, `webapp`, และ `nats-server`

### วิธีที่ 2: Local Development (ไม่ใช้ Docker)

วิธีนี้เหมาะสำหรับนักพัฒนาที่ต้องการแก้ไขโค้ดและดีบักการทำงานของแต่ละ Agent

1.  **Prerequisites:**
    -   ติดตั้ง Python 3.10 หรือสูงกว่า
    -   ติดตั้ง [NATS Server](https://docs.nats.io/running-a-nats-service/introduction/installation) และรันบนเครื่องของคุณ (หรือมี NATS server ให้เชื่อมต่อ)

2.  **Setup Environment:**
    -   สร้างและ Activate Virtual Environment:
        ```bash
        python -m venv venv
        source venv/bin/activate  # บน Windows ใช้ `venv\Scripts\activate`
        ```
    -   ติดตั้ง Dependencies:
        ```bash
        pip install -r agntics_ai/requirements.txt
        ```

3.  **Configuration:**
    -   เปิดไฟล์ `agntics_ai/config/config.yaml` และแก้ไข `nats.server_url` ให้ชี้ไปยัง NATS server ของคุณ (เช่น `nats://localhost:4222`)
    -   แก้ไข `llm.local_url` ให้ชี้ไปยัง Ollama API ของคุณ

4.  **Run Each Service:**
    เปิด Terminal แยกกัน 3 อัน และรันแต่ละ Agent ตามลำดับ:

    -   **Terminal 1: Control Agent**
        ```bash
        python start_control_agent.py
        ```
    -   **Terminal 2: Analysis Agent**
        ```bash
        python -m agntics_ai.agents.analysis_agent
        ```
    -   **Terminal 3: Recommendation Agent**
        ```bash
        python -m agntics_ai.agents.recommendation_agent
        ```

## 5. การตั้งค่าคอนฟิก (Configuration)

### Environment Variables (`.env`)

ใช้สำหรับตั้งค่าที่เปลี่ยนแปลงตามสภาพแวดล้อม (Development vs. Production)

-   `NATS_URL`: ที่อยู่ของ NATS server (เช่น `nats://nats:4222` สำหรับ Docker)
-   `API_KEY`: Secret key สำหรับป้องกัน API (ยังไม่ได้ใช้งานในปัจจุบัน)
-   `CONTROL_AGENT_URL`: URL ที่ `run_demo.py` ใช้เพื่อส่งข้อมูลไปยัง Control Agent

### Application Configuration (`agntics_ai/config/config.yaml`)

ไฟล์คอนฟิกหลักสำหรับพฤติกรรมของแอปพลิเคชัน

-   **`nats`**:
    -   `server_url`: ที่อยู่ NATS server (จะถูก override ด้วยค่าจาก `.env` หากมี)
    -   `stream_name`: ชื่อของ Stream ใน NATS
    -   `subjects`: กำหนดชื่อ Subject สำหรับแต่ละขั้นตอน (`input`, `analysis`, `output`)
-   **`llm`**:
    -   `local_url`: Endpoint ของ Ollama API
    -   `local_model`: ชื่อโมเดลที่ต้องการใช้ (เช่น `llama3`)
    -   `temperature`: ควบคุมความสร้างสรรค์ของ LLM (ค่าต่ำ = ตรงไปตรงมา)
    -   `max_tokens`: จำนวน Token สูงสุดที่ LLM จะสร้างได้
-   **`webapp`**: การตั้งค่าสำหรับ Flask web app
-   **`logging`**: กำหนดระดับและรูปแบบของ Log

## 6. คู่มือการใช้งาน (Usage Guide)

1.  **ส่งแจ้งเตือน:** ใช้ `curl` หรือ `run_demo.py` เพื่อส่งแจ้งเตือนไปยัง `http://localhost:8000/alert`
    ```bash
    # รันเดโม
    python run_demo.py
    ```

2.  **ติดตามสถานะ:**
    -   **Web UI:** เปิด [http://localhost:8080](http://localhost:8080) เพื่อดู Timeline การประมวลผล
    -   **Output Files:** ตรวจสอบไฟล์ที่ถูกสร้างขึ้นในไดเรกทอรี `data/`:
        -   `data/alerts/`: เก็บแจ้งเตือนเริ่มต้น
        -   `data/analyses/`: เก็บผลการวิเคราะห์จาก Analysis Agent
        -   `data/reports/`: เก็บรายงานฉบับเต็มจาก Recommendation Agent
    -   **Main Output:** ไฟล์ `output.json` จะถูกอัปเดตด้วยผลลัพธ์สรุปของแต่ละเซสชัน

## 7. การแก้ไขและพัฒนาต่อ (Modification & Extension)

### การแก้ไข Prompt ของ Agent

Prompt ถูกสร้างขึ้นแบบไดนามิกในโค้ดเพื่อใส่ข้อมูลจากแจ้งเตือนเข้าไป

-   **Analysis Agent Prompt:** อยู่ในฟังก์ชัน `create_analysis_prompt` ภายในไฟล์ `agntics_ai/utils/llm_handler_ollama.py`
-   **Recommendation Agent Prompt:** อยู่ในฟังก์ชัน `create_recommendation_prompt` ภายในไฟล์ `agntics_ai/utils/llm_handler_ollama.py`

คุณสามารถเข้าไปแก้ไขข้อความในฟังก์ชันเหล่านี้เพื่อปรับเปลี่ยนพฤติกรรมของ LLM ได้

### การเพิ่มเครื่องมือ (Tool) ใหม่

Recommendation Agent สามารถแนะนำเครื่องมือ (เช่น Splunk, CrowdStrike) ที่เกี่ยวข้องกับเทคนิคการโจมตีได้

1.  **สร้างไฟล์ Tool JSON:**
    ไปที่ไดเรกทอรี `agntics_ai/data/tool/` และสร้างไฟล์ JSON ใหม่ (หรือแก้ไขไฟล์ที่มีอยู่) โครงสร้างของไฟล์ควรเป็นไปตามตัวอย่าง `Output_N-Health_EndPoint.json`

2.  **โครงสร้างข้อมูล:**
    ข้อมูลสำคัญอยู่ภายใต้ `onBoarding.currentTechnologies` ซึ่งเป็น list ของ object ที่มี `technology` และ `product`

3.  **Logic การค้นหา:**
    ไฟล์ `agntics_ai/utils/tool_loader.py` ในฟังก์ชัน `find_relevant_tools` มีการ map ระหว่าง MITRE ATT&CK technique ID กับประเภทของเทคโนโลยี (เช่น `T1059` map กับ `EDR`, `ANTIVIRUS`) คุณสามารถเพิ่มหรือแก้ไข mapping นี้เพื่อให้ระบบรู้จักเครื่องมือของคุณ

### การเพิ่ม Agent ใหม่

หากคุณต้องการเพิ่มขั้นตอนการประมวลผลใหม่ (เช่น Agent สำหรับทำ Enrichment ข้อมูล) ให้ทำตามขั้นตอนต่อไปนี้:

1.  **สร้าง Agent File:** สร้างไฟล์ Python ใหม่ใน `agntics_ai/agents/` (เช่น `enrichment_agent.py`)
2.  **กำหนด NATS Subjects:**
    -   ใน `config.yaml`, เพิ่ม subject ใหม่ เช่น `enrichment: "agentAI.Enrichment"`
    -   ให้ Agent ใหม่ของคุณ **Subscribe** subject ที่เป็นผลลัพธ์ของขั้นตอนก่อนหน้า (เช่น `agentAI.Analysis`)
    -   ให้ Agent ใหม่ของคุณ **Publish** ผลลัพธ์ไปยัง subject ใหม่ (เช่น `agentAI.Enrichment`)
3.  **ปรับแก้ Agent ต่อเนื่อง:**
    -   แก้ไข Agent ที่จะทำงานในขั้นตอนถัดไป (เช่น `RecommendationAgent`) ให้ Subscribe subject ใหม่ที่คุณเพิ่งสร้าง (`agentAI.Enrichment`) แทน subject เดิม

