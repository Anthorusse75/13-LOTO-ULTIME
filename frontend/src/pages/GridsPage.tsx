import { useState } from "react";
import { useGenerateGrids, useTopGrids } from "@/hooks/useGrids";
import DrawBalls from "@/components/draws/DrawBalls";
import ScoreBar from "@/components/grids/ScoreBar";
import LoadingSpinner from "@/components/common/LoadingSpinner";
import { formatScore } from "@/utils/formatters";
import {
  OPTIMIZATION_METHODS,
  SCORING_PROFILES,
  SCORE_CRITERIA,
} from "@/utils/constants";
import type { GridScoreResponse } from "@/types/grid";
import { Loader2 } from "lucide-react";

export default function GridsPage() {
  const [count, setCount] = useState(10);
  const [method, setMethod] = useState("auto");
  const [profile, setProfile] = useState("equilibre");
  const [selectedGrid, setSelectedGrid] = useState<GridScoreResponse | null>(null);

  const { data: topGrids, isLoading: topLoading } = useTopGrids(10);
  const generateMutation = useGenerateGrids();

  const handleGenerate = () => {
    generateMutation.mutate({ count, method, profile });
  };

  const grids = generateMutation.data?.grids ?? [];

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Grilles</h1>

      {/* Generation form */}
      <div className="bg-surface rounded-lg border border-border p-6">
        <h2 className="text-sm font-semibold mb-4">Générer des grilles</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
          <div>
            <label className="text-xs text-text-secondary block mb-1">
              Nombre de grilles
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
          </div>
          <div>
            <label className="text-xs text-text-secondary block mb-1">
              Profil de scoring
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
          </div>
        </div>
        <button
          onClick={handleGenerate}
          disabled={generateMutation.isPending}
          className="px-6 py-2 bg-accent-blue text-white rounded-md text-sm font-medium hover:bg-accent-blue/90 disabled:opacity-50 flex items-center gap-2"
        >
          {generateMutation.isPending && <Loader2 size={16} className="animate-spin" />}
          Générer
        </button>

        {generateMutation.data && (
          <p className="text-xs text-text-secondary mt-2">
            {generateMutation.data.grids.length} grilles générées en{" "}
            {generateMutation.data.computation_time_ms.toFixed(0)}ms — méthode:{" "}
            {generateMutation.data.method_used}
          </p>
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
                <span className="text-xs text-text-secondary w-6">#{i + 1}</span>
                <DrawBalls numbers={g.numbers} stars={g.stars} size="sm" />
                <span className="ml-auto font-mono text-accent-green">
                  {formatScore(g.total_score)}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Grid detail */}
      {selectedGrid && (
        <div className="bg-surface rounded-lg border border-border p-6">
          <h2 className="text-sm font-semibold mb-4">
            Détail — Score: {formatScore(selectedGrid.total_score)}/10
          </h2>
          <div className="mb-4">
            <DrawBalls numbers={selectedGrid.numbers} stars={selectedGrid.stars} size="lg" />
          </div>
          <div className="space-y-2">
            {SCORE_CRITERIA.map((c) => (
              <ScoreBar
                key={c.key}
                label={c.label}
                value={selectedGrid.score_breakdown[c.key as keyof typeof selectedGrid.score_breakdown]}
              />
            ))}
          </div>
          {selectedGrid.star_score !== null && (
            <p className="text-sm text-text-secondary mt-3">
              Score étoiles:{" "}
              <span className="font-mono text-accent-purple">
                {(selectedGrid.star_score * 10).toFixed(2)}
              </span>
            </p>
          )}
        </div>
      )}

      {/* Top grids from DB */}
      <div className="bg-surface rounded-lg border border-border p-4">
        <h2 className="text-sm font-semibold mb-4">Top 10 — Meilleures grilles</h2>
        {topLoading ? (
          <LoadingSpinner />
        ) : topGrids && topGrids.length > 0 ? (
          <div className="space-y-2">
            {topGrids.map((g, i) => (
              <div
                key={g.id}
                className="flex items-center gap-4 p-2 rounded-md hover:bg-surface-hover"
              >
                <span className="text-xs text-text-secondary w-6">#{i + 1}</span>
                <DrawBalls numbers={g.numbers} stars={g.stars} size="sm" />
                <span className="text-xs text-text-secondary">{g.method}</span>
                <span className="ml-auto font-mono text-accent-green">
                  {formatScore(g.total_score)}
                </span>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-text-secondary text-sm">Aucune grille en base</p>
        )}
      </div>
    </div>
  );
}
