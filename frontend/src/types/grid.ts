export interface ScoreBreakdown {
  frequency: number;
  gap: number;
  cooccurrence: number;
  structure: number;
  balance: number;
  pattern_penalty: number;
}

export interface GridScoreRequest {
  numbers: number[];
  stars?: number[] | null;
  profile?: string;
  weights?: Record<string, number> | null;
}

export interface GridScoreResponse {
  numbers: number[];
  stars: number[] | null;
  total_score: number;
  score_breakdown: ScoreBreakdown;
  star_score: number | null;
}

export interface GridResponse {
  id: number;
  numbers: number[];
  stars: number[] | null;
  total_score: number;
  score_breakdown: ScoreBreakdown;
  rank: number | null;
  method: string;
  computed_at: string;
}

export interface GridGenerateRequest {
  count?: number;
  method?: string;
  weights?: Record<string, number> | null;
}

export interface GridGenerateResponse {
  grids: GridScoreResponse[];
  computation_time_ms: number;
  method_used: string;
}
