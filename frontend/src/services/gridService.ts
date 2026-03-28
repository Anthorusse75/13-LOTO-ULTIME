import type {
  GridGenerateRequest,
  GridGenerateResponse,
  GridResponse,
  GridScoreRequest,
  GridScoreResponse,
} from "@/types/grid";
import api from "./api";

export const gridService = {
  score: async (
    gameId: number,
    req: GridScoreRequest,
  ): Promise<GridScoreResponse> => {
    const { data } = await api.post(`/games/${gameId}/grids/score`, req);
    return data;
  },

  generate: async (
    gameId: number,
    req: GridGenerateRequest,
  ): Promise<GridGenerateResponse> => {
    const { data } = await api.post(`/games/${gameId}/grids/generate`, req);
    return data;
  },

  getTop: async (gameId: number, limit = 10): Promise<GridResponse[]> => {
    const { data } = await api.get(`/games/${gameId}/grids/top`, {
      params: { limit },
    });
    return data;
  },

  getById: async (gameId: number, gridId: number): Promise<GridResponse> => {
    const { data } = await api.get(`/games/${gameId}/grids/${gridId}`);
    return data;
  },
};
