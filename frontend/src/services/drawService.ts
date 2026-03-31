import type { PaginatedResponse } from "@/types/api";
import type { Draw } from "@/types/draw";
import api from "./api";

export const drawService = {
  getDraws: async (
    gameId: number,
    page = 1,
    pageSize = 50,
  ): Promise<PaginatedResponse<Draw>> => {
    const { data } = await api.get(`/games/${gameId}/draws`, {
      params: { page, page_size: pageSize },
    });
    return data;
  },

  getLatest: async (gameId: number): Promise<Draw> => {
    const { data } = await api.get(`/games/${gameId}/draws/latest`);
    return data;
  },
};
