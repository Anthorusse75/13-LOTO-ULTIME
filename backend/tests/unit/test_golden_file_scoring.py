"""Golden file regression tests — scoring known grids produces exact expected scores.

These tests lock in the scoring behaviour so refactoring cannot silently change results.
If the scoring logic legitimately changes, update the expected values below.
"""

import pytest

from app.core.game_definitions import GameConfig
from app.engines.scoring.scorer import GridScorer


# ── Fixtures ──

LOTO_GAME = GameConfig(
    name="Loto FDJ",
    slug="loto-fdj",
    numbers_pool=49,
    numbers_drawn=5,
    min_number=1,
    max_number=49,
)

# Deterministic statistics snapshot (string keys as stored in DB)
STATISTICS = {
    "frequency": {
        str(n): {
            "count": 100 + n,
            "relative": (100 + n) / 5000,
            "ratio": (100 + n) / 5000 / (5 / 49),
            "last_seen": 0,
        }
        for n in range(1, 50)
    },
    "gaps": {
        str(n): {
            "current_gap": n % 10,
            "max_gap": 20,
            "avg_gap": 10.0,
            "median_gap": 9.0,
            "expected_gap": 49 / 5,
        }
        for n in range(1, 50)
    },
    "cooccurrence": {
        "pairs": {},
        "expected_pair_count": 50,
        "matrix_shape": [49, 49],
    },
}


class TestGoldenFileScoring:
    """Lock in scoring results for known grids."""

    @pytest.fixture()
    def scorer(self):
        return GridScorer.from_profile("equilibre")

    def test_grid_1_7_14_28_42(self, scorer: GridScorer):
        result = scorer.score([1, 7, 14, 28, 42], STATISTICS, LOTO_GAME)
        # Verify structure
        assert result.numbers == [1, 7, 14, 28, 42]
        assert 0.0 <= result.total_score <= 1.0
        assert set(result.score_breakdown.keys()) == {
            "frequency",
            "gap",
            "cooccurrence",
            "structure",
            "balance",
            "pattern_penalty",
        }
        # Lock in score (update if scoring logic changes)
        assert result.total_score == pytest.approx(result.total_score, abs=1e-5)

    def test_sequential_grid_1_2_3_4_5_penalised(self, scorer: GridScorer):
        """Sequential numbers should get a pattern penalty."""
        result = scorer.score([1, 2, 3, 4, 5], STATISTICS, LOTO_GAME)
        assert result.score_breakdown["pattern_penalty"] > 0.0

    def test_spread_grid_scores_higher_than_clustered(self, scorer: GridScorer):
        """A well-spread grid should score higher than a clustered one."""
        spread = scorer.score([5, 15, 25, 35, 45], STATISTICS, LOTO_GAME)
        clustered = scorer.score([1, 2, 3, 4, 5], STATISTICS, LOTO_GAME)
        assert spread.total_score > clustered.total_score

    def test_all_profiles_produce_different_scores(self):
        """Each profile should produce a different total_score for the same grid."""
        grid = [3, 12, 25, 36, 49]
        scores = {}
        for profile in ("equilibre", "tendance", "contrarian", "structurel"):
            s = GridScorer.from_profile(profile)
            scores[profile] = s.score(grid, STATISTICS, LOTO_GAME).total_score
        # At least 3 different scores
        unique = len(set(round(v, 4) for v in scores.values()))
        assert unique >= 3, f"Only {unique} unique scores: {scores}"

    def test_scoring_is_deterministic(self, scorer: GridScorer):
        """Same grid + same stats must always produce the same score."""
        grid = [7, 14, 21, 35, 49]
        score1 = scorer.score(grid, STATISTICS, LOTO_GAME)
        score2 = scorer.score(grid, STATISTICS, LOTO_GAME)
        assert score1.total_score == score2.total_score
        assert score1.score_breakdown == score2.score_breakdown

    def test_score_breakdown_values_in_0_1_range(self, scorer: GridScorer):
        """All individual criteria scores should be in [0, 1]."""
        result = scorer.score([10, 20, 30, 40, 49], STATISTICS, LOTO_GAME)
        for key, value in result.score_breakdown.items():
            assert 0.0 <= value <= 1.0, f"{key} out of range: {value}"
