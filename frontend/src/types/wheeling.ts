// Wheeling system types

export interface WheelingGridItem {
  numbers: number[];
  stars: number[] | null;
}

export interface GainScenario {
  rank: number;
  name: string;
  match_numbers: number;
  match_stars: number;
  avg_prize: number;
  matching_grids_best: number;
  matching_grids_avg: number;
  matching_grids_worst: number;
  potential_gain_best: number;
  potential_gain_avg: number;
  potential_gain_worst: number;
}

export interface WheelingPreviewRequest {
  numbers: number[];
  stars?: number[] | null;
  guarantee: number;
}

export interface WheelingPreviewResponse {
  estimated_grid_count: number;
  estimated_cost: number;
  total_t_combinations: number;
  full_wheel_size: number;
  reduction_rate_estimate: number;
}

export interface WheelingGenerateRequest {
  numbers: number[];
  stars?: number[] | null;
  guarantee: number;
}

export interface WheelingGenerateResponse {
  id: number | null;
  grids: WheelingGridItem[];
  grid_count: number;
  total_cost: number;
  coverage_rate: number;
  reduction_rate: number;
  total_t_combinations: number;
  full_wheel_size: number;
  computation_time_ms: number;
  gain_scenarios: GainScenario[];
  number_distribution: Record<number, number>;
}

export interface WheelingSystemResponse {
  id: number;
  game_id: number;
  selected_numbers: number[];
  selected_stars: number[] | null;
  guarantee_level: number;
  grids: WheelingGridItem[];
  grid_count: number;
  total_cost: number;
  coverage_rate: number;
  reduction_rate: number;
  created_at: string;
}
