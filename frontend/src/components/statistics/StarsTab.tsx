import LoadingSpinner from "@/components/common/LoadingSpinner";
import { useStatistics } from "@/hooks/useStatistics";
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

export default function StarsTab() {
  const { data: stats, isLoading } = useStatistics();
  const slug = useGameStore((s) => s.currentGameSlug);
  const { data: game } = useQuery({
    queryKey: ["game", slug],
    queryFn: () => gameService.getBySlug(slug!),
    enabled: !!slug,
  });

  if (isLoading) return <LoadingSpinner />;

  const starName = game?.star_name ?? "Étoile";
  const pluralName =
    starName === "numéro chance" ? "numéros chance" : `${starName}s`;

  if (!stats?.star_frequencies || stats.star_frequencies.length === 0) {
    return (
      <div className="text-center py-12 text-text-secondary space-y-2">
        <p className="text-lg font-medium">Aucune statistique disponible</p>
        <p className="text-sm">
          Lancez un recalcul depuis Administration pour générer les statistiques
          des {pluralName}.
        </p>
      </div>
    );
  }

  const freqSorted = [...stats.star_frequencies].sort(
    (a, b) => a.number - b.number,
  );
  const gapSorted = stats.star_gaps
    ? [...stats.star_gaps].sort((a, b) => b.current_gap - a.current_gap)
    : [];

  return (
    <div className="space-y-8">
      {/* ── SECTION FRÉQUENCES ── */}
      <section className="space-y-4">
        <h2 className="text-base font-semibold flex items-center gap-2">
          <span className="inline-flex items-center justify-center w-6 h-6 rounded-full bg-accent-purple/20 text-accent-purple text-xs font-bold">
            ★
          </span>
          Fréquences des {pluralName}
        </h2>

        {/* Bar chart – frequency */}
        <div className="bg-surface rounded-lg border border-accent-purple/30 p-4">
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={freqSorted}>
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
                formatter={(v) => [v as number, "Tirages"]}
              />
              <Bar
                dataKey="count"
                fill="var(--color-accent-purple)"
                radius={[4, 4, 0, 0]}
              />
            </BarChart>
          </ResponsiveContainer>
          <p className="text-xs text-text-secondary mt-2">
            Nombre de fois où chaque {starName} a été tiré(e).
          </p>
        </div>

        {/* Frequency table */}
        <div className="bg-surface rounded-lg border border-border overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border bg-surface-hover">
                <th className="px-4 py-2 text-left text-text-secondary capitalize">
                  {starName}
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
              {[...freqSorted]
                .sort((a, b) => b.count - a.count)
                .map((f) => (
                  <tr
                    key={f.number}
                    className="border-b border-border hover:bg-surface-hover"
                  >
                    <td className="px-4 py-2">
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
      </section>

      {/* ── SECTION ÉCARTS ── */}
      {gapSorted.length > 0 && (
        <section className="space-y-4">
          <h2 className="text-base font-semibold flex items-center gap-2">
            <span className="inline-flex items-center justify-center w-6 h-6 rounded-full bg-accent-purple/20 text-accent-purple text-xs font-bold">
              ★
            </span>
            Écarts (retards) des {pluralName}
          </h2>

          {/* Bar chart – current gap */}
          <div className="bg-surface rounded-lg border border-accent-purple/30 p-4">
            <ResponsiveContainer width="100%" height={260}>
              <BarChart data={gapSorted}>
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
                  formatter={(v, name) => [
                    v as number,
                    name === "current_gap"
                      ? "Écart actuel"
                      : name === "expected_gap"
                        ? "Écart attendu"
                        : String(name),
                  ]}
                />
                <ReferenceLine
                  y={
                    gapSorted.length > 0
                      ? Math.round(
                          gapSorted.reduce((s, g) => s + g.expected_gap, 0) /
                            gapSorted.length,
                        )
                      : 0
                  }
                  stroke="var(--color-accent-purple)"
                  strokeDasharray="4 2"
                  label={{
                    value: "Écart moyen attendu",
                    fill: "var(--color-text-secondary)",
                    fontSize: 11,
                  }}
                />
                <Bar
                  dataKey="current_gap"
                  fill="var(--color-accent-purple)"
                  radius={[4, 4, 0, 0]}
                />
              </BarChart>
            </ResponsiveContainer>
            <p className="text-xs text-text-secondary mt-2">
              Nombre de tirages depuis la dernière apparition de chaque{" "}
              {starName}. La ligne pointillée indique l'écart théorique attendu.
            </p>
          </div>

          {/* Gap table */}
          <div className="bg-surface rounded-lg border border-border overflow-hidden">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border bg-surface-hover">
                  <th className="px-4 py-2 text-left text-text-secondary capitalize">
                    {starName}
                  </th>
                  <th className="px-4 py-2 text-right text-text-secondary">
                    Écart actuel
                  </th>
                  <th className="px-4 py-2 text-right text-text-secondary">
                    Max historique
                  </th>
                  <th className="px-4 py-2 text-right text-text-secondary">
                    Moyenne
                  </th>
                  <th className="px-4 py-2 text-right text-text-secondary">
                    Médiane
                  </th>
                  <th className="px-4 py-2 text-right text-text-secondary">
                    Attendu
                  </th>
                </tr>
              </thead>
              <tbody>
                {gapSorted.map((g) => (
                  <tr
                    key={g.number}
                    className="border-b border-border hover:bg-surface-hover"
                  >
                    <td className="px-4 py-2">
                      <span className="inline-flex items-center gap-2">
                        <span className="w-7 h-7 rounded-full bg-accent-purple/20 text-accent-purple text-sm font-bold flex items-center justify-center">
                          {g.number}
                        </span>
                        <span className="text-text-secondary text-xs capitalize">
                          {starName} {g.number}
                        </span>
                      </span>
                    </td>
                    <td
                      className={`px-4 py-2 text-right font-mono font-semibold ${
                        g.current_gap > 2 * g.expected_gap
                          ? "text-accent-red"
                          : g.current_gap < 0.5 * g.expected_gap
                            ? "text-accent-green"
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
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}
    </div>
  );
}
