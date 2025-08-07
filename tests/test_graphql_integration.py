#!/usr/bin/env python3
"""
Test script สำหรับทดสอบ GraphQL Integration ผ่าน NATS
"""
import asyncio
import json
import sys
from pathlib import Path

# Add agntics_ai to path
sys.path.append(str(Path(__file__).parent / "agntics_ai"))

from agntics_ai.utils.nats_handler import NATSHandler
from agntics_ai.utils.graphql_publisher import init_graphql_publisher
from agntics_ai.utils.output_handler import get_output_handler


async def test_graphql_integration():
    """ทดสอบการส่งข้อมูลจาก Agent AI ไป GraphQL ผ่าน NATS"""
    
    print("🔄 เริ่มทดสอบ GraphQL Integration...")
    
    # NATS Configuration
    nats_config = {
        "server_url": "nats://localhost:4222",
        "stream_name": "agentAI_stream",
        "auto_open_connection": True,
        "subjects": {
            "graphql_mutation": "agentAI.graphql.mutation"
        }
    }
    
    try:
        # เชื่อมต่อ NATS
        print("📡 เชื่อมต่อ NATS...")
        nats_handler = NATSHandler(nats_config)
        await nats_handler.connect()
        print("✅ เชื่อมต่อ NATS สำเร็จ")
        
        # Initialize GraphQL Publisher
        print("🚀 Initialize GraphQL Publisher...")
        publisher = init_graphql_publisher(nats_handler, "agentAI.graphql.mutation")
        print("✅ GraphQL Publisher พร้อมใช้งาน")
        
        # Initialize Output Handler
        print("📝 Initialize Output Handler...")
        output_handler = get_output_handler("test_output.json")
        print("✅ Output Handler พร้อมใช้งาน")
        
        # Test Session
        session_id = "test-session-001"
        
        print(f"\n🧪 ทดสอบการส่งข้อมูลสำหรับ session: {session_id}")
        
        # Test 1: Overview Update
        print("\n1️⃣ ทดสอบ Overview Update...")
        await publisher.publish_overview_update(
            session_id, 
            "ทดสอบการส่งข้อมูล Overview ผ่าน NATS ไป GraphQL"
        )
        
        output_handler.update_overview(
            session_id,
            "ทดสอบการส่งข้อมูล Overview ผ่าน Output Handler"
        )
        print("✅ Overview Update ส่งแล้ว")
        
        # Test 2: Attack Analysis Update  
        print("\n2️⃣ ทดสอบ Attack Analysis Update...")
        attack_data = [
            {
                "tacticID": "TA0001",
                "tacticName": "Initial Access",
                "confidence": 0.85
            },
            {
                "tacticID": "TA0002", 
                "tacticName": "Execution",
                "confidence": 0.92
            }
        ]
        
        await publisher.publish_attack_update(session_id, attack_data)
        output_handler.update_attack_mapping(session_id, attack_data)
        print("✅ Attack Analysis Update ส่งแล้ว")
        
        # Test 3: Timeline Update
        print("\n3️⃣ ทดสอบ Timeline Update...")
        timeline_data = [
            {"stage": "Received Alert", "status": "success", "errorMessage": ""},
            {"stage": "Type Agent", "status": "success", "errorMessage": ""},
            {"stage": "Analyze Root Cause", "status": "in_progress", "errorMessage": ""},
        ]
        
        await publisher.publish_timeline_update(session_id, timeline_data)
        output_handler.update_timeline(session_id, timeline_data)
        print("✅ Timeline Update ส่งแล้ว")
        
        # Test 4: Recommendation Update
        print("\n4️⃣ ทดสอบ Recommendation Update...")
        recommendations = [
            {
                "description": "Immediate Response",
                "content": "Block suspicious IP addresses and isolate affected systems"
            },
            {
                "description": "Investigation Path", 
                "content": "Analyze network logs for lateral movement patterns"
            }
        ]
        
        await publisher.publish_recommendation_update(session_id, recommendations)
        output_handler.update_recommendation(
            session_id,
            "Security Recommendations",
            "Detailed security recommendations based on analysis"
        )
        print("✅ Recommendation Update ส่งแล้ว")
        
        # Test 5: Executive Summary Update
        print("\n5️⃣ ทดสอบ Executive Summary Update...")
        await publisher.publish_executive_summary_update(
            session_id,
            "Incident Summary",
            "Critical security incident detected and analyzed. Immediate action required."
        )
        
        output_handler.update_executive_summary(
            session_id,
            "Executive Summary",
            "High-level incident overview for management"
        )
        print("✅ Executive Summary Update ส่งแล้ว")
        
        # Test 6: Session Management
        print("\n6️⃣ ทดสอบ Session Management...")
        await publisher.publish_session_created(session_id, {
            "alert_id": "ALERT-001",
            "alert_name": "Suspicious Process Execution",
            "severity": "High"
        })
        
        await asyncio.sleep(1)  # รอสักครู่
        
        await publisher.publish_session_completed(session_id, "completed")
        print("✅ Session Management ส่งแล้ว")
        
        # Test 7: Full Output Update
        print("\n7️⃣ ทดสอบ Full Output Update...")
        output_handler.save_to_file()  # จะ trigger full output publish
        print("✅ Full Output Update ส่งแล้ว")
        
        print("\n🎉 ทดสอบทั้งหมดเสร็จสิ้น!")
        print("\n📋 สิ่งที่ควรตรวจสอบ:")
        print("1. เช็ค Frontend GraphQL Server console สำหรับข้อความ mutation")
        print("2. เช็ค Frontend UI ว่ามีการอัพเดทข้อมูล real-time หรือไม่")
        print("3. เช็คไฟล์ test_output.json ว่ามีข้อมูลหรือไม่")
        
        # รอสักครู่ก่อนปิด connection
        await asyncio.sleep(2)
        
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # ปิด connection
        if 'nats_handler' in locals():
            await nats_handler.close()
            print("🔐 ปิด NATS connection แล้ว")


if __name__ == "__main__":
    print("🧪 Agent AI - GraphQL Integration Test")
    print("=" * 50)
    asyncio.run(test_graphql_integration())