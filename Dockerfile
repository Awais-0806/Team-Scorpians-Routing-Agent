FROM python:3.10-slim

# OpenMP aur required libraries install karo
RUN apt-get update && apt-get install -y \
    wget \
    libgomp1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir \
    fastapi==0.104.1 \
    uvicorn==0.24.0 \
    pydantic==2.5.0 \
    python-dotenv==1.0.0

RUN pip install --no-cache-dir \
    --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu \
    llama-cpp-python==0.2.79

RUN mkdir -p /app/model
COPY model.gguf /app/model/model.gguf

COPY app /app/app
COPY submit.py /app/submit.py

ENV LOCAL_MODEL_PATH=/app/model/model.gguf
ENV PYTHONUNBUFFERED=1

CMD ["python", "/app/submit.py"]