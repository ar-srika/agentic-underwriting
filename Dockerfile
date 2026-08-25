# Enterprise Multi-Agent Underwriting Platform Container
# Stage 1: Build React Frontend
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend-react
COPY frontend-react/package*.json ./
RUN npm ci
COPY frontend-react/ ./
RUN npm run build

# Stage 2: Python Backend & Unified Cloud Run Container
FROM python:3.11-slim
WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8080

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
# Ensure compiled React assets are copied in
COPY --from=frontend-builder /app/frontend-react/dist /app/frontend-react/dist

EXPOSE 8080

# Cloud Run dynamic PORT binding
CMD exec uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8080}
