import LoadingSpinner from "@/components/common/LoadingSpinner";
import { useFrequencies, useStatistics } from "@/hooks/useStatistics";
import { gameService } from "@/services/gameService";
import { useGameStore } from "@/stores/gameStore";
import { useQuery } from "@tanstack/react-query";
import {
  Bar,
  BarChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import NumberHeatmap from "./NumberHeatmap";

export default function FrequencyTab({ lastN }: { lastN?: number }) {
  const { data: freqs, isLoading } = useFrequencies(lastN);
  const { data: stats } = useStatistics();
  const slug = useGameStore((s) => s.currentGameSlug);
  const { data: game } = useQuery({
    queryKey: ["game", slug],
    queryFn: () => gameService.getBySlug(slug!),
    enabled: !!slug,
  });

  if (isLoading) return <LoadingSpinner />;
  if (!freqs || freqs.length === 0)
    return (
      <p className="text-text-secondary">
        Aucune donnée de fréquence disponible.
      </p>
    );

  const sorted = [...freqs].sort((a, b) => b.relative - a.relative);
  const top10 = sorted.slice(0, 10);
  const bottom10 = sorted.slice(-10).reverse();

  const heatmapData: Record<number, number> = {};
  freqs.forEach((f) => {
    heatmapData[f.number] = f.relative;
  });

  return (
    <div className="space-y-6">
      {/* Heatmap */}
      {game && (
        <div className="bg-surface rounded-lg border border-border p-4">
          <h3 className="text-sm font-semibold mb-3">Heatmap des fréquences</h3>
          <NumberHeatmap
            data={heatmapData}
            minNumber={game.min_number}
            maxNumber={game.max_number}
            colorScale="frequency"
          />
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top frequencies */}
        <div className="bg-surface rounded-lg border border-border p-4">
          <h3 className="text-sm font-semibold mb-3">Top 10 fréquences</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={top10} layout="vertical">
              <XAxis
                type="number"
                tick={{ fill: "var(--color-text-secondary)", fontSize: 12 }}
              />
              <YAxis
                type="category"
                dataKey="number"
                tick={{ fill: "var(--color-text-secondary)", fontSize: 12 }}
                width={30}
              />
              <Tooltip
                contentStyle={{
                  background: "var(--color-surface)",
                  border: "1px solid var(--color-border)",
                  borderRadius: 6,
                }}
              />
              <Bar
                dataKey="relative"
                fill="var(--color-accent-green)"
                radius={[0, 4, 4, 0]}
              />
            </BarChart>
          </ResponsiveContainer>
          <p className="text-xs text-text-secondary mt-2">
            Fréquence relative des 10 numéros les plus tirés.
          </p>
        </div>

        {/* Bottom frequencies */}
        <div className="bg-surface rounded-lg border border-border p-4">
          <h3 className="text-sm font-semibold mb-3">Bottom 10 fréquences</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={bottom10} layout="vertical">
              <XAxis
                type="number"
                tick={{ fill: "var(--color-text-secondary)", fontSize: 12 }}
              />
              <YAxis
                type="category"
                dataKey="number"
                tick={{ fill: "var(--color-text-secondary)", fontSize: 12 }}
                width={30}
              />
              <Tooltip
                contentStyle={{
                  background: "var(--color-surface)",
                  border: "1px solid var(--color-border)",
                  borderRadius: 6,
                }}
              />
              <Bar
                dataKey="relative"
                fill="var(--color-accent-red)"
                radius={[0, 4, 4, 0]}
              />
            </BarChart>
          </ResponsiveContainer>
          <p className="text-xs text-text-secondary mt-2">
            Fréquence relative des 10 numéros les moins tirés.
          </p>
        </div>
      </div>

      {/* Full table */}
      <div className="bg-surface rounded-lg border border-border overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-border bg-surface-hover">
              <th className="px-4 py-2 text-left text-text-secondary">
                Numéro
              </th>
              <th className="px-4 py-2 text-right text-text-secondary">
                Tirages
              </th>
              <th className="px-4 py-2 text-right text-text-secondary">
                Fréquence
              </th>
              <th className="px-4 py-2 text-right text-text-secondary">
                Ratio
              </th>
              <th className="px-4 py-2 text-right text-text-secondary">
                Dernier vu
              </th>
            </tr>
          </thead>
          <tbody>
            {sorted.map((f) => (
              <tr
                key={f.number}
                className="border-b border-border hover:bg-surface-hover"
              >
                <td className="px-4 py-2 font-mono">{f.number}</td>
                <td className="px-4 py-2 text-right font-mono">{f.count}</td>
                <td className="px-4 py-2 text-right font-mono">
                  {f.relative.toFixed(4)}
                </td>
                <td className="px-4 py-2 text-right font-mono">
                  {f.ratio.toFixed(3)}
                </td>
                <td className="px-4 py-2 text-right font-mono text-text-secondary">
                  il y a {f.last_seen} tirages
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Star / Numéro Chance Frequencies */}
      {stats?.star_frequencies && stats.star_frequencies.length > 0 && (
        <div className="space-y-4">
          <h2 className="text-lg font-semibold flex items-center gap-2">
            <span className="inline-flex items-center justify-center w-6 h-6 rounded-full bg-accent-purple/20 text-accent-purple text-xs">
              ★
            </span>
            Fréquences {game?.star_name ?? "Étoiles / N° Chance"}
          </h2>
          <div className="bg-surface rounded-lg border border-accent-purple/30 p-4">
            <ResponsiveContainer width="100%" height={250}>
              <BarChart
                data={[...stats.star_frequencies].sort(
                  (a, b) => a.number - b.number,
                )}
              >
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
                <Bar
                  dataKey="count"
                  fill="var(--color-accent-purple)"
                  radius={[4, 4, 0, 0]}
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <div className="bg-surface rounded-lg border border-border overflow-hidden">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border bg-surface-hover">
                  <th className="px-4 py-2 text-left text-text-secondary">
                    {game?.star_name ?? "Étoile"}
                  </th>
                  <th className="px-4 py-2 text-right text-text-secondary">
                    Tirages
                  </th>
                  <th className="px-4 py-2 text-right text-text-secondary">
                    Fréquence
                  </th>
                  <th className="px-4 py-2 text-right text-text-secondary">
                    Ratio
                  </th>
                  <th className="px-4 py-2 text-right text-text-secondary">
                    Dernier vu
                  </th>
                </tr>
              </thead>
              <tbody>
                {[...stats.star_frequencies]
                  .sort((a, b) => b.count - a.count)
                  .map((f) => (
                    <tr
                      key={f.number}
                      className="border-b border-border hover:bg-surface-hover"
                    >
                      <td className="px-4 py-2 font-mono">
                        <span className="inline-flex items-center justify-center w-7 h-7 rounded-full bg-accent-purple/20 text-accent-purple text-sm font-bold">
                          {f.number}
                        </span>
                      </td>
                      <td className="px-4 py-2 text-right font-mono">
                        {f.count}
                      </td>
                      <td className="px-4 py-2 text-right font-mono">
                        {f.relative.toFixed(4)}
                      </td>
                      <td className="px-4 py-2 text-right font-mono">
                        {f.ratio.toFixed(3)}
                      </td>
                      <td className="px-4 py-2 text-right font-mono text-text-secondary">
                        il y a {f.last_seen} tirages
                      </td>
                    </tr>
                  ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
