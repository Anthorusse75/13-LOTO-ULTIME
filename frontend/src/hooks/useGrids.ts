import { useQuery, useMutation } from "@tanstack/react-query";
import { gridService } from "@/services/gridService";
import { useGameStore } from "@/stores/gameStore";
import type { GridGenerateRequest, GridScoreRequest } from "@/types/grid";

export function useTopGrids(limit = 10) {
  const gameId = useGameStore((s) => s.currentGameId);
  return useQuery({
    queryKey: ["grids", gameId, "top", limit],
    queryFn: () => gridService.getTop(gameId!, limit),
    enabled: !!gameId,
    staleTime: 5 * 60 * 1000,
  });
}

export function useGenerateGrids() {
  const gameId = useGameStore((s) => s.currentGameId);
  return useMutation({
    mutationFn: (req: GridGenerateRequest) =>
      gridService.generate(gameId!, req),
  });
}

export function useScoreGrid() {
  const gameId = useGameStore((s) => s.currentGameId);
  return useMutation({
    mutationFn: (req: GridScoreRequest) => gridService.score(gameId!, req),
  });
}
