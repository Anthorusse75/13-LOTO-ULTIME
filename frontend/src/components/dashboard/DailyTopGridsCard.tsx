import DrawBalls from "@/components/draws/DrawBalls";
import { formatScore } from "@/utils/formatters";
import { Award } from "lucide-react";
import type { ScoredGrid } from "@/types/grid";

interface DailyTopGridsCardProps {
  grids: ScoredGrid[] | undefined;
  limit?: number;
}

export default function DailyTopGridsCard({
  grids,
  limit = 5,
}: DailyTopGridsCardProps) {
  const display = grids?.slice(0, limit);

  return (
    <div className="bg-surface rounded-lg border border-border p-4">
      <div className="flex items-center gap-2 mb-3">
        <Award size={16} className="text-accent-green" />
        <h3 className="text-sm font-semibold">Top {limit} Grilles du jour</h3>
      </div>
      {display && display.length > 0 ? (
        <div className="space-y-2">
          {display.map((g, i) => (
            <div
              key={g.id}
              className="flex items-center gap-3 p-2 rounded-md hover:bg-surface-hover"
            >
              <span className="text-xs text-text-secondary w-5">#{i + 1}</span>
              <DrawBalls numbers={g.numbers} stars={g.stars} size="sm" />
              <span className="ml-auto font-mono text-accent-green text-sm">
                {formatScore(g.total_score)}
              </span>
            </div>
          ))}
        </div>
      ) : (
        <p className="text-sm text-text-secondary">Aucune grille générée</p>
      )}
    </div>
  );
}
