import type { GameDefinition } from "@/types/game";
import api from "./api";

export const gameService = {
  getAll: async (): Promise<GameDefinition[]> => {
    const { data } = await api.get("/games");
    return data;
  },

  getBySlug: async (slug: string): Promise<GameDefinition> => {
    const { data } = await api.get(`/games/${slug}`);
    return data;
  },
};
