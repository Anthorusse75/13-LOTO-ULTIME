export type ResultType =
  | "grid"
  | "portfolio"
  | "wheeling"
  | "budget_plan"
  | "comparison"
  | "simulation";

export interface SaveResultRequest {
  result_type: ResultType;
  parameters: Record<string, unknown>;
  result_data: Record<string, unknown>;
  game_id?: number | null;
  name?: string | null;
  tags?: string[];
}

export interface SavedResult {
  id: number;
  user_id: number;
  game_id: number | null;
  result_type: ResultType;
  name: string | null;
  parameters: Record<string, unknown>;
  result_data: Record<string, unknown>;
  is_favorite: boolean;
  tags: string[];
  created_at: string;
  updated_at: string;
}

export interface UpdateTagsRequest {
  tags: string[];
}
