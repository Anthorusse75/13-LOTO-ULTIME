export interface MonteCarloGridRequest {
  numbers: number[];
  stars?: number[] | null;
  n_simulations?: number;
  seed?: number | null;
}

export interface MonteCarloPortfolioRequest {
  grids: number[][];
  n_simulations?: number;
  min_matches?: number;
  seed?: number | null;
}

export interface StabilityRequest {
  numbers: number[];
  n_bootstrap?: number;
  profile?: string;
  seed?: number | null;
}

export interface ComparisonRequest {
  numbers: number[];
  n_random?: number;
  profile?: string;
  seed?: number | null;
}

export interface MonteCarloGridResponse {
  grid: number[];
  stars: number[] | null;
  n_simulations: number;
  match_distribution: Record<number, number>;
  star_match_distribution: Record<number, number> | null;
  avg_matches: number;
  expected_matches: number;
  computation_time_ms: number;
}

export interface MonteCarloPortfolioResponse {
  n_simulations: number;
  hit_rate: number;
  min_matches_threshold: number;
  best_match_distribution: Record<number, number>;
  avg_best_matches: number;
  computation_time_ms: number;
}

export interface StabilityResponse {
  mean_score: number;
  std_score: number;
  cv: number;
  stability: number;
  ci_95_low: number;
  ci_95_high: number;
  min_score: number;
  max_score: number;
  computation_time_ms: number;
}

export interface ComparisonResponse {
  grid_score: number;
  random_mean: number;
  random_std: number;
  percentile: number;
  z_score: number;
  computation_time_ms: number;
}
