import { useQuery } from "@tanstack/react-query";
import { drawService } from "@/services/drawService";
import { useGameStore } from "@/stores/gameStore";

export function useDraws(skip = 0, limit = 50) {
  const gameId = useGameStore((s) => s.currentGameId);

  return useQuery({
    queryKey: ["draws", gameId, skip, limit],
    queryFn: () => drawService.getDraws(gameId!, skip, limit),
    enabled: !!gameId,
    staleTime: 5 * 60 * 1000,
  });
}

export function useLatestDraw() {
  const gameId = useGameStore((s) => s.currentGameId);

  return useQuery({
    queryKey: ["draws", gameId, "latest"],
    queryFn: () => drawService.getLatest(gameId!),
    enabled: !!gameId,
    refetchInterval: 60 * 1000,
  });
}
