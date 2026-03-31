import { useGameStore } from "@/stores/gameStore";
import { Clock, Trophy, Minus } from "lucide-react";
import type { GridDrawResult } from "@/types/automation";

interface Props {
  results: GridDrawResult[];
}

export default function PlayedGridsResults({ results }: Props) {
  const gameSlug = useGameStore((s) => s.currentGameSlug);
  const isEuromillions = gameSlug?.includes("euromillions");

  if (results.length === 0) {
    return (
      <div className="rounded-xl border border-surface-border bg-surface-card p-6 text-center">
        <Minus size={24} className="text-text-tertiary mx-auto mb-2" />
        <p className="text-sm text-text-secondary">
          Aucun résultat de grille jouée pour le moment.
        </p>
      </div>
    );
  }

  return (
    <div className="rounded-xl border border-surface-border bg-surface-card overflow-hidden">
      <div className="p-4 border-b border-surface-border flex items-center gap-2">
        <Trophy size={18} className="text-accent-gold" />
        <h3 className="text-sm font-semibold text-text-primary">
          Résultats des grilles jouées
        </h3>
      </div>
      <div className="divide-y divide-surface-border">
        {results.map((r) => (
          <div key={r.id} className="p-4 flex items-center gap-4">
            <div className="flex-1">
              <div className="flex flex-wrap gap-1.5 mb-2">
                {r.matched_numbers.map((n) => (
                  <span
                    key={n}
                    className="inline-flex items-center justify-center w-7 h-7 rounded-full text-xs font-bold bg-green-500/15 text-green-400"
                  >
                    {n}
                  </span>
                ))}
                {isEuromillions &&
                  r.matched_stars?.map((s) => (
                    <span
                      key={`s-${s}`}
                      className="inline-flex items-center justify-center w-7 h-7 rounded-full text-xs font-bold bg-accent-gold/15 text-accent-gold"
                    >
                      {s}★
                    </span>
                  ))}
              </div>
              <p className="text-xs text-text-tertiary">
                {r.match_count} n° + {r.star_match_count} ★ trouvés
              </p>
            </div>
            <div className="text-right">
              {r.prize_rank ? (
                <div>
                  <span className="text-sm font-bold text-accent-gold">
                    Rang {r.prize_rank}
                  </span>
                  <p className="text-xs text-text-secondary">
                    ~{r.estimated_prize?.toFixed(2)}€
                  </p>
                </div>
              ) : (
                <span className="text-xs text-text-tertiary">Pas de gain</span>
              )}
            </div>
            <div className="text-xs text-text-tertiary">
              <Clock size={12} className="inline mr-1" />
              {new Date(r.checked_at).toLocaleDateString("fr-FR")}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
