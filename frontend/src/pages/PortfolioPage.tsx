import ExplanationPanel from "@/components/common/ExplanationPanel";
import InfoTooltip from "@/components/common/InfoTooltip";
import LoadingSpinner from "@/components/common/LoadingSpinner";
import PageIntro from "@/components/common/PageIntro";
import DrawBalls from "@/components/draws/DrawBalls";
import SaveButton from "@/components/history/SaveButton";
import NumberHeatmap from "@/components/statistics/NumberHeatmap";
import { useGeneratePortfolio } from "@/hooks/usePortfolios";
import { gameService } from "@/services/gameService";
import { useGameStore } from "@/stores/gameStore";
import { PORTFOLIO_STRATEGIES } from "@/utils/constants";
import { formatScore } from "@/utils/formatters";
import { useQuery } from "@tanstack/react-query";
import { Loader2, X } from "lucide-react";
import { useRef, useState } from "react";

export default function PortfolioPage() {
  const [gridCount, setGridCount] = useState(7);
  const [strategy, setStrategy] = useState("balanced");
  const abortRef = useRef<AbortController | null>(null);

  const slug = useGameStore((s) => s.currentGameSlug);
  const { data: game } = useQuery({
    queryKey: ["game", slug],
    queryFn: () => gameService.getBySlug(slug!),
    enabled: !!slug,
  });

  const generateMutation = useGeneratePortfolio();

  const handleGenerate = () => {
    abortRef.current?.abort();
    const controller = new AbortController();
    abortRef.current = controller;
    generateMutation.mutate({ grid_count: gridCount, strategy });
  };

  const handleCancel = () => {
    abortRef.current?.abort();
    abortRef.current = null;
    generateMutation.reset();
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

      <PageIntro
        storageKey="portfolio"
        description="Le Portefeuille, c'est comme jouer plusieurs grilles complémentaires en même temps. Au lieu de miser tout sur une seule combinaison, vous répartissez vos chances sur plusieurs grilles qui se complètent intelligemment. L'objectif : couvrir un maximum de numéros possibles tout en gardant des grilles de bonne qualité."
        tip="Pour un premier essai, utilisez la stratégie « Équilibré » avec 7 grilles — c'est le meilleur compromis. Ensuite, regardez la carte de chaleur en bas : si un numéro est en rouge, c'est qu'il apparaît dans beaucoup de vos grilles. L'idéal est d'avoir un bon dégradé (pas tout rouge ou tout bleu)."
        terms={[
          {
            term: "Couverture",
            definition:
              "Pourcentage de numéros du jeu présents dans au moins une de vos grilles. Exemple : au Loto (49 numéros), si vos 7 grilles contiennent 35 numéros différents, la couverture est de 71%.",
            strength:
              "Plus c'est haut, moins vous risquez de « rater » un numéro gagnant",
          },
          {
            term: "Diversité",
            definition:
              "Mesure à quel point vos grilles sont différentes les unes des autres. Si deux grilles partagent 4 numéros sur 5, la diversité est faible.",
            strength:
              "Évite de jouer presque la même grille en double (gaspillage d'argent)",
          },
          {
            term: "Distance de Hamming",
            definition:
              "Nombre de numéros qui diffèrent entre deux grilles. Par exemple, si la grille A = [1,2,3,4,5] et la grille B = [1,2,3,6,7], la distance est 2 (seuls 4 et 5 changent). Plus cette valeur est élevée, plus les grilles sont différentes.",
            strength:
              "Un minimum élevé garantit qu'aucune paire de grilles ne se ressemble trop",
          },
          {
            term: "Score moyen",
            definition:
              "Moyenne des scores individuels de chaque grille (sur 10). Un portefeuille idéal a à la fois un bon score moyen ET une bonne diversité.",
          },
          {
            term: "Carte de chaleur (heatmap)",
            definition:
              "Grille visuelle montrant combien de fois chaque numéro apparaît dans votre portefeuille. Vert foncé = très présent (dans beaucoup de grilles), rouge = peu ou pas présent.",
            strength:
              "Permet de repérer en un coup d'œil les « trous » dans votre couverture",
          },
        ]}
      />

      {/* Generation form */}
      <div className="bg-surface rounded-lg border border-border p-6">
        <h2 className="text-sm font-semibold mb-4">Générer un portefeuille</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          <div>
            <label className="text-xs text-text-secondary block mb-1">
              Nombre de grilles
              <InfoTooltip text="Combien de grilles différentes voulez-vous jouer ? Plus vous en jouez, meilleure est la couverture, mais plus ça coûte. 7 grilles est un bon compromis." />
            </label>
            <input
              type="number"
              min={2}
              max={200}
              value={gridCount}
              onChange={(e) => setGridCount(Number(e.target.value))}
              className="w-full bg-surface-hover border border-border rounded-md px-3 py-2 text-sm font-mono focus:outline-none focus:ring-1 focus:ring-accent-blue"
            />
            <p className="text-xs text-text-secondary mt-1">
              💡 Entre 5 et 10 pour un bon rapport couverture/budget. Jusqu'à
              200 pour une couverture maximale.
            </p>
          </div>
          <div>
            <label className="text-xs text-text-secondary block mb-1">
              Stratégie
              <InfoTooltip text="La stratégie détermine comment l'algorithme sélectionne les grilles. Chaque stratégie privilégie un aspect différent." />
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
            <p className="text-xs text-text-secondary mt-1">
              {PORTFOLIO_STRATEGIES.find((s) => s.value === strategy)
                ?.description ?? ""}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={handleGenerate}
            disabled={generateMutation.isPending}
            className="px-6 py-2 bg-accent-blue text-white rounded-md text-sm font-medium hover:bg-accent-blue/90 disabled:opacity-50 flex items-center gap-2"
          >
            {generateMutation.isPending && (
              <Loader2 size={16} className="animate-spin" />
            )}
            Générer portefeuille
          </button>
          {generateMutation.isPending && (
            <button
              onClick={handleCancel}
              className="px-4 py-2 bg-accent-red/10 text-accent-red border border-accent-red/30 rounded-md text-sm font-medium hover:bg-accent-red/20 flex items-center gap-2 transition-colors"
            >
              <X size={16} />
              Annuler
            </button>
          )}
        </div>
      </div>

      {generateMutation.isPending && (
        <LoadingSpinner message="Optimisation en cours..." />
      )}

      {/* Error state */}
      {generateMutation.isError && !generateMutation.isPending && (
        <div className="bg-surface rounded-lg border border-accent-red/30 p-6 text-center">
          <p className="text-accent-red text-sm">
            Erreur lors de la génération du portefeuille. Veuillez réessayer.
          </p>
        </div>
      )}

      {/* Empty state */}
      {!portfolio &&
        !generateMutation.isPending &&
        !generateMutation.isError && (
          <div className="bg-surface rounded-lg border border-border p-8 text-center">
            <p className="text-text-secondary text-sm mb-2">
              Aucun portefeuille généré.
            </p>
            <p className="text-text-secondary text-xs">
              Choisissez le nombre de grilles et la stratégie, puis cliquez sur
              « Générer portefeuille » pour optimiser votre jeu.
            </p>
          </div>
        )}

      {/* Results */}
      {portfolio && (
        <>
          {/* KPIs */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-surface rounded-lg border border-border p-4">
              <p className="text-xs text-text-secondary flex items-center">
                Score moyen
                <InfoTooltip text="Note moyenne de vos grilles sur 10. Plus c'est haut, plus vos grilles sont statistiquement intéressantes individuellement." />
              </p>
              <p className="font-mono text-lg text-accent-green">
                {formatScore(portfolio.avg_grid_score)}
                <span className="text-xs text-text-secondary font-sans">
                  {" "}
                  /10
                </span>
              </p>
              <p className="text-xs text-text-secondary mt-0.5">
                {Number(portfolio.avg_grid_score) >= 0.7
                  ? "Excellent — vos grilles sont de très bonne qualité"
                  : Number(portfolio.avg_grid_score) >= 0.5
                    ? "Bon — qualité correcte"
                    : "Moyen — essayez une autre stratégie"}
              </p>
            </div>
            <div className="bg-surface rounded-lg border border-border p-4">
              <p className="text-xs text-text-secondary flex items-center">
                Diversité
                <InfoTooltip text="Mesure à quel point vos grilles sont différentes les unes des autres. 100% = toutes les grilles sont complètement différentes. 0% = toutes les grilles sont identiques." />
              </p>
              <p className="font-mono text-lg">
                {(portfolio.diversity_score * 100).toFixed(1)}%
              </p>
              <p className="text-xs text-text-secondary mt-0.5">
                {portfolio.diversity_score >= 0.8
                  ? "Très diversifié — peu de numéros en commun"
                  : portfolio.diversity_score >= 0.5
                    ? "Diversité correcte"
                    : "Faible — vos grilles se ressemblent beaucoup"}
              </p>
            </div>
            <div className="bg-surface rounded-lg border border-border p-4">
              <p className="text-xs text-text-secondary flex items-center">
                Couverture
                <InfoTooltip text="Pourcentage de numéros du jeu présents dans au moins une de vos grilles. 100% = chaque numéro du jeu est dans au moins une grille." />
              </p>
              <p className="font-mono text-lg">
                {(portfolio.coverage_score * 100).toFixed(1)}%
              </p>
              <p className="text-xs text-text-secondary mt-0.5">
                {portfolio.coverage_score >= 0.8
                  ? "Excellente couverture de l'espace de jeu"
                  : portfolio.coverage_score >= 0.5
                    ? "Couverture correcte — quelques trous"
                    : "Faible — ajoutez des grilles pour mieux couvrir"}
              </p>
            </div>
            <div className="bg-surface rounded-lg border border-border p-4">
              <p className="text-xs text-text-secondary flex items-center">
                Distance min.
                <InfoTooltip text="Nombre minimum de numéros qui diffèrent entre deux grilles de votre portefeuille. Si c'est 3, cela signifie que même vos deux grilles les plus proches ont au moins 3 numéros différents." />
              </p>
              <p className="font-mono text-lg">
                {portfolio.min_hamming_distance?.toFixed(1) ?? "—"}
              </p>
              <p className="text-xs text-text-secondary mt-0.5">
                {(portfolio.min_hamming_distance ?? 0) >= 3
                  ? "Bon écart entre les grilles"
                  : "Certaines grilles sont assez proches"}
              </p>
            </div>
          </div>

          {/* Grids list */}
          <div className="bg-surface rounded-lg border border-border p-4">
            <h2 className="text-sm font-semibold mb-1">
              Grilles du portefeuille
            </h2>
            <p className="text-xs text-text-secondary mb-4">
              Voici vos {portfolio.grids.length} grilles optimisées. Chaque
              ligne affiche les numéros à jouer et le score de la grille sur 10.
              {game?.star_name
                ? ` Les boules colorées à droite sont les ${game.star_name}s.`
                : ""}
            </p>
            <div className="space-y-2">
              {portfolio.grids.map((g, i) => (
                <div
                  key={i}
                  className="flex items-center gap-4 p-2 rounded-md hover:bg-surface-hover"
                >
                  <span className="text-xs text-text-secondary w-6">
                    #{i + 1}
                  </span>
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
              <h2 className="text-sm font-semibold mb-1 flex items-center gap-2">
                Carte de couverture numérique
                <InfoTooltip text="Chaque case représente un numéro du jeu. La couleur indique dans combien de grilles ce numéro apparaît. Vert foncé = présent dans beaucoup de grilles. Rouge = absent ou dans très peu de grilles. L'idéal est qu'aucun numéro ne soit oublié." />
              </h2>
              <p className="text-xs text-text-secondary mb-3">
                Chaque numéro est coloré selon sa présence dans vos grilles.
                Plus un numéro est vert, plus il revient souvent dans votre
                portefeuille. Les numéros rouges sont peu ou pas couverts —
                c'est normal de ne pas tout couvrir, mais gardez un œil sur les
                « trous ».
              </p>

              {/* Legend */}
              <div className="flex items-center gap-4 mb-3 text-xs text-text-secondary">
                <span className="flex items-center gap-1">
                  <span className="w-3 h-3 rounded-sm bg-accent-red/80 inline-block" />
                  Peu présent (0-1 grille)
                </span>
                <span className="flex items-center gap-1">
                  <span className="w-3 h-3 rounded-sm bg-accent-amber/80 inline-block" />
                  Moyennement (2-3 grilles)
                </span>
                <span className="flex items-center gap-1">
                  <span className="w-3 h-3 rounded-sm bg-accent-green/80 inline-block" />
                  Très présent (4+ grilles)
                </span>
              </div>

              <NumberHeatmap
                data={coverageMap}
                minNumber={game.min_number}
                maxNumber={game.max_number}
                colorScale="frequency"
              />
            </div>
          )}

          <p className="text-xs text-text-secondary">
            Stratégie:{" "}
            {PORTFOLIO_STRATEGIES.find((s) => s.value === portfolio.strategy)
              ?.label ?? portfolio.strategy}{" "}
            — Méthode: {portfolio.method_used} — Temps:{" "}
            {portfolio.computation_time_ms.toFixed(0)}ms
          </p>

          {/* Explainability */}
          {portfolio.explanation && (
            <ExplanationPanel explanation={portfolio.explanation} />
          )}

          {/* Save to history */}
          <SaveButton
            resultType="portfolio"
            parameters={{ grid_count: gridCount, strategy }}
            resultData={{
              grids: portfolio.grids,
              diversity_score: portfolio.diversity_score,
              coverage_score: portfolio.coverage_score,
              avg_grid_score: portfolio.avg_grid_score,
            }}
            name={`Portfolio ${portfolio.grid_count} grilles`}
          />
        </>
      )}
    </div>
  );
}
