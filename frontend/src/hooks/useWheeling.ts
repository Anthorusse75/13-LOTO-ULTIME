import { wheelingService } from "@/services/wheelingService";
import { useGameStore } from "@/stores/gameStore";
import type {
  WheelingGenerateRequest,
  WheelingPreviewRequest,
} from "@/types/wheeling";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

export function useWheelingPreview() {
  const gameId = useGameStore((s) => s.currentGameId);
  return useMutation({
    mutationFn: (req: WheelingPreviewRequest) =>
      wheelingService.preview(gameId!, req),
  });
}

export function useWheelingGenerate() {
  const gameId = useGameStore((s) => s.currentGameId);
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (req: WheelingGenerateRequest) =>
      wheelingService.generate(gameId!, req),
    onSuccess: (data) => {
      toast.success(
        `Système généré : ${data.grid_count} grilles, couverture ${(data.coverage_rate * 100).toFixed(0)}%`,
      );
      queryClient.invalidateQueries({ queryKey: ["wheeling", gameId] });
    },
  });
}

export function useWheelingHistory() {
  const gameId = useGameStore((s) => s.currentGameId);
  return useQuery({
    queryKey: ["wheeling", gameId, "history"],
    queryFn: () => wheelingService.getHistory(gameId!),
    enabled: !!gameId,
    staleTime: 5 * 60 * 1000,
  });
}

export function useDeleteWheelingSystem() {
  const gameId = useGameStore((s) => s.currentGameId);
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (systemId: number) =>
      wheelingService.delete(gameId!, systemId),
    onSuccess: () => {
      toast.success("Système supprimé");
      queryClient.invalidateQueries({ queryKey: ["wheeling", gameId] });
    },
  });
}
