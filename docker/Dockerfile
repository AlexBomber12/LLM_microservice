FROM nvidia/cuda:12.4.0-runtime-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    python3.11 python3.11-venv python3-pip curl git && \
    rm -rf /var/lib/apt/lists/*
RUN apt-get update && apt-get install -y tini && rm -rf /var/lib/apt/lists/*

# ensure Python 3.11 is used for all installs
RUN python3.11 -m pip install --upgrade pip

ENV PYTHONUNBUFFERED=1 \
    HF_HOME=/models/.cache

RUN python3.11 -m pip install --no-cache-dir fastapi uvicorn[standard] vllm huggingface-hub httpx

WORKDIR /app
COPY . /app

RUN python3.11 -m pip install --no-cache-dir ".[server]"

# tini as the init process
ENTRYPOINT ["tini", "-g", "--"]

# launch FastAPI via Uvicorn
CMD ["uvicorn", "llm_microservice.server.main:app", "--host", "0.0.0.0", "--port", "8000"]
