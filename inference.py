import os
import sys
import requests

API_BASE_URL = os.getenv("API_BASE_URL", "https://eliab-data-privacy-agent-geu.hf.space")
MODEL_NAME = os.getenv("MODEL_NAME", "baseline-agent")
HF_TOKEN = os.getenv("HF_TOKEN")  # no default

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


def solve_task(task_id: str, payload) -> dict:
    """Reset environment then send one action step, return step result."""
    try:
        # Reset for this task
        requests.post(
            f"{API_BASE_URL}/reset",
            json={"task_id": task_id},
            timeout=30,
        )
    except Exception:
        pass  # continue even if reset fails

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
    # Try to fetch task list from server; fall back to local TASKS list
    try:
        r = requests.get(f"{API_BASE_URL}/tasks", timeout=15)
        if r.status_code == 200:
            data = r.json()
            task_ids = [t["id"] for t in data.get("tasks", [])]
        else:
            task_ids = [t["id"] for t in TASKS]
    except Exception:
        task_ids = [t["id"] for t in TASKS]

    # Build a quick lookup for payloads
    payload_map = {t["id"]: t["payload"] for t in TASKS}

    for task_id in task_ids:
        payload = payload_map.get(task_id, "")

        # ── [START] block ──────────────────────────────────────────────
        print(f"[START] task={task_id}", flush=True)

        result = solve_task(task_id, payload)

        reward = float(result.get("reward", 0.0))
        step_num = 1

        # ── [STEP] block ───────────────────────────────────────────────
        print(f"[STEP] step={step_num} reward={reward}", flush=True)

        # ── [END] block ────────────────────────────────────────────────
        print(f"[END] task={task_id} score={reward} steps={step_num}", flush=True)

    sys.stdout.flush()


if __name__ == "__main__":
    run()

