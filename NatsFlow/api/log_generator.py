# api/log_generator.py
import random
import uuid
from fastapi import APIRouter, Query

loggen_router = APIRouter()

# Predefined values
TRIAGE_LEVELS = ["Low", "Medium", "High", "Critical"]
SEVERITIES = ["info", "warning", "error", "critical"]
MITRE_IDS = ["T1003", "T1059", "T1204", "T1071"]

# Generate base IP block (first 2 octets)
def generate_random_ip_block():
    first = random.randint(1, 223)
    second = random.randint(0, 255)
    return f"{first}.{second}"

# Generate full log using base IP block
def generate_random_log(base_ip_prefix: str):
    ip_count = random.randint(1, 3)
    ips = [
        f"{base_ip_prefix}.{random.randint(0, 255)}.{random.randint(1, 254)}"
        for _ in range(ip_count)
    ]

    return {
        "alert": {"id": str(uuid.uuid4())},
        "triage": {
            "triage_level": random.choice(TRIAGE_LEVELS),
            "score": random.randint(0, 100),
            "mitre_ids": random.sample(MITRE_IDS, random.randint(0, len(MITRE_IDS))),
            "src_ip": ips,
            "severity": random.choice(SEVERITIES)
        }
    }

# GET /api/logs/generate-logs?count=5
@loggen_router.get("/generate-logs")
def generate_logs(count: int = Query(1, ge=1, le=20)):
    base_ip_prefix = generate_random_ip_block()
    return [generate_random_log(base_ip_prefix) for _ in range(count)]
