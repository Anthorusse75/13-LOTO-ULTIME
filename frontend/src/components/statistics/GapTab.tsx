import LoadingSpinner from "@/components/common/LoadingSpinner";
import { useGaps, useStatistics } from "@/hooks/useStatistics";
import { gameService } from "@/services/gameService";
import { useGameStore } from "@/stores/gameStore";
import { useQuery } from "@tanstack/react-query";
import {
  Bar,
  BarChart,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

export default function GapTab() {
  const { data: gaps, isLoading } = useGaps();
  const { data: stats } = useStatistics();
  const slug = useGameStore((s) => s.currentGameSlug);
  const { data: game } = useQuery({
    queryKey: ["game", slug],
    queryFn: () => gameService.getBySlug(slug!),
    enabled: !!slug,
  });

  if (isLoading) return <LoadingSpinner />;
  if (!gaps || gaps.length === 0)
    return (
      <p className="text-text-secondary">Aucune donnée d'écart disponible.</p>
    );

  const sorted = [...gaps].sort((a, b) => b.current_gap - a.current_gap);
  const avgExpected =
    gaps.reduce((s, g) => s + g.expected_gap, 0) / gaps.length;

  // Critical gaps: current_gap > 2 * expected_gap
  const critical = sorted.filter((g) => g.current_gap > 2 * g.expected_gap);

  return (
    <div className="space-y-6">
      {/* Critical gaps alert */}
      {critical.length > 0 && (
        <div className="bg-accent-amber/10 border border-accent-amber/30 rounded-lg p-4">
          <h3 className="text-sm font-semibold text-accent-amber mb-2">
            Écarts critiques ({critical.length})
          </h3>
          <div className="flex gap-2 flex-wrap">
            {critical.map((g) => (
              <span
                key={g.number}
                className="px-2 py-1 bg-accent-amber/20 rounded text-xs font-mono"
              >
                N°{g.number}: {g.current_gap} (moy: {g.expected_gap.toFixed(1)})
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Chart */}
      <div className="bg-surface rounded-lg border border-border p-4">
        <h3 className="text-sm font-semibold mb-3">
          Écarts courants par numéro
        </h3>
        <ResponsiveContainer width="100%" height={350}>
          <BarChart data={sorted.slice(0, 20)}>
            <XAxis
              dataKey="number"
              tick={{ fill: "var(--color-text-secondary)", fontSize: 12 }}
            />
            <YAxis
              tick={{ fill: "var(--color-text-secondary)", fontSize: 12 }}
            />
            <Tooltip
              contentStyle={{
                background: "var(--color-surface)",
                border: "1px solid var(--color-border)",
                borderRadius: 6,
              }}
            />
            <ReferenceLine
              y={avgExpected}
              stroke="var(--color-accent-amber)"
              strokeDasharray="3 3"
              label={{
                value: "Moy. attendue",
                fill: "var(--color-accent-amber)",
                fontSize: 11,
              }}
            />
            <Bar
              dataKey="current_gap"
              fill="var(--color-accent-red)"
              radius={[4, 4, 0, 0]}
            />
          </BarChart>
        </ResponsiveContainer>
        <p className="text-xs text-text-secondary mt-2">
          Écart courant des 20 numéros les plus en retard. La ligne pointillée
          représente la moyenne attendue.
        </p>
      </div>

      {/* Table */}
      <div className="bg-surface rounded-lg border border-border overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-border bg-surface-hover">
              <th className="px-4 py-2 text-left text-text-secondary">
                Numéro
              </th>
              <th className="px-4 py-2 text-right text-text-secondary">
                Écart actuel
              </th>
              <th className="px-4 py-2 text-right text-text-secondary">Max</th>
              <th className="px-4 py-2 text-right text-text-secondary">
                Moyen
              </th>
              <th className="px-4 py-2 text-right text-text-secondary">
                Médian
              </th>
              <th className="px-4 py-2 text-right text-text-secondary">
                Attendu
              </th>
            </tr>
          </thead>
          <tbody>
            {sorted.map((g) => (
              <tr
                key={g.number}
                className="border-b border-border hover:bg-surface-hover"
              >
                <td className="px-4 py-2 font-mono">{g.number}</td>
                <td
                  className={`px-4 py-2 text-right font-mono ${
                    g.current_gap > 2 * g.expected_gap ? "text-accent-red" : ""
                  }`}
                >
                  {g.current_gap}
                </td>
                <td className="px-4 py-2 text-right font-mono">{g.max_gap}</td>
                <td className="px-4 py-2 text-right font-mono">
                  {g.avg_gap.toFixed(1)}
                </td>
                <td className="px-4 py-2 text-right font-mono">
                  {g.median_gap.toFixed(1)}
                </td>
                <td className="px-4 py-2 text-right font-mono text-text-secondary">
                  {g.expected_gap.toFixed(1)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Star / Numéro chance – Gaps */}
      {stats?.star_gaps && stats.star_gaps.length > 0 && game && (
        <div className="space-y-4">
          <h3 className="text-base font-semibold text-purple-400">
            Écarts — {game.star_name ?? "Étoiles"}
          </h3>

          {/* Chart */}
          <div className="bg-surface rounded-lg border border-border p-4">
            <ResponsiveContainer width="100%" height={250}>
              <BarChart
                data={[...stats.star_gaps].sort(
                  (a, b) => b.current_gap - a.current_gap,
                )}
              >
                <XAxis
                  dataKey="number"
                  tick={{
                    fill: "var(--color-text-secondary)",
                    fontSize: 12,
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
                    background: "var(--color-surface)",
                    border: "1px solid var(--color-border)",
                    borderRadius: 6,
                  }}
                />
                <Bar
                  dataKey="current_gap"
                  fill="#a855f7"
                  radius={[4, 4, 0, 0]}
                />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Table */}
          <div className="bg-surface rounded-lg border border-border overflow-hidden">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border bg-surface-hover">
                  <th className="px-4 py-2 text-left text-text-secondary">
                    {game.star_name ?? "Étoile"}
                  </th>
                  <th className="px-4 py-2 text-right text-text-secondary">
                    Écart actuel
                  </th>
                  <th className="px-4 py-2 text-right text-text-secondary">
                    Max
                  </th>
                  <th className="px-4 py-2 text-right text-text-secondary">
                    Moyen
                  </th>
                  <th className="px-4 py-2 text-right text-text-secondary">
                    Médian
                  </th>
                  <th className="px-4 py-2 text-right text-text-secondary">
                    Attendu
                  </th>
                </tr>
              </thead>
              <tbody>
                {[...stats.star_gaps]
                  .sort((a, b) => b.current_gap - a.current_gap)
                  .map((g) => {
                    const starName = `${game.star_name ?? "Étoile"} ${g.number}`;
                    return (
                      <tr
                        key={g.number}
                        className="border-b border-border hover:bg-surface-hover"
                      >
                        <td className="px-4 py-2">
                          <span className="inline-flex items-center gap-1.5">
                            <span className="w-6 h-6 rounded-full bg-purple-500/20 text-purple-400 text-xs font-mono flex items-center justify-center">
                              {g.number}
                            </span>
                            {starName}
                          </span>
                        </td>
                        <td
                          className={`px-4 py-2 text-right font-mono ${
                            g.current_gap > 2 * g.expected_gap
                              ? "text-accent-red"
                              : ""
                          }`}
                        >
                          {g.current_gap}
                        </td>
                        <td className="px-4 py-2 text-right font-mono">
                          {g.max_gap}
                        </td>
                        <td className="px-4 py-2 text-right font-mono">
                          {g.avg_gap.toFixed(1)}
                        </td>
                        <td className="px-4 py-2 text-right font-mono">
                          {g.median_gap.toFixed(1)}
                        </td>
                        <td className="px-4 py-2 text-right font-mono text-text-secondary">
                          {g.expected_gap.toFixed(1)}
                        </td>
                      </tr>
                    );
                  })}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
