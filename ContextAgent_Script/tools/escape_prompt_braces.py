import json
import re


def load_escaped_prompt_template(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # Variables that must stay unescaped
    protected_vars = ["log", "mitre_attack_type", "client_tools_json"]

    # Step 1: Temporarily protect LangChain input variables
    for var in protected_vars:
        content = content.replace(f"{{{var}}}", f"<<{var}>>")

    # Step 2: Escape all curly braces
    content = content.replace("{", "{{").replace("}", "}}")

    # Step 3: Restore protected variables
    for var in protected_vars:
        content = content.replace(f"<<{var}>>", f"{{{var}}}")

    return content