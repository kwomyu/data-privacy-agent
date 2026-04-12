import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from server.environment import DataPrivacyEnv, MyAction, MyObservation

app = FastAPI()
env = DataPrivacyEnv()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/reset")
def reset(body: dict):
    task_id = body.get("task_id", "mask-emails")
    obs = env.reset(task_id=task_id)
    return {"observation": obs.dict(), "reward": 0.05, "done": False}

@app.post("/step")
def step(body: dict):
    action_data = body.get("action", {})
    action = MyAction(**action_data)
    obs = env.step(action)
    return {"observation": obs.dict(), "reward": obs.reward, "done": obs.done}

@app.get("/state")
def state():
    s = env.state
    return s

@app.get("/tasks")
def tasks():
    return {"tasks": [
        {"id": "mask-emails"},
        {"id": "redact-phones"},
        {"id": "sanitize-json"},
    ]}

@app.get("/", response_class=HTMLResponse)
def read_root():
    return "<h1>🛡️ Data Privacy Environment — ONLINE</h1><p><a href='/docs'>API Docs</a></p>"

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7860)
