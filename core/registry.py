from typing import Callable


class SkillRegistry:
    def __init__(self):
        self._skills: dict = {}

    def register(self, name: str, handler: Callable, description: str, params: dict):
        self._skills[name] = {
            "handler": handler,
            "description": description,
            "params": params,
        }

    def manifest(self) -> list:
        return [
            {"name": n, "description": s["description"], "params": s["params"]}
            for n, s in self._skills.items()
        ]

    def call(self, name: str, params: dict):
        if name not in self._skills:
            raise ValueError(f"Unknown skill: {name}")
        return self._skills[name]["handler"](**(params or {}))