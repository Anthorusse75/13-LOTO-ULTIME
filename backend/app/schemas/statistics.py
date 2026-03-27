from datetime import datetime

from pydantic import BaseModel

# ── Frequency ──


class FrequencyItem(BaseModel):
    number: int
    count: int
    relative: float
    ratio: float
    last_seen: int


# ── Gap ──


class GapItem(BaseModel):
    number: int
    current_gap: int
    max_gap: int
    avg_gap: float
    min_gap: int
    median_gap: float
    expected_gap: float


# ── Cooccurrence ──


class CooccurrencePairItem(BaseModel):
    pair: str
    count: int
    expected: float
    affinity: float


class CooccurrenceResponse(BaseModel):
    pairs: list[CooccurrencePairItem]
    expected_pair_count: float
    matrix_shape: list[int]


# ── Temporal ──


class TemporalNumberEntry(BaseModel):
    number: int
    freq: float
    delta: float


class TemporalWindowItem(BaseModel):
    window_size: int
    hot_numbers: list[TemporalNumberEntry]
    cold_numbers: list[TemporalNumberEntry]


class TemporalResponse(BaseModel):
    windows: list[TemporalWindowItem]
    momentum: dict[str, float] = {}


# ── Distribution ──


class SumStats(BaseModel):
    mean: float
    std: float
    min: int
    max: int
    median: float


class EvenOddDistribution(BaseModel):
    mean_even: float
    mean_odd: float


class DistributionResponse(BaseModel):
    entropy: float
    max_entropy: float
    uniformity_score: float
    chi2_statistic: float
    chi2_pvalue: float
    is_uniform: bool
    sum_stats: SumStats
    even_odd_distribution: EvenOddDistribution
    decades: dict[str, int]


# ── Bayesian ──


class BayesianItem(BaseModel):
    number: int
    alpha: float
    beta: float
    posterior_mean: float
    ci_95_low: float
    ci_95_high: float
    ci_width: float


# ── Graph ──


class CentralityItem(BaseModel):
    number: int
    degree: float
    betweenness: float
    eigenvector: float
    community: int


class GraphResponse(BaseModel):
    communities: list[list[int]]
    centrality: list[CentralityItem]
    density: float
    clustering_coefficient: float


# ── Full snapshot ──


class StatisticsResponse(BaseModel):
    game_id: int
    computed_at: datetime
    draw_count: int
    frequencies: list[FrequencyItem]
    gaps: list[GapItem]
    hot_numbers: list[int]
    cold_numbers: list[int]
    distribution_entropy: float
    uniformity_score: float
