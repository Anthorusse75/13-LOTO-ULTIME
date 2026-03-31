import { historyService } from "@/services/historyService";
import { useGameStore } from "@/stores/gameStore";
import type { SaveResultRequest } from "@/types/history";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

export function useSavedResults(
  page = 1,
  pageSize = 20,
  resultType?: string,
  isFavorite?: boolean,
  tag?: string,
) {
  const gameId = useGameStore((s) => s.currentGameId);
  return useQuery({
    queryKey: ["history", gameId, page, pageSize, resultType, isFavorite, tag],
    queryFn: () =>
      historyService.list(gameId!, page, pageSize, resultType, isFavorite, tag),
    enabled: !!gameId,
    staleTime: 5 * 60 * 1000,
  });
}

export function useSaveResult() {
  const gameId = useGameStore((s) => s.currentGameId);
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (req: SaveResultRequest) => historyService.save(gameId!, req),
    onSuccess: () => {
      toast.success("Résultat sauvegardé");
      queryClient.invalidateQueries({ queryKey: ["history", gameId] });
    },
  });
}

export function useDeleteSavedResult() {
  const gameId = useGameStore((s) => s.currentGameId);
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => historyService.delete(gameId!, id),
    onSuccess: () => {
      toast.success("Résultat supprimé");
      queryClient.invalidateQueries({ queryKey: ["history", gameId] });
    },
  });
}

export function useToggleSavedFavorite() {
  const gameId = useGameStore((s) => s.currentGameId);
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => historyService.toggleFavorite(gameId!, id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["history", gameId] });
    },
  });
}

export function useDuplicateSavedResult() {
  const gameId = useGameStore((s) => s.currentGameId);
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => historyService.duplicate(gameId!, id),
    onSuccess: () => {
      toast.success("Résultat dupliqué");
      queryClient.invalidateQueries({ queryKey: ["history", gameId] });
    },
  });
}
