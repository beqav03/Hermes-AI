import json

import ollama

from config.settings import OLLAMA_MODEL, OLLAMA_TIMEOUT


class OllamaBrain:
    def __init__(self, model: str = OLLAMA_MODEL):
        self.model = model

    def parse_intent(self, user_input: str, system_prompt: str) -> dict:
        response = ollama.chat(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input},
            ],
            format="json",
            options={
                "temperature": 0.1,
                "num_ctx": 2048,
                "num_predict": 256,
            },
        )
        return json.loads(response["message"]["content"])