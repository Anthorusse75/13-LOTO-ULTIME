import { useQuery } from "@tanstack/react-query";
import { AxiosError } from "axios";
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
    retry: (_count, error) => {
      const status = (error as AxiosError)?.response?.status;
      return status !== 404 && status !== 422;
    },
    refetchInterval: (query) => (query.state.data ? 60_000 : false),
    staleTime: 5 * 60 * 1000,
  });
}
