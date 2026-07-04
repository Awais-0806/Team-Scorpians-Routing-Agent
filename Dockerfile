# Team Scorpians - agent container
# This does NOT need ROCm/GPU access itself -- it's a thin orchestrator that
# calls (1) the local Gemma model over HTTP, served by the separate
# `local-model` container in docker-compose.yml (which DOES use ROCm), and
# (2) the Fireworks API over HTTPS.

FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY router_agent.py gemma_fireworks.py ./

ENV LOCAL_BASE_URL=http://local-model:8000/v1
ENV LOCAL_MODEL=google/gemma-4-e4b-it
ENV FIREWORKS_MODEL=accounts/fireworks/models/gemma-4-31b-it

EXPOSE 8080
CMD ["uvicorn", "router_agent:app", "--host", "0.0.0.0", "--port", "8080"]
