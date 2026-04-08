FROM python:3.10-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir fastapi uvicorn pydantic pandas openenv-core openai requests

EXPOSE 8000

CMD ["python", "server/app.py"]
