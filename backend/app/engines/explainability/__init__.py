"""Explainability engine — generate human-readable explanations for all result types."""

from dataclasses import dataclass, field


@dataclass
class Explanation:
    """Three-level explanation structure."""

    summary: str  # L1 — one short sentence (≤ 150 chars)
    interpretation: str  # L2 — paragraph for regular players
    technical: str  # L3 — formula/weights/method for experts
    highlights: list[str] = field(default_factory=list)  # strong points
    warnings: list[str] = field(default_factory=list)  # attention points
