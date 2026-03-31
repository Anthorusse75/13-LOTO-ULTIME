import AiAnalysisPanel from "@/components/common/AiAnalysisPanel";
import type { GridScoreResponse } from "@/types/grid";
import { useCallback } from "react";

interface GridAiAnalysisProps {
  grid: GridScoreResponse;
  method: string;
  profile: string;
}

export default function GridAiAnalysis({
  grid,
  method,
  profile,
}: GridAiAnalysisProps) {
  const gridKey = `${grid.numbers.join(",")}-${grid.stars?.join(",") ?? ""}`;

  const buildContext = useCallback((): Record<string, unknown> => {
    const bd = grid.score_breakdown;
    return {
      numbers: grid.numbers,
      stars: grid.stars,
      total_score: grid.total_score,
      score_breakdown: {
        frequency: bd.frequency,
        gap: bd.gap,
        cooccurrence: bd.cooccurrence,
        structure: bd.structure,
        balance: bd.balance,
        pattern_penalty: bd.pattern_penalty,
      },
      method,
      profile,
    };
  }, [grid, method, profile]);

  return (
    <AiAnalysisPanel
      topic="grid"
      buildContext={buildContext}
      dataKey={gridKey}
      buttonLabel="Analyser cette grille en détail"
      description={`Obtenez une explication détaillée de chaque barre de score par un expert en mathématiques. L'IA analysera les 6 critères de votre grille [${grid.numbers.join(", ")}] et vous expliquera ce que chaque score signifie concrètement.`}
    />
  );
}
