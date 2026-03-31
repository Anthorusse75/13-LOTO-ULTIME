"""Wheeling explainer — stub for Phase C."""

from app.engines.explainability import Explanation
from app.engines.explainability.templates import WARNING_REMINDER, WHEELING_INTERPRETATION, WHEELING_SUMMARY, WHEELING_TECHNICAL


def explain_wheeling(
    n_numbers: int,
    base: int,
    guarantee: int,
    n_combos: int,
    coverage: float,
    cost: float,
    method: str = "greedy",
    computation_time_ms: float = 0,
) -> Explanation:
    """Generate explanation for a wheeling system."""
    return Explanation(
        summary=WHEELING_SUMMARY.format(
            n_numbers=n_numbers, base=base, guarantee=guarantee, n_combos=n_combos
        ),
        interpretation=WHEELING_INTERPRETATION.format(
            n_numbers=n_numbers, base=base, guarantee=guarantee,
            n_combos=n_combos, cost=cost,
        ),
        technical=WHEELING_TECHNICAL.format(
            n_numbers=n_numbers, base=base, guarantee=guarantee,
            n_combos=n_combos, coverage=coverage, cost=cost,
            method=method, time_ms=computation_time_ms,
        ),
        highlights=[],
        warnings=[WARNING_REMINDER],
    )
