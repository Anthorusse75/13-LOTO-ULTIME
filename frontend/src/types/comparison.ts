/** Comparison types for strategy comparison. */

export interface StrategyConfig {
  type:
    | "top"
    | "portfolio"
    | "random"
    | "wheeling"
    | "budget"
    | "profile"
    | "method";
  count?: number;
  numbers?: number[];
  stars?: number[];
  guarantee?: number;
  profile?: string;
  method?: string;
  budget?: number;
  objective?: string;
}

export interface ComparisonRequest {
  strategies: StrategyConfig[];
  include_gain_scenarios?: boolean;
}

export interface StrategyMetrics {
  type: string;
  label: string;
  grid_count: number;
  grids: Array<{ numbers: number[]; stars?: number[] | null }> | null;
  avg_score: number | null;
  score_variance: number | null;
  diversity: number | null;
  coverage: number | null;
  cost: number;
  robustness: number | null;
  expected_gain: number | null;
}

export interface ComparisonSummary {
  best_score: string | null;
  best_diversity: string | null;
  best_coverage: string | null;
  best_cost: string | null;
  recommendation: string;
}

export interface ComparisonResponse {
  strategies: StrategyMetrics[];
  summary: ComparisonSummary;
}
