import type { ComparisonRequest, ComparisonResponse } from "@/types/comparison";
import api from "./api";

export const comparisonService = {
  compare: async (
    gameId: number,
    req: ComparisonRequest,
  ): Promise<ComparisonResponse> => {
    const { data } = await api.post(
      `/games/${gameId}/comparison/compare`,
      req,
      { timeout: 120_000 },
    );
    return data;
  },
};
