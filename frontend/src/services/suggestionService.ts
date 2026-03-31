import type { DailySuggestionResponse } from "@/types/automation";
import api from "./api";

export const suggestionService = {
  getDaily: async (
    gameId: number,
    count = 3,
  ): Promise<DailySuggestionResponse> => {
    const { data } = await api.get(`/games/${gameId}/suggestions/daily`, {
      params: { count },
    });
    return data;
  },
};
