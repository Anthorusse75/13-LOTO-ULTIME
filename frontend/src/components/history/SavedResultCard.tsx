import DrawBalls from "@/components/draws/DrawBalls";
import {
  useDeleteSavedResult,
  useDuplicateSavedResult,
  useToggleSavedFavorite,
} from "@/hooks/useHistory";
import type { SavedResult } from "@/types/history";
import { formatScore } from "@/utils/formatters";
import { ChevronDown, ChevronUp, Copy, Heart, Trash2 } from "lucide-react";
import { useState } from "react";

const TYPE_LABELS: Record<string, string> = {
  grid: "Grille",
  portfolio: "Portfolio",
  wheeling: "Wheeling",
  budget_plan: "Plan budget",
  comparison: "Comparaison",
  simulation: "Simulation",
};

interface SavedResultCardProps {
  result: SavedResult;
}

/* ── Render the actual result_data depending on type ── */

function GridDetail({
  data,
  params,
}: {
  data: Record<string, unknown>;
  params: Record<string, unknown>;
}) {
  const numbers = (data.numbers as number[]) ?? [];
  const stars = (data.stars as number[] | null) ?? undefined;
  const score = data.total_score as number | undefined;
  const breakdown = data.score_breakdown as Record<string, number> | undefined;

  return (
    <div className="space-y-3">
      <div className="flex items-center gap-3">
        <DrawBalls numbers={numbers} stars={stars} size="md" />
        {score != null && (
          <span className="font-mono text-accent-green text-sm">
            {formatScore(score)}/10
          </span>
        )}
      </div>
      {breakdown && (
        <div className="grid grid-cols-3 gap-x-4 gap-y-1 text-xs text-text-secondary">
          {Object.entries(breakdown).map(([k, v]) => (
            <div key={k} className="flex justify-between">
              <span className="capitalize">{k.replace("_", " ")}</span>
              <span className="font-mono">{(v as number).toFixed(2)}</span>
            </div>
          ))}
        </div>
      )}
      {params.method && (
        <p className="text-xs text-text-secondary">
          Méthode : {params.method as string} | Profil :{" "}
          {(params.profile as string) ?? "—"}
        </p>
      )}
    </div>
  );
}

function PortfolioDetail({
  data,
  params,
}: {
  data: Record<string, unknown>;
  params: Record<string, unknown>;
}) {
  const grids =
    (data.grids as Array<{
      numbers: number[];
      stars?: number[] | null;
      score: number;
    }>) ?? [];
  const diversity = data.diversity_score as number | undefined;
  const coverage = data.coverage_score as number | undefined;
  const avgScore = data.avg_grid_score as number | undefined;

  return (
    <div className="space-y-3">
      {/* KPIs */}
      <div className="flex flex-wrap gap-4 text-xs">
        {avgScore != null && (
          <div>
            <span className="text-text-secondary">Score moyen </span>
            <span className="font-mono text-accent-green">
              {formatScore(avgScore)}/10
            </span>
          </div>
        )}
        {diversity != null && (
          <div>
            <span className="text-text-secondary">Diversité </span>
            <span className="font-mono">{(diversity * 100).toFixed(1)}%</span>
          </div>
        )}
        {coverage != null && (
          <div>
            <span className="text-text-secondary">Couverture </span>
            <span className="font-mono">{(coverage * 100).toFixed(1)}%</span>
          </div>
        )}
        {params.strategy && (
          <div>
            <span className="text-text-secondary">Stratégie </span>
            <span className="font-mono">{params.strategy as string}</span>
          </div>
        )}
      </div>

      {/* Grids list */}
      <div className="space-y-1.5">
        <p className="text-xs text-text-secondary font-semibold">
          {grids.length} grilles :
        </p>
        {grids.map((g, i) => (
          <div key={i} className="flex items-center gap-3 py-1">
            <span className="text-xs text-text-secondary w-5">#{i + 1}</span>
            <DrawBalls
              numbers={g.numbers}
              stars={g.stars ?? undefined}
              size="sm"
            />
            <span className="ml-auto font-mono text-accent-green text-xs">
              {formatScore(g.score)}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

function SimulationDetail({ data }: { data: Record<string, unknown> }) {
  const avgMatches = data.avg_matches as number | undefined;
  const expected = data.expected_matches as number | undefined;
  const nSims = data.n_simulations as number | undefined;
  const distribution = data.match_distribution as
    | Record<string, number>
    | undefined;

  return (
    <div className="space-y-2 text-xs">
      <div className="flex flex-wrap gap-4">
        {nSims != null && (
          <div>
            <span className="text-text-secondary">Simulations </span>
            <span className="font-mono">{nSims.toLocaleString("fr-FR")}</span>
          </div>
        )}
        {avgMatches != null && (
          <div>
            <span className="text-text-secondary">Moyenne matches </span>
            <span className="font-mono">{avgMatches.toFixed(2)}</span>
          </div>
        )}
        {expected != null && (
          <div>
            <span className="text-text-secondary">Espérance </span>
            <span className="font-mono">{expected.toFixed(2)}</span>
          </div>
        )}
      </div>
      {distribution && (
        <div className="flex flex-wrap gap-2">
          {Object.entries(distribution)
            .sort(([a], [b]) => Number(a) - Number(b))
            .map(([k, v]) => (
              <div key={k} className="bg-surface-hover rounded px-2 py-1">
                <span className="text-text-secondary">
                  {k} match{Number(k) > 1 ? "es" : ""}{" "}
                </span>
                <span className="font-mono">
                  {(v as number).toLocaleString("fr-FR")}
                </span>
              </div>
            ))}
        </div>
      )}
    </div>
  );
}

function GenericDetail({
  data,
  params,
}: {
  data: Record<string, unknown>;
  params: Record<string, unknown>;
}) {
  const entries = Object.entries({ ...params, ...data }).filter(
    ([, v]) => typeof v !== "object" || v === null,
  );
  return (
    <div className="grid grid-cols-2 gap-x-4 gap-y-1 text-xs text-text-secondary">
      {entries.map(([k, v]) => (
        <div key={k} className="flex justify-between">
          <span className="capitalize">{k.replace(/_/g, " ")}</span>
          <span className="font-mono">{String(v)}</span>
        </div>
      ))}
    </div>
  );
}

function ResultDataView({ result }: { result: SavedResult }) {
  const data = result.result_data;
  const params = result.parameters;

  switch (result.result_type) {
    case "grid":
      return <GridDetail data={data} params={params} />;
    case "portfolio":
      return <PortfolioDetail data={data} params={params} />;
    case "simulation":
      return <SimulationDetail data={data} />;
    default:
      return <GenericDetail data={data} params={params} />;
  }
}

/* ── Main card ── */

export default function SavedResultCard({ result }: SavedResultCardProps) {
  const [expanded, setExpanded] = useState(false);
  const deleteMutation = useDeleteSavedResult();
  const toggleFavorite = useToggleSavedFavorite();
  const duplicateMutation = useDuplicateSavedResult();

  return (
    <div className="bg-surface rounded-lg border border-border overflow-hidden">
      {/* Header row — clickable to expand */}
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-start justify-between gap-3 p-4 text-left hover:bg-surface-hover/50 transition-colors"
      >
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="text-xs font-medium px-2 py-0.5 rounded-full bg-accent-blue/10 text-accent-blue">
              {TYPE_LABELS[result.result_type] ?? result.result_type}
            </span>
            {result.name && (
              <span className="text-sm font-medium truncate">
                {result.name}
              </span>
            )}
          </div>
          <p className="text-xs text-text-secondary mt-1">
            {new Date(result.created_at).toLocaleDateString("fr-FR", {
              day: "numeric",
              month: "short",
              year: "numeric",
              hour: "2-digit",
              minute: "2-digit",
            })}
          </p>
          {/* Tags inline */}
          {result.tags.length > 0 && (
            <div className="flex gap-1 flex-wrap mt-1">
              {result.tags.map((tag) => (
                <span
                  key={tag}
                  className="text-[10px] px-1.5 py-0.5 rounded bg-surface-hover text-text-secondary"
                >
                  #{tag}
                </span>
              ))}
            </div>
          )}
        </div>

        <div className="flex items-center gap-1 shrink-0">
          <span
            onClick={(e) => {
              e.stopPropagation();
              toggleFavorite.mutate(result.id);
            }}
            title={
              result.is_favorite ? "Retirer des favoris" : "Ajouter aux favoris"
            }
            className="p-1.5 rounded hover:bg-surface-hover transition-colors cursor-pointer"
            role="button"
          >
            <Heart
              size={14}
              className={
                result.is_favorite
                  ? "fill-accent-red text-accent-red"
                  : "text-text-secondary"
              }
            />
          </span>
          <span
            onClick={(e) => {
              e.stopPropagation();
              duplicateMutation.mutate(result.id);
            }}
            title="Dupliquer"
            className="p-1.5 rounded hover:bg-surface-hover transition-colors cursor-pointer"
            role="button"
          >
            <Copy size={14} className="text-text-secondary" />
          </span>
          <span
            onClick={(e) => {
              e.stopPropagation();
              deleteMutation.mutate(result.id);
            }}
            title="Supprimer"
            className="p-1.5 rounded hover:bg-surface-hover transition-colors hover:text-accent-red cursor-pointer"
            role="button"
          >
            <Trash2 size={14} className="text-text-secondary" />
          </span>
          {expanded ? (
            <ChevronUp size={14} className="text-text-secondary ml-1" />
          ) : (
            <ChevronDown size={14} className="text-text-secondary ml-1" />
          )}
        </div>
      </button>

      {/* Expanded detail */}
      {expanded && (
        <div className="px-4 pb-4 pt-0 border-t border-border/50">
          <div className="pt-3">
            <ResultDataView result={result} />
          </div>
        </div>
      )}
    </div>
  );
}
