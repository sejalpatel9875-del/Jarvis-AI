# Production Multi-Stage Dockerfile for J.A.R.V.I.S. AI OS v5.1.0

# ----------------------------------------------------
# Stage 1: Build Dependencies
# ----------------------------------------------------
FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# ----------------------------------------------------
# Stage 2: Final Production Container
# ----------------------------------------------------
FROM python:3.12-slim AS runner

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH=/home/jarvisuser/.local/bin:$PATH \
    PORT=8000

# Create non-root user for security
RUN groupadd -g 10001 jarvisgroup && \
    useradd -u 10000 -g jarvisgroup -s /bin/bash -m jarvisuser

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /root/.local /home/jarvisuser/.local
COPY --chown=jarvisuser:jarvisgroup . .

USER jarvisuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:${PORT}/api/v1/health || exit 1

CMD ["sh", "-c", "uvicorn api.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 4"]
