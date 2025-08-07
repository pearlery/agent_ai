example_log_body = {
          "node": {
            "id": "ea9632d7-8202-4b1d-92f1-d2ea18b542cf",
            "alert_id": "YOMA-2503-000769",
            "alert_name": "WINDOWS METHODOLOGY [UAC Bypass via Sdclt.exe] on host yb-lt2338.yomabank.org",
            "tags": "Alert",
            "incident_type": None,
            "severity": "High",
            "alert_status": "Closed",
            "log_source": "Trellix Helix",
            "case_result": "FalsePositives",
            "detected_time": "2025-03-20T01:11:38.959Z",
            "mitre": [
              {
                "id": "T1112",
                "link": "https://attack.mitre.org/techniques/T1112",
                "name_tactics": "Defense Evasion",
                "name_technique": "Modify Registry",
                "name_subtechnique": None
              },
              {
                "id": "T1548.002",
                "link": "https://attack.mitre.org/techniques/T1548/002",
                "name_tactics": "Defense Evasion",
                "name_technique": "Abuse Elevation Control Mechanism",
                "name_subtechnique": "Bypass User Account Control"
              },
              {
                "id": "T1548.002",
                "link": "https://attack.mitre.org/techniques/T1548/002",
                "name_tactics": "Privilege Escalation",
                "name_technique": "Abuse Elevation Control Mechanism",
                "name_subtechnique": "Bypass User Account Control"
              },
              {
                "id": "T1548",
                "link": "https://attack.mitre.org/techniques/T1548",
                "name_tactics": "Defense Evasion",
                "name_technique": "Abuse Elevation Control Mechanism",
                "name_subtechnique": None
              },
              {
                "id": "T1548",
                "link": "https://attack.mitre.org/techniques/T1548",
                "name_tactics": "Privilege Escalation",
                "name_technique": "Abuse Elevation Control Mechanism",
                "name_subtechnique": None
              }
            ],
            "objectMarking": [
              {
                "id": "3732dad0-3d47-4a09-9378-674e7385767a",
                "definition": "YOMA BANK"
              }
            ],
            "contexts": {
              "domain": None,
              "endpoint_type": None,
              "os": "windows 11 22631",
              "user": "yb-lt2338$",
              "user_priv": None,
              "src_ip": [
                "192.168.100.28"
              ]
            },
            "events": [
              {
                "domain": None,
                "dst_ip": None,
                "dst_port": None,
                "src_ip": None,
                "src_port": None,
                "user": None,
                "ip_malicious": None,
                "hash_malicious": None,
                "hash": {
                  "sha1": None,
                  "sha256": None,
                  "md5": None
                },
                "file_name": "c:\\users\\moetheingioo\\appdata\\local\\microsoft\\onedrive\\25.031.0217.0003\\filecoauth.exe",
                "file_size": None,
                "file_path": None,
                "cmd_line": "\"C:\\Users\\moetheingioo\\AppData\\Local\\Microsoft\\OneDrive\\25.031.0217.0003\\FileCoAuth.exe\" -Embedding",
                "parent_process": "c:\\windows\\system32\\svchost.exe",
                "event_type": "audit_success"
              },
              {
                "domain": None,
                "dst_ip": None,
                "dst_port": None,
                "src_ip": None,
                "src_port": None,
                "user": None,
                "ip_malicious": None,
                "hash_malicious": None,
                "hash": {
                  "sha1": None,
                  "sha256": None,
                  "md5": None
                },
                "file_name": "c:\\users\\moetheingioo\\appdata\\local\\microsoft\\onedrive\\25.031.0217.0003\\filecoauth.exe",
                "file_size": None,
                "file_path": None,
                "cmd_line": "\"C:\\Users\\moetheingioo\\AppData\\Local\\Microsoft\\OneDrive\\25.031.0217.0003\\FileCoAuth.exe\" -Embedding",
                "parent_process": "c:\\windows\\system32\\svchost.exe",
                "event_type": "audit_success"
              },
              {
                "domain": None,
                "dst_ip": None,
                "dst_port": None,
                "src_ip": None,
                "src_port": None,
                "user": None,
                "ip_malicious": None,
                "hash_malicious": None,
                "hash": {
                  "sha1": None,
                  "sha256": None,
                  "md5": None
                },
                "file_name": "c:\\users\\moetheingioo\\appdata\\local\\microsoft\\onedrive\\25.031.0217.0003\\filecoauth.exe",
                "file_size": None,
                "file_path": None,
                "cmd_line": "\"C:\\Users\\moetheingioo\\AppData\\Local\\Microsoft\\OneDrive\\25.031.0217.0003\\FileCoAuth.exe\" -Embedding",
                "parent_process": "c:\\windows\\system32\\svchost.exe",
                "event_type": "audit_success"
              },
              {
                "domain": None,
                "dst_ip": None,
                "dst_port": None,
                "src_ip": None,
                "src_port": None,
                "user": None,
                "ip_malicious": None,
                "hash_malicious": None,
                "hash": {
                  "sha1": None,
                  "sha256": None,
                  "md5": None
                },
                "file_name": "c:\\users\\moetheingioo\\appdata\\local\\microsoft\\onedrive\\25.031.0217.0003\\filecoauth.exe",
                "file_size": None,
                "file_path": None,
                "cmd_line": "\"C:\\Users\\moetheingioo\\AppData\\Local\\Microsoft\\OneDrive\\25.031.0217.0003\\FileCoAuth.exe\" -Embedding",
                "parent_process": "c:\\windows\\system32\\svchost.exe",
                "event_type": "audit_success"
              },
              {
                "domain": None,
                "dst_ip": None,
                "dst_port": None,
                "src_ip": None,
                "src_port": None,
                "user": None,
                "ip_malicious": None,
                "hash_malicious": None,
                "hash": {
                  "sha1": None,
                  "sha256": None,
                  "md5": None
                },
                "file_name": "c:\\users\\moetheingioo\\appdata\\local\\microsoft\\onedrive\\25.031.0217.0003\\filecoauth.exe",
                "file_size": None,
                "file_path": None,
                "cmd_line": "\"C:\\Users\\moetheingioo\\AppData\\Local\\Microsoft\\OneDrive\\25.031.0217.0003\\FileCoAuth.exe\" -Embedding",
                "parent_process": "c:\\windows\\system32\\svchost.exe",
                "event_type": "audit_success"
              },
              {
                "domain": None,
                "dst_ip": None,
                "dst_port": None,
                "src_ip": None,
                "src_port": None,
                "user": None,
                "ip_malicious": None,
                "hash_malicious": None,
                "hash": {
                  "sha1": None,
                  "sha256": None,
                  "md5": None
                },
                "file_name": "c:\\users\\moetheingioo\\appdata\\local\\microsoft\\onedrive\\25.031.0217.0003\\filecoauth.exe",
                "file_size": None,
                "file_path": None,
                "cmd_line": "\"C:\\Users\\moetheingioo\\AppData\\Local\\Microsoft\\OneDrive\\25.031.0217.0003\\FileCoAuth.exe\" -Embedding",
                "parent_process": "c:\\windows\\system32\\svchost.exe",
                "event_type": "audit_success"
              },
              {
                "domain": None,
                "dst_ip": None,
                "dst_port": None,
                "src_ip": None,
                "src_port": None,
                "user": None,
                "ip_malicious": None,
                "hash_malicious": None,
                "hash": {
                  "sha1": None,
                  "sha256": None,
                  "md5": None
                },
                "file_name": "c:\\users\\moetheingioo\\appdata\\local\\microsoft\\onedrive\\25.031.0217.0003\\filecoauth.exe",
                "file_size": None,
                "file_path": None,
                "cmd_line": "\"C:\\Users\\moetheingioo\\AppData\\Local\\Microsoft\\OneDrive\\25.031.0217.0003\\FileCoAuth.exe\" -Embedding",
                "parent_process": "c:\\windows\\system32\\svchost.exe",
                "event_type": "audit_success"
              },
              {
                "domain": None,
                "dst_ip": None,
                "dst_port": None,
                "src_ip": None,
                "src_port": None,
                "user": None,
                "ip_malicious": None,
                "hash_malicious": None,
                "hash": {
                  "sha1": None,
                  "sha256": None,
                  "md5": None
                },
                "file_name": "c:\\users\\moetheingioo\\appdata\\local\\microsoft\\onedrive\\25.031.0217.0003\\filecoauth.exe",
                "file_size": None,
                "file_path": None,
                "cmd_line": "\"C:\\Users\\moetheingioo\\AppData\\Local\\Microsoft\\OneDrive\\25.031.0217.0003\\FileCoAuth.exe\" -Embedding",
                "parent_process": "c:\\windows\\system32\\svchost.exe",
                "event_type": "audit_success"
              },
              {
                "domain": None,
                "dst_ip": None,
                "dst_port": None,
                "src_ip": None,
                "src_port": None,
                "user": None,
                "ip_malicious": None,
                "hash_malicious": None,
                "hash": {
                  "sha1": None,
                  "sha256": None,
                  "md5": None
                },
                "file_name": "c:\\users\\moetheingioo\\appdata\\local\\microsoft\\onedrive\\25.031.0217.0003\\filecoauth.exe",
                "file_size": None,
                "file_path": None,
                "cmd_line": "\"C:\\Users\\moetheingioo\\AppData\\Local\\Microsoft\\OneDrive\\25.031.0217.0003\\FileCoAuth.exe\" -Embedding",
                "parent_process": "c:\\windows\\system32\\svchost.exe",
                "event_type": "audit_success"
              },
              {
                "domain": None,
                "dst_ip": None,
                "dst_port": None,
                "src_ip": None,
                "src_port": None,
                "user": None,
                "ip_malicious": None,
                "hash_malicious": None,
                "hash": {
                  "sha1": None,
                  "sha256": None,
                  "md5": None
                },
                "file_name": "c:\\users\\moetheingioo\\appdata\\local\\microsoft\\onedrive\\25.031.0217.0003\\filecoauth.exe",
                "file_size": None,
                "file_path": None,
                "cmd_line": "\"C:\\Users\\moetheingioo\\AppData\\Local\\Microsoft\\OneDrive\\25.031.0217.0003\\FileCoAuth.exe\" -Embedding",
                "parent_process": "c:\\windows\\system32\\svchost.exe",
                "event_type": "audit_success"
              },
              {
                "domain": None,
                "dst_ip": None,
                "dst_port": None,
                "src_ip": None,
                "src_port": None,
                "user": None,
                "ip_malicious": None,
                "hash_malicious": None,
                "hash": {
                  "sha1": None,
                  "sha256": None,
                  "md5": None
                },
                "file_name": "c:\\users\\moetheingioo\\appdata\\local\\microsoft\\onedrive\\25.031.0217.0003\\filecoauth.exe",
                "file_size": None,
                "file_path": None,
                "cmd_line": "\"C:\\Users\\moetheingioo\\AppData\\Local\\Microsoft\\OneDrive\\25.031.0217.0003\\FileCoAuth.exe\" -Embedding",
                "parent_process": "c:\\windows\\system32\\svchost.exe",
                "event_type": "audit_success"
              },
              {
                "domain": None,
                "dst_ip": None,
                "dst_port": None,
                "src_ip": None,
                "src_port": None,
                "user": None,
                "ip_malicious": None,
                "hash_malicious": None,
                "hash": {
                  "sha1": None,
                  "sha256": None,
                  "md5": None
                },
                "file_name": "c:\\users\\moetheingioo\\appdata\\local\\microsoft\\onedrive\\25.031.0217.0003\\filecoauth.exe",
                "file_size": None,
                "file_path": None,
                "cmd_line": "\"C:\\Users\\moetheingioo\\AppData\\Local\\Microsoft\\OneDrive\\25.031.0217.0003\\FileCoAuth.exe\" -Embedding",
                "parent_process": "c:\\windows\\system32\\svchost.exe",
                "event_type": "audit_success"
              },
              {
                "domain": None,
                "dst_ip": None,
                "dst_port": None,
                "src_ip": None,
                "src_port": None,
                "user": None,
                "ip_malicious": None,
                "hash_malicious": None,
                "hash": {
                  "sha1": None,
                  "sha256": None,
                  "md5": None
                },
                "file_name": "c:\\users\\moetheingioo\\appdata\\local\\microsoft\\onedrive\\25.031.0217.0003\\filecoauth.exe",
                "file_size": None,
                "file_path": None,
                "cmd_line": "\"C:\\Users\\moetheingioo\\AppData\\Local\\Microsoft\\OneDrive\\25.031.0217.0003\\FileCoAuth.exe\" -Embedding",
                "parent_process": "c:\\windows\\system32\\svchost.exe",
                "event_type": "audit_success"
              },
              {
                "domain": None,
                "dst_ip": None,
                "dst_port": None,
                "src_ip": None,
                "src_port": None,
                "user": None,
                "ip_malicious": None,
                "hash_malicious": None,
                "hash": {
                  "sha1": None,
                  "sha256": None,
                  "md5": None
                },
                "file_name": "c:\\users\\moetheingioo\\appdata\\local\\microsoft\\onedrive\\25.031.0217.0003\\filecoauth.exe",
                "file_size": None,
                "file_path": None,
                "cmd_line": "\"C:\\Users\\moetheingioo\\AppData\\Local\\Microsoft\\OneDrive\\25.031.0217.0003\\FileCoAuth.exe\" -Embedding",
                "parent_process": "c:\\windows\\system32\\svchost.exe",
                "event_type": "audit_success"
              },
              {
                "domain": None,
                "dst_ip": None,
                "dst_port": None,
                "src_ip": None,
                "src_port": None,
                "user": None,
                "ip_malicious": None,
                "hash_malicious": None,
                "hash": {
                  "sha1": None,
                  "sha256": None,
                  "md5": None
                },
                "file_name": "c:\\users\\moetheingioo\\appdata\\local\\microsoft\\onedrive\\25.031.0217.0003\\filecoauth.exe",
                "file_size": None,
                "file_path": None,
                "cmd_line": "\"C:\\Users\\moetheingioo\\AppData\\Local\\Microsoft\\OneDrive\\25.031.0217.0003\\FileCoAuth.exe\" -Embedding",
                "parent_process": "c:\\windows\\system32\\svchost.exe",
                "event_type": "audit_success"
              },
              {
                "domain": None,
                "dst_ip": None,
                "dst_port": None,
                "src_ip": None,
                "src_port": None,
                "user": None,
                "ip_malicious": None,
                "hash_malicious": None,
                "hash": {
                  "sha1": None,
                  "sha256": None,
                  "md5": None
                },
                "file_name": "c:\\users\\moetheingioo\\appdata\\local\\microsoft\\onedrive\\25.031.0217.0003\\filecoauth.exe",
                "file_size": None,
                "file_path": None,
                "cmd_line": "\"C:\\Users\\moetheingioo\\AppData\\Local\\Microsoft\\OneDrive\\25.031.0217.0003\\FileCoAuth.exe\" -Embedding",
                "parent_process": "c:\\windows\\system32\\svchost.exe",
                "event_type": "audit_success"
              },
              {
                "domain": None,
                "dst_ip": None,
                "dst_port": None,
                "src_ip": None,
                "src_port": None,
                "user": None,
                "ip_malicious": None,
                "hash_malicious": None,
                "hash": {
                  "sha1": None,
                  "sha256": None,
                  "md5": None
                },
                "file_name": "c:\\users\\moetheingioo\\appdata\\local\\microsoft\\onedrive\\25.031.0217.0003\\filecoauth.exe",
                "file_size": None,
                "file_path": None,
                "cmd_line": "\"C:\\Users\\moetheingioo\\AppData\\Local\\Microsoft\\OneDrive\\25.031.0217.0003\\FileCoAuth.exe\" -Embedding",
                "parent_process": "c:\\windows\\system32\\svchost.exe",
                "event_type": "audit_success"
              },
              {
                "domain": None,
                "dst_ip": None,
                "dst_port": None,
                "src_ip": None,
                "src_port": None,
                "user": None,
                "ip_malicious": None,
                "hash_malicious": None,
                "hash": {
                  "sha1": None,
                  "sha256": None,
                  "md5": None
                },
                "file_name": "c:\\users\\moetheingioo\\appdata\\local\\microsoft\\onedrive\\25.031.0217.0003\\filecoauth.exe",
                "file_size": None,
                "file_path": None,
                "cmd_line": "\"C:\\Users\\moetheingioo\\AppData\\Local\\Microsoft\\OneDrive\\25.031.0217.0003\\FileCoAuth.exe\" -Embedding",
                "parent_process": "c:\\windows\\system32\\svchost.exe",
                "event_type": "audit_success"
              }
            ],
            "sla": {
              "mttd": 73,
              "mtta": 11,
              "mttt": 5,
              "mtti": None,
              "mttn": None,
              "mttv": 39155.283,
              "mttr": None
            }
          }
        }


example_prediction_body = {
  "prediction": {
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
    ],
    "subtechnique": [
      [
        "Bypass User Account Control",
        0.999921352605669
      ]
    ]
  }
}