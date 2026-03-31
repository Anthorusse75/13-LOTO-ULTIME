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
import {
  ChevronDown,
  ChevronUp,
  Crown,
  Layers,
  Loader2,
  Minus,
  Play,
  Plus,
  Trash2,
  Trophy,
  Wallet,
} from "lucide-react";
import { useCallback, useMemo, useState } from "react";

const OBJECTIVES = [
  {
    value: "balanced",
    label: "Équilibré",
    description: "Compromis qualité / couverture / diversité",
    color: "text-accent-blue",
    bg: "bg-accent-blue/10",
    border: "border-accent-blue/40",
    activeBg: "bg-accent-blue",
  },
  {
    value: "quality",
    label: "Qualité",
    description: "Maximise le score moyen des grilles",
    color: "text-amber-400",
    bg: "bg-amber-500/10",
    border: "border-amber-500/40",
    activeBg: "bg-amber-500",
  },
  {
    value: "coverage",
    label: "Couverture",
    description: "Maximise la couverture numérique",
    color: "text-emerald-400",
    bg: "bg-emerald-500/10",
    border: "border-emerald-500/40",
    activeBg: "bg-emerald-500",
  },
] as const;

const STRATEGY_META: Record<
  string,
  { label: string; icon: typeof Trophy; color: string; bg: string }
> = {
  top: {
    label: "Top Grilles",
    icon: Trophy,
    color: "text-amber-400",
    bg: "bg-amber-500/10",
  },
  portfolio: {
    label: "Portefeuille",
    icon: Layers,
    color: "text-emerald-400",
    bg: "bg-emerald-500/10",
  },
  wheeling: {
    label: "Système réduit",
    icon: Crown,
    color: "text-purple-400",
    bg: "bg-purple-500/10",
  },
};

function RecommendationCard({ rec }: { rec: BudgetRecommendation }) {
  const [expanded, setExpanded] = useState(false);
  const meta = STRATEGY_META[rec.strategy] ?? {
    label: rec.strategy,
    icon: Trophy,
    color: "text-gray-400",
    bg: "bg-gray-500/10",
  };
  const Icon = meta.icon;

  return (
    <div
      className={`rounded-xl border p-5 transition-all ${
        rec.is_recommended
          ? "border-accent-blue/50 bg-accent-blue/5 shadow-lg shadow-accent-blue/10 ring-1 ring-accent-blue/30"
          : "border-border-primary bg-bg-secondary hover:border-border-primary/80"
      }`}
    >
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <div
            className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-lg ${meta.bg} ${meta.color}`}
          >
            <Icon size={20} />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-base font-bold text-text-primary">
                {meta.label}
              </span>
              {rec.is_recommended && (
                <span className="rounded-full bg-accent-blue px-2.5 py-0.5 text-[11px] font-bold text-white uppercase tracking-wider">
                  Recommandé
                </span>
              )}
            </div>
            <p className="text-xs text-text-secondary mt-0.5 max-w-md">
              {rec.explanation}
            </p>
          </div>
        </div>
        <div className="text-right">
          <div className="text-xl font-bold text-accent-blue tabular-nums">
            {rec.total_cost.toFixed(2)} €
          </div>
          <div className="text-xs text-text-secondary">
            {rec.grid_count} grille{rec.grid_count > 1 ? "s" : ""}
          </div>
        </div>
      </div>

      {/* Metrics */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 mb-4">
        <MiniStat label="Grilles" value={String(rec.grid_count)} />
        {rec.avg_score != null && (
          <MiniStat label="Score moyen" value={rec.avg_score.toFixed(2)} />
        )}
        {rec.diversity_score != null && (
          <MiniStat
            label="Diversité"
            value={(rec.diversity_score * 100).toFixed(1) + "%"}
          />
        )}
        {rec.coverage_rate != null && (
          <MiniStat
            label="Couverture"
            value={(rec.coverage_rate * 100).toFixed(1) + "%"}
          />
        )}
      </div>

      {/* Gain scenarios */}
      <div className="grid grid-cols-3 gap-2 text-sm mb-4">
        <div className="rounded-lg bg-emerald-500/10 border border-emerald-500/20 p-2.5 text-center">
          <div className="text-[11px] font-medium text-emerald-400/80 uppercase tracking-wider">
            Optimiste
          </div>
          <div className="font-bold text-emerald-400 mt-0.5 tabular-nums">
            {rec.expected_gain.optimistic.toFixed(2)} €
          </div>
        </div>
        <div className="rounded-lg bg-amber-500/10 border border-amber-500/20 p-2.5 text-center">
          <div className="text-[11px] font-medium text-amber-400/80 uppercase tracking-wider">
            Moyen
          </div>
          <div className="font-bold text-amber-400 mt-0.5 tabular-nums">
            {rec.expected_gain.mean.toFixed(2)} €
          </div>
        </div>
        <div className="rounded-lg bg-red-500/10 border border-red-500/20 p-2.5 text-center">
          <div className="text-[11px] font-medium text-red-400/80 uppercase tracking-wider">
            Pessimiste
          </div>
          <div className="font-bold text-red-400 mt-0.5 tabular-nums">
            {rec.expected_gain.pessimistic.toFixed(2)} €
          </div>
        </div>
      </div>

      {/* Expandable grids */}
      <button
        onClick={() => setExpanded(!expanded)}
        className="flex items-center gap-1.5 text-sm font-medium text-accent-blue hover:text-accent-blue/80 transition-colors"
      >
        {expanded ? (
          <ChevronUp className="h-4 w-4" />
        ) : (
          <ChevronDown className="h-4 w-4" />
        )}
        {expanded ? "Masquer" : "Voir"} les {rec.grid_count} grilles
      </button>
      {expanded && (
        <div className="mt-3 max-h-64 overflow-y-auto rounded-lg border border-border-primary bg-bg-primary/50 p-3">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-text-secondary text-xs uppercase tracking-wider">
                <th className="text-left py-1.5">#</th>
                <th className="text-left py-1.5">Numéros</th>
                <th className="text-left py-1.5">Étoiles</th>
              </tr>
            </thead>
            <tbody>
              {rec.grids.map((g, i) => (
                <tr
                  key={i}
                  className="border-t border-border-primary/50 hover:bg-surface-hover/30"
                >
                  <td className="py-1.5 text-text-secondary tabular-nums">
                    {i + 1}
                  </td>
                  <td className="py-1.5 font-mono tabular-nums">
                    {g.numbers.join(" - ")}
                  </td>
                  <td className="py-1.5 font-mono text-amber-400 tabular-nums">
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
    <div className="rounded-lg bg-bg-primary/50 border border-border-primary/50 p-2.5 text-center">
      <div className="text-[11px] text-text-secondary uppercase tracking-wider">
        {label}
      </div>
      <div className="font-bold text-text-primary mt-0.5">{value}</div>
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

  const toggleNumber = useCallback(
    (n: number) => {
      setSelectedNumbers((prev) =>
        prev.includes(n)
          ? prev.filter((x) => x !== n)
          : [...prev, n].slice(0, 20),
      );
    },
    [],
  );

  const handleOptimize = () => {
    optimizeMutation.mutate(
      {
        budget,
        objective,
        numbers:
          useNumbers && selectedNumbers.length > 0
            ? selectedNumbers
            : undefined,
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

  const aiContext = useMemo(
    () => ({
      slug,
      budget,
      objective,
      strategies: result?.recommendations.map((r) => r.strategy) ?? [],
    }),
    [slug, budget, objective, result],
  );

  const isLoto = game?.slug.includes("loto");

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
          {
            term: "Top Grilles",
            definition:
              "Sélectionne les grilles avec les meilleurs scores individuels.",
          },
          {
            term: "Portefeuille",
            definition:
              "Ensemble diversifié de grilles minimisant le chevauchement.",
          },
          {
            term: "Système réduit",
            definition:
              "Couverture combinatoire garantissant un gain si vos numéros sont tirés (nécessite de sélectionner des numéros).",
          },
        ]}
      />

      {/* ── Step 1: Budget & Objective ── */}
      <div className="rounded-xl bg-surface p-5 space-y-5">
        <h2 className="text-lg font-semibold">1. Budget & Objectif</h2>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
          {/* Budget stepper */}
          <div className="space-y-2">
            <label className="text-sm font-medium text-text-secondary">
              Budget (€)
            </label>
            <div className="flex items-center gap-2">
              <div className="inline-flex items-center rounded-xl border border-border-primary bg-bg-primary overflow-hidden">
                <button
                  onClick={() => setBudget((b) => Math.max(1, b - 5))}
                  className="px-3 py-2.5 text-text-secondary hover:bg-surface-hover hover:text-text-primary transition-colors"
                  aria-label="Moins"
                >
                  <Minus size={14} />
                </button>
                <input
                  type="number"
                  min={1}
                  max={10000}
                  step={1}
                  value={budget}
                  onChange={(e) => setBudget(Number(e.target.value) || 1)}
                  className="w-20 bg-transparent text-center text-lg font-bold text-text-primary outline-none tabular-nums [appearance:textfield] [&::-webkit-inner-spin-button]:appearance-none [&::-webkit-outer-spin-button]:appearance-none"
                />
                <button
                  onClick={() => setBudget((b) => Math.min(10000, b + 5))}
                  className="px-3 py-2.5 text-text-secondary hover:bg-surface-hover hover:text-text-primary transition-colors"
                  aria-label="Plus"
                >
                  <Plus size={14} />
                </button>
              </div>
              <span className="text-lg font-bold text-text-secondary">€</span>
            </div>
          </div>

          {/* Objective selector — styled like Wheeling guarantee presets */}
          <div className="space-y-2">
            <label className="text-sm font-medium text-text-secondary">
              Objectif
            </label>
            <div className="flex flex-wrap gap-2">
              {OBJECTIVES.map((obj) => (
                <button
                  key={obj.value}
                  onClick={() => setObjective(obj.value)}
                  className={`flex-1 min-w-[100px] rounded-xl px-3 py-2.5 text-sm transition-all ${
                    objective === obj.value
                      ? `${obj.activeBg} text-white shadow-lg`
                      : `${obj.bg} border ${obj.border} ${obj.color} hover:brightness-125`
                  }`}
                >
                  <div className="font-semibold">{obj.label}</div>
                  <div
                    className={`text-xs mt-0.5 ${objective === obj.value ? "text-white/80" : "opacity-70"}`}
                  >
                    {obj.description}
                  </div>
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* ── Step 2: Optional number selection ── */}
      <div className="rounded-xl bg-surface p-5 space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold">
            2. Numéros favoris{" "}
            <span className="text-sm font-normal text-text-secondary">
              (optionnel)
            </span>
          </h2>
          <label className="relative inline-flex items-center cursor-pointer gap-2">
            <input
              type="checkbox"
              checked={useNumbers}
              onChange={(e) => setUseNumbers(e.target.checked)}
              className="sr-only peer"
            />
            <div className="w-9 h-5 bg-border-primary rounded-full peer peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-0.5 after:left-[2px] after:bg-white after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-accent-blue" />
            <span className="text-xs text-text-secondary">
              Sélectionner des numéros
            </span>
          </label>
        </div>

        {useNumbers && game && (
          <>
            <p className="text-xs text-text-secondary">
              Active la stratégie Système réduit. Sélectionnez au moins{" "}
              {game.numbers_drawn + 1} numéros (max 20) —{" "}
              <span className="font-semibold text-text-primary">
                {selectedNumbers.length} sélectionné
                {selectedNumbers.length > 1 ? "s" : ""}
              </span>
            </p>

            {/* 3D ball grid — same style as WheelingPage */}
            <div className="inline-grid grid-cols-10 gap-1.5 p-3 rounded-xl bg-surface-hover/40 border border-white/10">
              {Array.from(
                { length: game.max_number - game.min_number + 1 },
                (_, i) => {
                  const n = game.min_number + i;
                  const isSelected = selectedNumbers.includes(n);
                  return (
                    <button
                      key={n}
                      onClick={() => toggleNumber(n)}
                      className="w-10 h-10 rounded-full text-xs font-bold transition-all duration-150 flex items-center justify-center relative overflow-hidden cursor-pointer"
                      style={{
                        transform: isSelected ? "scale(1.15)" : "scale(1)",
                        opacity: isSelected ? 1 : 0.4,
                      }}
                    >
                      <span
                        className="absolute inset-0 rounded-full"
                        style={{
                          background: isLoto
                            ? "radial-gradient(circle at 35% 30%, #5ba3f5, #1a6dd4 55%, #0c4a9e 80%, #082f6a)"
                            : "radial-gradient(circle at 35% 30%, #f07070, #c62828 55%, #8e1a1a 80%, #5c1010)",
                          boxShadow: isSelected
                            ? isLoto
                              ? "0 0 12px 3px rgba(59,130,246,0.6), inset -2px -3px 5px rgba(0,0,0,0.35), inset 2px 2px 4px rgba(255,255,255,0.15)"
                              : "0 0 12px 3px rgba(220,38,38,0.6), inset -2px -3px 5px rgba(0,0,0,0.35), inset 2px 2px 4px rgba(255,255,255,0.15)"
                            : "inset -2px -3px 5px rgba(0,0,0,0.35), inset 2px 2px 4px rgba(255,255,255,0.15)",
                        }}
                      />
                      <span
                        className="absolute rounded-full"
                        style={{
                          width: "58%",
                          height: "58%",
                          background:
                            "radial-gradient(circle at 45% 40%, #ffffff, #e2e2e2 80%)",
                          boxShadow:
                            "inset 0 1px 2px rgba(0,0,0,0.08), 0 0 1px rgba(0,0,0,0.15)",
                        }}
                      />
                      {isSelected && (
                        <span
                          className="absolute inset-0 rounded-full"
                          style={{
                            border: "3px solid #fff",
                            boxShadow: "0 0 0 2px rgba(255,255,255,0.5)",
                          }}
                        />
                      )}
                      <span className="relative z-10 text-gray-900">{n}</span>
                    </button>
                  );
                },
              )}
            </div>

            {selectedNumbers.length > 0 && (
              <div className="text-sm text-text-secondary">
                Sélection :{" "}
                {[...selectedNumbers].sort((a, b) => a - b).join(", ")}
              </div>
            )}
          </>
        )}

        {!useNumbers && (
          <p className="text-xs text-text-secondary italic">
            Activez la sélection pour débloquer la stratégie Système réduit.
          </p>
        )}
      </div>

      {/* ── Launch button ── */}
      <button
        onClick={handleOptimize}
        disabled={optimizeMutation.isPending || budget < 1}
        className="flex items-center justify-center gap-2 w-full rounded-xl bg-accent-blue px-6 py-3.5 text-sm font-bold text-white shadow-lg shadow-accent-blue/25 hover:bg-accent-blue/90 hover:shadow-accent-blue/40 disabled:opacity-40 disabled:shadow-none disabled:cursor-not-allowed transition-all"
      >
        {optimizeMutation.isPending ? (
          <Loader2 size={18} className="animate-spin" />
        ) : (
          <Play size={18} />
        )}
        {optimizeMutation.isPending
          ? "Optimisation en cours…"
          : "Lancer l'optimisation"}
      </button>

      {/* ── Results ── */}
      {result && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold">
              Recommandations — {result.recommendations.length} stratégie
              {result.recommendations.length > 1 ? "s" : ""}
            </h2>
            {result.max_grids > 0 && (
              <span className="text-sm text-text-secondary tabular-nums">
                Budget : {result.budget.toFixed(2)} € — max {result.max_grids}{" "}
                grilles
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
        <div className="rounded-xl bg-surface p-5">
          <button
            onClick={() => setShowHistory(!showHistory)}
            className="flex items-center gap-2 text-lg font-semibold w-full text-left"
          >
            Historique
            {showHistory ? (
              <ChevronUp className="h-5 w-5" />
            ) : (
              <ChevronDown className="h-5 w-5" />
            )}
            <span className="text-sm font-normal text-text-secondary">
              ({history.length})
            </span>
          </button>
          {showHistory && (
            <div className="mt-3 space-y-2">
              {history.map((plan) => (
                <div
                  key={plan.id}
                  className="group flex items-center justify-between rounded-xl border border-border-primary bg-bg-secondary p-3.5 hover:border-accent-blue/30 transition-colors"
                >
                  <button
                    onClick={() => loadPlan(plan)}
                    className="text-left flex-1"
                  >
                    <div className="text-sm font-semibold text-text-primary">
                      {plan.budget.toFixed(2)} € — {plan.objective}
                    </div>
                    <div className="text-xs text-text-secondary mt-0.5">
                      {new Date(plan.created_at).toLocaleString("fr-FR")} —{" "}
                      {plan.recommendations.length} stratégies
                    </div>
                  </button>
                  <button
                    onClick={() => deleteMutation.mutate(plan.id)}
                    className="ml-2 rounded-lg p-2 text-red-400 opacity-0 group-hover:opacity-100 hover:bg-red-500/10 transition-all"
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
        buildContext={() => aiContext}
        dataKey={`budget-${result?.id ?? "none"}`}
      />
    </div>
  );
}
