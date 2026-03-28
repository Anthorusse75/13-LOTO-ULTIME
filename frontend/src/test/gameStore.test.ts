import { describe, expect, it, beforeEach } from "vitest";
import { useGameStore } from "@/stores/gameStore";

describe("gameStore", () => {
  beforeEach(() => {
    useGameStore.setState({ currentGameId: null, currentGameSlug: null });
  });

  it("starts with null values", () => {
    const state = useGameStore.getState();
    expect(state.currentGameId).toBeNull();
    expect(state.currentGameSlug).toBeNull();
  });

  it("setGame updates id and slug", () => {
    useGameStore.getState().setGame(1, "euromillions");
    const state = useGameStore.getState();
    expect(state.currentGameId).toBe(1);
    expect(state.currentGameSlug).toBe("euromillions");
  });

  it("setGame can change game", () => {
    useGameStore.getState().setGame(1, "euromillions");
    useGameStore.getState().setGame(2, "loto-fdj");
    const state = useGameStore.getState();
    expect(state.currentGameId).toBe(2);
    expect(state.currentGameSlug).toBe("loto-fdj");
  });
});
