// Budget types

export interface GainScenarioSummary {
  optimistic: number;
  mean: number;
  pessimistic: number;
}

export interface BudgetRecommendation {
  strategy: string;
  grids: Array<{ numbers: number[]; stars?: number[] | null }>;
  grid_count: number;
  total_cost: number;
  avg_score: number | null;
  diversity_score: number | null;
  coverage_rate: number | null;
  expected_gain: GainScenarioSummary;
  explanation: string;
  is_recommended: boolean;
}

export interface BudgetOptimizeRequest {
  budget: number;
  objective: string;
  numbers?: number[] | null;
}

export interface BudgetOptimizeResponse {
  id: number | null;
  budget: number;
  grid_price: number;
  max_grids: number;
  recommendations: BudgetRecommendation[];
}

export interface BudgetPlanResponse {
  id: number;
  game_id: number;
  budget: number;
  objective: string;
  selected_numbers: number[] | null;
  recommendations: BudgetRecommendation[];
  chosen_strategy: string | null;
  created_at: string;
}
