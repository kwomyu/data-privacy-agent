from pydantic import BaseModel, Field
import re
import json

print("LOADED NEW ENV FILE")


def _clamp(score: float) -> float:
    try:
        s = float(score)
    except (TypeError, ValueError):
        return 0.05
    if s != s:
        return 0.05
    if s <= 0.0:
        return 0.05
    if s >= 1.0:
        return 0.95
    return round(s, 4)


class MyObservation(BaseModel):
    data: str = Field(..., description="The dataset to process")
    instruction: str = Field(..., description="Task-specific instruction")
    reward: float = Field(default=0.05)
    done: bool = Field(default=False)


class MyAction(BaseModel):
    command: str = Field(..., description="Action: mask, redact, or clean")
    target: str = Field(..., description="What to act on")


class DataPrivacyEnv:
    def __init__(self):
        self.scenarios = {
            "mask-emails": "Name,Email\nKwomyu,kwomyu@email.com\nDev,test@dev.io",
            "redact-phones": "Log: User accessed from +91-98765-43210 at 10AM.",
            "sanitize-json": '{"user_id": "UID123", "personal_mail": "secret@mail.com"}'
        }
        self.current_task_id = "mask-emails"
        self.data = self.scenarios[self.current_task_id]
        self.reward = 0.05
        self.done = False

    def reset(self, task_id="mask-emails") -> MyObservation:
        self.current_task_id = task_id
        self.data = self.scenarios.get(task_id, self.scenarios["mask-emails"])
        self.reward = 0.05
        self.done = False
        return MyObservation(
            data=self.data,
            instruction=f"Task: {task_id}",
            reward=0.05,
            done=False,
        )

    def step(self, action: MyAction) -> MyObservation:
        if self.current_task_id == "mask-emails":
            if action.command == "mask" and action.target == "email":
                self.data = re.sub(r'\S+@\S+', '[MASKED]', self.data)
            else:
                self.reward = 0.05
                self.done = True
                return MyObservation(data=self.data, instruction=self.current_task_id, reward=0.05, done=True)

        elif self.current_task_id == "redact-phones":
            if action.command == "redact" and action.target == "phone":
                self.data = re.sub(r'\+\d{2}-\d{5}-\d{5}', '[REDACTED]', self.data)
            else:
                self.reward = 0.05
                self.done = True
                return MyObservation(data=self.data, instruction=self.current_task_id, reward=0.05, done=True)

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
                    self.reward = 0.05
                    self.done = True
                    return MyObservation(data=self.data, instruction=self.current_task_id, reward=0.05, done=True)
            else:
                self.reward = 0.05
                self.done = True
                return MyObservation(data=self.data, instruction=self.current_task_id, reward=0.05, done=True)

        self.reward = _clamp(self.calculate_score())
        self.done = True
        return MyObservation(data=self.data, instruction=self.current_task_id, reward=self.reward, done=True)

    def calculate_score(self) -> float:
        if self.current_task_id == "mask-emails":
            total = len(re.findall(r'\S+@\S+', self.scenarios["mask-emails"]))
            masked = self.data.count("[MASKED]")
            return (masked / total * 0.94) if total > 0 else 0.05

        if self.current_task_id == "redact-phones":
            return 0.94 if "[REDACTED]" in self.data else 0.05

        if self.current_task_id == "sanitize-json":
            return 0.94 if ("hashed_id" in self.data.lower() and "personal_mail" not in self.data.lower()) else 0.05

        return 0.05

    @property
    def state(self):
        return {
            "observation": MyObservation(
                data=self.data,
                instruction=self.current_task_id,
                reward=_clamp(self.reward),
                done=self.done,
            ).dict(),
            "reward": _clamp(self.reward),
            "done": self.done,
        }
