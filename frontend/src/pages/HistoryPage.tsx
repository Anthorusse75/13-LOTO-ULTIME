import LoadingSpinner from "@/components/common/LoadingSpinner";
import PageIntro from "@/components/common/PageIntro";
import DrawBalls from "@/components/draws/DrawBalls";
import {
  useFavoriteGrids,
  usePlayedGrids,
  useTogglePlayed,
} from "@/hooks/useGrids";
import { drawService } from "@/services/drawService";
import { useGameStore } from "@/stores/gameStore";
import type { Draw } from "@/types/draw";
import type { GridResponse } from "@/types/grid";
import { useQuery } from "@tanstack/react-query";
import { CheckCircle2, TrendingUp, Trophy } from "lucide-react";
import { useMemo, useState } from "react";
import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

type HistoryTab = "played" | "favorites";

function matchCount(gridNumbers: number[], drawNumbers: number[]): number {
  const s = new Set(drawNumbers);
  return gridNumbers.filter((n) => s.has(n)).length;
}

function starMatchCount(
  gridStars: number[] | null,
  drawStars: number[] | null,
): number {
  if (!gridStars || !drawStars) return 0;
  const s = new Set(drawStars);
  return gridStars.filter((n) => s.has(n)).length;
}

function getResultLabel(
  matches: number,
  total: number,
  _starMatches: number,
): string {
  const pct = matches / total;
  if (pct >= 1) return "🏆 Jackpot!";
  if (pct >= 0.8) return "⭐ Excellent";
  if (pct >= 0.6) return "✅ Bon";
  if (pct >= 0.4) return "👍 Moyen";
  return "❌ Raté";
}

interface ComparedGrid extends GridResponse {
  bestDraw: Draw | null;
  bestMatch: number;
  bestStarMatch: number;
  numbersDrawn: number;
}

export default function HistoryPage() {
  const [tab, setTab] = useState<HistoryTab>("played");

  const gameId = useGameStore((s) => s.currentGameId);
  const { data: playedGrids = [], isLoading: loadingPlayed } = usePlayedGrids();
  const { data: favoriteGrids = [], isLoading: loadingFavorites } =
    useFavoriteGrids();
  const togglePlayed = useTogglePlayed();

  const { data: recentDraws = [] } = useQuery({
    queryKey: ["draws", gameId, "recent"],
    queryFn: () => drawService.getDraws(gameId!, 0, 100),
    enabled: !!gameId,
    staleTime: 5 * 60 * 1000,
  });

  const gridsToShow = tab === "played" ? playedGrids : favoriteGrids;
  const isLoading = tab === "played" ? loadingPlayed : loadingFavorites;

  // Enrich played grids with best draw comparison
  const enrichedGrids: ComparedGrid[] = useMemo(() => {
    return gridsToShow.map((grid) => {
      let bestDraw: Draw | null = null;
      let bestMatch = 0;
      let bestStarMatch = 0;

      for (const draw of recentDraws) {
        const m = matchCount(grid.numbers, draw.numbers);
        const sm = starMatchCount(grid.stars, draw.stars);
        if (m > bestMatch || (m === bestMatch && sm > bestStarMatch)) {
          bestMatch = m;
          bestStarMatch = sm;
          bestDraw = draw;
        }
      }

      return {
        ...grid,
        bestDraw,
        bestMatch,
        bestStarMatch,
        numbersDrawn: grid.numbers.length,
      };
    });
  }, [gridsToShow, recentDraws]);

  // Cumulative performance chart data
  const chartData = useMemo(() => {
    if (playedGrids.length === 0 || recentDraws.length === 0) return [];

    return playedGrids
      .filter((g) => g.played_at)
      .sort(
        (a, b) =>
          new Date(a.played_at!).getTime() - new Date(b.played_at!).getTime(),
      )
      .map((grid, idx) => {
        let bestMatch = 0;
        for (const draw of recentDraws) {
          const m = matchCount(grid.numbers, draw.numbers);
          if (m > bestMatch) bestMatch = m;
        }
        const pct = (bestMatch / grid.numbers.length) * 100;
        return {
          label: `Grille ${idx + 1}`,
          score: Math.round(grid.total_score * 100),
          matchPct: Math.round(pct),
          date: grid.played_at
            ? new Date(grid.played_at).toLocaleDateString("fr-FR")
            : "",
        };
      });
  }, [playedGrids, recentDraws]);

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Historique</h1>

      <PageIntro
        storageKey="history"
        description="Bienvenue dans votre journal de bord ! Cette page compare vos grilles (jouées ou favorites) aux vrais tirages de la FDJ. Après chaque tirage, revenez ici pour voir combien de numéros vous aviez trouvés. Par exemple, si vous avez joué la grille [3, 12, 27, 35, 41] et que le tirage était [3, 10, 27, 35, 44], vous aurez 3 numéros sur 5 — un résultat « ✅ Bon »."
        tip="Marquez vos grilles comme « jouées » depuis la page Grilles (bouton ✓), puis revenez ici après le tirage officiel. Le système compare automatiquement vos grilles aux 100 derniers tirages."
        terms={[
          {
            term: "Grille jouée",
            definition:
              "Une grille que vous avez marquée comme ayant été effectivement jouée (achetée en bureau de tabac ou en ligne). Ça permet de la distinguer des grilles que vous « surveillez » sans les jouer.",
          },
          {
            term: "Meilleure correspondance",
            definition:
              "Le meilleur résultat obtenu en comparant votre grille à tous les tirages récents. Par exemple, « 3/5 numéros + 1 étoile » signifie que, parmi les 100 derniers tirages, le meilleur était un tirage où 3 de vos numéros et 1 de vos étoiles étaient sortis.",
          },
          {
            term: "Performance cumulée (graphique)",
            definition:
              "Le graphique montre l'évolution de vos résultats au fil du temps. La courbe bleue = le score de qualité de la grille (/100), la courbe verte = le % de numéros correspondants avec le meilleur tirage. Si la courbe verte monte, vos choix s'améliorent !",
            strength:
              "Identifie si vos stratégies de sélection progressent au fil du temps",
          },
          {
            term: "Résultat (🏆⭐✅👍❌)",
            definition:
              "Un indicateur rapide de votre résultat : 🏆 Jackpot = tous les numéros, ⭐ Excellent = 80%+, ✅ Bon = 60%+, 👍 Moyen = 40%+, ❌ Raté = moins de 40%. Par exemple au Loto (5 numéros) : 4/5 = ⭐ Excellent, 3/5 = ✅ Bon, 2/5 = 👍 Moyen.",
          },
        ]}
      />

      {/* Tabs */}
      <div className="flex gap-1 border-b border-border pb-px">
        {(
          [
            {
              key: "played" as HistoryTab,
              label: "Grilles jouées",
              count: playedGrids.length,
            },
            {
              key: "favorites" as HistoryTab,
              label: "Favoris",
              count: favoriteGrids.length,
            },
          ] as const
        ).map((t) => (
          <button
            key={t.key}
            onClick={() => setTab(t.key)}
            className={`px-4 py-2 text-sm flex items-center gap-1.5 rounded-t-md transition-colors ${
              tab === t.key
                ? "bg-surface text-text-primary border border-border border-b-transparent -mb-px"
                : "text-text-secondary hover:text-text-primary"
            }`}
          >
            {t.label}
            <span className="text-xs bg-surface-hover px-1.5 py-0.5 rounded-full">
              {t.count}
            </span>
          </button>
        ))}
      </div>

      {isLoading && <LoadingSpinner message="Chargement..." />}

      {!isLoading && gridsToShow.length === 0 && (
        <div className="bg-surface rounded-lg border border-border p-8 text-center">
          <p className="text-text-secondary text-sm">
            {tab === "played"
              ? "Vous n'avez encore marqué aucune grille comme jouée. Allez sur la page Grilles, choisissez une grille, puis cliquez sur le bouton ✓ pour la marquer comme « jouée ». Elle apparaîtra ici avec ses résultats."
              : "Aucun favori pour l'instant. Depuis la page Grilles, cliquez sur l'étoile ⭐ pour ajouter une grille à vos favoris. Vous pourrez la suivre ici sans forcément la jouer."}
          </p>
        </div>
      )}

      {/* Cumulative performance chart (played tab only) */}
      {tab === "played" && chartData.length >= 2 && (
        <div className="bg-surface rounded-lg border border-border p-4">
          <h2 className="text-sm font-semibold mb-3 flex items-center gap-2">
            <TrendingUp size={16} className="text-accent-green" />
            Performance cumulée
          </h2>
          <ResponsiveContainer width="100%" height={180}>
            <LineChart data={chartData}>
              <CartesianGrid
                strokeDasharray="3 3"
                stroke="var(--color-border)"
              />
              <XAxis
                dataKey="date"
                tick={{ fontSize: 11, fill: "var(--color-text-secondary)" }}
              />
              <YAxis
                tick={{ fontSize: 11, fill: "var(--color-text-secondary)" }}
                unit="%"
              />
              <Tooltip
                contentStyle={{
                  background: "var(--color-surface)",
                  border: "1px solid var(--color-border)",
                  borderRadius: "6px",
                  fontSize: "12px",
                }}
                formatter={(val, name) => [
                  `${val as number}${name === "matchPct" ? "%" : ""}`,
                  name === "matchPct" ? "Correspondance" : "Score",
                ]}
              />
              <Line
                type="monotone"
                dataKey="matchPct"
                stroke="var(--color-accent-green)"
                strokeWidth={2}
                dot={{ r: 3 }}
                name="matchPct"
              />
              <Line
                type="monotone"
                dataKey="score"
                stroke="var(--color-accent-blue)"
                strokeWidth={2}
                dot={{ r: 3 }}
                name="score"
              />
            </LineChart>
          </ResponsiveContainer>
          <p className="text-xs text-text-secondary mt-2 text-center">
            📘 Courbe bleue : score de qualité de la grille (/100) · 📗 Courbe
            verte : % de numéros trouvés dans le meilleur tirage
          </p>
          <p className="text-xs text-text-secondary mt-1 text-center italic">
            Si la courbe verte monte avec le temps, c'est que vos sélections
            s'améliorent !
          </p>
        </div>
      )}

      {/* Grid list */}
      {!isLoading && enrichedGrids.length > 0 && (
        <div className="space-y-3">
          {enrichedGrids.map((grid) => (
            <div
              key={grid.id}
              className="bg-surface rounded-lg border border-border p-4 space-y-3"
            >
              <div className="flex items-start justify-between gap-4 flex-wrap">
                <div className="space-y-2">
                  <DrawBalls
                    numbers={grid.numbers}
                    stars={grid.stars ?? undefined}
                    size="sm"
                  />
                  <div className="flex items-center gap-3 text-xs text-text-secondary flex-wrap">
                    <span>
                      Score :{" "}
                      <span className="text-accent-blue font-mono">
                        {(grid.total_score * 100).toFixed(0)}/100
                      </span>
                    </span>
                    <span>
                      Méthode : <span className="font-mono">{grid.method}</span>
                    </span>
                    {grid.played_at && (
                      <span>
                        Joué le :{" "}
                        {new Date(grid.played_at).toLocaleDateString("fr-FR")}
                      </span>
                    )}
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  {tab === "played" && (
                    <button
                      onClick={() => togglePlayed.mutate(grid.id)}
                      title="Marquer comme non jouée"
                      className="text-xs px-2 py-1 bg-surface-hover border border-border rounded flex items-center gap-1 hover:border-accent-red/50 hover:text-accent-red transition-colors"
                    >
                      <CheckCircle2 size={12} className="text-accent-green" />
                      Jouée
                    </button>
                  )}
                </div>
              </div>

              {/* Best draw comparison */}
              {grid.bestDraw && (
                <div className="rounded-md bg-surface-hover border border-border p-3 space-y-2">
                  <div className="flex items-center justify-between flex-wrap gap-2">
                    <p className="text-xs font-semibold flex items-center gap-1">
                      <Trophy size={12} className="text-accent-yellow" />
                      Meilleure correspondance — tirage du{" "}
                      {new Date(grid.bestDraw.draw_date).toLocaleDateString(
                        "fr-FR",
                      )}
                    </p>
                    <span className="text-xs font-semibold">
                      {getResultLabel(
                        grid.bestMatch,
                        grid.numbersDrawn,
                        grid.bestStarMatch,
                      )}
                    </span>
                  </div>
                  <DrawBalls
                    numbers={grid.bestDraw.numbers}
                    stars={grid.bestDraw.stars ?? undefined}
                    size="sm"
                    highlight={grid.numbers}
                  />
                  <p className="text-xs text-text-secondary">
                    {grid.bestMatch}/{grid.numbersDrawn} numéros correspondants
                    {grid.bestStarMatch > 0 &&
                      ` + ${grid.bestStarMatch} étoile${grid.bestStarMatch > 1 ? "s" : ""}`}
                    {" — "}
                    {grid.bestMatch === 0
                      ? "aucun numéro en commun avec ce tirage"
                      : grid.bestMatch === grid.numbersDrawn
                        ? "tous vos numéros étaient dans ce tirage !"
                        : `${grid.bestMatch} de vos numéros étaient dans ce tirage`}
                  </p>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
