FROM python:3.10-slim

WORKDIR /app

# Copy all files into the container
COPY . .

# Install the basic requirements directly
RUN pip install --no-cache-dir fastapi uvicorn pydantic pandas openenv-core

# Expose the OpenEnv port
EXPOSE 8000

# Start the server (using the module path)
CMD ["python", "server/app.py"]
