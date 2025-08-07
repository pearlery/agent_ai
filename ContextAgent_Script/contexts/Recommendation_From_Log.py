import asyncio
from agents.agent_factory import AgentFactory
from tools.Example_Log_Keeper import example_log_body as example_log
from tools.Example_Log_Keeper import example_type_body as example_type
from contexts.compose_tools_data import compose_full_tools_data_from_log
from pydantic import BaseModel
from typing import Dict, Any


async def call_recommendation_agent_from_script(input_data: Dict[str, Any]) -> Dict[str, Any]:
    try:
        print(input_data)
        # Validate or use fallback examples
        log_data = input_data.get("log", {}).get("node") #or example_log["node"]
        type_data = input_data.get("type") #or example_type

        # Wrap as Pydantic if needed, or keep as dict
        tools_data = await compose_full_tools_data_from_log({"node": log_data})

        # Create and run the recommendation agent
        agent_factory = AgentFactory()
        agent = agent_factory.create_recommending_agent()

        response = agent(
            log=log_data,
            mitre_attack_type=type_data,
            client_tools_json=tools_data
        )
        return {"status": "success", "result": response}

    except Exception as e:
        return {"status": "error", "detail": str(e)}





#Testing code via script
"""
temp_input_data = {
  "log": {
    "node": {
      "alert_id": "YOMA-2503-000769",
      "alert_name": "WINDOWS METHODOLOGY [UAC Bypass via Sdclt.exe] on host yb-lt2338.yomabank.org",
      "alert_status": "Closed",
      "case_result": "FalsePositives",
      "contexts": {
        "os": "windows 11 22631",
        "src_ip": [
          "192.168.100.28"
        ],
        "user": "yb-lt2338$"
      },
      "detected_time": "2025-03-20T01:11:38.959Z",
      "events": [
        {
          "cmd_line": "\"C:\\Users\\moetheingioo\\AppData\\Local\\Microsoft\\OneDrive\\25.031.0217.0003\\FileCoAuth.exe\" -Embedding",
          "event_type": "audit_success",
          "file_name": "c:\\users\\moetheingioo\\appdata\\local\\microsoft\\onedrive\\25.031.0217.0003\\filecoauth.exe",
          "hash": {},
          "parent_process": "c:\\windows\\system32\\svchost.exe"
        },
        {
          "cmd_line": "\"C:\\Users\\moetheingioo\\AppData\\Local\\Microsoft\\OneDrive\\25.031.0217.0003\\FileCoAuth.exe\" -Embedding",
          "event_type": "audit_success",
          "file_name": "c:\\users\\moetheingioo\\appdata\\local\\microsoft\\onedrive\\25.031.0217.0003\\filecoauth.exe",
          "hash": {},
          "parent_process": "c:\\windows\\system32\\svchost.exe"
        },
        {
          "cmd_line": "\"C:\\Users\\moetheingioo\\AppData\\Local\\Microsoft\\OneDrive\\25.031.0217.0003\\FileCoAuth.exe\" -Embedding",
          "event_type": "audit_success",
          "file_name": "c:\\users\\moetheingioo\\appdata\\local\\microsoft\\onedrive\\25.031.0217.0003\\filecoauth.exe",
          "hash": {},
          "parent_process": "c:\\windows\\system32\\svchost.exe"
        },
        {
          "cmd_line": "\"C:\\Users\\moetheingioo\\AppData\\Local\\Microsoft\\OneDrive\\25.031.0217.0003\\FileCoAuth.exe\" -Embedding",
          "event_type": "audit_success",
          "file_name": "c:\\users\\moetheingioo\\appdata\\local\\microsoft\\onedrive\\25.031.0217.0003\\filecoauth.exe",
          "hash": {},
          "parent_process": "c:\\windows\\system32\\svchost.exe"
        },
        {
          "cmd_line": "\"C:\\Users\\moetheingioo\\AppData\\Local\\Microsoft\\OneDrive\\25.031.0217.0003\\FileCoAuth.exe\" -Embedding",
          "event_type": "audit_success",
          "file_name": "c:\\users\\moetheingioo\\appdata\\local\\microsoft\\onedrive\\25.031.0217.0003\\filecoauth.exe",
          "hash": {},
          "parent_process": "c:\\windows\\system32\\svchost.exe"
        },
        {
          "cmd_line": "\"C:\\Users\\moetheingioo\\AppData\\Local\\Microsoft\\OneDrive\\25.031.0217.0003\\FileCoAuth.exe\" -Embedding",
          "event_type": "audit_success",
          "file_name": "c:\\users\\moetheingioo\\appdata\\local\\microsoft\\onedrive\\25.031.0217.0003\\filecoauth.exe",
          "hash": {},
          "parent_process": "c:\\windows\\system32\\svchost.exe"
        },
        {
          "cmd_line": "\"C:\\Users\\moetheingioo\\AppData\\Local\\Microsoft\\OneDrive\\25.031.0217.0003\\FileCoAuth.exe\" -Embedding",
          "event_type": "audit_success",
          "file_name": "c:\\users\\moetheingioo\\appdata\\local\\microsoft\\onedrive\\25.031.0217.0003\\filecoauth.exe",
          "hash": {},
          "parent_process": "c:\\windows\\system32\\svchost.exe"
        },
        {
          "cmd_line": "\"C:\\Users\\moetheingioo\\AppData\\Local\\Microsoft\\OneDrive\\25.031.0217.0003\\FileCoAuth.exe\" -Embedding",
          "event_type": "audit_success",
          "file_name": "c:\\users\\moetheingioo\\appdata\\local\\microsoft\\onedrive\\25.031.0217.0003\\filecoauth.exe",
          "hash": {},
          "parent_process": "c:\\windows\\system32\\svchost.exe"
        },
        {
          "cmd_line": "\"C:\\Users\\moetheingioo\\AppData\\Local\\Microsoft\\OneDrive\\25.031.0217.0003\\FileCoAuth.exe\" -Embedding",
          "event_type": "audit_success",
          "file_name": "c:\\users\\moetheingioo\\appdata\\local\\microsoft\\onedrive\\25.031.0217.0003\\filecoauth.exe",
          "hash": {},
          "parent_process": "c:\\windows\\system32\\svchost.exe"
        },
        {
          "cmd_line": "\"C:\\Users\\moetheingioo\\AppData\\Local\\Microsoft\\OneDrive\\25.031.0217.0003\\FileCoAuth.exe\" -Embedding",
          "event_type": "audit_success",
          "file_name": "c:\\users\\moetheingioo\\appdata\\local\\microsoft\\onedrive\\25.031.0217.0003\\filecoauth.exe",
          "hash": {},
          "parent_process": "c:\\windows\\system32\\svchost.exe"
        },
        {
          "cmd_line": "\"C:\\Users\\moetheingioo\\AppData\\Local\\Microsoft\\OneDrive\\25.031.0217.0003\\FileCoAuth.exe\" -Embedding",
          "event_type": "audit_success",
          "file_name": "c:\\users\\moetheingioo\\appdata\\local\\microsoft\\onedrive\\25.031.0217.0003\\filecoauth.exe",
          "hash": {},
          "parent_process": "c:\\windows\\system32\\svchost.exe"
        },
        {
          "cmd_line": "\"C:\\Users\\moetheingioo\\AppData\\Local\\Microsoft\\OneDrive\\25.031.0217.0003\\FileCoAuth.exe\" -Embedding",
          "event_type": "audit_success",
          "file_name": "c:\\users\\moetheingioo\\appdata\\local\\microsoft\\onedrive\\25.031.0217.0003\\filecoauth.exe",
          "hash": {},
          "parent_process": "c:\\windows\\system32\\svchost.exe"
        },
        {
          "cmd_line": "\"C:\\Users\\moetheingioo\\AppData\\Local\\Microsoft\\OneDrive\\25.031.0217.0003\\FileCoAuth.exe\" -Embedding",
          "event_type": "audit_success",
          "file_name": "c:\\users\\moetheingioo\\appdata\\local\\microsoft\\onedrive\\25.031.0217.0003\\filecoauth.exe",
          "hash": {},
          "parent_process": "c:\\windows\\system32\\svchost.exe"
        },
        {
          "cmd_line": "\"C:\\Users\\moetheingioo\\AppData\\Local\\Microsoft\\OneDrive\\25.031.0217.0003\\FileCoAuth.exe\" -Embedding",
          "event_type": "audit_success",
          "file_name": "c:\\users\\moetheingioo\\appdata\\local\\microsoft\\onedrive\\25.031.0217.0003\\filecoauth.exe",
          "hash": {},
          "parent_process": "c:\\windows\\system32\\svchost.exe"
        },
        {
          "cmd_line": "\"C:\\Users\\moetheingioo\\AppData\\Local\\Microsoft\\OneDrive\\25.031.0217.0003\\FileCoAuth.exe\" -Embedding",
          "event_type": "audit_success",
          "file_name": "c:\\users\\moetheingioo\\appdata\\local\\microsoft\\onedrive\\25.031.0217.0003\\filecoauth.exe",
          "hash": {},
          "parent_process": "c:\\windows\\system32\\svchost.exe"
        },
        {
          "cmd_line": "\"C:\\Users\\moetheingioo\\AppData\\Local\\Microsoft\\OneDrive\\25.031.0217.0003\\FileCoAuth.exe\" -Embedding",
          "event_type": "audit_success",
          "file_name": "c:\\users\\moetheingioo\\appdata\\local\\microsoft\\onedrive\\25.031.0217.0003\\filecoauth.exe",
          "hash": {},
          "parent_process": "c:\\windows\\system32\\svchost.exe"
        },
        {
          "cmd_line": "\"C:\\Users\\moetheingioo\\AppData\\Local\\Microsoft\\OneDrive\\25.031.0217.0003\\FileCoAuth.exe\" -Embedding",
          "event_type": "audit_success",
          "file_name": "c:\\users\\moetheingioo\\appdata\\local\\microsoft\\onedrive\\25.031.0217.0003\\filecoauth.exe",
          "hash": {},
          "parent_process": "c:\\windows\\system32\\svchost.exe"
        },
        {
          "cmd_line": "\"C:\\Users\\moetheingioo\\AppData\\Local\\Microsoft\\OneDrive\\25.031.0217.0003\\FileCoAuth.exe\" -Embedding",
          "event_type": "audit_success",
          "file_name": "c:\\users\\moetheingioo\\appdata\\local\\microsoft\\onedrive\\25.031.0217.0003\\filecoauth.exe",
          "hash": {},
          "parent_process": "c:\\windows\\system32\\svchost.exe"
        }
      ],
      "id": "ea9632d7-8202-4b1d-92f1-d2ea18b542cf",
      "log_source": "Trellix Helix",
      "mitre": [
        {
          "id": "T1112",
          "link": "https://attack.mitre.org/techniques/T1112",
          "name_tactics": "Defense Evasion",
          "name_technique": "Modify Registry"
        },
        {
          "id": "T1548.002",
          "link": "https://attack.mitre.org/techniques/T1548/002",
          "name_subtechnique": "Bypass User Account Control",
          "name_tactics": "Defense Evasion",
          "name_technique": "Abuse Elevation Control Mechanism"
        },
        {
          "id": "T1548.002",
          "link": "https://attack.mitre.org/techniques/T1548/002",
          "name_subtechnique": "Bypass User Account Control",
          "name_tactics": "Privilege Escalation",
          "name_technique": "Abuse Elevation Control Mechanism"
        },
        {
          "id": "T1548",
          "link": "https://attack.mitre.org/techniques/T1548",
          "name_tactics": "Defense Evasion",
          "name_technique": "Abuse Elevation Control Mechanism"
        },
        {
          "id": "T1548",
          "link": "https://attack.mitre.org/techniques/T1548",
          "name_tactics": "Privilege Escalation",
          "name_technique": "Abuse Elevation Control Mechanism"
        }
      ],
      "objectMarking": [
        {
          "definition": "YOMA BANK",
          "id": "3732dad0-3d47-4a09-9378-674e7385767a"
        }
      ],
      "severity": "High",
      "sla": {
        "mtta": 11,
        "mttd": 73,
        "mttt": 5,
        "mttv": 39155.283
      },
      "tags": "Alert"
    }
  },
  "type": {
    "Mitre_Match": [
      {
        "Detection": "DS0024,DS0002,DS0009,DS0022,DS0017",
        "subtechnique": "",
        "tactic": "Defense Evasion",
        "technique": "Abuse Elevation Control Mechanism"
      },
      {
        "Detection": "DS0024,DS0009,DS0017",
        "subtechnique": "Bypass User Account Control",
        "tactic": "Defense Evasion",
        "technique": "Abuse Elevation Control Mechanism"
      }
    ],
    "prediction": {
      "subtechnique": [
        [
          "Bypass User Account Control",
          0.999921352605669
        ]
      ],
      "tactic": [
        [
          "Privilege Escalation",
          0.8073485842635361
        ],
        [
          "Defense Evasion",
          0.1913660317755721
        ]
      ],
      "technique": [
        [
          "Abuse Elevation Control Mechanism",
          0.9999484878515933
        ]
      ]
    }
  }
}


if __name__ == "__main__":
    # Example usage with fallback only (no override)
    input_data = temp_input_data

    result = asyncio.run(call_recommendation_agent_from_script(input_data))
    print(result)
    
"""