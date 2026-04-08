import os
import sys
import requests
from openai import OpenAI

# --- Hackathon-injected environment variables ---
API_BASE_URL = os.environ.get("API_BASE_URL", "https://eliab-data-privacy-agent-geu.hf.space")
API_KEY = os.environ.get("API_KEY", "dummy-key")
LLM_BASE_URL = os.environ.get("LLM_BASE_URL", API_BASE_URL)
MODEL_NAME = os.environ.get("MODEL_NAME", "gpt-4o-mini")

# --- Initialize OpenAI client pointing to hackathon's LiteLLM proxy ---
client = OpenAI(
    base_url=LLM_BASE_URL,
    api_key=API_KEY,
)

# --- Task definitions with sample payloads ---
TASKS = [
    {
        "id": "mask-emails",
        "payload": "name,email\nAlice,alice@example.com\nBob,bob@test.org",
        "instruction": "Mask all email addresses in the following CSV by replacing them with [MASKED]. Return only the modified CSV, nothing else.",
    },
    {
        "id": "redact-phones",
        "payload": "Call me at +1-800-555-0199 or 020 7946 0958.",
        "instruction": "Redact all phone numbers in the following text by replacing them with [REDACTED]. Return only the modified text, nothing else.",
    },
    {
        "id": "sanitize-json",
        "payload": '{"user_id": "42", "password": "s3cr3t", "api_key": "abc123"}',
        "instruction": "Sanitize the following JSON by removing sensitive fields like password and api_key. Return only valid JSON, nothing else.",
    },
]


def call_llm(instruction: str, payload: str) -> str:
    """Call the hackathon LiteLLM proxy to process a task."""
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": instruction},
            {"role": "user", "content": payload},
        ],
        max_tokens=512,
        temperature=0,
    )
    return response.choices[0].message.content.strip()


def submit_step(task_id: str, processed_output: str) -> float:
    """Submit the processed result to the environment and get reward."""
    try:
        requests.post(
            f"{API_BASE_URL}/reset",
            json={"task_id": task_id},
            timeout=30,
        )
        res = requests.post(
            f"{API_BASE_URL}/step",
            json={"action": {"task": task_id, "payload": processed_output}},
            timeout=30,
        )
        data = res.json()
        return float(data.get("reward", 0.0))
    except Exception as e:
        print(f"[WARN] step error: {e}", flush=True)
        return 0.0


def run():
    try:
        r = requests.get(f"{API_BASE_URL}/tasks", timeout=15)
        if r.status_code == 200:
            task_ids = [t["id"] for t in r.json().get("tasks", [])]
        else:
            task_ids = [t["id"] for t in TASKS]
    except Exception:
        task_ids = [t["id"] for t in TASKS]

    task_map = {t["id"]: t for t in TASKS}

    for task_id in task_ids:
        task = task_map.get(task_id)
        if not task:
            continue

        print(f"[START] task={task_id}", flush=True)

        llm_output = call_llm(task["instruction"], task["payload"])
        reward = submit_step(task_id, llm_output)

        print(f"[STEP] step=1 reward={reward}", flush=True)
        print(f"[END] task={task_id} score={reward} steps=1", flush=True)

    sys.stdout.flush()


if __name__ == "__main__":
    run()
