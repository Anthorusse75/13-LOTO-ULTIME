import LoadingSpinner from "@/components/common/LoadingSpinner";
import PageIntro from "@/components/common/PageIntro";
import DrawBalls from "@/components/draws/DrawBalls";
import ScoreBar from "@/components/grids/ScoreBar";
import { useFavoriteGrids, useToggleFavorite } from "@/hooks/useGrids";
import type { GridResponse } from "@/types/grid";
import { SCORE_CRITERIA } from "@/utils/constants";
import { formatScore } from "@/utils/formatters";
import { Heart, Star } from "lucide-react";
import { useState } from "react";

export default function FavoritesPage() {
  const { data: favorites = [], isLoading } = useFavoriteGrids();
  const toggleFavorite = useToggleFavorite();
  const [selected, setSelected] = useState<GridResponse | null>(null);

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <Star size={22} className="text-accent-yellow" />
        <h1 className="text-2xl font-bold">Mes favoris</h1>

        <PageIntro
          storageKey="favorites"
          description="Vos favoris sont les grilles que vous avez marquées d'un cœur depuis la page Grilles. Retrouvez-les ici pour les consulter, les comparer ou les exporter en PDF."
          tip="Ajoutez en favori les grilles avec les meilleurs scores avant chaque tirage, puis utilisez l'Historique pour suivre leurs performances dans le temps."
          terms={[
            {
              term: "Score",
              definition:
                "Note de 0 à 10 résumant la qualité statistique de la grille selon 6 critères.",
              strength: "Plus c'est haut, mieux c'est",
            },
            {
              term: "Critères du score",
              definition:
                "Fréquence + Écart + Cooccurrence + Structure + Équilibre - Pénalité de pattern.",
            },
          ]}
        />
      </div>

      {isLoading && <LoadingSpinner message="Chargement des favoris..." />}

      {!isLoading && favorites.length === 0 && (
        <div className="bg-surface rounded-lg border border-border p-10 text-center">
          <Heart
            size={36}
            className="mx-auto mb-3 text-text-secondary opacity-40"
          />
          <p className="text-text-secondary text-sm">
            Aucune grille en favori.
          </p>
          <p className="text-text-secondary text-xs mt-1">
            Ajoutez des grilles depuis la page{" "}
            <a href="/grids" className="text-accent-blue hover:underline">
              Grilles
            </a>
            .
          </p>
        </div>
      )}

      {!isLoading && favorites.length > 0 && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {/* List */}
          <div className="bg-surface rounded-lg border border-border p-4">
            <p className="text-xs text-text-secondary mb-3">
              {favorites.length} grille{favorites.length > 1 ? "s" : ""} en
              favori
            </p>
            <div className="space-y-2">
              {favorites.map((g, i) => (
                <div
                  key={g.id}
                  onClick={() => setSelected(g)}
                  className={`flex items-center gap-3 p-2.5 rounded-md cursor-pointer transition-colors ${
                    selected?.id === g.id
                      ? "bg-accent-blue/10 border border-accent-blue/30"
                      : "hover:bg-surface-hover"
                  }`}
                >
                  <span className="text-xs text-text-secondary w-5 shrink-0">
                    #{i + 1}
                  </span>
                  <DrawBalls numbers={g.numbers} stars={g.stars} size="sm" />
                  <span className="text-xs text-text-secondary ml-1 hidden sm:block">
                    {g.method}
                  </span>
                  <span className="ml-auto font-mono text-sm text-accent-green shrink-0">
                    {formatScore(g.total_score)}
                  </span>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      toggleFavorite.mutate(g.id);
                    }}
                    title="Retirer des favoris"
                    className="p-1 shrink-0 rounded hover:bg-surface-hover transition-colors"
                    aria-label="Retirer des favoris"
                  >
                    <Heart
                      size={15}
                      className="fill-accent-red text-accent-red"
                    />
                  </button>
                </div>
              ))}
            </div>
          </div>

          {/* Detail panel */}
          <div className="bg-surface rounded-lg border border-border p-4">
            {!selected ? (
              <div className="flex items-center justify-center h-full min-h-[160px]">
                <p className="text-text-secondary text-sm">
                  Sélectionnez une grille pour voir les détails
                </p>
              </div>
            ) : (
              <div className="space-y-4">
                <div>
                  <p className="text-xs text-text-secondary mb-2">
                    Score :{" "}
                    <span className="text-accent-green font-mono">
                      {formatScore(selected.total_score)}/10
                    </span>
                    {" · "}Méthode :{" "}
                    <span className="font-mono">{selected.method}</span>
                  </p>
                  <DrawBalls
                    numbers={selected.numbers}
                    stars={selected.stars}
                    size="md"
                  />
                </div>

                <div className="space-y-2">
                  {SCORE_CRITERIA.map((c) => (
                    <ScoreBar
                      key={c.key}
                      label={c.label}
                      tooltip={c.tooltip}
                      value={
                        selected.score_breakdown[
                          c.key as keyof typeof selected.score_breakdown
                        ]
                      }
                    />
                  ))}
                </div>

                {selected.star_score !== null && (
                  <p className="text-xs text-text-secondary">
                    Score étoiles :{" "}
                    <span className="font-mono text-accent-purple">
                      {(selected.star_score * 10).toFixed(2)}
                    </span>
                  </p>
                )}

                <button
                  onClick={() => toggleFavorite.mutate(selected.id)}
                  className="w-full mt-1 py-1.5 border border-accent-red/50 text-accent-red rounded-md text-xs hover:bg-accent-red/5 transition-colors flex items-center justify-center gap-1.5"
                >
                  <Heart size={13} className="fill-accent-red" />
                  Retirer des favoris
                </button>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
