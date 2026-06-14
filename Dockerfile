FROM python:3.12-slim

WORKDIR /app

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy finance_agents tools source
COPY finance_agents/src/finance_agents /app/finance_agents_src/finance_agents

# Copy backend app
COPY backend/app /app/app

# Ensure finance_agents is importable
ENV PYTHONPATH="/app/finance_agents_src:${PYTHONPATH}"

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
