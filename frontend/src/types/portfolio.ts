export interface PortfolioGridItem {
  numbers: number[];
  stars: number[] | null;
  score: number;
}

export interface PortfolioResponse {
  id: number;
  game_id: number;
  name: string;
  strategy: string;
  grid_count: number;
  grids: PortfolioGridItem[];
  diversity_score: number;
  coverage_score: number;
  avg_grid_score: number;
  min_hamming_distance: number | null;
  computed_at: string;
}

export interface PortfolioGenerateRequest {
  grid_count?: number;
  strategy?: string;
}

export interface PortfolioGenerateResponse {
  strategy: string;
  grid_count: number;
  grids: PortfolioGridItem[];
  diversity_score: number;
  coverage_score: number;
  avg_grid_score: number;
  min_hamming_distance: number | null;
  computation_time_ms: number;
  method_used: string;
}
