import { useState, useMemo, useCallback } from "react";
import { useQuery } from "@tanstack/react-query";
import { Layers, Trash2, Download, ChevronDown, ChevronUp } from "lucide-react";

import AiAnalysisPanel from "@/components/common/AiAnalysisPanel";
import PageIntro from "@/components/common/PageIntro";
import { gameService } from "@/services/gameService";
import { useGameStore } from "@/stores/gameStore";
import {
  useWheelingPreview,
  useWheelingGenerate,
  useWheelingHistory,
  useDeleteWheelingSystem,
} from "@/hooks/useWheeling";
import type {
  WheelingGenerateResponse,
  WheelingSystemResponse,
  GainScenario,
} from "@/types/wheeling";

const GUARANTEE_PRESETS = [
  { value: 2, label: "Économique (t=2)", desc: "Couverture minimale, peu de grilles" },
  { value: 3, label: "Équilibré (t=3)", desc: "Bon compromis coût/couverture" },
  { value: 4, label: "Maximal (t=4)", desc: "Couverture étendue, plus de grilles" },
] as const;

export default function WheelingPage() {
  const slug = useGameStore((s) => s.currentGameSlug);
  const { data: game } = useQuery({
    queryKey: ["game", slug],
    queryFn: () => gameService.getBySlug(slug!),
    enabled: !!slug,
  });

  // Selection state
  const [selectedNumbers, setSelectedNumbers] = useState<number[]>([]);
  const [selectedStars, setSelectedStars] = useState<number[]>([]);
  const [guarantee, setGuarantee] = useState(3);

  // Results
  const [result, setResult] = useState<WheelingGenerateResponse | null>(null);
  const [showHistory, setShowHistory] = useState(false);

  // Mutations
  const previewMutation = useWheelingPreview();
  const generateMutation = useWheelingGenerate();
  const { data: history } = useWheelingHistory();
  const deleteMutation = useDeleteWheelingSystem();

  const k = game?.numbers_drawn ?? 5;
  const maxGuarantee = k;
  const starLabel = game?.star_name ?? "étoile";

  // Number grid
  const toggleNumber = useCallback(
    (n: number) => {
      setSelectedNumbers((prev) =>
        prev.includes(n) ? prev.filter((x) => x !== n) : prev.length < 20 ? [...prev, n] : prev,
      );
      setResult(null);
    },
    [],
  );

  const toggleStar = useCallback(
    (s: number) => {
      setSelectedStars((prev) =>
        prev.includes(s) ? prev.filter((x) => x !== s) : prev.length < 6 ? [...prev, s] : prev,
      );
      setResult(null);
    },
    [],
  );

  const canPreview = selectedNumbers.length >= k + 1 && guarantee >= 2 && guarantee <= maxGuarantee;

  const handlePreview = () => {
    if (!canPreview) return;
    previewMutation.mutate({
      numbers: selectedNumbers,
      stars: selectedStars.length > 0 ? selectedStars : null,
      guarantee,
    });
  };

  const handleGenerate = () => {
    if (!canPreview) return;
    generateMutation.mutate(
      {
        numbers: selectedNumbers,
        stars: selectedStars.length > 0 ? selectedStars : null,
        guarantee,
      },
      { onSuccess: (data) => setResult(data) },
    );
  };

  const handleLoadSystem = (system: WheelingSystemResponse) => {
    setSelectedNumbers(system.selected_numbers);
    setSelectedStars(system.selected_stars ?? []);
    setGuarantee(system.guarantee_level);
    setResult({
      id: system.id,
      grids: system.grids,
      grid_count: system.grid_count,
      total_cost: system.total_cost,
      coverage_rate: system.coverage_rate,
      reduction_rate: system.reduction_rate,
      total_t_combinations: 0,
      full_wheel_size: 0,
      computation_time_ms: 0,
      gain_scenarios: [],
      number_distribution: {},
    });
    setShowHistory(false);
  };

  const exportCSV = () => {
    if (!result) return;
    const header = "Grille,Numéros,Étoiles\n";
    const rows = result.grids
      .map(
        (g, i) =>
          `${i + 1},"${g.numbers.join("-")}","${g.stars?.join("-") ?? ""}"`,
      )
      .join("\n");
    const blob = new Blob([header + rows], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `wheeling_system_t${guarantee}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const aiContext = useMemo(
    () => ({
      selected_numbers: selectedNumbers,
      selected_stars: selectedStars,
      guarantee,
      grid_count: result?.grid_count,
      coverage_rate: result?.coverage_rate,
      total_cost: result?.total_cost,
      reduction_rate: result?.reduction_rate,
    }),
    [selectedNumbers, selectedStars, guarantee, result],
  );

  if (!game) {
    return <div className="p-6 text-text-secondary">Chargement du jeu...</div>;
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold flex items-center gap-2">
        <Layers className="h-7 w-7 text-accent-blue" />
        Système réduit (Wheeling)
      </h1>

      <PageIntro
        storageKey="wheeling"
        description="Sélectionnez vos numéros favoris et générez un système réduit optimisé qui garantit une couverture combinatoire maximale avec un minimum de grilles. Le système utilise un algorithme de covering design C(n,k,t)."
        tip="Plus vous sélectionnez de numéros, plus le système nécessitera de grilles. Commencez avec 8-10 numéros pour une première exploration."
        terms={[
          { term: "Covering design C(n,k,t)", definition: "Ensemble minimal de grilles de k numéros couvrant toutes les t-combinaisons parmi n numéros sélectionnés." },
          { term: "Garantie t", definition: "Niveau de sous-combinaison garanti : si t numéros parmi vos sélectionnés sont tirés, au moins une grille les contient." },
          { term: "Full wheel", definition: "Toutes les combinaisons C(n,k) — exhaustif mais très coûteux." },
          { term: "Taux de réduction", definition: "Pourcentage d'économie par rapport au full wheel." },
        ]}
      />

      {/* ── Step 1: Number Selection ── */}
      <div className="rounded-xl bg-surface p-5 space-y-4">
        <h2 className="text-lg font-semibold">
          1. Sélection des numéros
          <span className="ml-2 text-sm font-normal text-text-secondary">
            ({selectedNumbers.length}/{game.max_number} sélectionnés, min {k + 1})
          </span>
        </h2>

        {/* Lottery ticket layout */}
        <div className="flex flex-col sm:flex-row items-start gap-4">
          {/* Main number grid — 10 columns like a real lottery ticket */}
          <div>
            <h3 className="text-sm font-semibold uppercase tracking-wide text-accent-blue mb-3">
              Numéros
            </h3>
            <div className="inline-grid grid-cols-10 gap-1.5 p-3 rounded-xl bg-surface-hover/40 border border-white/10">
              {Array.from({ length: game.max_number - game.min_number + 1 }, (_, i) => {
                const n = game.min_number + i;
                const isSelected = selectedNumbers.includes(n);
                return (
                  <button
                    key={n}
                    onClick={() => toggleNumber(n)}
                    className={`
                      w-9 h-9 rounded-full text-xs font-bold transition-all duration-150
                      flex items-center justify-center
                      ${isSelected
                        ? "bg-accent-blue text-white shadow-lg shadow-accent-blue/40 scale-110 ring-2 ring-accent-blue/50"
                        : "bg-white/10 text-text-primary hover:bg-accent-blue/20 hover:scale-105"
                      }
                    `}
                  >
                    {n}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Stars / Numéro Chance — side panel */}
          {game.stars_pool && (
            <div>
              <h3 className="text-sm font-semibold uppercase tracking-wide mb-3" style={{
                color: game.slug === "loto" ? "#e53e3e" : "#d69e2e",
              }}>
                {starLabel}s
                <span className="ml-1 font-normal normal-case text-text-secondary">
                  ({selectedStars.length} sel.)
                </span>
              </h3>
              <div className={`inline-grid gap-1.5 p-3 rounded-xl border ${game.stars_pool <= 10 ? "grid-cols-5" : "grid-cols-4"}`} style={{
                backgroundColor: game.slug === "loto" ? "rgba(229,62,62,0.05)" : "rgba(214,158,46,0.05)",
                borderColor: game.slug === "loto" ? "rgba(229,62,62,0.2)" : "rgba(214,158,46,0.2)",
              }}>
                {Array.from({ length: game.stars_pool }, (_, i) => {
                  const s = i + 1;
                  const isSelected = selectedStars.includes(s);
                  const isLoto = game.slug === "loto";
                  return (
                    <button
                      key={s}
                      onClick={() => toggleStar(s)}
                      className={`
                        w-9 h-9 rounded-full text-xs font-bold transition-all duration-150
                        flex items-center justify-center
                        ${isSelected
                          ? isLoto
                            ? "bg-red-500 text-white shadow-lg shadow-red-500/40 scale-110 ring-2 ring-red-500/50"
                            : "bg-yellow-500 text-white shadow-lg shadow-yellow-500/40 scale-110 ring-2 ring-yellow-500/50"
                          : isLoto
                            ? "bg-red-500/10 text-red-400 hover:bg-red-500/20 hover:scale-105"
                            : "bg-yellow-500/10 text-yellow-400 hover:bg-yellow-500/20 hover:scale-105"
                        }
                      `}
                    >
                      {s}
                    </button>
                  );
                })}
              </div>
            </div>
          )}
        </div>

        {selectedNumbers.length > 0 && (
          <div className="text-sm text-text-secondary">
            Numéros : {[...selectedNumbers].sort((a, b) => a - b).join(", ")}
            {selectedStars.length > 0 && (
              <> — {starLabel}s : {[...selectedStars].sort((a, b) => a - b).join(", ")}</>
            )}
          </div>
        )}
      </div>

      {/* ── Step 2: Configuration ── */}
      <div className="rounded-xl bg-surface p-5 space-y-4">
        <h2 className="text-lg font-semibold">2. Configuration</h2>

        <div className="flex flex-wrap gap-3">
          {GUARANTEE_PRESETS.filter((p) => p.value <= maxGuarantee).map((preset) => (
            <button
              key={preset.value}
              onClick={() => { setGuarantee(preset.value); setResult(null); }}
              className={`
                px-4 py-2 rounded-lg text-sm transition-all
                ${guarantee === preset.value
                  ? "bg-accent-blue text-white"
                  : "bg-surface-hover text-text-primary hover:bg-accent-blue/20"
                }
              `}
            >
              <div className="font-medium">{preset.label}</div>
              <div className="text-xs opacity-75">{preset.desc}</div>
            </button>
          ))}
        </div>

        <div className="flex gap-3">
          <button
            onClick={handlePreview}
            disabled={!canPreview || previewMutation.isPending}
            className="px-4 py-2 rounded-lg bg-surface-hover text-text-primary hover:bg-accent-blue/20 disabled:opacity-50 text-sm"
          >
            {previewMutation.isPending ? "Estimation..." : "Estimer"}
          </button>
          <button
            onClick={handleGenerate}
            disabled={!canPreview || generateMutation.isPending}
            className="px-4 py-2 rounded-lg bg-accent-blue text-white hover:bg-accent-blue/80 disabled:opacity-50 text-sm font-medium"
          >
            {generateMutation.isPending ? "Génération..." : "Générer le système"}
          </button>
        </div>

        {/* Preview results */}
        {previewMutation.data && !result && (
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-3">
            <StatCard label="Grilles estimées" value={previewMutation.data.estimated_grid_count} />
            <StatCard label="Coût estimé" value={`${previewMutation.data.estimated_cost.toFixed(2)} €`} />
            <StatCard label="Combinaisons t" value={previewMutation.data.total_t_combinations} />
            <StatCard
              label="Réduction vs full"
              value={`${previewMutation.data.reduction_rate_estimate.toFixed(1)}%`}
            />
          </div>
        )}
      </div>

      {/* ── Step 3: Results ── */}
      {result && (
        <div className="rounded-xl bg-surface p-5 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold">3. Résultats</h2>
            <button
              onClick={exportCSV}
              className="flex items-center gap-1 text-sm text-accent-blue hover:underline"
            >
              <Download className="h-4 w-4" /> Exporter CSV
            </button>
          </div>

          {/* Metrics */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <StatCard label="Grilles" value={result.grid_count} />
            <StatCard label="Coût total" value={`${result.total_cost.toFixed(2)} €`} />
            <StatCard
              label="Couverture"
              value={`${(result.coverage_rate * 100).toFixed(1)}%`}
              highlight={result.coverage_rate === 1}
            />
            <StatCard label="Réduction" value={`${result.reduction_rate.toFixed(1)}%`} />
          </div>

          {result.computation_time_ms > 0 && (
            <p className="text-xs text-text-secondary">
              Calculé en {result.computation_time_ms.toFixed(0)} ms
            </p>
          )}

          {/* Grids table */}
          <div className="overflow-x-auto max-h-96">
            <table className="w-full text-sm">
              <thead className="sticky top-0 bg-surface">
                <tr className="border-b border-border text-left text-text-secondary">
                  <th className="py-2 px-3 w-16">#</th>
                  <th className="py-2 px-3">Numéros</th>
                  {game?.stars_pool && <th className="py-2 px-3">{starLabel}s</th>}
                </tr>
              </thead>
              <tbody>
                {result.grids.map((g, i) => (
                  <tr key={i} className="border-b border-border/50 hover:bg-surface-hover">
                    <td className="py-1.5 px-3 text-text-secondary">{i + 1}</td>
                    <td className="py-1.5 px-3 font-mono">
                      {g.numbers.join(" - ")}
                    </td>
                    {game?.stars_pool && (
                      <td className="py-1.5 px-3 font-mono text-yellow-500">
                        {g.stars?.join(" - ") ?? "—"}
                      </td>
                    )}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Coverage Matrix (heatmap) */}
          {result.number_distribution && Object.keys(result.number_distribution).length > 0 && (
            <div>
              <h3 className="text-sm font-semibold mb-2">Distribution des numéros</h3>
              <div className="flex flex-wrap gap-1.5">
                {[...selectedNumbers].sort((a, b) => a - b).map((n) => {
                  const count = result.number_distribution[n] ?? 0;
                  const maxCount = Math.max(...Object.values(result.number_distribution));
                  const intensity = maxCount > 0 ? count / maxCount : 0;
                  return (
                    <div
                      key={n}
                      className="w-10 h-10 rounded-lg flex flex-col items-center justify-center text-xs"
                      style={{
                        backgroundColor: `rgba(59, 130, 246, ${0.1 + intensity * 0.7})`,
                        color: intensity > 0.5 ? "white" : "inherit",
                      }}
                    >
                      <span className="font-medium">{n}</span>
                      <span className="text-[10px] opacity-75">×{count}</span>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Gain Scenarios */}
          {result.gain_scenarios.length > 0 && (
            <GainScenariosTable scenarios={result.gain_scenarios} />
          )}
        </div>
      )}

      {/* ── History ── */}
      <div className="rounded-xl bg-surface p-5 space-y-3">
        <button
          onClick={() => setShowHistory(!showHistory)}
          className="flex items-center gap-2 text-lg font-semibold w-full text-left"
        >
          Historique des systèmes
          {showHistory ? <ChevronUp className="h-5 w-5" /> : <ChevronDown className="h-5 w-5" />}
          {history && (
            <span className="text-sm font-normal text-text-secondary">
              ({history.length})
            </span>
          )}
        </button>

        {showHistory && history && (
          <div className="space-y-2">
            {history.length === 0 && (
              <p className="text-sm text-text-secondary">Aucun système sauvegardé.</p>
            )}
            {history.map((sys) => (
              <div
                key={sys.id}
                className="flex items-center justify-between p-3 rounded-lg bg-surface-hover"
              >
                <div
                  className="flex-1 cursor-pointer"
                  onClick={() => handleLoadSystem(sys)}
                >
                  <div className="text-sm font-medium">
                    t={sys.guarantee_level} — {sys.grid_count} grilles — {sys.total_cost.toFixed(2)} €
                  </div>
                  <div className="text-xs text-text-secondary">
                    Numéros : {sys.selected_numbers.join(", ")} —{" "}
                    {new Date(sys.created_at).toLocaleDateString("fr-FR")}
                  </div>
                </div>
                <button
                  onClick={() => deleteMutation.mutate(sys.id)}
                  className="p-1.5 rounded hover:bg-red-500/20 text-red-400"
                >
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* AI Analysis */}
      <AiAnalysisPanel
        topic="wheeling"
        buildContext={() => aiContext}
        dataKey={`${selectedNumbers.join(",")}-${guarantee}-${result?.grid_count ?? 0}`}
        description="Demandez une analyse experte de votre système réduit, incluant des conseils sur le choix des numéros et le niveau de garantie."
      />
    </div>
  );
}

// ── Subcomponents ──

function StatCard({
  label,
  value,
  highlight,
}: {
  label: string;
  value: string | number;
  highlight?: boolean;
}) {
  return (
    <div
      className={`rounded-lg p-3 ${
        highlight ? "bg-green-500/10 border border-green-500/30" : "bg-surface-hover"
      }`}
    >
      <div className="text-xs text-text-secondary">{label}</div>
      <div className={`text-lg font-bold ${highlight ? "text-green-400" : ""}`}>
        {value}
      </div>
    </div>
  );
}

function GainScenariosTable({ scenarios }: { scenarios: GainScenario[] }) {
  return (
    <div>
      <h3 className="text-sm font-semibold mb-2">Scénarios de gains</h3>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-border text-left text-text-secondary">
              <th className="py-2 px-2">Rang</th>
              <th className="py-2 px-2">Match</th>
              <th className="py-2 px-2">Gain moyen</th>
              <th className="py-2 px-2 text-green-400">Optimiste</th>
              <th className="py-2 px-2 text-yellow-400">Moyen</th>
              <th className="py-2 px-2 text-red-400">Pessimiste</th>
            </tr>
          </thead>
          <tbody>
            {scenarios.map((s) => (
              <tr key={s.rank} className="border-b border-border/50">
                <td className="py-1.5 px-2 font-medium">{s.name}</td>
                <td className="py-1.5 px-2 text-text-secondary">
                  {s.match_numbers}n{s.match_stars > 0 ? `+${s.match_stars}★` : ""}
                </td>
                <td className="py-1.5 px-2">{s.avg_prize.toLocaleString("fr-FR")} €</td>
                <td className="py-1.5 px-2 text-green-400">
                  {s.matching_grids_best}g → {s.potential_gain_best.toLocaleString("fr-FR")} €
                </td>
                <td className="py-1.5 px-2 text-yellow-400">
                  {s.matching_grids_avg.toFixed(1)}g → {s.potential_gain_avg.toLocaleString("fr-FR")} €
                </td>
                <td className="py-1.5 px-2 text-red-400">
                  {s.matching_grids_worst}g → {s.potential_gain_worst.toLocaleString("fr-FR")} €
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
