import LoadingSpinner from "@/components/common/LoadingSpinner";
import DrawBalls from "@/components/draws/DrawBalls";
import PageIntro from "@/components/common/PageIntro";
import { useFavoriteGrids, usePlayedGrids, useTogglePlayed } from "@/hooks/useGrids";
import { drawService } from "@/services/drawService";
import { useGameStore } from "@/stores/gameStore";
import type { Draw } from "@/types/draw";
import type { GridResponse } from "@/types/grid";
import { useQuery } from "@tanstack/react-query";
import { CheckCircle2, Trophy, TrendingUp } from "lucide-react";
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

function starMatchCount(gridStars: number[] | null, drawStars: number[] | null): number {
  if (!gridStars || !drawStars) return 0;
  const s = new Set(drawStars);
  return gridStars.filter((n) => s.has(n)).length;
}

function getResultLabel(matches: number, total: number, starMatches: number): string {
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
  const { data: favoriteGrids = [], isLoading: loadingFavorites } = useFavoriteGrids();
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

      return { ...grid, bestDraw, bestMatch, bestStarMatch, numbersDrawn: grid.numbers.length };
    });
  }, [gridsToShow, recentDraws]);

  // Cumulative performance chart data
  const chartData = useMemo(() => {
    if (playedGrids.length === 0 || recentDraws.length === 0) return [];

    return playedGrids
      .filter((g) => g.played_at)
      .sort((a, b) => new Date(a.played_at!).getTime() - new Date(b.played_at!).getTime())
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
          date: grid.played_at ? new Date(grid.played_at).toLocaleDateString("fr-FR") : "",
        };
      });
  }, [playedGrids, recentDraws]);

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Historique</h1>

      <PageIntro
        storageKey="history"
        description="La page Historique vous permet de suivre vos grilles jouées et de les comparer aux tirages réels. C'est votre tableau de bord personnel pour suivre vos performances dans le temps."
        tip="Marquez vos grilles comme 'jouées' depuis la page Grilles, puis revenez ici après le tirage pour voir combien de numéros correspondaient."
        terms={[
          { term: "Grille jouée", definition: "Une grille que vous avez marquée comme ayant été jouée à un tirage réel." },
          { term: "Meilleure correspondance", definition: "Nombre maximum de numéros communs entre votre grille et un tirage réel récent." },
          { term: "Performance cumulée", definition: "Évolution de votre score moyen au fil du temps. Permet de voir si vos sélections de grilles s'améliorent.", strength: "Identifie les tendances sur le long terme" },
        ]}
      />

      {/* Tabs */}
      <div className="flex gap-1 border-b border-border pb-px">
        {([
          { key: "played" as HistoryTab, label: "Grilles jouées", count: playedGrids.length },
          { key: "favorites" as HistoryTab, label: "Favoris", count: favoriteGrids.length },
        ] as const).map((t) => (
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
              ? "Aucune grille jouée. Marquez vos grilles comme jouées depuis la page Grilles."
              : "Aucun favori. Ajoutez des grilles aux favoris depuis la page Grilles."}
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
              <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
              <XAxis dataKey="date" tick={{ fontSize: 11, fill: "var(--color-text-secondary)" }} />
              <YAxis tick={{ fontSize: 11, fill: "var(--color-text-secondary)" }} unit="%" />
              <Tooltip
                contentStyle={{
                  background: "var(--color-surface)",
                  border: "1px solid var(--color-border)",
                  borderRadius: "6px",
                  fontSize: "12px",
                }}
                formatter={(val: number, name: string) => [
                  `${val}${name === "matchPct" ? "%" : ""}`,
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
            Bleu : score (/100) · Vert : meilleure correspondance avec les tirages réels
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
                  <DrawBalls numbers={grid.numbers} stars={grid.stars ?? undefined} size="sm" />
                  <div className="flex items-center gap-3 text-xs text-text-secondary flex-wrap">
                    <span>Score : <span className="text-accent-blue font-mono">{(grid.total_score * 100).toFixed(0)}/100</span></span>
                    <span>Méthode : <span className="font-mono">{grid.method}</span></span>
                    {grid.played_at && (
                      <span>Joué le : {new Date(grid.played_at).toLocaleDateString("fr-FR")}</span>
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
                      {new Date(grid.bestDraw.draw_date).toLocaleDateString("fr-FR")}
                    </p>
                    <span className="text-xs font-semibold">
                      {getResultLabel(grid.bestMatch, grid.numbersDrawn, grid.bestStarMatch)}
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
                    {grid.bestStarMatch > 0 && ` + ${grid.bestStarMatch} étoiles`}
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


