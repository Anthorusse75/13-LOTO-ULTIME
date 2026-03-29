"""Prometheus metrics — counters, histograms and gauges for LOTO ULTIME."""

from prometheus_client import Counter, Gauge, Histogram, make_asgi_app

# ─────────────────────────────────────────────────────────────────────────────
# HTTP request metrics (recorded by middleware in main.py)
# ─────────────────────────────────────────────────────────────────────────────
http_requests_total = Counter(
    "loto_http_requests_total",
    "Total number of HTTP requests",
    ["method", "endpoint", "status_code"],
)

http_request_duration_seconds = Histogram(
    "loto_http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint"],
    buckets=[0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
)

# ─────────────────────────────────────────────────────────────────────────────
# Statistical engine metrics
# ─────────────────────────────────────────────────────────────────────────────
engine_compute_duration_seconds = Histogram(
    "loto_engine_compute_duration_seconds",
    "Time taken to compute a statistical engine",
    ["engine", "game"],
    buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5],
)

engine_errors_total = Counter(
    "loto_engine_errors_total",
    "Number of statistical engine computation errors",
    ["engine", "game"],
)

# ─────────────────────────────────────────────────────────────────────────────
# Scraper metrics
# ─────────────────────────────────────────────────────────────────────────────
scraper_fetches_total = Counter(
    "loto_scraper_fetches_total",
    "Total number of scraper fetch attempts",
    ["game", "status"],  # status: success | failure | circuit_open
)

scraper_draws_saved_total = Counter(
    "loto_scraper_draws_saved_total",
    "Total number of draws saved to the database",
    ["game"],
)

scraper_draws_skipped_total = Counter(
    "loto_scraper_draws_skipped_total",
    "Total number of draws skipped (duplicate or validation error)",
    ["game", "reason"],  # reason: duplicate | validation_error
)

# ─────────────────────────────────────────────────────────────────────────────
# Business metrics (gauges — updated by health job)
# ─────────────────────────────────────────────────────────────────────────────
draws_total = Gauge(
    "loto_draws_total",
    "Total number of draws in the database",
    ["game"],
)

grids_total = Gauge(
    "loto_grids_total",
    "Total number of scored grids in the database",
)

last_pipeline_run_timestamp = Gauge(
    "loto_last_pipeline_run_timestamp_seconds",
    "Unix timestamp of the last successful nightly pipeline run",
)

last_statistics_snapshot_timestamp = Gauge(
    "loto_last_statistics_snapshot_timestamp_seconds",
    "Unix timestamp of the last statistics snapshot computation",
    ["game"],
)

# ─────────────────────────────────────────────────────────────────────────────
# ASGI app to mount at /metrics
# ─────────────────────────────────────────────────────────────────────────────
metrics_app = make_asgi_app()
