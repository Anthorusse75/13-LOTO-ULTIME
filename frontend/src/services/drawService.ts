import api from "./api";
import type { Draw } from "@/types/draw";

export const drawService = {
  getDraws: async (gameId: number, skip = 0, limit = 50): Promise<Draw[]> => {
    const { data } = await api.get(`/games/${gameId}/draws`, {
      params: { skip, limit },
    });
    return data;
  },

  getLatest: async (gameId: number): Promise<Draw> => {
    const { data } = await api.get(`/games/${gameId}/draws/latest`);
    return data;
  },
};
