import { useMutation } from "@tanstack/react-query";
import { portfolioService } from "@/services/portfolioService";
import { useGameStore } from "@/stores/gameStore";
import type { PortfolioGenerateRequest } from "@/types/portfolio";

export function useGeneratePortfolio() {
  const gameId = useGameStore((s) => s.currentGameId);
  return useMutation({
    mutationFn: (req: PortfolioGenerateRequest) =>
      portfolioService.generate(gameId!, req),
  });
}
