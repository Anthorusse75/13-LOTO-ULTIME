import api from "./api";

export interface CoachRequest {
  page: string;
  context: Record<string, unknown>;
}

export interface CoachResponse {
  advice: string | null;
}

export interface AnalysisRequest {
  topic: string;
  context: Record<string, unknown>;
}

export interface GridAnalysisRequest {
  numbers: number[];
  stars: number[] | null;
  total_score: number;
  score_breakdown: Record<string, number>;
  method: string;
  profile: string;
}

export async function getCoachAdvice(
  body: CoachRequest,
): Promise<CoachResponse> {
  const { data } = await api.post<CoachResponse>("/coach", body);
  return data;
}

export async function getAnalysis(
  body: AnalysisRequest,
): Promise<CoachResponse> {
  const { data } = await api.post<CoachResponse>("/coach/analyze", body);
  return data;
}

export async function getGridAnalysis(
  body: GridAnalysisRequest,
): Promise<CoachResponse> {
  const { data } = await api.post<CoachResponse>("/coach/analyze", {
    topic: "grid",
    context: body,
  });
  return data;
}
