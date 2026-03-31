import { budgetService } from "@/services/budgetService";
import { useGameStore } from "@/stores/gameStore";
import type { BudgetOptimizeRequest } from "@/types/budget";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

export function useBudgetOptimize() {
  const gameId = useGameStore((s) => s.currentGameId);
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (req: BudgetOptimizeRequest) =>
      budgetService.optimize(gameId!, req),
    onSuccess: (data) => {
      const count = data.recommendations.length;
      toast.success(
        `${count} stratégie${count > 1 ? "s" : ""} générée${count > 1 ? "s" : ""}`,
      );
      queryClient.invalidateQueries({ queryKey: ["budget", gameId] });
    },
  });
}

export function useBudgetHistory() {
  const gameId = useGameStore((s) => s.currentGameId);
  return useQuery({
    queryKey: ["budget", gameId, "history"],
    queryFn: () => budgetService.getHistory(gameId!),
    enabled: !!gameId,
    staleTime: 5 * 60 * 1000,
  });
}

export function useDeleteBudgetPlan() {
  const gameId = useGameStore((s) => s.currentGameId);
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (planId: number) => budgetService.delete(gameId!, planId),
    onSuccess: () => {
      toast.success("Plan supprimé");
      queryClient.invalidateQueries({ queryKey: ["budget", gameId] });
    },
  });
}
