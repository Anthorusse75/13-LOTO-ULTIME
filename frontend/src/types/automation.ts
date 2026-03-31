export interface SuggestionGrid {
  numbers: number[];
  stars: number[] | null;
  total_score: number;
  method: string;
}

export interface DailySuggestionResponse {
  game_id: number;
  date: string;
  grids: SuggestionGrid[];
  reason: string;
}

export interface GridDrawResult {
  id: number;
  scored_grid_id: number;
  draw_id: number;
  matched_numbers: number[];
  matched_stars: number[] | null;
  match_count: number;
  star_match_count: number;
  prize_rank: number | null;
  estimated_prize: number | null;
  checked_at: string;
}
