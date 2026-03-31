import { Layers } from "lucide-react";
import { formatScore } from "@/utils/formatters";

interface PortfolioSummaryCardProps {
  strategy?: string;
  gridCount?: number;
  diversityScore?: number;
  avgGridScore?: number;
}

export default function PortfolioSummaryCard({
  strategy,
  gridCount,
  diversityScore,
  avgGridScore,
}: PortfolioSummaryCardProps) {
  const hasData = gridCount !== undefined && gridCount > 0;

  return (
    <div className="bg-surface rounded-lg border border-border p-4">
      <div className="flex items-center gap-2 mb-3">
        <Layers size={16} className="text-accent-purple" />
        <h3 className="text-sm font-semibold">Dernier portefeuille</h3>
      </div>
      {hasData ? (
        <div className="space-y-2 text-sm">
          <div className="flex justify-between">
            <span className="text-text-secondary">Stratégie</span>
            <span className="font-medium">{strategy ?? "—"}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-text-secondary">Grilles</span>
            <span className="font-medium">{gridCount}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-text-secondary">Diversité</span>
            <span className="font-mono text-accent-blue">
              {diversityScore !== undefined
                ? formatScore(diversityScore)
                : "—"}
            </span>
          </div>
          <div className="flex justify-between">
            <span className="text-text-secondary">Score moyen</span>
            <span className="font-mono text-accent-green">
              {avgGridScore !== undefined ? formatScore(avgGridScore) : "—"}
            </span>
          </div>
        </div>
      ) : (
        <p className="text-sm text-text-secondary">
          Aucun portefeuille généré
        </p>
      )}
    </div>
  );
}
