import { portfolioService } from "@/services/portfolioService";
import { useGameStore } from "@/stores/gameStore";
import type { PortfolioGenerateRequest } from "@/types/portfolio";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

export function useGeneratePortfolio() {
  const gameId = useGameStore((s) => s.currentGameId);
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (req: PortfolioGenerateRequest) =>
      portfolioService.generate(gameId!, req),
    onSuccess: (data) => {
      toast.success(`Portefeuille de ${data.grids.length} grilles généré`);
      queryClient.invalidateQueries({ queryKey: ["portfolios", gameId] });
    },
  });
}
