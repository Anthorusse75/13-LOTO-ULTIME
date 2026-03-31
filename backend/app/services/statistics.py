"""Statistics service — orchestrates all statistical engines."""

import time
from datetime import UTC, datetime
from typing import Any

import numpy as np
import structlog

from app.core.exceptions import EngineComputationError, InsufficientDataError
from app.core.game_definitions import GameConfig
from app.core.metrics import (
    engine_compute_duration_seconds,
    engine_errors_total,
    last_statistics_snapshot_timestamp,
)
from app.engines.statistics import (
    BayesianEngine,
    CooccurrenceEngine,
    DistributionEngine,
    FrequencyEngine,
    GapEngine,
    GraphEngine,
    TemporalEngine,
)
from app.models.statistics import StatisticsSnapshot
from app.repositories.draw_repository import DrawRepository
from app.repositories.statistics_repository import StatisticsRepository

logger = structlog.get_logger(__name__)

MIN_DRAWS_REQUIRED = 10


class StatisticsService:
    """Orchestrate the full statistics computation pipeline."""

    def __init__(
        self,
        draw_repo: DrawRepository,
        stats_repo: StatisticsRepository,
    ):
        self._draw_repo = draw_repo
        self._stats_repo = stats_repo
        self._engines = {
            "frequency": FrequencyEngine(),
            "gaps": GapEngine(),
            "cooccurrence": CooccurrenceEngine(),
            "temporal": TemporalEngine(),
            "distribution": DistributionEngine(),
            "bayesian": BayesianEngine(),
            "graph": GraphEngine(),
        }

    async def compute_all(self, game_id: int, game: GameConfig) -> StatisticsSnapshot:
        """Run the full statistics pipeline and persist a snapshot."""
        log = logger.bind(game_id=game_id, game_slug=game.slug)
        log.info("statistics_pipeline_started")

        # 1. Extract draw matrix
        draws = await self._draw_repo.get_numbers_matrix(game_id)
        n_draws = draws.shape[0]

        if n_draws < MIN_DRAWS_REQUIRED:
            raise InsufficientDataError(f"Need at least {MIN_DRAWS_REQUIRED} draws, got {n_draws}")

        log.info("draws_extracted", n_draws=n_draws)

        # 2. Run all engines
        results = {}
        for name, engine in self._engines.items():
            t0 = time.perf_counter()
            try:
                results[name] = engine.compute(draws, game)
                engine_compute_duration_seconds.labels(engine=name, game=game.slug).observe(
                    time.perf_counter() - t0
                )
                log.debug("engine_completed", engine=name)
            except Exception as exc:
                engine_errors_total.labels(engine=name, game=game.slug).inc()
                log.error("engine_failed", engine=name, error=str(exc))
                results[name] = {}  # empty dict — partial result, pipeline continues

        # 3. Compute star statistics (if game has stars)
        star_frequencies = None
        star_gaps = None
        if game.stars_pool and game.stars_drawn:
            star_draws = await self._draw_repo.get_stars_matrix(game_id)
            if star_draws.shape[0] >= MIN_DRAWS_REQUIRED:
                star_game = GameConfig(
                    name=game.name,
                    slug=game.slug,
                    numbers_pool=game.stars_pool,
                    numbers_drawn=game.stars_drawn,
                    min_number=1,
                    max_number=game.stars_pool,
                )
                try:
                    star_frequencies = FrequencyEngine().compute(star_draws, star_game)
                    star_gaps = GapEngine().compute(star_draws, star_game)
                    log.info("star_statistics_computed", n_star_draws=star_draws.shape[0])
                except Exception as exc:
                    log.warning("star_statistics_failed", error=str(exc))

        # 4. Persist snapshot
        snapshot = StatisticsSnapshot(
            game_id=game_id,
            computed_at=datetime.now(UTC),
            draw_count=n_draws,
            frequencies=results["frequency"],
            gaps=results["gaps"],
            cooccurrence_matrix=results["cooccurrence"],
            temporal_trends=results["temporal"],
            distribution_stats=results["distribution"],
            bayesian_priors=results["bayesian"],
            graph_metrics=results["graph"],
            star_frequencies=star_frequencies,
            star_gaps=star_gaps,
        )

        created = await self._stats_repo.create(snapshot)
        # Update Prometheus gauge with snapshot timestamp
        last_statistics_snapshot_timestamp.labels(game=game.slug).set_to_current_time()
        log.info("statistics_pipeline_completed", snapshot_id=created.id)
        return created

    async def get_latest(self, game_id: int) -> StatisticsSnapshot | None:
        """Return the most recent statistics snapshot."""
        return await self._stats_repo.get_latest(game_id)

    def compute_single(
        self, engine_name: str, draws: np.ndarray, game: GameConfig
    ) -> dict[int | str, Any]:
        """Run a single engine on a draw matrix (no persistence)."""
        engine = self._engines.get(engine_name)
        if engine is None:
            raise EngineComputationError(f"Unknown engine: {engine_name}")
        return engine.compute(draws, game)
