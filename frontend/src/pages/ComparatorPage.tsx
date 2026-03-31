import PageIntro from "@/components/common/PageIntro";
import ComparisonRadar from "@/components/comparison/ComparisonRadar";
import ComparisonScatter from "@/components/comparison/ComparisonScatter";
import ComparisonSummary from "@/components/comparison/ComparisonSummary";
import ComparisonTable from "@/components/comparison/ComparisonTable";
import StrategySelector from "@/components/comparison/StrategySelector";
import { useComparison } from "@/hooks/useComparison";
import type { ComparisonResponse, StrategyConfig } from "@/types/comparison";
import { Loader2, Play, Scale } from "lucide-react";
import { useState } from "react";

export default function ComparatorPage() {
  const [strategies, setStrategies] = useState<StrategyConfig[]>([
    { type: "top", count: 10 },
    { type: "portfolio", count: 10 },
  ]);
  const [result, setResult] = useState<ComparisonResponse | null>(null);

  const comparison = useComparison();

  const handleCompare = () => {
    comparison.mutate(
      { strategies, include_gain_scenarios: false },
      { onSuccess: (data) => setResult(data) },
    );
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <Scale size={28} className="text-accent-blue" />
        <h1 className="text-2xl font-bold text-text-primary">
          Comparateur de stratégies
        </h1>
      </div>

      <PageIntro
        storageKey="comparator"
        description="Comparez jusqu'à 5 stratégies de jeu côte à côte. Visualisez les différences sur le score moyen, la diversité, la couverture et le coût pour choisir l'approche la plus adaptée à votre style."
        tip="Sélectionnez au moins 2 stratégies, ajustez le nombre de grilles, puis lancez la comparaison."
        terms={[
          {
            term: "Score moyen",
            definition:
              "Qualité moyenne des grilles selon les critères statistiques",
          },
          {
            term: "Diversité",
            definition:
              "Distance moyenne entre les grilles (0 = identiques, 1 = très différentes)",
          },
          {
            term: "Couverture",
            definition:
              "Pourcentage de combinaisons couvertes par l'ensemble des grilles",
          },
        ]}
      />

      {/* ── Step 1: Strategy selection ── */}
      <div className="rounded-xl bg-surface p-5 space-y-5">
        <h2 className="text-lg font-semibold">1. Sélection des stratégies</h2>

        <StrategySelector strategies={strategies} onChange={setStrategies} />
      </div>

      {/* ── Step 2: Launch ── */}
      <div className="rounded-xl bg-surface p-5 space-y-4">
        <h2 className="text-lg font-semibold">2. Lancer la comparaison</h2>

        <div className="flex items-center gap-4">
          <button
            onClick={handleCompare}
            disabled={strategies.length < 2 || comparison.isPending}
            className="flex items-center gap-2 rounded-xl bg-accent-blue px-6 py-3 text-sm font-bold text-white shadow-lg shadow-accent-blue/25 hover:bg-accent-blue/90 hover:shadow-accent-blue/40 disabled:opacity-40 disabled:shadow-none disabled:cursor-not-allowed transition-all"
          >
            {comparison.isPending ? (
              <Loader2 size={18} className="animate-spin" />
            ) : (
              <Play size={18} />
            )}
            {comparison.isPending ? "Comparaison…" : "Comparer"}
          </button>

          {strategies.length < 2 && (
            <span className="text-xs text-text-secondary">
              Ajoutez au moins 2 stratégies pour comparer
            </span>
          )}
        </div>
      </div>

      {/* ── Step 3: Results ── */}
      {result && (
        <div className="space-y-6">
          <h2 className="text-lg font-semibold">3. Résultats</h2>

          <ComparisonSummary summary={result.summary} />

          <ComparisonTable strategies={result.strategies} />

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <ComparisonRadar strategies={result.strategies} />
            <ComparisonScatter strategies={result.strategies} />
          </div>
        </div>
      )}
    </div>
  );
}
