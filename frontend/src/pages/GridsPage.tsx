import ExplanationPanel from "@/components/common/ExplanationPanel";
import InfoTooltip from "@/components/common/InfoTooltip";
import LoadingSpinner from "@/components/common/LoadingSpinner";
import PageIntro from "@/components/common/PageIntro";
import DrawBalls from "@/components/draws/DrawBalls";
import CustomWeightsEditor from "@/components/grids/CustomWeightsEditor";
import ScoreBar from "@/components/grids/ScoreBar";
import SaveButton from "@/components/history/SaveButton";
import {
  useGenerateGrids,
  useToggleFavorite,
  useTopGrids,
} from "@/hooks/useGrids";
import { useSaveResult } from "@/hooks/useHistory";
import { useGameStore } from "@/stores/gameStore";
import type { GridScoreResponse } from "@/types/grid";
import {
  OPTIMIZATION_METHODS,
  SCORE_CRITERIA,
  SCORING_PROFILES,
} from "@/utils/constants";
import { formatScore } from "@/utils/formatters";
import { exportGridPDF, exportReportPDF } from "@/utils/pdfExport";
import { Download, FileText, Heart, Loader2, Save } from "lucide-react";
import { useState } from "react";

export default function GridsPage() {
  const [count, setCount] = useState(10);
  const [method, setMethod] = useState("auto");
  const [profile, setProfile] = useState("equilibre");
  const [topMethodFilter, setTopMethodFilter] = useState("all");
  const [selectedGrid, setSelectedGrid] = useState<GridScoreResponse | null>(
    null,
  );
  const [customWeights, setCustomWeights] = useState<Record<
    string,
    number
  > | null>(null);

  const { data: topGrids, isLoading: topLoading } = useTopGrids(10);
  const generateMutation = useGenerateGrids();
  const toggleFavoriteMutation = useToggleFavorite();
  const saveMutation = useSaveResult();
  const gameId = useGameStore((s) => s.currentGameId);

  const handleGenerate = () => {
    generateMutation.mutate({
      count,
      method,
      profile,
      weights: customWeights ?? undefined,
    });
  };

  const grids = generateMutation.data?.grids ?? [];

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Grilles</h1>

      <PageIntro
        storageKey="grids"
        description="C'est ici que la magie opère ! Cette page vous permet de générer des grilles optimisées grâce à nos algorithmes, inspirés de la recherche en mathématiques et en intelligence artificielle. Chaque grille reçoit un score de 0 à 10 basé sur l'analyse de milliers de tirages passés. Par exemple, une grille avec un score de 7.5/10 signifie qu'elle respecte bien les tendances historiques (numéros fréquents, bonne répartition, etc.)."
        tip="Commencez avec la méthode « Auto » qui choisit le meilleur algorithme pour vous. Essayez ensuite différentes méthodes et comparez les scores. Cliquez sur une grille pour voir le détail de chaque critère."
        terms={[
          {
            term: "Score total (0 à 10)",
            definition:
              "La note globale de la grille. C'est une moyenne pondérée de 6 critères (fréquence, retard, co-occurrence, structure, équilibre, pénalité). Par exemple, une grille à 8/10 a de bons scores sur la majorité des critères. C'est comme une note à un examen avec plusieurs matières.",
            strength: "Permet de comparer rapidement les grilles entre elles",
            limit:
              "Dépend de la quantité de tirages historiques disponibles — plus il y a de tirages, plus le score est fiable",
          },
          {
            term: "Méthode : Algorithme génétique",
            definition:
              "Imagine 100 grilles tirées au hasard. L'algorithme prend les meilleures, les « croise » entre elles (comme des parents), ajoute de petites mutations, et recommence sur plusieurs générations. Au bout de 50 générations, les grilles survivantes sont les plus optimisées.",
            strength: "Explore un très grand nombre de combinaisons",
            limit: "Calcul un peu plus long (quelques secondes)",
          },
          {
            term: "Méthode : Recuit simulé",
            definition:
              "Comme le refroidissement du métal en forge : au début, l'algorithme accepte des modifications même si elles sont mauvaises (pour explorer). Puis il devient de plus en plus strict, ne gardant que les améliorations. Résultat : il ne reste « piégé » dans aucune solution médiocre.",
            strength: "Bon équilibre entre rapidité et qualité du résultat",
          },
          {
            term: "Méthode : Bayésien",
            definition:
              "Cet algorithme « apprend » des tirages récents. Si le numéro 7 sort souvent ces derniers mois, il lui donne plus de chances d'être sélectionné. C'est comme un joueur qui surveille les tendances avant de remplir sa grille.",
            strength: "S'adapte rapidement aux tendances récentes du jeu",
          },
          {
            term: "Profil de scoring",
            definition:
              "Vous permet de choisir votre style : « Équilibré » = tous les critères comptent pareil. « Audacieux » = favorise les numéros rares (plus risqué, mais gains potentiellement plus élevés). « Prudent » = favorise les numéros fréquents (plus « sûr » statistiquement).",
          },
          {
            term: "Pénalité de pattern",
            definition:
              "Un malus appliqué aux grilles qui semblent « trop régulières ». Par exemple, la grille [2, 4, 6, 8, 10] (tous les pairs qui se suivent) est très improbable en pratique. La pénalité réduit le score de ces grilles suspectes.",
            limit: "Ne garantit pas la diversité entre les grilles générées",
          },
        ]}
      />

      {/* Generation form */}
      <div className="bg-surface rounded-lg border border-border p-6">
        <h2 className="text-sm font-semibold mb-4">Générer des grilles</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
          <div>
            <label className="text-xs text-text-secondary block mb-1">
              Nombre de grilles
              <InfoTooltip text="Combien de grilles voulez-vous générer ? Entre 5 et 10 pour commencer, c'est un bon compromis qualité/budget." />
            </label>
            <input
              type="number"
              min={1}
              max={100}
              value={count}
              onChange={(e) => setCount(Number(e.target.value))}
              className="w-full bg-surface-hover border border-border rounded-md px-3 py-2 text-sm font-mono focus:outline-none focus:ring-1 focus:ring-accent-blue"
            />
          </div>
          <div>
            <label className="text-xs text-text-secondary block mb-1">
              Méthode d'optimisation
              <InfoTooltip text="L'algorithme utilisé pour trouver les meilleures combinaisons. « Auto » choisit la méthode la plus adaptée pour vous." />
            </label>
            <select
              value={method}
              onChange={(e) => setMethod(e.target.value)}
              className="w-full bg-surface-hover border border-border rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-accent-blue"
            >
              {OPTIMIZATION_METHODS.map((m) => (
                <option key={m.value} value={m.value}>
                  {m.label}
                </option>
              ))}
            </select>
            {OPTIMIZATION_METHODS.find((m) => m.value === method)
              ?.description && (
              <p className="text-xs text-text-secondary mt-1 italic">
                {
                  OPTIMIZATION_METHODS.find((m) => m.value === method)
                    ?.description
                }
              </p>
            )}
          </div>
          <div>
            <label className="text-xs text-text-secondary block mb-1">
              Profil de scoring
              <InfoTooltip text="Votre style de jeu : prudent (numéros fréquents), audacieux (numéros rares), ou équilibré (un peu des deux)." />
            </label>
            <div className="flex gap-2 flex-wrap">
              {SCORING_PROFILES.map((p) => (
                <button
                  key={p.value}
                  type="button"
                  onClick={() => setProfile(p.value)}
                  className={`px-2 py-1 rounded text-xs cursor-pointer transition-colors ${
                    profile === p.value
                      ? "bg-accent-blue text-white"
                      : "bg-surface-hover text-text-secondary hover:bg-surface-hover/80"
                  }`}
                >
                  {p.label}
                </button>
              ))}
            </div>
            {SCORING_PROFILES.find((p) => p.value === profile)?.description && (
              <p className="text-xs text-text-secondary mt-1 italic">
                {SCORING_PROFILES.find((p) => p.value === profile)?.description}
              </p>
            )}
          </div>
        </div>

        {/* Custom weights */}
        <div className="mb-4">
          <CustomWeightsEditor onChange={setCustomWeights} />
        </div>
        <button
          onClick={handleGenerate}
          disabled={generateMutation.isPending}
          className="px-6 py-2 bg-accent-blue text-white rounded-md text-sm font-medium hover:bg-accent-blue/90 disabled:opacity-50 flex items-center gap-2"
        >
          {generateMutation.isPending && (
            <Loader2 size={16} className="animate-spin" />
          )}
          Générer
        </button>

        {generateMutation.data && (
          <div className="flex items-center gap-3 mt-2 flex-wrap">
            <p className="text-xs text-text-secondary">
              {generateMutation.data.grids.length} grilles générées en{" "}
              {generateMutation.data.computation_time_ms.toFixed(0)}ms —
              méthode: {generateMutation.data.method_used}
            </p>
            <button
              onClick={() =>
                exportReportPDF({
                  gameName: generateMutation.data!.method_used,
                  grids: generateMutation.data!.grids,
                  method: generateMutation.data!.method_used,
                  computationMs: generateMutation.data!.computation_time_ms,
                })
              }
              className="flex items-center gap-1.5 px-3 py-1 text-xs border border-border rounded-md hover:bg-surface-hover transition-colors"
            >
              <FileText size={12} />
              Rapport PDF
            </button>
          </div>
        )}
      </div>

      {/* Generated grids */}
      {grids.length > 0 && (
        <div className="bg-surface rounded-lg border border-border p-4">
          <h2 className="text-sm font-semibold mb-4">Grilles générées</h2>
          <div className="space-y-2">
            {grids.map((g, i) => (
              <div
                key={i}
                onClick={() => setSelectedGrid(g)}
                className={`flex items-center gap-4 p-3 rounded-md cursor-pointer transition-colors ${
                  selectedGrid === g
                    ? "bg-accent-blue/10 border border-accent-blue/30"
                    : "hover:bg-surface-hover"
                }`}
              >
                <span className="text-xs text-text-secondary w-6">
                  #{i + 1}
                </span>
                <DrawBalls numbers={g.numbers} stars={g.stars} size="sm" />
                <span className="ml-auto font-mono text-accent-green">
                  {formatScore(g.total_score)}
                </span>
                <button
                  title="Sauvegarder cette grille"
                  onClick={(e) => {
                    e.stopPropagation();
                    if (!gameId) return;
                    saveMutation.mutate({
                      result_type: "grid",
                      parameters: { profile, method },
                      result_data: {
                        numbers: g.numbers,
                        stars: g.stars,
                        total_score: g.total_score,
                        score_breakdown: g.score_breakdown,
                      },
                      game_id: gameId,
                      name: `Grille ${formatScore(g.total_score)}`,
                      tags: [],
                    });
                  }}
                  className="p-1.5 rounded-md hover:bg-accent-blue/10 text-text-secondary hover:text-accent-blue transition-colors"
                >
                  <Save size={14} />
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Grid detail */}
      {selectedGrid && (
        <div className="bg-surface rounded-lg border border-border p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-sm font-semibold">
              Détail — Score: {formatScore(selectedGrid.total_score)}/10
              <InfoTooltip text="Le score détaillé ci-dessous montre la contribution de chaque critère. Chaque barre représente une « matière » de la note globale." />
            </h2>
            <button
              onClick={() =>
                exportGridPDF(
                  selectedGrid,
                  "Loto Ultime",
                  generateMutation.data?.method_used ?? method,
                )
              }
              className="flex items-center gap-1.5 px-3 py-1 text-xs border border-border rounded-md hover:bg-surface-hover transition-colors"
            >
              <Download size={12} />
              Exporter PDF
            </button>
          </div>
          <p className="text-xs text-text-secondary mb-3">
            {selectedGrid.total_score >= 8
              ? "🏆 Excellente grille ! Elle coche presque tous les critères."
              : selectedGrid.total_score >= 6
                ? "✅ Bonne grille avec un profil équilibré."
                : selectedGrid.total_score >= 4
                  ? "👍 Grille correcte, mais certains critères pourraient être améliorés."
                  : "⚠️ Grille faible — essayez une autre méthode ou un autre profil."}
          </p>
          <div className="mb-4">
            <DrawBalls
              numbers={selectedGrid.numbers}
              stars={selectedGrid.stars}
              size="lg"
            />
          </div>
          <p className="text-xs text-text-secondary mb-2">
            Chaque barre ci-dessous représente un critère. Passez la souris sur
            le « ? » pour comprendre ce que chaque critère mesure :
          </p>
          <div className="space-y-2">
            {SCORE_CRITERIA.map((c) => (
              <ScoreBar
                key={c.key}
                label={c.label}
                tooltip={c.tooltip}
                value={
                  selectedGrid.score_breakdown[
                    c.key as keyof typeof selectedGrid.score_breakdown
                  ]
                }
              />
            ))}
          </div>
          {selectedGrid.star_score !== null && (
            <p className="text-sm text-text-secondary mt-3">
              Score étoiles:{" "}
              <span className="font-mono text-accent-purple">
                {(selectedGrid.star_score * 10).toFixed(2)}
              </span>
              <InfoTooltip text="Score spécifique aux étoiles (EuroMillions). Évalue si vos étoiles sont bien choisies selon les mêmes critères que les numéros principaux." />
            </p>
          )}

          {/* Explainability */}
          {selectedGrid.explanation && (
            <div className="mt-4">
              <ExplanationPanel explanation={selectedGrid.explanation} />
            </div>
          )}

          {/* Save to history */}
          <div className="mt-4">
            <SaveButton
              resultType="grid"
              parameters={{ profile, method, weights: customWeights }}
              resultData={{
                numbers: selectedGrid.numbers,
                stars: selectedGrid.stars,
                total_score: selectedGrid.total_score,
                score_breakdown: selectedGrid.score_breakdown,
              }}
              name={`Grille ${formatScore(selectedGrid.total_score)}`}
            />
          </div>
        </div>
      )}

      {/* Top grids from DB */}
      <div className="bg-surface rounded-lg border border-border p-4">
        <div className="flex items-center justify-between mb-2">
          <h2 className="text-sm font-semibold">
            Top 10 — Meilleures grilles
            <InfoTooltip text="Ces grilles sont calculées automatiquement chaque nuit. Ce sont les 10 meilleures combinaisons trouvées par nos algorithmes, classées par score décroissant." />
          </h2>
          <select
            value={topMethodFilter}
            onChange={(e) => setTopMethodFilter(e.target.value)}
            className="bg-surface-hover border border-border rounded-md px-2 py-1 text-xs focus:outline-none focus:ring-1 focus:ring-accent-blue"
          >
            <option value="all">Toutes méthodes</option>
            {OPTIMIZATION_METHODS.filter((m) => m.value !== "auto").map((m) => (
              <option key={m.value} value={m.value}>
                {m.label}
              </option>
            ))}
          </select>
        </div>
        <p className="text-xs text-text-secondary mb-3">
          Cliquez sur le cœur ❤️ pour ajouter une grille à vos favoris et la
          retrouver facilement dans l'onglet Historique.
        </p>
        {topLoading ? (
          <LoadingSpinner />
        ) : topGrids && topGrids.length > 0 ? (
          <div className="space-y-2">
            {topGrids
              .filter(
                (g) =>
                  topMethodFilter === "all" || g.method === topMethodFilter,
              )
              .map((g, i) => (
                <div
                  key={g.id}
                  className="flex items-center gap-4 p-2 rounded-md hover:bg-surface-hover"
                >
                  <span className="text-xs text-text-secondary w-6">
                    #{i + 1}
                  </span>
                  <DrawBalls numbers={g.numbers} stars={g.stars} size="sm" />
                  <span className="text-xs text-text-secondary">
                    {g.method}
                  </span>
                  <button
                    onClick={() => toggleFavoriteMutation.mutate(g.id)}
                    className="p-1 rounded hover:bg-surface-hover transition-colors"
                    aria-label={
                      g.is_favorite
                        ? "Retirer des favoris"
                        : "Ajouter aux favoris"
                    }
                  >
                    <Heart
                      size={16}
                      className={
                        g.is_favorite
                          ? "fill-accent-red text-accent-red"
                          : "text-text-secondary"
                      }
                    />
                  </button>
                  <span className="ml-auto font-mono text-accent-green">
                    {formatScore(g.total_score)}
                  </span>
                </div>
              ))}
          </div>
        ) : (
          <div className="text-center py-6">
            <p className="text-text-secondary text-sm mb-3">
              Aucune grille scorée en base.
            </p>
            <p className="text-text-secondary text-xs">
              Utilisez le formulaire ci-dessus pour générer vos premières
              grilles, ou lancez le job de scoring depuis l'administration.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
