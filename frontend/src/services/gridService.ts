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
    const { data } = await api.post(`/games/${gameId}/grids/generate`, req, {
      timeout: 120_000,
    });
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

  deleteGrid: async (gameId: number, gridId: number): Promise<void> => {
    await api.delete(`/games/${gameId}/grids/${gridId}`);
  },

  toggleFavorite: async (
    gameId: number,
    gridId: number,
  ): Promise<GridResponse> => {
    const { data } = await api.patch(
      `/games/${gameId}/grids/${gridId}/favorite`,
    );
    return data;
  },

  togglePlayed: async (
    gameId: number,
    gridId: number,
  ): Promise<GridResponse> => {
    const { data } = await api.patch(
      `/games/${gameId}/grids/${gridId}/played`,
    );
    return data;
  },

  getFavorites: async (gameId: number): Promise<GridResponse[]> => {
    const { data } = await api.get(`/games/${gameId}/grids/favorites`);
    return data;
  },

  getPlayed: async (gameId: number): Promise<GridResponse[]> => {
    const { data } = await api.get(`/games/${gameId}/grids/played`);
    return data;
  },
};
