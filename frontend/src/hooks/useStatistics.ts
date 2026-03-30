import { statisticsService } from "@/services/statisticsService";
import { useGameStore } from "@/stores/gameStore";
import { useQuery } from "@tanstack/react-query";
import { AxiosError } from "axios";

export function useStatistics() {
  const gameId = useGameStore((s) => s.currentGameId);
  return useQuery({
    queryKey: ["statistics", gameId],
    queryFn: () => statisticsService.getAll(gameId!),
    enabled: !!gameId,
    retry: (_count, error) => {
      const status = (error as AxiosError)?.response?.status;
      return status !== 404 && status !== 422;
    },
    staleTime: 5 * 60 * 1000,
  });
}

export function useFrequencies(lastN?: number) {
  const gameId = useGameStore((s) => s.currentGameId);
  return useQuery({
    queryKey: ["statistics", gameId, "frequencies", lastN ?? "all"],
    queryFn: () => statisticsService.getFrequencies(gameId!, lastN),
    enabled: !!gameId,
    staleTime: 5 * 60 * 1000,
  });
}

export function useGaps(lastN?: number) {
  const gameId = useGameStore((s) => s.currentGameId);
  return useQuery({
    queryKey: ["statistics", gameId, "gaps", lastN ?? "all"],
    queryFn: () => statisticsService.getGaps(gameId!, lastN),
    enabled: !!gameId,
    staleTime: 5 * 60 * 1000,
  });
}

export function useCooccurrences() {
  const gameId = useGameStore((s) => s.currentGameId);
  return useQuery({
    queryKey: ["statistics", gameId, "cooccurrences"],
    queryFn: () => statisticsService.getCooccurrences(gameId!),
    enabled: !!gameId,
    staleTime: 5 * 60 * 1000,
  });
}

export function useTemporal() {
  const gameId = useGameStore((s) => s.currentGameId);
  return useQuery({
    queryKey: ["statistics", gameId, "temporal"],
    queryFn: () => statisticsService.getTemporal(gameId!),
    enabled: !!gameId,
    staleTime: 5 * 60 * 1000,
  });
}

export function useDistribution() {
  const gameId = useGameStore((s) => s.currentGameId);
  return useQuery({
    queryKey: ["statistics", gameId, "distribution"],
    queryFn: () => statisticsService.getDistribution(gameId!),
    enabled: !!gameId,
    staleTime: 5 * 60 * 1000,
  });
}

export function useBayesian() {
  const gameId = useGameStore((s) => s.currentGameId);
  return useQuery({
    queryKey: ["statistics", gameId, "bayesian"],
    queryFn: () => statisticsService.getBayesian(gameId!),
    enabled: !!gameId,
    staleTime: 5 * 60 * 1000,
  });
}

export function useGraph() {
  const gameId = useGameStore((s) => s.currentGameId);
  return useQuery({
    queryKey: ["statistics", gameId, "graph"],
    queryFn: () => statisticsService.getGraph(gameId!),
    enabled: !!gameId,
    staleTime: 5 * 60 * 1000,
  });
}
