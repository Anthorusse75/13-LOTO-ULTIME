import type {
  WheelingGenerateRequest,
  WheelingGenerateResponse,
  WheelingPreviewRequest,
  WheelingPreviewResponse,
  WheelingSystemResponse,
} from "@/types/wheeling";
import api from "./api";

export const wheelingService = {
  preview: async (
    gameId: number,
    req: WheelingPreviewRequest,
  ): Promise<WheelingPreviewResponse> => {
    const { data } = await api.post(`/games/${gameId}/wheeling/preview`, req);
    return data;
  },

  generate: async (
    gameId: number,
    req: WheelingGenerateRequest,
  ): Promise<WheelingGenerateResponse> => {
    const { data } = await api.post(`/games/${gameId}/wheeling/generate`, req, {
      timeout: 60_000,
    });
    return data;
  },

  getHistory: async (gameId: number): Promise<WheelingSystemResponse[]> => {
    const { data } = await api.get(`/games/${gameId}/wheeling/history`);
    return data;
  },

  getById: async (
    gameId: number,
    systemId: number,
  ): Promise<WheelingSystemResponse> => {
    const { data } = await api.get(
      `/games/${gameId}/wheeling/${systemId}`,
    );
    return data;
  },

  delete: async (gameId: number, systemId: number): Promise<void> => {
    await api.delete(`/games/${gameId}/wheeling/${systemId}`);
  },
};
