import AiAnalysisPanel from "@/components/common/AiAnalysisPanel";
import PageIntro from "@/components/common/PageIntro";
import {
  useBudgetHistory,
  useBudgetOptimize,
  useDeleteBudgetPlan,
} from "@/hooks/useBudget";
import { gameService } from "@/services/gameService";
import { useGameStore } from "@/stores/gameStore";
import type {
  BudgetOptimizeResponse,
  BudgetPlanResponse,
  BudgetRecommendation,
} from "@/types/budget";
import { useQuery } from "@tanstack/react-query";
import { ChevronDown, ChevronUp, Trash2, Wallet } from "lucide-react";
import { useState } from "react";

const OBJECTIVES = [
  { value: "balanced", label: "Équilibré", description: "Compromis qualité / couverture / diversité" },
  { value: "quality", label: "Qualité", description: "Maximise le score moyen des grilles" },
  { value: "coverage", label: "Couverture", description: "Maximise la couverture numérique" },
] as const;

const STRATEGY_LABELS: Record<string, string> = {
  top: "🏆 Top Grilles",
  portfolio: "📊 Portefeuille",
  wheeling: "🎯 Système réduit",
};

function RecommendationCard({ rec }: { rec: BudgetRecommendation }) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div
      className={`rounded-xl border p-5 transition-shadow ${
        rec.is_recommended
          ? "border-accent-blue bg-accent-blue/5 shadow-lg ring-2 ring-accent-blue/30"
          : "border-border-primary bg-bg-secondary"
      }`}
    >
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <span className="text-lg font-semibold">
            {STRATEGY_LABELS[rec.strategy] ?? rec.strategy}
          </span>
          {rec.is_recommended && (
            <span className="rounded-full bg-accent-blue px-2.5 py-0.5 text-xs font-bold text-white">
              Recommandé
            </span>
          )}
        </div>
        <span className="text-xl font-bold text-accent-blue">
          {rec.total_cost.toFixed(2)} €
        </span>
      </div>

      <p className="text-sm text-text-secondary mb-3">{rec.explanation}</p>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-3">
        <MiniStat label="Grilles" value={String(rec.grid_count)} />
        {rec.avg_score != null && (
          <MiniStat label="Score moyen" value={rec.avg_score.toFixed(2)} />
        )}
        {rec.diversity_score != null && (
          <MiniStat label="Diversité" value={(rec.diversity_score * 100).toFixed(1) + "%"} />
        )}
        {rec.coverage_rate != null && (
          <MiniStat label="Couverture" value={(rec.coverage_rate * 100).toFixed(1) + "%"} />
        )}
      </div>

      {/* Gain scenarios */}
      <div className="grid grid-cols-3 gap-2 text-sm mb-3">
        <div className="rounded-lg bg-green-500/10 p-2 text-center">
          <div className="text-xs text-text-secondary">Optimiste</div>
          <div className="font-semibold text-green-400">
            {rec.expected_gain.optimistic.toFixed(2)} €
          </div>
        </div>
        <div className="rounded-lg bg-yellow-500/10 p-2 text-center">
          <div className="text-xs text-text-secondary">Moyen</div>
          <div className="font-semibold text-yellow-400">
            {rec.expected_gain.mean.toFixed(2)} €
          </div>
        </div>
        <div className="rounded-lg bg-red-500/10 p-2 text-center">
          <div className="text-xs text-text-secondary">Pessimiste</div>
          <div className="font-semibold text-red-400">
            {rec.expected_gain.pessimistic.toFixed(2)} €
          </div>
        </div>
      </div>

      {/* Expandable grids */}
      <button
        onClick={() => setExpanded(!expanded)}
        className="flex items-center gap-1 text-sm text-accent-blue hover:underline"
      >
        {expanded ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
        {expanded ? "Masquer" : "Voir"} les {rec.grid_count} grilles
      </button>
      {expanded && (
        <div className="mt-3 max-h-64 overflow-y-auto rounded-lg border border-border-primary p-3">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-text-secondary">
                <th className="text-left py-1">#</th>
                <th className="text-left py-1">Numéros</th>
                <th className="text-left py-1">Étoiles</th>
              </tr>
            </thead>
            <tbody>
              {rec.grids.map((g, i) => (
                <tr key={i} className="border-t border-border-primary">
                  <td className="py-1 text-text-secondary">{i + 1}</td>
                  <td className="py-1 font-mono">
                    {g.numbers.join(" - ")}
                  </td>
                  <td className="py-1 font-mono text-yellow-400">
                    {g.stars?.join(" - ") ?? "—"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

function MiniStat({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg bg-bg-tertiary p-2 text-center">
      <div className="text-xs text-text-secondary">{label}</div>
      <div className="font-semibold">{value}</div>
    </div>
  );
}

export default function BudgetPage() {
  const slug = useGameStore((s) => s.currentGameSlug);
  const { data: game } = useQuery({
    queryKey: ["game", slug],
    queryFn: () => gameService.getBySlug(slug!),
    enabled: !!slug,
  });

  // Form state
  const [budget, setBudget] = useState<number>(20);
  const [objective, setObjective] = useState("balanced");
  const [useNumbers, setUseNumbers] = useState(false);
  const [selectedNumbers, setSelectedNumbers] = useState<number[]>([]);

  // API
  const optimizeMutation = useBudgetOptimize();
  const { data: history } = useBudgetHistory();
  const deleteMutation = useDeleteBudgetPlan();
  const [result, setResult] = useState<BudgetOptimizeResponse | null>(null);
  const [showHistory, setShowHistory] = useState(false);

  const toggleNumber = (n: number) => {
    setSelectedNumbers((prev) =>
      prev.includes(n) ? prev.filter((x) => x !== n) : [...prev, n].slice(0, 20),
    );
  };

  const handleOptimize = () => {
    optimizeMutation.mutate(
      {
        budget,
        objective,
        numbers: useNumbers && selectedNumbers.length > 0 ? selectedNumbers : undefined,
      },
      { onSuccess: (data) => setResult(data) },
    );
  };

  const loadPlan = (plan: BudgetPlanResponse) => {
    setResult({
      id: plan.id,
      budget: plan.budget,
      grid_price: 0,
      max_grids: 0,
      recommendations: plan.recommendations,
    });
  };

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold flex items-center gap-2">
        <Wallet className="h-7 w-7 text-accent-blue" />
        Optimisation Budget
      </h1>

      <PageIntro
        storageKey="budget"
        description="Définissez votre budget et votre objectif pour recevoir des recommandations personnalisées. Le système compare automatiquement plusieurs stratégies (top grilles, portefeuille diversifié, système réduit) et vous indique laquelle maximise votre objectif."
        tip="Commencez avec un budget modeste pour explorer les différentes stratégies, puis ajustez selon vos préférences."
        terms={[
          { term: "Top Grilles", definition: "Sélectionne les grilles avec les meilleurs scores individuels." },
          { term: "Portefeuille", definition: "Ensemble diversifié de grilles minimisant le chevauchement." },
          { term: "Système réduit", definition: "Couverture combinatoire garantissant un gain si vos numéros sont tirés (nécessite de sélectionner des numéros)." },
        ]}
      />

      {/* ── Budget & Objective Form ── */}
      <div className="rounded-xl border border-border-primary bg-bg-secondary p-5 space-y-4">
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {/* Budget input */}
          <div>
            <label className="block text-sm font-medium text-text-secondary mb-1">
              Budget (€)
            </label>
            <input
              type="number"
              min={1}
              max={10000}
              step={1}
              value={budget}
              onChange={(e) => setBudget(Number(e.target.value))}
              className="w-full rounded-lg border border-border-primary bg-bg-primary px-3 py-2 text-text-primary focus:ring-2 focus:ring-accent-blue focus:outline-none"
            />
          </div>

          {/* Objective selector */}
          <div>
            <label className="block text-sm font-medium text-text-secondary mb-1">
              Objectif
            </label>
            <div className="flex gap-2">
              {OBJECTIVES.map((obj) => (
                <button
                  key={obj.value}
                  onClick={() => setObjective(obj.value)}
                  title={obj.description}
                  className={`flex-1 rounded-lg border px-3 py-2 text-sm font-medium transition-colors ${
                    objective === obj.value
                      ? "border-accent-blue bg-accent-blue/20 text-accent-blue"
                      : "border-border-primary bg-bg-primary text-text-secondary hover:bg-bg-tertiary"
                  }`}
                >
                  {obj.label}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Optional numbers */}
        <div>
          <label className="flex items-center gap-2 text-sm">
            <input
              type="checkbox"
              checked={useNumbers}
              onChange={(e) => setUseNumbers(e.target.checked)}
              className="rounded"
            />
            <span className="text-text-secondary">
              Sélectionner des numéros (active la stratégie Système réduit)
            </span>
          </label>
        </div>

        {useNumbers && game && (
          <div>
            <p className="text-xs text-text-secondary mb-2">
              Sélectionnez au moins {game.numbers_drawn + 1} numéros (max 20)
              — {selectedNumbers.length} sélectionné{selectedNumbers.length > 1 ? "s" : ""}
            </p>
            <div className="flex flex-wrap gap-1.5">
              {Array.from({ length: game.max_number - game.min_number + 1 }, (_, i) => game.min_number + i).map(
                (n) => (
                  <button
                    key={n}
                    onClick={() => toggleNumber(n)}
                    className={`h-9 w-9 rounded-full text-sm font-semibold transition-colors ${
                      selectedNumbers.includes(n)
                        ? "bg-accent-blue text-white shadow"
                        : "bg-bg-tertiary text-text-secondary hover:bg-bg-primary"
                    }`}
                  >
                    {n}
                  </button>
                ),
              )}
            </div>
          </div>
        )}

        <button
          onClick={handleOptimize}
          disabled={optimizeMutation.isPending || budget < 1}
          className="w-full rounded-lg bg-accent-blue px-4 py-2.5 font-semibold text-white transition-colors hover:bg-accent-blue/80 disabled:opacity-50"
        >
          {optimizeMutation.isPending ? "Optimisation en cours…" : "Optimiser"}
        </button>
      </div>

      {/* ── Results ── */}
      {result && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold">
              Recommandations — {result.recommendations.length} stratégie{result.recommendations.length > 1 ? "s" : ""}
            </h2>
            {result.max_grids > 0 && (
              <span className="text-sm text-text-secondary">
                Budget : {result.budget.toFixed(2)} € — max {result.max_grids} grilles
              </span>
            )}
          </div>
          {result.recommendations.map((rec, i) => (
            <RecommendationCard key={i} rec={rec} />
          ))}
        </div>
      )}

      {/* ── History ── */}
      {history && history.length > 0 && (
        <div className="rounded-xl border border-border-primary bg-bg-secondary p-4">
          <button
            onClick={() => setShowHistory(!showHistory)}
            className="flex items-center gap-2 text-sm font-medium text-text-secondary hover:text-text-primary"
          >
            {showHistory ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
            Historique ({history.length})
          </button>
          {showHistory && (
            <div className="mt-3 space-y-2">
              {history.map((plan) => (
                <div
                  key={plan.id}
                  className="flex items-center justify-between rounded-lg border border-border-primary bg-bg-primary p-3"
                >
                  <button
                    onClick={() => loadPlan(plan)}
                    className="text-left flex-1"
                  >
                    <div className="text-sm font-medium">
                      {plan.budget.toFixed(2)} € — {plan.objective}
                    </div>
                    <div className="text-xs text-text-secondary">
                      {new Date(plan.created_at).toLocaleString("fr-FR")} — {plan.recommendations.length} stratégies
                    </div>
                  </button>
                  <button
                    onClick={() => deleteMutation.mutate(plan.id)}
                    className="ml-2 rounded-lg p-2 text-red-400 hover:bg-red-500/10"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* ── AI Analysis ── */}
      <AiAnalysisPanel
        topic="budget"
        buildContext={() => ({
          slug,
          budget,
          objective,
          strategies: result?.recommendations.map((r) => r.strategy) ?? [],
        })}
        dataKey={`budget-${result?.id ?? "none"}`}
      />
    </div>
  );
}
