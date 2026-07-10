FROM python:3.10-slim

WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy full code
COPY . .

# Entrypoint for Batch Judge
ENTRYPOINT ["python", "submit.py"]