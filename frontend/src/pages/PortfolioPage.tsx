import { useState } from "react";
import { useGeneratePortfolio } from "@/hooks/usePortfolios";
import { useGameStore } from "@/stores/gameStore";
import { useQuery } from "@tanstack/react-query";
import { gameService } from "@/services/gameService";
import DrawBalls from "@/components/draws/DrawBalls";
import NumberHeatmap from "@/components/statistics/NumberHeatmap";
import LoadingSpinner from "@/components/common/LoadingSpinner";
import { formatScore } from "@/utils/formatters";
import { PORTFOLIO_STRATEGIES } from "@/utils/constants";
import { Loader2 } from "lucide-react";

export default function PortfolioPage() {
  const [gridCount, setGridCount] = useState(7);
  const [strategy, setStrategy] = useState("balanced");

  const slug = useGameStore((s) => s.currentGameSlug);
  const { data: game } = useQuery({
    queryKey: ["game", slug],
    queryFn: () => gameService.getBySlug(slug!),
    enabled: !!slug,
  });

  const generateMutation = useGeneratePortfolio();

  const handleGenerate = () => {
    generateMutation.mutate({ grid_count: gridCount, strategy });
  };

  const portfolio = generateMutation.data;

  // Build coverage heatmap
  const coverageMap: Record<number, number> = {};
  if (portfolio && game) {
    for (let n = game.min_number; n <= game.max_number; n++) {
      coverageMap[n] = 0;
    }
    portfolio.grids.forEach((g) => {
      g.numbers.forEach((n) => {
        coverageMap[n] = (coverageMap[n] || 0) + 1;
      });
    });
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Portefeuille</h1>

      {/* Generation form */}
      <div className="bg-surface rounded-lg border border-border p-6">
        <h2 className="text-sm font-semibold mb-4">Générer un portefeuille</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          <div>
            <label className="text-xs text-text-secondary block mb-1">
              Nombre de grilles
            </label>
            <input
              type="number"
              min={2}
              max={50}
              value={gridCount}
              onChange={(e) => setGridCount(Number(e.target.value))}
              className="w-full bg-surface-hover border border-border rounded-md px-3 py-2 text-sm font-mono focus:outline-none focus:ring-1 focus:ring-accent-blue"
            />
          </div>
          <div>
            <label className="text-xs text-text-secondary block mb-1">
              Stratégie
            </label>
            <select
              value={strategy}
              onChange={(e) => setStrategy(e.target.value)}
              className="w-full bg-surface-hover border border-border rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-accent-blue"
            >
              {PORTFOLIO_STRATEGIES.map((s) => (
                <option key={s.value} value={s.value}>
                  {s.label}
                </option>
              ))}
            </select>
          </div>
        </div>
        <button
          onClick={handleGenerate}
          disabled={generateMutation.isPending}
          className="px-6 py-2 bg-accent-blue text-white rounded-md text-sm font-medium hover:bg-accent-blue/90 disabled:opacity-50 flex items-center gap-2"
        >
          {generateMutation.isPending && <Loader2 size={16} className="animate-spin" />}
          Générer portefeuille
        </button>
      </div>

      {generateMutation.isPending && <LoadingSpinner message="Optimisation en cours..." />}

      {/* Empty state */}
      {!portfolio && !generateMutation.isPending && (
        <div className="bg-surface rounded-lg border border-border p-8 text-center">
          <p className="text-text-secondary text-sm mb-2">Aucun portefeuille généré.</p>
          <p className="text-text-secondary text-xs">Choisissez le nombre de grilles et la stratégie, puis cliquez sur « Générer portefeuille » pour optimiser votre jeu.</p>
        </div>
      )}

      {/* Results */}
      {portfolio && (
        <>
          {/* KPIs */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-surface rounded-lg border border-border p-4">
              <p className="text-xs text-text-secondary">Score moyen</p>
              <p className="font-mono text-lg text-accent-green">
                {formatScore(portfolio.avg_grid_score)}
              </p>
            </div>
            <div className="bg-surface rounded-lg border border-border p-4">
              <p className="text-xs text-text-secondary">Diversité</p>
              <p className="font-mono text-lg">
                {(portfolio.diversity_score * 100).toFixed(1)}%
              </p>
            </div>
            <div className="bg-surface rounded-lg border border-border p-4">
              <p className="text-xs text-text-secondary">Couverture</p>
              <p className="font-mono text-lg">
                {(portfolio.coverage_score * 100).toFixed(1)}%
              </p>
            </div>
            <div className="bg-surface rounded-lg border border-border p-4">
              <p className="text-xs text-text-secondary">Distance Hamming min</p>
              <p className="font-mono text-lg">
                {portfolio.min_hamming_distance?.toFixed(1) ?? "—"}
              </p>
            </div>
          </div>

          {/* Grids list */}
          <div className="bg-surface rounded-lg border border-border p-4">
            <h2 className="text-sm font-semibold mb-4">Grilles du portefeuille</h2>
            <div className="space-y-2">
              {portfolio.grids.map((g, i) => (
                <div
                  key={i}
                  className="flex items-center gap-4 p-2 rounded-md hover:bg-surface-hover"
                >
                  <span className="text-xs text-text-secondary w-6">#{i + 1}</span>
                  <DrawBalls numbers={g.numbers} stars={g.stars} size="sm" />
                  <span className="ml-auto font-mono text-accent-green">
                    {formatScore(g.score)}
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Coverage heatmap */}
          {game && (
            <div className="bg-surface rounded-lg border border-border p-4">
              <h2 className="text-sm font-semibold mb-3">Couverture numérique</h2>
              <NumberHeatmap
                data={coverageMap}
                minNumber={game.min_number}
                maxNumber={game.max_number}
                colorScale="frequency"
              />
            </div>
          )}

          <p className="text-xs text-text-secondary">
            Stratégie: {portfolio.strategy} — Méthode: {portfolio.method_used} —
            Temps: {portfolio.computation_time_ms.toFixed(0)}ms
          </p>
        </>
      )}
    </div>
  );
}
