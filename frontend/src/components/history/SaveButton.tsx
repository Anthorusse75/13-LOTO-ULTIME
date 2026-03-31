import { useSaveResult } from "@/hooks/useHistory";
import { useGameStore } from "@/stores/gameStore";
import type { ResultType } from "@/types/history";
import { Save } from "lucide-react";

interface SaveButtonProps {
  resultType: ResultType;
  parameters: Record<string, unknown>;
  resultData: Record<string, unknown>;
  name?: string;
  className?: string;
}

export default function SaveButton({
  resultType,
  parameters,
  resultData,
  name,
  className = "",
}: SaveButtonProps) {
  const gameId = useGameStore((s) => s.currentGameId);
  const saveMutation = useSaveResult();

  const handleSave = () => {
    if (!gameId) return;
    saveMutation.mutate({
      result_type: resultType,
      parameters,
      result_data: resultData,
      game_id: gameId,
      name: name ?? null,
      tags: [],
    });
  };

  return (
    <button
      onClick={handleSave}
      disabled={saveMutation.isPending || !gameId}
      title="Sauvegarder dans l'historique"
      className={`inline-flex items-center gap-1.5 px-3 py-1.5 text-xs rounded-md border border-border
        bg-surface-hover hover:bg-accent-blue/10 hover:border-accent-blue/30
        disabled:opacity-40 disabled:cursor-not-allowed transition-colors ${className}`}
    >
      <Save size={14} />
      {saveMutation.isPending ? "..." : "Sauvegarder"}
    </button>
  );
}
