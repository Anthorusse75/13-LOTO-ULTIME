import { useQuery } from "@tanstack/react-query";
import { statisticsService } from "@/services/statisticsService";
import { useGameStore } from "@/stores/gameStore";

export function useStatistics() {
  const gameId = useGameStore((s) => s.currentGameId);
  return useQuery({
    queryKey: ["statistics", gameId],
    queryFn: () => statisticsService.getAll(gameId!),
    enabled: !!gameId,
    staleTime: 5 * 60 * 1000,
  });
}

export function useFrequencies() {
  const gameId = useGameStore((s) => s.currentGameId);
  return useQuery({
    queryKey: ["statistics", gameId, "frequencies"],
    queryFn: () => statisticsService.getFrequencies(gameId!),
    enabled: !!gameId,
    staleTime: 5 * 60 * 1000,
  });
}

export function useGaps() {
  const gameId = useGameStore((s) => s.currentGameId);
  return useQuery({
    queryKey: ["statistics", gameId, "gaps"],
    queryFn: () => statisticsService.getGaps(gameId!),
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
