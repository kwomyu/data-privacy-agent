from openenv.core.env_server import Environment, Action, Observation
from pydantic import Field
import re
import json


print("LOADED NEW ENV FILE")


class MyObservation(Observation):
    data: str = Field(..., description="The dataset to process")
    instruction: str = Field(..., description="Task-specific instruction")

class MyAction(Action):
    command: str = Field(..., description="Action: 'mask', 'redact', or 'clean'")
    target: str = Field(..., description="What to act on (e.g., 'email', 'phone', 'json')")

class DataPrivacyEnv(Environment):
    def __init__(self):
        super().__init__()

        self.scenarios = {
            "mask-emails": "Name,Email\nKwomyu,kwomyu@email.com\nDev,test@dev.io",
            "redact-phones": "Log: User accessed from +91-98765-43210 at 10AM.",
            "sanitize-json": '{"user_id": "UID123", "personal_mail": "secret@mail.com"}'
        }

        self.current_task_id = "mask-emails"
        self.data = self.scenarios[self.current_task_id]

        # REQUIRED STATE VARIABLES
        self.reward = 0.0
        self.done = False

    def reset(self, task_id="mask-emails", seed=None, episode_id=None) -> MyObservation:
        self.current_task_id = task_id
        self.data = self.scenarios.get(task_id, self.scenarios["mask-emails"])

        self.reward = 0.0
        self.done = False

        return MyObservation(
            data=self.data,
            instruction=f"Task: {task_id}"
        )

    def step(self, action: MyAction) -> MyObservation:

        # --- Task 1 ---
        if self.current_task_id == "mask-emails":
            if action.command == "mask" and action.target == "email":
                self.data = re.sub(r'\S+@\S+', '[MASKED]', self.data)
            else:
                self.reward = -0.2  # penalty for wrong action

        # --- Task 2 ---
        elif self.current_task_id == "redact-phones":
            if action.command == "redact" and action.target == "phone":
                self.data = re.sub(r'\+\d{2}-\d{5}-\d{5}', '[REDACTED]', self.data)
            else:
                self.reward = -0.2

        # --- Task 3 ---
        elif self.current_task_id == "sanitize-json":
            if action.command == "clean" and action.target == "json":
                try:
                    obj = json.loads(self.data)
                    if "personal_mail" in obj:
                        obj["email"] = "[MASKED]"
                        del obj["personal_mail"]
                    obj["user_id"] = "HASHED_ID"
                    self.data = json.dumps(obj)
                except Exception:
                    self.reward = 0.0
            else:
                self.reward = 0.0

        # Calculate reward ONLY if not penalized already
        if self.reward == 0.0:
            self.reward = self.calculate_score()

        self.done = True

        return MyObservation(
            data=self.data,
            instruction=f"Current Status: {self.current_task_id}"
        )

    def calculate_score(self) -> float:
        if self.current_task_id == "mask-emails":
            total = len(re.findall(r'\S+@\S+', self.scenarios["mask-emails"]))
            masked = self.data.count("[MASKED]")
            return masked / total if total > 0 else 0.0

        if self.current_task_id == "redact-phones":
            return 1.0 if "[REDACTED]" in self.data else 0.0

        if self.current_task_id == "sanitize-json":
            return 1.0 if "hashed_id" in self.data.lower() and "personal_mail" not in self.data.lower() else 0.0

        return 0.0

    @property
    def state(self):
        return {
            "observation": MyObservation(
                data=self.data,
                instruction=f"Current Status: {self.current_task_id}"
            ),
            "reward": self.reward,
            "done": self.done
        }
