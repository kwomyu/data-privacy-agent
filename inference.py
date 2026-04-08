import os
import sys
import requests

API_BASE_URL = os.getenv("API_BASE_URL", "https://eliab-data-privacy-agent-geu.hf.space")

TASKS = [
    {
        "id": "mask-emails",
        "payload": "name,email\nAlice,alice@example.com\nBob,bob@test.org",
    },
    {
        "id": "redact-phones",
        "payload": "Call me at +1-800-555-0199 or 020 7946 0958.",
    },
    {
        "id": "sanitize-json",
        "payload": {"user_id": "42", "password": "s3cr3t", "api_key": "abc123"},
    },
]


def solve_task(task_id, payload):
    try:
        requests.post(
            f"{API_BASE_URL}/reset",
            json={"task_id": task_id},
            timeout=30,
        )
    except Exception:
        pass

    try:
        res = requests.post(
            f"{API_BASE_URL}/step",
            json={"action": {"task": task_id, "payload": payload}},
            timeout=30,
        )
        return res.json()
    except Exception as e:
        return {"reward": 0.0, "error": str(e)}


def run():
    try:
        r = requests.get(f"{API_BASE_URL}/tasks", timeout=15)
        if r.status_code == 200:
            data = r.json()
            task_ids = [t["id"] for t in data.get("tasks", [])]
        else:
            task_ids = [t["id"] for t in TASKS]
    except Exception:
        task_ids = [t["id"] for t in TASKS]

    payload_map = {t["id"]: t["payload"] for t in TASKS}

    for task_id in task_ids:
        payload = payload_map.get(task_id, "")

        print(f"[START] task={task_id}", flush=True)

        result = solve_task(task_id, payload)
        reward = float(result.get("reward", 0.0))

        print(f"[STEP] step=1 reward={reward}", flush=True)
        print(f"[END] task={task_id} score={reward} steps=1", flush=True)

    sys.stdout.flush()


if __name__ == "__main__":
    run()
