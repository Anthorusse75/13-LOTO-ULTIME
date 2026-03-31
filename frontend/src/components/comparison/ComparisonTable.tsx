import type { StrategyMetrics } from "@/types/comparison";
import { ArrowDown, ArrowUp, Minus } from "lucide-react";

const METRIC_LABELS: Record<string, { label: string; unit?: string }> = {
  grid_count: { label: "Grilles" },
  avg_score: { label: "Score moyen" },
  score_variance: { label: "Variance" },
  diversity: { label: "Diversité", unit: "%" },
  coverage: { label: "Couverture", unit: "%" },
  cost: { label: "Coût", unit: "€" },
  robustness: { label: "Robustesse", unit: "%" },
  expected_gain: { label: "Gain espéré", unit: "€" },
};

const METRIC_KEYS: Array<keyof StrategyMetrics> = [
  "grid_count",
  "avg_score",
  "score_variance",
  "diversity",
  "coverage",
  "cost",
  "robustness",
  "expected_gain",
];

function formatValue(key: string, value: unknown): string {
  if (value == null) return "—";
  if (typeof value === "number") {
    if (key === "diversity" || key === "coverage" || key === "robustness") {
      return (value * 100).toFixed(1);
    }
    if (key === "cost" || key === "expected_gain") {
      return value.toFixed(2);
    }
    if (key === "grid_count") return String(value);
    return value.toFixed(4);
  }
  return String(value);
}

function getBestWorstIdx(
  key: string,
  strategies: StrategyMetrics[],
): { best: number | null; worst: number | null } {
  const values = strategies.map((s) => {
    const v = s[key as keyof StrategyMetrics];
    return typeof v === "number" ? v : null;
  });
  const valid = values.filter((v): v is number => v !== null);
  if (valid.length < 2) return { best: null, worst: null };

  const isLowerBetter = key === "cost" || key === "score_variance";
  const best = isLowerBetter ? Math.min(...valid) : Math.max(...valid);
  const worst = isLowerBetter ? Math.max(...valid) : Math.min(...valid);
  return {
    best: values.indexOf(best),
    worst: values.indexOf(worst),
  };
}

interface Props {
  strategies: StrategyMetrics[];
}

export default function ComparisonTable({ strategies }: Props) {
  if (strategies.length === 0) return null;

  return (
    <div className="rounded-xl border border-border-primary bg-bg-secondary overflow-hidden">
      <div className="px-5 py-4 border-b border-border-primary">
        <h3 className="text-sm font-semibold text-text-primary">
          Tableau comparatif détaillé
        </h3>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-border-primary bg-bg-primary/50">
              <th className="px-5 py-3 text-left text-xs font-semibold text-text-secondary uppercase tracking-wider">
                Métrique
              </th>
              {strategies.map((s, idx) => (
                <th
                  key={idx}
                  className="px-5 py-3 text-center text-xs font-semibold text-text-primary uppercase tracking-wider"
                >
                  {s.label}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {METRIC_KEYS.map((key, rowIdx) => {
              const { best, worst } = getBestWorstIdx(key, strategies);
              const meta = METRIC_LABELS[key] ?? { label: key };
              return (
                <tr
                  key={key}
                  className={`border-b border-border-primary last:border-0 transition-colors hover:bg-surface-hover/30 ${rowIdx % 2 === 0 ? "bg-transparent" : "bg-bg-primary/20"}`}
                >
                  <td className="px-5 py-3 font-medium text-text-secondary">
                    <div className="flex items-center gap-2">
                      {meta.label}
                      {meta.unit && (
                        <span className="text-[10px] text-text-secondary/60">
                          ({meta.unit})
                        </span>
                      )}
                    </div>
                  </td>
                  {strategies.map((s, idx) => {
                    const val = s[key as keyof StrategyMetrics];
                    const isBest = best === idx && val != null;
                    const isWorst = worst === idx && val != null;
                    return (
                      <td key={idx} className="px-5 py-3 text-center">
                        <div className="inline-flex items-center gap-1.5">
                          <span
                            className={`tabular-nums font-semibold ${
                              isBest
                                ? "text-emerald-400"
                                : isWorst
                                  ? "text-red-400/70"
                                  : "text-text-primary"
                            }`}
                          >
                            {formatValue(key, val)}
                          </span>
                          {isBest && (
                            <ArrowUp
                              size={12}
                              className="text-emerald-400"
                            />
                          )}
                          {isWorst && (
                            <ArrowDown
                              size={12}
                              className="text-red-400/70"
                            />
                          )}
                          {!isBest && !isWorst && val != null && (
                            <Minus
                              size={12}
                              className="text-text-secondary/30"
                            />
                          )}
                        </div>
                      </td>
                    );
                  })}
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
