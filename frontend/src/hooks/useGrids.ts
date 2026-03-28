import { gridService } from "@/services/gridService";
import { useGameStore } from "@/stores/gameStore";
import type { GridGenerateRequest, GridScoreRequest } from "@/types/grid";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

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
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (req: GridGenerateRequest) =>
      gridService.generate(gameId!, req),
    onSuccess: (data) => {
      toast.success(`${data.grids.length} grilles générées avec succès`);
      queryClient.invalidateQueries({ queryKey: ["grids", gameId] });
    },
  });
}

export function useScoreGrid() {
  const gameId = useGameStore((s) => s.currentGameId);
  return useMutation({
    mutationFn: (req: GridScoreRequest) => gridService.score(gameId!, req),
    onSuccess: () => {
      toast.success("Grille scorée avec succès");
    },
  });
}
