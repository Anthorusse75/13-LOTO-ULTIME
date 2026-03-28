import InfoTooltip from "@/components/common/InfoTooltip";
import LoadingSpinner from "@/components/common/LoadingSpinner";
import DrawBalls from "@/components/draws/DrawBalls";
import ScoreBar from "@/components/grids/ScoreBar";
import {
  useCompareRandom,
  useMonteCarloGrid,
  useStability,
} from "@/hooks/useSimulation";
import { gameService } from "@/services/gameService";
import { useGameStore } from "@/stores/gameStore";
import { useQuery } from "@tanstack/react-query";
import {
  BarChart3,
  Dices,
  Loader2,
  ShieldCheck,
  TrendingUp,
} from "lucide-react";
import { useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

type SimTab = "monte-carlo" | "stability" | "comparison";

export default function SimulationPage() {
  const [tab, setTab] = useState<SimTab>("monte-carlo");
  const [numbersInput, setNumbersInput] = useState("");
  const [nSim, setNSim] = useState(10000);

  const slug = useGameStore((s) => s.currentGameSlug);
  const { data: game } = useQuery({
    queryKey: ["game", slug],
    queryFn: () => gameService.getBySlug(slug!),
    enabled: !!slug,
  });

  const mcMutation = useMonteCarloGrid();
  const stabMutation = useStability();
  const compMutation = useCompareRandom();

  const parseNumbers = (): number[] =>
    numbersInput
      .split(/[\s,;]+/)
      .map(Number)
      .filter((n) => !isNaN(n) && n > 0);

  const isValid = game && parseNumbers().length === game.numbers_drawn;

  const tabs: { key: SimTab; label: string; icon: React.ReactNode }[] = [
    { key: "monte-carlo", label: "Monte Carlo", icon: <Dices size={14} /> },
    { key: "stability", label: "Stabilité", icon: <ShieldCheck size={14} /> },
    { key: "comparison", label: "Comparaison", icon: <BarChart3 size={14} /> },
  ];

  // Monte Carlo
  const handleMC = () => {
    mcMutation.mutate({ numbers: parseNumbers(), n_simulations: nSim });
  };
  const mc = mcMutation.data;
  const mcChartData = mc
    ? Object.entries(mc.match_distribution)
        .map(([k, v]) => ({ matches: Number(k), count: v }))
        .sort((a, b) => a.matches - b.matches)
    : [];

  // Stability (backend caps at 1000)
  const handleStability = () => {
    stabMutation.mutate({ numbers: parseNumbers(), n_bootstrap: Math.min(nSim, 1000) });
  };
  const stab = stabMutation.data;

  // Comparison
  const handleComparison = () => {
    compMutation.mutate({
      numbers: parseNumbers(),
      n_random: nSim,
    });
  };
  const comp = compMutation.data;

  const isPending =
    mcMutation.isPending || stabMutation.isPending || compMutation.isPending;

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Simulation</h1>

      {/* Input section */}
      <div className="bg-surface rounded-lg border border-border p-6">
        <h2 className="text-sm font-semibold mb-4">Grille à simuler</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          <div>
            <label className="text-xs text-text-secondary block mb-1">
              Numéros ({game?.numbers_drawn ?? "?"} attendus, séparés par
              virgule)
            </label>
            <input
              type="text"
              value={numbersInput}
              onChange={(e) => setNumbersInput(e.target.value)}
              placeholder={`ex: 3, 12, 25, 34, 49`}
              className="w-full bg-surface-hover border border-border rounded-md px-3 py-2 text-sm font-mono focus:outline-none focus:ring-1 focus:ring-accent-blue"
            />
            {numbersInput && !isValid && (
              <p className="text-xs text-accent-red mt-1">
                Saisissez exactement {game?.numbers_drawn} numéros entre{" "}
                {game?.min_number} et {game?.max_number}
              </p>
            )}
          </div>
          <div>
            <label className="text-xs text-text-secondary block mb-1">
              Nombre de simulations
            </label>
            <input
              type="number"
              min={1000}
              max={100000}
              step={1000}
              value={nSim}
              onChange={(e) => setNSim(Number(e.target.value))}
              className="w-full bg-surface-hover border border-border rounded-md px-3 py-2 text-sm font-mono focus:outline-none focus:ring-1 focus:ring-accent-blue"
            />
          </div>
        </div>
        {isValid && (
          <div className="flex items-center gap-2 text-sm text-text-secondary">
            <span>Numéros sélectionnés :</span>
            <DrawBalls numbers={parseNumbers()} size="sm" />
          </div>
        )}
      </div>

      {/* Tabs */}
      <div className="flex gap-1 border-b border-border pb-px">
        {tabs.map((t) => (
          <button
            key={t.key}
            onClick={() => setTab(t.key)}
            className={`px-4 py-2 text-sm flex items-center gap-1.5 rounded-t-md transition-colors ${
              tab === t.key
                ? "bg-surface text-text-primary border border-border border-b-transparent -mb-px"
                : "text-text-secondary hover:text-text-primary"
            }`}
          >
            {t.icon}
            {t.label}
          </button>
        ))}
      </div>

      {/* Tab content */}
      {tab === "monte-carlo" && (
        <div className="space-y-4">
          <button
            onClick={handleMC}
            disabled={!isValid || isPending}
            className="px-6 py-2 bg-accent-blue text-white rounded-md text-sm font-medium hover:bg-accent-blue/90 disabled:opacity-50 flex items-center gap-2"
          >
            {mcMutation.isPending && (
              <Loader2 size={16} className="animate-spin" />
            )}
            Lancer Monte Carlo
          </button>

          {!mc && !mcMutation.isPending && (
            <div className="bg-surface rounded-lg border border-border p-6 text-center">
              <p className="text-text-secondary text-sm">
                Saisissez une grille et lancez la simulation Monte Carlo pour
                estimer vos chances de correspondance.
              </p>
            </div>
          )}

          {mcMutation.isPending && (
            <LoadingSpinner message="Simulation en cours..." />
          )}

          {mc && (
            <>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                <div className="bg-surface rounded-lg border border-border p-4">
                  <p className="text-xs text-text-secondary flex items-center">
                    Simulations
                    <InfoTooltip text="Nombre total de tirages simulés aléatoirement." />
                  </p>
                  <p className="font-mono text-lg">
                    {mc.n_simulations.toLocaleString()}
                  </p>
                </div>
                <div className="bg-surface rounded-lg border border-border p-4">
                  <p className="text-xs text-text-secondary flex items-center">
                    Moyenne correspondances
                    <InfoTooltip text="Nombre moyen de numéros de votre grille retrouvés dans les tirages simulés." />
                  </p>
                  <p className="font-mono text-lg text-accent-green">
                    {mc.avg_matches.toFixed(2)}
                  </p>
                </div>
                <div className="bg-surface rounded-lg border border-border p-4">
                  <p className="text-xs text-text-secondary flex items-center">
                    Espérance théorique
                    <InfoTooltip text="Nombre de correspondances attendu par les mathématiques pures (distribution hypergéométrique)." />
                  </p>
                  <p className="font-mono text-lg">
                    {mc.expected_matches.toFixed(2)}
                  </p>
                </div>
              </div>

              <div className="bg-surface rounded-lg border border-border p-4">
                <h3 className="text-sm font-semibold mb-3">
                  Distribution des correspondances
                </h3>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={mcChartData}>
                    <CartesianGrid
                      strokeDasharray="3 3"
                      stroke="var(--color-border)"
                    />
                    <XAxis
                      dataKey="matches"
                      tick={{
                        fill: "var(--color-text-secondary)",
                        fontSize: 12,
                      }}
                      label={{
                        value: "Correspondances",
                        position: "bottom",
                        fill: "var(--color-text-secondary)",
                      }}
                    />
                    <YAxis
                      tick={{
                        fill: "var(--color-text-secondary)",
                        fontSize: 12,
                      }}
                    />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: "var(--color-surface)",
                        border: "1px solid var(--color-border)",
                        borderRadius: "6px",
                      }}
                    />
                    <Bar
                      dataKey="count"
                      fill="var(--color-accent-blue)"
                      radius={[4, 4, 0, 0]}
                    />
                  </BarChart>
                </ResponsiveContainer>
                <p className="text-xs text-text-secondary mt-2">
                  Distribution des correspondances observées lors de la
                  simulation Monte Carlo.
                </p>
              </div>

              <p className="text-xs text-text-secondary">
                Temps: {mc.computation_time_ms.toFixed(0)}ms
              </p>
            </>
          )}
        </div>
      )}

      {tab === "stability" && (
        <div className="space-y-4">
          <button
            onClick={handleStability}
            disabled={!isValid || isPending}
            className="px-6 py-2 bg-accent-purple text-white rounded-md text-sm font-medium hover:bg-accent-purple/90 disabled:opacity-50 flex items-center gap-2"
          >
            {stabMutation.isPending && (
              <Loader2 size={16} className="animate-spin" />
            )}
            Analyser la stabilité
          </button>
          {nSim > 1000 && (
            <p className="text-xs text-text-secondary">Bootstrap limité à 1 000 itérations.</p>
          )}

          {stabMutation.isError && (
            <div className="bg-surface rounded-lg border border-accent-red/30 p-4">
              <p className="text-accent-red text-sm">Erreur lors de l'analyse de stabilité. Veuillez réessayer.</p>
            </div>
          )}

          {!stab && !stabMutation.isPending && !stabMutation.isError && (
            <div className="bg-surface rounded-lg border border-border p-6 text-center">
              <p className="text-text-secondary text-sm">
                Testez la robustesse de votre grille par bootstrap : entrez vos
                numéros et lancez l'analyse de stabilité.
              </p>
            </div>
          )}

          {stabMutation.isPending && (
            <LoadingSpinner message="Bootstrap en cours..." />
          )}

          {stab && (
            <>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="bg-surface rounded-lg border border-border p-4">
                  <p className="text-xs text-text-secondary flex items-center">
                    Score moyen
                    <InfoTooltip text="Score moyen obtenu par bootstrap (ré-échantillonnage répété de l'historique)." />
                  </p>
                  <p className="font-mono text-lg text-accent-green">
                    {stab.mean_score.toFixed(2)}
                  </p>
                </div>
                <div className="bg-surface rounded-lg border border-border p-4">
                  <p className="text-xs text-text-secondary flex items-center">
                    Écart-type
                    <InfoTooltip text="Mesure de dispersion du score : un écart-type faible indique une grille stable." />
                  </p>
                  <p className="font-mono text-lg">
                    {stab.std_score.toFixed(3)}
                  </p>
                </div>
                <div className="bg-surface rounded-lg border border-border p-4">
                  <p className="text-xs text-text-secondary flex items-center">
                    CV
                    <InfoTooltip text="Coefficient de variation = écart-type / moyenne. Plus il est bas, plus la grille est stable." />
                  </p>
                  <p className="font-mono text-lg">
                    {(stab.cv * 100).toFixed(1)}%
                  </p>
                </div>
                <div className="bg-surface rounded-lg border border-border p-4">
                  <p className="text-xs text-text-secondary">Stabilité</p>
                  <ScoreBar value={stab.stability} max={1} label="Stabilité" />
                </div>
              </div>

              <div className="bg-surface rounded-lg border border-border p-4">
                <h3 className="text-sm font-semibold mb-3">
                  Intervalle de confiance (95%)
                </h3>
                <div className="flex items-center gap-4">
                  <p className="font-mono text-accent-red">
                    {stab.ci_95_low.toFixed(3)}
                  </p>
                  <div className="flex-1 h-3 bg-surface-hover rounded-full relative overflow-hidden">
                    <div
                      className="absolute h-full bg-gradient-to-r from-accent-red via-accent-green to-accent-red rounded-full"
                      style={{
                        left: `${(stab.ci_95_low / stab.max_score) * 100}%`,
                        right: `${100 - (stab.ci_95_high / stab.max_score) * 100}%`,
                      }}
                    />
                  </div>
                  <p className="font-mono text-accent-green">
                    {stab.ci_95_high.toFixed(3)}
                  </p>
                </div>
                <div className="flex justify-between mt-2 text-xs text-text-secondary">
                  <span>Min: {stab.min_score.toFixed(3)}</span>
                  <span>Max: {stab.max_score.toFixed(3)}</span>
                </div>
              </div>

              <p className="text-xs text-text-secondary">
                Temps: {stab.computation_time_ms.toFixed(0)}ms
              </p>
            </>
          )}
        </div>
      )}

      {tab === "comparison" && (
        <div className="space-y-4">
          <button
            onClick={handleComparison}
            disabled={!isValid || isPending}
            className="px-6 py-2 bg-accent-green text-white rounded-md text-sm font-medium hover:bg-accent-green/90 disabled:opacity-50 flex items-center gap-2"
          >
            {compMutation.isPending && (
              <Loader2 size={16} className="animate-spin" />
            )}
            Comparer au hasard
          </button>

          {!comp && !compMutation.isPending && (
            <div className="bg-surface rounded-lg border border-border p-6 text-center">
              <p className="text-text-secondary text-sm">
                Comparez le score de votre grille à celui de grilles générées
                aléatoirement pour évaluer sa qualité relative.
              </p>
            </div>
          )}

          {compMutation.isPending && (
            <LoadingSpinner message="Comparaison en cours..." />
          )}

          {comp && (
            <>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                <div className="bg-surface rounded-lg border border-border p-4">
                  <p className="text-xs text-text-secondary">
                    Score de la grille
                  </p>
                  <p className="font-mono text-lg text-accent-green">
                    {comp.grid_score.toFixed(3)}
                  </p>
                </div>
                <div className="bg-surface rounded-lg border border-border p-4">
                  <p className="text-xs text-text-secondary">
                    Moyenne aléatoire
                  </p>
                  <p className="font-mono text-lg">
                    {comp.random_mean.toFixed(3)}
                  </p>
                </div>
                <div className="bg-surface rounded-lg border border-border p-4">
                  <p className="text-xs text-text-secondary">
                    Écart-type aléatoire
                  </p>
                  <p className="font-mono text-lg">
                    {comp.random_std.toFixed(3)}
                  </p>
                </div>
              </div>

              <div className="bg-surface rounded-lg border border-border p-4">
                <h3 className="text-sm font-semibold mb-3">
                  Position relative
                </h3>
                <div className="flex items-center gap-4 mb-4">
                  <TrendingUp size={20} className="text-accent-blue" />
                  <div className="flex-1">
                    <div className="flex justify-between text-xs text-text-secondary mb-1">
                      <span>Percentile</span>
                      <span className="font-mono">
                        {comp.percentile.toFixed(1)}%
                      </span>
                    </div>
                    <div className="h-4 bg-surface-hover rounded-full overflow-hidden">
                      <div
                        className="h-full rounded-full transition-all"
                        style={{
                          width: `${comp.percentile}%`,
                          backgroundColor:
                            comp.percentile >= 80
                              ? "var(--color-accent-green)"
                              : comp.percentile >= 50
                                ? "var(--color-accent-yellow)"
                                : "var(--color-accent-red)",
                        }}
                      />
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-4">
                  <BarChart3 size={20} className="text-accent-purple" />
                  <div>
                    <p className="text-sm">
                      Z-score:{" "}
                      <span
                        className={`font-mono font-semibold ${
                          comp.z_score > 1
                            ? "text-accent-green"
                            : comp.z_score < -1
                              ? "text-accent-red"
                              : "text-text-primary"
                        }`}
                      >
                        {comp.z_score > 0 ? "+" : ""}
                        {comp.z_score.toFixed(2)}
                      </span>
                    </p>
                    <p className="text-xs text-text-secondary">
                      {comp.z_score > 2
                        ? "Bien au-dessus de la moyenne"
                        : comp.z_score > 1
                          ? "Au-dessus de la moyenne"
                          : comp.z_score > -1
                            ? "Dans la moyenne"
                            : "En-dessous de la moyenne"}
                    </p>
                  </div>
                </div>
              </div>

              <p className="text-xs text-text-secondary">
                Temps: {comp.computation_time_ms.toFixed(0)}ms
              </p>
            </>
          )}
        </div>
      )}
    </div>
  );
}
