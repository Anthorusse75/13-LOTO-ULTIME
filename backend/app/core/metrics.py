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
# Wheeling / Système réduit metrics (OBS-01)
# ─────────────────────────────────────────────────────────────────────────────
wheeling_generations_total = Counter(
    "loto_wheeling_generations_total",
    "Total number of wheeling system generations",
    ["game", "guarantee_level"],
)

wheeling_generation_duration_seconds = Histogram(
    "loto_wheeling_generation_duration_seconds",
    "Time to generate a wheeling system",
    ["game"],
    buckets=[0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0],
)

wheeling_grid_count = Histogram(
    "loto_wheeling_grid_count",
    "Number of grids in generated wheeling systems",
    ["game"],
    buckets=[5, 10, 20, 50, 100, 200, 500],
)

# ─────────────────────────────────────────────────────────────────────────────
# Budget optimizer metrics (OBS-01)
# ─────────────────────────────────────────────────────────────────────────────
budget_optimizations_total = Counter(
    "loto_budget_optimizations_total",
    "Total number of budget optimization requests",
    ["game", "objective"],
)

budget_optimization_duration_seconds = Histogram(
    "loto_budget_optimization_duration_seconds",
    "Time to compute a budget optimization",
    ["game"],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5],
)

budget_amount_euros = Histogram(
    "loto_budget_amount_euros",
    "Budget amounts submitted by users (euros)",
    buckets=[2, 5, 10, 20, 50, 100, 200, 500],
)

# ─────────────────────────────────────────────────────────────────────────────
# Comparison / Comparateur metrics (OBS-01)
# ─────────────────────────────────────────────────────────────────────────────
comparisons_total = Counter(
    "loto_comparisons_total",
    "Total number of strategy comparisons",
    ["game"],
)

comparison_strategies_count = Histogram(
    "loto_comparison_strategies_count",
    "Number of strategies per comparison request",
    buckets=[2, 3, 4, 5],
)

comparison_duration_seconds = Histogram(
    "loto_comparison_duration_seconds",
    "Time to compute a strategy comparison",
    ["game"],
    buckets=[0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0],
)

# ─────────────────────────────────────────────────────────────────────────────
# Export metrics (OBS-01)
# ─────────────────────────────────────────────────────────────────────────────
exports_total = Counter(
    "loto_exports_total",
    "Total number of export requests",
    ["format"],  # csv | json | pdf
)

# ─────────────────────────────────────────────────────────────────────────────
# Cache metrics (OBS-01)
# ─────────────────────────────────────────────────────────────────────────────
cache_hits_total = Counter(
    "loto_cache_hits_total",
    "Total cache hits",
    ["cache_name"],
)

cache_misses_total = Counter(
    "loto_cache_misses_total",
    "Total cache misses",
    ["cache_name"],
)

# ─────────────────────────────────────────────────────────────────────────────
# ASGI app to mount at /metrics
# ─────────────────────────────────────────────────────────────────────────────
metrics_app = make_asgi_app()
