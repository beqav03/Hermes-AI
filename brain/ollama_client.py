import json
import ollama


class OllamaBrain:
    def __init__(self, model: str = "qwen2.5:7b-instruct"):
        self.model = model

    def parse_intent(self, user_input: str, system_prompt: str) -> dict:
        response = ollama.chat(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input},
            ],
            format="json",
            options={"temperature": 0.1},
        )
        return json.loads(response["message"]["content"])