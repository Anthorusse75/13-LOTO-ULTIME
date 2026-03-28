export interface ApiError {
  detail: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  limit: number;
}

export interface HealthResponse {
  status: string;
  version: string;
  database: string;
}
