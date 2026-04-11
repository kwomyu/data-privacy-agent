import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from openenv.core.env_server import create_fastapi_app
from server.environment import DataPrivacyEnv, MyAction, MyObservation

# 1. Initialize the OpenEnv App
app = create_fastapi_app(DataPrivacyEnv, MyAction, MyObservation)

# 2. Add CORS so the Meta judges can connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Health check endpoint (required by validator)
@app.get("/health")
def health():
    return {"status": "ok"}

# 4. The Professional HTML Landing Page
@app.get("/", response_class=HTMLResponse)
def read_root():
    return """
    <html>
        <head>
            <title>Data Privacy Environment</title>
            <style>
                body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; padding: 50px; background-color: #f4f7f6; line-height: 1.6; }
                .container { max-width: 800px; margin: auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
                h1 { color: #1e40af; border-bottom: 2px solid #e5e7eb; padding-bottom: 10px; }
                .status { font-weight: bold; color: #059669; }
                .task-list { background: #eff6ff; padding: 15px; border-radius: 8px; border-left: 5px solid #3b82f6; }
                code { background: #f3f4f6; padding: 2px 5px; border-radius: 4px; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🛡️ Data Privacy & Compliance Environment</h1>
                <p><strong>Status:</strong> <span class="status">ONLINE</span></p>
                <p><strong>Institution:</strong> Graphic Era University (GEU)</p>
                <p>This environment evaluates AI agents on their ability to sanitize and redact sensitive PII (Personally Identifiable Information).</p>

                <div class="task-list">
                    <strong>Available Task IDs:</strong>
                    <ul>
                        <li><code>mask-emails</code> (Easy)</li>
                        <li><code>redact-phones</code> (Medium)</li>
                        <li><code>sanitize-json</code> (Hard)</li>
                    </ul>
                </div>

                <p>📖 <strong>Developer Note:</strong> Access the interactive API documentation at <a href="/docs">/docs</a> to test endpoints.</p>
            </div>
        </body>
    </html>
    """

# 5. The Entry Point
def main():
    uvicorn.run(app, host="0.0.0.0", port=7860, proxy_headers=True, forwarded_allow_ips="*")

if __name__ == "__main__":
    main()
