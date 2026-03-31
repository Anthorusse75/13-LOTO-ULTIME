import type { ComparisonSummary as SummaryType } from "@/types/comparison";
import { Lightbulb } from "lucide-react";

interface Props {
  summary: SummaryType;
}

export default function ComparisonSummary({ summary }: Props) {
  return (
    <div className="rounded-xl border border-accent-blue/30 bg-accent-blue/5 p-5">
      <div className="flex items-start gap-3">
        <Lightbulb size={20} className="text-accent-blue shrink-0 mt-0.5" />
        <div className="space-y-2">
          <h3 className="text-sm font-semibold text-text-primary">
            Résumé de la comparaison
          </h3>
          <p className="text-sm text-text-secondary leading-relaxed">
            {summary.recommendation}
          </p>
          <div className="flex flex-wrap gap-3 mt-2">
            {summary.best_score && (
              <Badge label="Meilleur score" value={summary.best_score} color="blue" />
            )}
            {summary.best_diversity && (
              <Badge label="Meilleure diversité" value={summary.best_diversity} color="green" />
            )}
            {summary.best_coverage && (
              <Badge label="Meilleure couverture" value={summary.best_coverage} color="amber" />
            )}
            {summary.best_cost && (
              <Badge label="Plus économique" value={summary.best_cost} color="purple" />
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

function Badge({
  label,
  value,
  color,
}: {
  label: string;
  value: string;
  color: string;
}) {
  const colorClasses: Record<string, string> = {
    blue: "bg-accent-blue/10 text-accent-blue",
    green: "bg-emerald-500/10 text-emerald-400",
    amber: "bg-amber-500/10 text-amber-400",
    purple: "bg-purple-500/10 text-purple-400",
  };

  return (
    <span
      className={`inline-flex items-center gap-1 rounded-full px-2.5 py-1 text-xs font-medium ${colorClasses[color] ?? colorClasses.blue}`}
    >
      {label}: {value}
    </span>
  );
}
