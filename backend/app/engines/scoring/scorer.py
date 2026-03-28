"""Grid scorer — orchestrates all criteria with weighted scoring."""

from dataclasses import dataclass, field

from app.core.game_definitions import GameConfig

from .balance_criterion import BalanceCriterion
from .cooccurrence_criterion import CooccurrenceCriterion
from .frequency_criterion import FrequencyCriterion
from .gap_criterion import GapCriterion
from .pattern_penalty import PatternPenalty
from .structure_criterion import StructureCriterion

# ── Predefined weight profiles ──

PROFILES: dict[str, dict[str, float]] = {
    "equilibre": {
        "frequency": 0.20,
        "gap": 0.20,
        "cooccurrence": 0.15,
        "structure": 0.15,
        "balance": 0.20,
        "pattern_penalty": 0.10,
    },
    "tendance": {
        "frequency": 0.35,
        "gap": 0.10,
        "cooccurrence": 0.25,
        "structure": 0.10,
        "balance": 0.15,
        "pattern_penalty": 0.05,
    },
    "contrarian": {
        "frequency": 0.10,
        "gap": 0.35,
        "cooccurrence": 0.10,
        "structure": 0.15,
        "balance": 0.20,
        "pattern_penalty": 0.10,
    },
    "structurel": {
        "frequency": 0.10,
        "gap": 0.10,
        "cooccurrence": 0.10,
        "structure": 0.30,
        "balance": 0.30,
        "pattern_penalty": 0.10,
    },
}


def normalize_weights(raw: dict[str, float]) -> dict[str, float]:
    """Normalize weights so that the 5 main criteria sum to 1 (penalty kept separate)."""
    penalty = raw.get("pattern_penalty", 0.10)
    main_keys = [k for k in raw if k != "pattern_penalty"]
    total_main = sum(raw[k] for k in main_keys)
    if total_main <= 0:
        total_main = 1.0
    normalized = {k: raw[k] / total_main for k in main_keys}
    normalized["pattern_penalty"] = penalty / (total_main + penalty) if (total_main + penalty) > 0 else 0.0
    return normalized


@dataclass
class ScoredResult:
    """Result of scoring a single grid."""

    numbers: list[int]
    total_score: float
    score_breakdown: dict[str, float]
    stars: list[int] | None = None
    star_score: float | None = None


@dataclass
class GridScorer:
    """Orchestrate 5 criteria + 1 penalty into a single grid score."""

    weights: dict[str, float] = field(default_factory=lambda: PROFILES["equilibre"].copy())

    def __post_init__(self):
        self._frequency = FrequencyCriterion()
        self._gap = GapCriterion()
        self._cooccurrence = CooccurrenceCriterion()
        self._structure = StructureCriterion()
        self._balance = BalanceCriterion()
        self._penalty = PatternPenalty()

    @staticmethod
    def from_profile(name: str) -> "GridScorer":
        """Create a scorer with a predefined weight profile."""
        if name not in PROFILES:
            raise ValueError(f"Unknown profile '{name}'. Available: {list(PROFILES.keys())}")
        return GridScorer(weights=PROFILES[name].copy())

    def score(
        self,
        grid: list[int],
        statistics: dict,
        game: GameConfig,
    ) -> ScoredResult:
        """Score a grid against a statistics snapshot (dict form)."""
        frequencies = statistics.get("frequency", {})
        gaps = statistics.get("gaps", {})
        cooccurrences = statistics.get("cooccurrence", {})

        breakdown: dict[str, float] = {}

        breakdown["frequency"] = self._frequency.compute(
            grid, game, frequencies=frequencies
        )
        breakdown["gap"] = self._gap.compute(grid, game, gaps=gaps)
        breakdown["cooccurrence"] = self._cooccurrence.compute(
            grid, game, cooccurrences=cooccurrences
        )
        breakdown["structure"] = self._structure.compute(grid, game)
        breakdown["balance"] = self._balance.compute(grid, game)
        breakdown["pattern_penalty"] = self._penalty.compute(grid, game)

        w = normalize_weights(self.weights)

        total = sum(
            w[name] * breakdown[name]
            for name in ("frequency", "gap", "cooccurrence", "structure", "balance")
        ) - w["pattern_penalty"] * breakdown["pattern_penalty"]

        total = max(0.0, min(1.0, total))

        return ScoredResult(
            numbers=sorted(grid),
            total_score=round(total, 6),
            score_breakdown={k: round(v, 6) for k, v in breakdown.items()},
        )

    def score_with_stars(
        self,
        grid: list[int],
        stars: list[int],
        statistics: dict,
        game: GameConfig,
    ) -> ScoredResult:
        """Score a grid including star/complementary numbers."""
        result = self.score(grid, statistics, game)

        # Star scoring: frequency + gap only (limited data)
        star_freq = statistics.get("star_frequency", {})
        star_gaps = statistics.get("star_gaps", {})

        if star_freq and star_gaps:
            star_scores = []
            for s in stars:
                key = str(s)
                f_score = star_freq.get(key, {}).get("ratio", 1.0)
                g_data = star_gaps.get(key, {})
                g_current = g_data.get("current_gap", 0)
                g_avg = g_data.get("avg_gap", 1)
                g_ratio = (g_current - g_avg) / g_avg if g_avg > 0 else 0
                import math
                g_score = 1.0 / (1.0 + math.exp(-3.0 * g_ratio))
                star_scores.append(0.5 * f_score + 0.5 * g_score)

            star_score = sum(star_scores) / len(star_scores) if star_scores else 0.5
        else:
            star_score = 0.5

        # Combined: 85% main numbers + 15% stars (per doc 08 sec 6)
        combined = 0.85 * result.total_score + 0.15 * star_score
        combined = max(0.0, min(1.0, round(combined, 6)))

        return ScoredResult(
            numbers=result.numbers,
            total_score=combined,
            score_breakdown=result.score_breakdown,
            stars=sorted(stars),
            star_score=round(star_score, 6),
        )
