from brain.ollama_client import OllamaBrain
from config.prompts import build_system_prompt
from core.registry import SkillRegistry


class Router:
    def __init__(self, registry: SkillRegistry, brain: OllamaBrain, status_cb=None):
        self.registry = registry
        self.brain = brain
        self.status = status_cb or (lambda s: None)

    def handle(self, user_input: str) -> str:
        self.status("THINKING")
        system_prompt = build_system_prompt(self.registry.manifest())
        plan = self.brain.parse_intent(user_input, system_prompt)

        if plan.get("skill") in (None, "none"):
            return plan.get("reply", "I didn't understand that.")

        self.status("EXECUTING")
        try:
            result = self.registry.call(plan["skill"], plan.get("params", {}))
            return result or "Done."
        except Exception as e:
            self.status("ERROR")
            return f"Error running {plan['skill']}: {e}"