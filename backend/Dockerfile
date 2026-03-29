# ── Stage 1: Build ──
FROM python:3.12-slim AS builder

WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends gcc \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml ./
RUN pip install --no-cache-dir --prefix=/install .

# ── Stage 2: Runtime ──
FROM python:3.12-slim AS runtime

WORKDIR /app

COPY --from=builder /install /usr/local

COPY alembic.ini alembic/ ./alembic/
COPY game_configs/ ./game_configs/
COPY app/ ./app/

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
