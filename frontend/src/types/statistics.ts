export interface FrequencyItem {
  number: number;
  count: number;
  relative: number;
  ratio: number;
  last_seen: number;
}

export interface GapItem {
  number: number;
  current_gap: number;
  max_gap: number;
  avg_gap: number;
  min_gap: number;
  median_gap: number;
  expected_gap: number;
}

export interface CooccurrencePairItem {
  pair: string;
  count: number;
  expected: number;
  affinity: number;
}

export interface CooccurrenceResponse {
  pairs: CooccurrencePairItem[];
  expected_pair_count: number;
  matrix_shape: number[];
}

export interface TemporalNumberEntry {
  number: number;
  freq: number;
  delta: number;
}

export interface TemporalWindowItem {
  window_size: number;
  hot_numbers: TemporalNumberEntry[];
  cold_numbers: TemporalNumberEntry[];
}

export interface TemporalResponse {
  windows: TemporalWindowItem[];
  momentum: Record<string, number>;
}

export interface SumStats {
  mean: number;
  std: number;
  min: number;
  max: number;
  median: number;
}

export interface EvenOddDistribution {
  mean_even: number;
  mean_odd: number;
}

export interface DistributionResponse {
  entropy: number;
  max_entropy: number;
  uniformity_score: number;
  chi2_statistic: number;
  chi2_pvalue: number;
  is_uniform: boolean;
  sum_stats: SumStats;
  even_odd_distribution: EvenOddDistribution;
  decades: Record<string, number>;
}

export interface BayesianItem {
  number: number;
  alpha: number;
  beta: number;
  posterior_mean: number;
  ci_95_low: number;
  ci_95_high: number;
  ci_width: number;
}

export interface CentralityItem {
  number: number;
  degree: number;
  betweenness: number;
  eigenvector: number;
  community: number;
}

export interface GraphResponse {
  communities: number[][];
  centrality: CentralityItem[];
  density: number;
  clustering_coefficient: number;
}

export interface StatisticsResponse {
  game_id: number;
  computed_at: string;
  draw_count: number;
  frequencies: FrequencyItem[];
  gaps: GapItem[];
  hot_numbers: number[];
  cold_numbers: number[];
  distribution_entropy: number;
  uniformity_score: number;
  star_frequencies: FrequencyItem[] | null;
  star_gaps: GapItem[] | null;
}
