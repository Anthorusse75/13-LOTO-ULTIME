"""Statistics service — orchestrates all statistical engines."""

from datetime import UTC, datetime

import numpy as np
import structlog

from app.core.exceptions import EngineComputationError, InsufficientDataError
from app.core.game_definitions import GameConfig
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
            try:
                results[name] = engine.compute(draws, game)
                log.debug("engine_completed", engine=name)
            except Exception as exc:
                log.error("engine_failed", engine=name, error=str(exc))
                raise EngineComputationError(f"Engine '{name}' failed: {exc}") from exc

        # 3. Persist snapshot
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
        )

        created = await self._stats_repo.create(snapshot)
        log.info("statistics_pipeline_completed", snapshot_id=created.id)
        return created

    async def get_latest(self, game_id: int) -> StatisticsSnapshot | None:
        """Return the most recent statistics snapshot."""
        return await self._stats_repo.get_latest(game_id)

    def compute_single(self, engine_name: str, draws: np.ndarray, game: GameConfig) -> dict:
        """Run a single engine on a draw matrix (no persistence)."""
        engine = self._engines.get(engine_name)
        if engine is None:
            raise EngineComputationError(f"Unknown engine: {engine_name}")
        return engine.compute(draws, game)
