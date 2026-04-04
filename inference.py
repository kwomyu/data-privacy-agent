import os
import requests

API_BASE_URL = os.getenv("API_BASE_URL", "https://eliab-data-privacy-agent-geu.hf.space")
MODEL_NAME = os.getenv("MODEL_NAME", "baseline-agent")
HF_TOKEN = os.getenv("HF_TOKEN")  # no default


def solve(task_id, payload):
    requests.post(f"{API_BASE_URL}/reset")

    res = requests.post(
        f"{API_BASE_URL}/step",
        json={"action": {"task": task_id, "payload": payload}},
    )

    return res.json()


def run():
    tasks = requests.get(f"{API_BASE_URL}/tasks").json()["tasks"]

    outputs = []

    for t in tasks:
        task_id = t["id"]

        if task_id == "mask-emails":
            payload = "email me at test@gmail.com"
        elif task_id == "redact-phones":
            payload = "call 123-456-7890"
        else:
            payload = {"password": "abc", "api_key": "123"}

        result = solve(task_id, payload)
        outputs.append(result)

    return outputs


if __name__ == "__main__":
    print(run())
