# ── Stage 1: Build dependencies ──
FROM python:3.11-slim AS builder

WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends gcc \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml ./
RUN pip install --no-cache-dir --prefix=/install .

# ── Stage 2: Runtime ──
FROM python:3.11-slim AS runtime

# Install PostgreSQL client (for pg_dump backups) + create non-root user
RUN apt-get update && apt-get install -y --no-install-recommends postgresql-client \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --gid 1000 appuser \
    && useradd --uid 1000 --gid appuser --create-home appuser

WORKDIR /app

# Install deps from builder
COPY --from=builder /install /usr/local

# Copy application code
COPY alembic.ini ./
COPY alembic/ ./alembic/
COPY game_configs/ ./game_configs/
COPY app/ ./app/
COPY entrypoint.sh ./

# Ensure entrypoint is executable & create data dir
RUN chmod +x entrypoint.sh \
    && mkdir -p /app/data && chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh"]
