import os
import sys
import requests
from openai import OpenAI

# --- Hackathon-injected environment variables ---
API_BASE_URL = os.environ.get("API_BASE_URL", "https://api.openai.com/v1")
MODEL_NAME = os.environ.get("MODEL_NAME", "gpt-4o-mini")
HF_TOKEN = os.environ.get("HF_TOKEN")

if HF_TOKEN is None:
    raise ValueError("HF_TOKEN environment variable is required")

# --- Environment server URL (your HF Space) ---
ENV_URL = os.environ.get("ENV_URL", "https://eliab-data-privacy-agent-geu.hf.space")

# --- OpenAI client pointed at hackathon LLM proxy ---
client = OpenAI(
    base_url=API_BASE_URL,
    api_key=HF_TOKEN,
)

# --- Task definitions ---
TASKS = [
    {
        "id": "mask-emails",
        "env": "data-privacy-pro",
        "payload": "name,email\nAlice,alice@example.com\nBob,bob@test.org",
        "instruction": "Mask all email addresses in the following CSV by replacing them with [MASKED]. Return only the modified CSV, nothing else.",
    },
    {
        "id": "redact-phones",
        "env": "data-privacy-pro",
        "payload": "Call me at +1-800-555-0199 or 020 7946 0958.",
        "instruction": "Redact all phone numbers in the following text by replacing them with [REDACTED]. Return only the modified text, nothing else.",
    },
    {
        "id": "sanitize-json",
        "env": "data-privacy-pro",
        "payload": '{"user_id": "42", "password": "s3cr3t", "api_key": "abc123"}',
        "instruction": "Sanitize the following JSON by removing sensitive fields like password and api_key. Return only valid JSON, nothing else.",
    },
]


def _clamp(score: float) -> float:
    """Ensure score is strictly between 0 and 1, never exactly 0.0 or 1.0."""
    try:
        s = float(score)
    except (TypeError, ValueError):
        return 0.05
    if s != s:  # NaN
        return 0.05
    if s <= 0.0:
        return 0.05
    if s >= 1.0:
        return 0.95
    return s


def call_llm(instruction: str, payload: str) -> str:
    """Call the hackathon LLM proxy via OpenAI client."""
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


def submit_to_env(task_id: str, processed_output: str) -> float:
    """Reset the env for this task, then submit the LLM output as a step."""
    # Reset
    try:
        requests.post(
            f"{ENV_URL}/reset",
            json={"task_id": task_id},
            timeout=30,
        )
    except Exception as e:
        print(f"[WARN] reset error for {task_id}: {e}", file=sys.stderr, flush=True)

    # Step
    try:
        res = requests.post(
            f"{ENV_URL}/step",
            json={"action": {"task": task_id, "payload": processed_output}},
            timeout=30,
        )
        data = res.json()
        raw_reward = float(data.get("reward", 0.05))
        return _clamp(raw_reward)
    except Exception as e:
        print(f"[WARN] step error for {task_id}: {e}", file=sys.stderr, flush=True)
        return 0.05


def run():
    for task in TASKS:
        task_id = task["id"]
        env_name = task["env"]

        # --- [START] ---
        print(f"[START] task={task_id} env={env_name} model={MODEL_NAME}", flush=True)

        llm_output = task["payload"]  # fallback: original payload
        action_str = "submit"
        error_str = "null"
        reward = 0.05
        success = False

        try:
            llm_output = call_llm(task["instruction"], task["payload"])
            action_str = "llm_process"
        except Exception as e:
            error_str = str(e).replace("\n", " ")
            print(f"[WARN] LLM call failed for {task_id}: {e}", file=sys.stderr, flush=True)

        try:
            reward = submit_to_env(task_id, llm_output)
            success = reward > 0.5
        except Exception as e:
            error_str = str(e).replace("\n", " ")

        reward = _clamp(reward)

        # --- [STEP] ---
        print(
            f"[STEP] step=1 action={action_str} reward={reward:.4f} done=true error={error_str}",
            flush=True,
        )

        # --- [END] ---
        print(
            f"[END] success={'true' if success else 'false'} steps=1 score={reward:.4f}",
            flush=True,
        )

    sys.stdout.flush()


if __name__ == "__main__":
    run()
