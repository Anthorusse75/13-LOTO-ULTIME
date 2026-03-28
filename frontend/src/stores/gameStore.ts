import { create } from "zustand";
import { persist } from "zustand/middleware";

interface GameState {
  currentGameId: number | null;
  currentGameSlug: string | null;
  setGame: (id: number, slug: string) => void;
}

export const useGameStore = create<GameState>()(
  persist(
    (set) => ({
      currentGameId: null,
      currentGameSlug: null,
      setGame: (id, slug) => set({ currentGameId: id, currentGameSlug: slug }),
    }),
    { name: "game-storage" }
  )
);
