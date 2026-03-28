import api from "./api";
import type { GameDefinition } from "@/types/game";

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
