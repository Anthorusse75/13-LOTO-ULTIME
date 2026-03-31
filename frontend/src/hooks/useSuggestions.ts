import { suggestionService } from "@/services/suggestionService";
import { useGameStore } from "@/stores/gameStore";
import { useQuery } from "@tanstack/react-query";

export function useSuggestions(count = 3) {
  const gameId = useGameStore((s) => s.currentGameId);
  return useQuery({
    queryKey: ["suggestions", "daily", gameId, count],
    queryFn: () => suggestionService.getDaily(gameId!, count),
    enabled: !!gameId,
    staleTime: 5 * 60 * 1000,
  });
}
