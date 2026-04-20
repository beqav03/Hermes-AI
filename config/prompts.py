import json


def build_system_prompt(skills: list) -> str:
    skill_list = json.dumps(skills, ensure_ascii=False, indent=2)
    return (
        "You are Hermes, a Windows AI assistant. The user speaks English or Georgian.\n\n"
        "Parse the user's command and return JSON in this exact format:\n"
        '{"skill": "<skill_name>", "params": {...}}\n\n'
        "If no skill matches, return:\n"
        '{"skill": "none", "reply": "<short explanation in the user\'s language>"}\n\n'
        f"Available skills:\n{skill_list}\n\n"
        "Return JSON only. No other text."
    )