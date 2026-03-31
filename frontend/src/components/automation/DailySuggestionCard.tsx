import { useSuggestions } from "@/hooks/useSuggestions";
import { useGameStore } from "@/stores/gameStore";
import { Loader2, Sparkles } from "lucide-react";

export default function DailySuggestionCard() {
  const gameSlug = useGameStore((s) => s.currentGameSlug);
  const { data, isLoading, error } = useSuggestions(3);

  const isEuromillions = gameSlug?.includes("euromillions");

  if (isLoading) {
    return (
      <div className="rounded-xl border border-surface-border bg-surface-card p-6 flex items-center justify-center gap-2">
        <Loader2 size={18} className="animate-spin text-accent-blue" />
        <span className="text-sm text-text-secondary">
          Chargement des suggestions…
        </span>
      </div>
    );
  }

  if (error || !data || data.grids.length === 0) {
    return null;
  }

  return (
    <div className="rounded-xl border border-accent-gold/30 bg-accent-gold/5 p-5 space-y-4">
      <div className="flex items-center gap-2">
        <Sparkles size={20} className="text-accent-gold" />
        <h3 className="text-sm font-semibold text-text-primary">
          Suggestions du jour
        </h3>
        <span className="text-xs text-text-tertiary ml-auto">{data.date}</span>
      </div>

      <p className="text-xs text-text-secondary">{data.reason}</p>

      <div className="space-y-3">
        {data.grids.map((grid, i) => (
          <div
            key={i}
            className="flex items-center gap-3 p-3 rounded-lg bg-surface-overlay/50"
          >
            <span className="text-xs font-bold text-text-tertiary w-6">
              #{i + 1}
            </span>
            <div className="flex flex-wrap gap-1.5">
              {grid.numbers.map((n) => (
                <span
                  key={n}
                  className="inline-flex items-center justify-center w-8 h-8 rounded-full text-xs font-bold bg-accent-blue/15 text-accent-blue"
                >
                  {n}
                </span>
              ))}
              {isEuromillions &&
                grid.stars?.map((s) => (
                  <span
                    key={`s-${s}`}
                    className="inline-flex items-center justify-center w-8 h-8 rounded-full text-xs font-bold bg-accent-gold/15 text-accent-gold"
                  >
                    {s}★
                  </span>
                ))}
            </div>
            <span className="ml-auto text-xs text-text-tertiary">
              {grid.total_score.toFixed(1)} pts
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
