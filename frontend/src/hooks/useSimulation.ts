import { useMutation } from "@tanstack/react-query";
import { simulationService } from "@/services/simulationService";
import { useGameStore } from "@/stores/gameStore";
import type {
  MonteCarloGridRequest,
  MonteCarloPortfolioRequest,
  StabilityRequest,
  ComparisonRequest,
} from "@/types/simulation";

export function useMonteCarloGrid() {
  const gameId = useGameStore((s) => s.currentGameId);
  return useMutation({
    mutationFn: (req: MonteCarloGridRequest) =>
      simulationService.monteCarlo(gameId!, req),
  });
}

export function useMonteCarloPortfolio() {
  const gameId = useGameStore((s) => s.currentGameId);
  return useMutation({
    mutationFn: (req: MonteCarloPortfolioRequest) =>
      simulationService.monteCarloPortfolio(gameId!, req),
  });
}

export function useStability() {
  const gameId = useGameStore((s) => s.currentGameId);
  return useMutation({
    mutationFn: (req: StabilityRequest) =>
      simulationService.stability(gameId!, req),
  });
}

export function useCompareRandom() {
  const gameId = useGameStore((s) => s.currentGameId);
  return useMutation({
    mutationFn: (req: ComparisonRequest) =>
      simulationService.compareRandom(gameId!, req),
  });
}
