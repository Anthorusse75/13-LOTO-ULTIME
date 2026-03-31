import { comparisonService } from "@/services/comparisonService";
import { useGameStore } from "@/stores/gameStore";
import type { ComparisonRequest } from "@/types/comparison";
import { useMutation } from "@tanstack/react-query";
import { toast } from "sonner";

export function useComparison() {
  const gameId = useGameStore((s) => s.currentGameId);
  return useMutation({
    mutationFn: (req: ComparisonRequest) =>
      comparisonService.compare(gameId!, req),
    onSuccess: (data) => {
      const count = data.strategies.length;
      toast.success(
        `${count} stratégie${count > 1 ? "s" : ""} comparée${count > 1 ? "s" : ""}`,
      );
    },
  });
}
