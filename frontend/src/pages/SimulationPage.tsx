import AiAnalysisPanel from "@/components/common/AiAnalysisPanel";
import ExplanationPanel from "@/components/common/ExplanationPanel";
import InfoTooltip from "@/components/common/InfoTooltip";
import LoadingSpinner from "@/components/common/LoadingSpinner";
import PageIntro from "@/components/common/PageIntro";
import DrawBalls from "@/components/draws/DrawBalls";
import ScoreBar from "@/components/grids/ScoreBar";
import SaveButton from "@/components/history/SaveButton";
import { useGenerateGrids } from "@/hooks/useGrids";
import {
  useCompareRandom,
  useMonteCarloGrid,
  useStability,
} from "@/hooks/useSimulation";
import { gameService } from "@/services/gameService";
import { useGameStore } from "@/stores/gameStore";
import { OPTIMIZATION_METHODS } from "@/utils/constants";
import { formatScore } from "@/utils/formatters";
import { useQuery } from "@tanstack/react-query";
import {
  BarChart3,
  Dices,
  Loader2,
  ShieldCheck,
  TrendingUp,
  Trophy,
} from "lucide-react";
import { useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
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

  // Strategy comparison
  const [stratA, setStratA] = useState("genetic");
  const [stratB, setStratB] = useState("annealing");
  const [stratCount, setStratCount] = useState(10);
  const genAMutation = useGenerateGrids();
  const genBMutation = useGenerateGrids();

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
    stabMutation.mutate({
      numbers: parseNumbers(),
      n_bootstrap: Math.min(nSim, 1000),
    });
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

  // Strategy comparison
  const handleStratCompare = () => {
    genAMutation.mutate({
      count: stratCount,
      method: stratA,
      profile: "equilibre",
    });
    genBMutation.mutate({
      count: stratCount,
      method: stratB,
      profile: "equilibre",
    });
  };

  const isPending =
    mcMutation.isPending || stabMutation.isPending || compMutation.isPending;

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Simulation</h1>

      <PageIntro
        storageKey="simulation"
        description="Cette page est votre laboratoire d'expérimentation ! Vous pouvez tester n'importe quelle grille et voir comment elle se comporte. C'est comme avoir un simulateur de vol pour vos grilles de loto : aucun risque, que de l'information. Attention : ces outils ne prédisent pas le prochain tirage (personne ne le peut !), mais ils vous aident à comprendre si votre grille est « bien construite » statistiquement."
        tip="Commencez par entrer vos numéros dans le champ ci-dessous, puis essayez chaque onglet. Monte Carlo vous dit la probabilité de vos numéros, Stabilité vérifie que votre grille est fiable, Comparaison la mesure face au hasard."
        terms={[
          {
            term: "Monte Carlo",
            definition:
              "Imaginez qu'on fasse 10 000 tirages fictifs dans une urne. On compte combien de fois vos numéros sortent. Par exemple, si vous avez en moyenne 1.2 correspondances sur 5, c'est normal (c'est la loi des probabilités). Si vous obtenez 2.5, votre grille contient des numéros qui sortent plus souvent que la moyenne.",
            strength:
              "Donne une estimation très fiable des probabilités de correspondance",
            limit:
              "Le résultat converge toujours vers l'espérance théorique — c'est rassurant mais pas surprenant !",
          },
          {
            term: "Stabilité (bootstrap)",
            definition:
              "On prend l'historique réel des tirages, on le « mélange » 1000 fois au hasard, et on recalcule le score de votre grille à chaque fois. Si le score ne bouge presque pas (CV < 5%), ça veut dire que votre grille est robuste : elle n'est pas bonne « par chance » mais grâce à ses caractéristiques.",
            strength:
              "Un CV (coefficient de variation) < 5% = grille très fiable",
            limit: "Limité à 1 000 itérations côté serveur",
          },
          {
            term: "Comparaison au hasard",
            definition:
              "On génère des milliers de grilles complètement au hasard et on compare leur score au vôtre. Le percentile vous dit : « votre grille est meilleure que X% des grilles aléatoires ». Par exemple, un percentile de 85% signifie que vous faites mieux que 85 grilles aléatoires sur 100.",
            strength:
              "Si votre percentile est > 80%, votre grille est probablement bien optimisée",
          },
          {
            term: "Z-score",
            definition:
              "C'est comme une note comparée à la classe. Z = 0 = vous êtes dans la moyenne. Z = +2 = vous êtes 2 « étages » au-dessus de la moyenne (top ~2%). Z = -1 = légèrement en dessous. En résumé : Z > 1 c'est bien, Z > 2 c'est excellent.",
          },
          {
            term: "Comparaison de stratégies",
            definition:
              "Met en duel deux algorithmes (par ex. Génétique vs Bayésien) sur un même lot de grilles. Comme un match : chaque algorithme génère N grilles, on compare les scores moyens, max et min. Le gagnant est celui qui produit les meilleurs scores en moyenne.",
            strength:
              "Permet de choisir la meilleure stratégie pour votre jeu avant de générer vos vraies grilles",
          },
        ]}
      />

      {/* Input section */}
      <div className="bg-surface rounded-lg border border-border p-6">
        <h2 className="text-sm font-semibold mb-2">Grille à simuler</h2>
        <p className="text-xs text-text-secondary mb-4">
          Entrez les numéros de la grille que vous souhaitez tester. Vous pouvez
          entrer une grille que vous avez en tête, ou recopier une grille depuis
          la page Grilles.
        </p>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          <div>
            <label className="text-xs text-text-secondary block mb-1">
              Numéros ({game?.numbers_drawn ?? "?"} attendus, séparés par
              virgule)
              <InfoTooltip
                text={`Tapez vos ${game?.numbers_drawn ?? "N"} numéros séparés par des virgules. Par exemple : 3, 12, 25, 34, 49`}
              />
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
              <InfoTooltip text="Plus il y a de simulations, plus le résultat est précis. 10 000 est un bon choix. 100 000 est plus précis mais plus lent." />
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
                  Ce graphique montre la répartition des résultats : par
                  exemple, la barre « 2 » indique combien de tirages simulés ont
                  donné exactement 2 numéros en commun avec votre grille. Les
                  barres les plus hautes représentent les résultats les plus
                  fréquents.
                </p>
              </div>

              <p className="text-xs text-text-secondary">
                Temps: {mc.computation_time_ms.toFixed(0)}ms
              </p>

              {/* Explainability */}
              {mc.explanation && (
                <ExplanationPanel explanation={mc.explanation} />
              )}

              {/* AI Analysis */}
              <AiAnalysisPanel
                topic="simulation"
                buildContext={() => ({
                  type: "monte_carlo",
                  numbers: parseNumbers(),
                  n_simulations: mc.n_simulations,
                  avg_matches: mc.avg_matches,
                  expected_matches: mc.expected_matches,
                  match_distribution: mc.match_distribution,
                })}
                dataKey={`mc-${mc.computation_time_ms}`}
                description="L'IA interprète les résultats de votre simulation Monte Carlo."
              />

              {/* Save to history */}
              <SaveButton
                resultType="simulation"
                parameters={{ numbers: parseNumbers(), n_simulations: nSim }}
                resultData={{
                  avg_matches: mc.avg_matches,
                  expected_matches: mc.expected_matches,
                  match_distribution: mc.match_distribution,
                }}
                name={`MC ${mc.n_simulations.toLocaleString()} sims`}
              />
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
            <p className="text-xs text-text-secondary">
              Bootstrap limité à 1 000 itérations.
            </p>
          )}

          {stabMutation.isError && (
            <div className="bg-surface rounded-lg border border-accent-red/30 p-4">
              <p className="text-accent-red text-sm">
                Erreur lors de l'analyse de stabilité. Veuillez réessayer.
              </p>
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
                    <InfoTooltip text="Score moyen obtenu en recalculant sur 1000 échantillons différents de l'historique. Plus il est élevé, mieux c'est." />
                  </p>
                  <p className="font-mono text-lg text-accent-green">
                    {stab.mean_score.toFixed(2)}
                  </p>
                </div>
                <div className="bg-surface rounded-lg border border-border p-4">
                  <p className="text-xs text-text-secondary flex items-center">
                    Écart-type
                    <InfoTooltip text="Mesure la « dispersion » du score. Un écart-type de 0.02 signifie que le score ne bouge presque pas d'un échantillon à l'autre — votre grille est stable." />
                  </p>
                  <p className="font-mono text-lg">
                    {stab.std_score.toFixed(3)}
                  </p>
                </div>
                <div className="bg-surface rounded-lg border border-border p-4">
                  <p className="text-xs text-text-secondary flex items-center">
                    CV
                    <InfoTooltip text="Coefficient de Variation = écart-type ÷ moyenne × 100. Moins de 5% = très stable, 5-10% = stable, plus de 10% = fragile." />
                  </p>
                  <p
                    className={`font-mono text-lg ${stab.cv * 100 < 5 ? "text-accent-green" : stab.cv * 100 < 10 ? "text-accent-yellow" : "text-accent-red"}`}
                  >
                    {(stab.cv * 100).toFixed(1)}%
                  </p>
                  <p className="text-xs text-text-secondary mt-1">
                    {stab.cv * 100 < 5
                      ? "Très stable ✅"
                      : stab.cv * 100 < 10
                        ? "Correcte 👍"
                        : "Fragile ⚠️"}
                  </p>
                </div>
                <div className="bg-surface rounded-lg border border-border p-4">
                  <p className="text-xs text-text-secondary">Stabilité</p>
                  <ScoreBar value={stab.stability} max={1} label="Stabilité" />
                </div>
              </div>

              <div className="bg-surface rounded-lg border border-border p-4">
                <h3 className="text-sm font-semibold mb-1">
                  Intervalle de confiance (95%)
                </h3>
                <p className="text-xs text-text-secondary mb-3">
                  Dans 95% des cas, le score de votre grille se situe entre les
                  deux bornes ci-dessous. Plus l'intervalle est étroit, plus la
                  grille est fiable.
                </p>
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

              {/* AI Analysis */}
              <AiAnalysisPanel
                topic="simulation"
                buildContext={() => ({
                  type: "stability",
                  numbers: parseNumbers(),
                  mean_score: stab.mean_score,
                  std_score: stab.std_score,
                  cv: stab.cv,
                  ci_95_low: stab.ci_95_low,
                  ci_95_high: stab.ci_95_high,
                  stability: stab.stability,
                  min_score: stab.min_score,
                  max_score: stab.max_score,
                })}
                dataKey={`stab-${stab.computation_time_ms}`}
                description="L'IA évalue la stabilité de votre grille."
              />
            </>
          )}
        </div>
      )}

      {tab === "comparison" && (
        <div className="space-y-6">
          {/* Versus random section */}
          <div className="bg-surface rounded-lg border border-border p-4">
            <h2 className="text-sm font-semibold mb-3 flex items-center gap-2">
              <TrendingUp size={14} />
              Comparer ma grille au hasard
            </h2>
            <button
              onClick={handleComparison}
              disabled={!isValid || isPending}
              className="px-4 py-2 bg-accent-green text-white rounded-md text-sm font-medium hover:bg-accent-green/90 disabled:opacity-50 flex items-center gap-2"
            >
              {compMutation.isPending && (
                <Loader2 size={16} className="animate-spin" />
              )}
              Comparer au hasard
            </button>

            {!comp && !compMutation.isPending && (
              <p className="text-text-secondary text-sm mt-3">
                Entrez votre grille ci-dessus, puis cliquez sur « Comparer au
                hasard ». On va générer des milliers de grilles aléatoires et
                voir où la vôtre se situe. C'est comme comparer votre devoir à
                celui de toute la classe !
              </p>
            )}

            {compMutation.isPending && (
              <div className="mt-3">
                <LoadingSpinner message="Comparaison en cours..." />
              </div>
            )}

            {comp && (
              <>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mt-4">
                  <div className="bg-surface-hover rounded-md border border-border p-3">
                    <p className="text-xs text-text-secondary flex items-center">
                      Score de la grille
                      <InfoTooltip text="Le score de qualité de votre grille, calculé selon les mêmes critères que sur la page Grilles." />
                    </p>
                    <p className="font-mono text-lg text-accent-green">
                      {comp.grid_score.toFixed(3)}
                    </p>
                  </div>
                  <div className="bg-surface-hover rounded-md border border-border p-3">
                    <p className="text-xs text-text-secondary flex items-center">
                      Moyenne aléatoire
                      <InfoTooltip text="Le score moyen des grilles tirées au hasard. Plus votre score est au-dessus de cette moyenne, mieux c'est." />
                    </p>
                    <p className="font-mono text-lg">
                      {comp.random_mean.toFixed(3)}
                    </p>
                  </div>
                  <div className="bg-surface-hover rounded-md border border-border p-3">
                    <p className="text-xs text-text-secondary flex items-center">
                      Percentile
                      <InfoTooltip text="Votre grille fait mieux que ce pourcentage de grilles aléatoires. 90% = vous battez 9 grilles sur 10." />
                    </p>
                    <p
                      className={`font-mono text-lg ${comp.percentile >= 80 ? "text-accent-green" : comp.percentile >= 50 ? "text-accent-yellow" : "text-accent-red"}`}
                    >
                      {comp.percentile.toFixed(1)}%
                    </p>
                    <p className="text-xs text-text-secondary mt-1">
                      {comp.percentile >= 90
                        ? "Excellent ! Top 10% 🏆"
                        : comp.percentile >= 80
                          ? "Très bien, top 20% ⭐"
                          : comp.percentile >= 50
                            ? "Correct, au-dessus de la moyenne 👍"
                            : "En dessous de la moyenne — essayez une grille optimisée"}
                    </p>
                  </div>
                </div>
                <div className="mt-3 flex items-center gap-4">
                  <BarChart3
                    size={16}
                    className="text-accent-purple shrink-0"
                  />
                  <p className="text-sm">
                    Z-score:{" "}
                    <span
                      className={`font-mono font-semibold ${comp.z_score > 1 ? "text-accent-green" : comp.z_score < -1 ? "text-accent-red" : "text-text-primary"}`}
                    >
                      {comp.z_score > 0 ? "+" : ""}
                      {comp.z_score.toFixed(2)}
                    </span>
                    {" — "}
                    {comp.z_score > 2
                      ? "Bien au-dessus de la moyenne"
                      : comp.z_score > 1
                        ? "Au-dessus de la moyenne"
                        : comp.z_score > -1
                          ? "Dans la moyenne"
                          : "En-dessous de la moyenne"}
                  </p>
                </div>
                <p className="text-xs text-text-secondary mt-2">
                  Temps: {comp.computation_time_ms.toFixed(0)}ms
                </p>

                {/* Explainability */}
                {comp.explanation && (
                  <ExplanationPanel explanation={comp.explanation} />
                )}

                {/* AI Analysis */}
                <AiAnalysisPanel
                  topic="simulation"
                  buildContext={() => ({
                    type: "comparison",
                    numbers: parseNumbers(),
                    grid_score: comp.grid_score,
                    random_mean: comp.random_mean,
                    percentile: comp.percentile,
                    z_score: comp.z_score,
                  })}
                  dataKey={`comp-${comp.computation_time_ms}`}
                  description="L'IA analyse le positionnement de votre grille par rapport au hasard."
                />

                {/* Save to history */}
                <SaveButton
                  resultType="comparison"
                  parameters={{ numbers: parseNumbers(), n_random: nSim }}
                  resultData={{
                    grid_score: comp.grid_score,
                    percentile: comp.percentile,
                    z_score: comp.z_score,
                    random_mean: comp.random_mean,
                  }}
                  name={`Comparaison P${comp.percentile.toFixed(0)}%`}
                />
              </>
            )}
          </div>

          {/* Strategy A vs B section */}
          <div className="bg-surface rounded-lg border border-border p-4">
            <h2 className="text-sm font-semibold mb-2 flex items-center gap-2">
              <BarChart3 size={14} />
              Comparer deux stratégies d'optimisation
            </h2>
            <p className="text-xs text-text-secondary mb-3">
              Mettez en duel deux algorithmes : chacun génère le même nombre de
              grilles, et on compare les scores. Comme un match de boxe entre
              deux méthodes !
            </p>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
              <div>
                <label className="text-xs text-text-secondary block mb-1">
                  Stratégie A
                  <InfoTooltip text="Le premier algorithme à tester. Par exemple, essayez Génétique vs Bayésien pour voir lequel est le plus performant sur votre jeu." />
                </label>
                <select
                  value={stratA}
                  onChange={(e) => setStratA(e.target.value)}
                  className="w-full bg-surface-hover border border-border rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-accent-blue"
                >
                  {OPTIMIZATION_METHODS.filter((m) => m.value !== "auto").map(
                    (m) => (
                      <option key={m.value} value={m.value}>
                        {m.label}
                      </option>
                    ),
                  )}
                </select>
              </div>
              <div>
                <label className="text-xs text-text-secondary block mb-1">
                  Stratégie B
                </label>
                <select
                  value={stratB}
                  onChange={(e) => setStratB(e.target.value)}
                  className="w-full bg-surface-hover border border-border rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-accent-blue"
                >
                  {OPTIMIZATION_METHODS.filter((m) => m.value !== "auto").map(
                    (m) => (
                      <option key={m.value} value={m.value}>
                        {m.label}
                      </option>
                    ),
                  )}
                </select>
              </div>
              <div>
                <label className="text-xs text-text-secondary block mb-1">
                  Grilles par stratégie
                </label>
                <input
                  type="number"
                  min={1}
                  max={50}
                  value={stratCount}
                  onChange={(e) => setStratCount(Number(e.target.value))}
                  className="w-full bg-surface-hover border border-border rounded-md px-3 py-2 text-sm font-mono focus:outline-none focus:ring-1 focus:ring-accent-blue"
                />
              </div>
            </div>
            <button
              onClick={handleStratCompare}
              disabled={
                stratA === stratB ||
                genAMutation.isPending ||
                genBMutation.isPending
              }
              className="px-4 py-2 bg-accent-purple text-white rounded-md text-sm font-medium hover:bg-accent-purple/90 disabled:opacity-50 flex items-center gap-2"
            >
              {(genAMutation.isPending || genBMutation.isPending) && (
                <Loader2 size={14} className="animate-spin" />
              )}
              Lancer la comparaison
            </button>
            {stratA === stratB && (
              <p className="text-xs text-accent-red mt-1">
                Sélectionnez deux stratégies différentes.
              </p>
            )}

            {(genAMutation.data ||
              genBMutation.data ||
              genAMutation.isPending ||
              genBMutation.isPending ||
              genAMutation.isError ||
              genBMutation.isError) && (
              <div className="mt-4 space-y-4">
                {/* Per-strategy panels */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {[
                    {
                      label: stratA,
                      mutation: genAMutation,
                      color: "text-accent-blue",
                      borderColor: "border-accent-blue/40",
                    },
                    {
                      label: stratB,
                      mutation: genBMutation,
                      color: "text-accent-purple",
                      borderColor: "border-accent-purple/40",
                    },
                  ].map(({ label, mutation, color, borderColor }) => (
                    <div
                      key={label}
                      className={`bg-surface-hover rounded-md border ${borderColor} p-3 space-y-2 min-h-[120px]`}
                    >
                      <p
                        className={`text-xs font-semibold uppercase tracking-wide ${color}`}
                      >
                        {OPTIMIZATION_METHODS.find((m) => m.value === label)
                          ?.label ?? label}
                      </p>

                      {mutation.isPending && (
                        <div className="flex items-center gap-2 text-xs text-text-secondary">
                          <Loader2 size={13} className="animate-spin" />
                          Calcul en cours…
                        </div>
                      )}

                      {mutation.isError && (
                        <p className="text-xs text-accent-red">
                          Erreur lors de la génération. Réessayez dans quelques
                          instants.
                        </p>
                      )}

                      {mutation.data && (
                        <>
                          <div className="grid grid-cols-3 gap-2 text-center">
                            <div>
                              <p className="text-xs text-text-secondary">
                                Moy.
                              </p>
                              <p className="font-mono text-sm">
                                {formatScore(
                                  mutation.data.grids.reduce(
                                    (a, g) => a + g.total_score,
                                    0,
                                  ) / mutation.data.grids.length,
                                )}
                              </p>
                            </div>
                            <div>
                              <p className="text-xs text-text-secondary">
                                Max.
                              </p>
                              <p className={`font-mono text-sm ${color}`}>
                                {formatScore(
                                  Math.max(
                                    ...mutation.data.grids.map(
                                      (g) => g.total_score,
                                    ),
                                  ),
                                )}
                              </p>
                            </div>
                            <div>
                              <p className="text-xs text-text-secondary">
                                Min.
                              </p>
                              <p className="font-mono text-sm">
                                {formatScore(
                                  Math.min(
                                    ...mutation.data.grids.map(
                                      (g) => g.total_score,
                                    ),
                                  ),
                                )}
                              </p>
                            </div>
                          </div>
                          <p className="text-xs text-text-secondary">
                            Temps :{" "}
                            {mutation.data.computation_time_ms.toFixed(0)} ms
                          </p>
                          <div className="space-y-1 max-h-32 overflow-y-auto">
                            {mutation.data.grids.slice(0, 5).map((g, i) => (
                              <div key={i} className="flex items-center gap-2">
                                <DrawBalls
                                  numbers={g.numbers}
                                  stars={g.stars}
                                  size="sm"
                                />
                                <span className="ml-auto font-mono text-xs text-accent-green">
                                  {formatScore(g.total_score)}
                                </span>
                              </div>
                            ))}
                            {mutation.data.grids.length > 5 && (
                              <p className="text-xs text-text-secondary">
                                +{mutation.data.grids.length - 5} autres grilles
                              </p>
                            )}
                          </div>
                        </>
                      )}
                    </div>
                  ))}
                </div>

                {/* Analysis — only when both results are available */}
                {genAMutation.data &&
                  genBMutation.data &&
                  (() => {
                    const dataA = genAMutation.data.grids;
                    const dataB = genBMutation.data.grids;
                    const avgA =
                      dataA.reduce((s, g) => s + g.total_score, 0) /
                      dataA.length;
                    const avgB =
                      dataB.reduce((s, g) => s + g.total_score, 0) /
                      dataB.length;
                    const maxA = Math.max(...dataA.map((g) => g.total_score));
                    const maxB = Math.max(...dataB.map((g) => g.total_score));
                    const minA = Math.min(...dataA.map((g) => g.total_score));
                    const minB = Math.min(...dataB.map((g) => g.total_score));

                    const winner =
                      avgA > avgB ? stratA : avgB > avgA ? stratB : null;
                    const winnerLabel =
                      OPTIMIZATION_METHODS.find((m) => m.value === winner)
                        ?.label ?? winner;
                    const diff = Math.abs(avgA - avgB);
                    const diffPct = (
                      (diff / Math.min(avgA, avgB)) *
                      100
                    ).toFixed(1);

                    const chartData = [
                      { metric: "Moy.", A: avgA, B: avgB },
                      { metric: "Max.", A: maxA, B: maxB },
                      { metric: "Min.", A: minA, B: minB },
                    ];

                    const interpretation =
                      diff < 0.05
                        ? "Les deux stratégies produisent des résultats très similaires sur ce lot. Essayez avec plus de grilles pour différencier davantage."
                        : avgA > avgB
                          ? `La stratégie A (${OPTIMIZATION_METHODS.find((m) => m.value === stratA)?.label}) produit des grilles avec un score moyen ${diffPct}% plus élevé. Elle semble mieux adaptée à votre jeu actuel.`
                          : `La stratégie B (${OPTIMIZATION_METHODS.find((m) => m.value === stratB)?.label}) produit des grilles avec un score moyen ${diffPct}% plus élevé. Elle semble mieux adaptée à votre jeu actuel.`;

                    return (
                      <div className="bg-surface rounded-md border border-border p-4 space-y-4">
                        <h3 className="text-sm font-semibold flex items-center gap-2">
                          <Trophy size={14} className="text-accent-yellow" />
                          Analyse comparative
                        </h3>

                        {/* Winner badge */}
                        <div
                          className={`flex items-center gap-3 rounded-md px-3 py-2 ${winner ? "bg-accent-green/10 border border-accent-green/30" : "bg-surface-hover border border-border"}`}
                        >
                          {winner ? (
                            <>
                              <Trophy
                                size={16}
                                className="text-accent-yellow shrink-0"
                              />
                              <div>
                                <p className="text-sm font-semibold text-accent-green">
                                  Stratégie gagnante : {winnerLabel}
                                </p>
                                <p className="text-xs text-text-secondary">
                                  +{diffPct}% de score moyen par rapport à
                                  l'autre stratégie
                                </p>
                              </div>
                            </>
                          ) : (
                            <p className="text-sm text-text-secondary">
                              Égalité parfaite sur ce lot.
                            </p>
                          )}
                        </div>

                        {/* Bar chart */}
                        <ResponsiveContainer width="100%" height={180}>
                          <BarChart data={chartData} barCategoryGap="30%">
                            <CartesianGrid
                              strokeDasharray="3 3"
                              stroke="var(--color-border)"
                            />
                            <XAxis
                              dataKey="metric"
                              tick={{
                                fill: "var(--color-text-secondary)",
                                fontSize: 12,
                              }}
                            />
                            <YAxis
                              domain={[
                                Math.floor(Math.min(minA, minB) * 10) / 10 -
                                  0.1,
                                Math.ceil(Math.max(maxA, maxB) * 10) / 10 + 0.1,
                              ]}
                              tick={{
                                fill: "var(--color-text-secondary)",
                                fontSize: 11,
                              }}
                            />
                            <Tooltip
                              contentStyle={{
                                backgroundColor: "var(--color-surface)",
                                border: "1px solid var(--color-border)",
                                borderRadius: "6px",
                              }}
                              formatter={(val, name) => [
                                (val as number).toFixed(3),
                                name === "A"
                                  ? (OPTIMIZATION_METHODS.find(
                                      (m) => m.value === stratA,
                                    )?.label ?? stratA)
                                  : (OPTIMIZATION_METHODS.find(
                                      (m) => m.value === stratB,
                                    )?.label ?? stratB),
                              ]}
                            />
                            <Bar dataKey="A" radius={[4, 4, 0, 0]}>
                              {chartData.map((_, i) => (
                                <Cell key={i} fill="var(--color-accent-blue)" />
                              ))}
                            </Bar>
                            <Bar dataKey="B" radius={[4, 4, 0, 0]}>
                              {chartData.map((_, i) => (
                                <Cell
                                  key={i}
                                  fill="var(--color-accent-purple)"
                                />
                              ))}
                            </Bar>
                          </BarChart>
                        </ResponsiveContainer>
                        <div className="flex gap-4 text-xs text-text-secondary">
                          <span className="flex items-center gap-1">
                            <span className="w-3 h-3 rounded-sm bg-accent-blue inline-block" />{" "}
                            {OPTIMIZATION_METHODS.find(
                              (m) => m.value === stratA,
                            )?.label ?? stratA}{" "}
                            (A)
                          </span>
                          <span className="flex items-center gap-1">
                            <span className="w-3 h-3 rounded-sm bg-accent-purple inline-block" />{" "}
                            {OPTIMIZATION_METHODS.find(
                              (m) => m.value === stratB,
                            )?.label ?? stratB}{" "}
                            (B)
                          </span>
                        </div>

                        {/* Interpretation */}
                        <p className="text-xs text-text-secondary leading-relaxed border-t border-border pt-3">
                          💡 {interpretation}
                        </p>
                      </div>
                    );
                  })()}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
