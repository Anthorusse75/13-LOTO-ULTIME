import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  ErrorBar,
} from "recharts";
import { useBayesian } from "@/hooks/useStatistics";
import LoadingSpinner from "@/components/common/LoadingSpinner";

export default function BayesianTab() {
  const { data: bayesian, isLoading } = useBayesian();

  if (isLoading) return <LoadingSpinner />;
  if (!bayesian || bayesian.length === 0)
    return <p className="text-text-secondary">Aucune donnée bayésienne disponible.</p>;

  const sorted = [...bayesian].sort((a, b) => b.posterior_mean - a.posterior_mean);

  const chartData = sorted.slice(0, 20).map((b) => ({
    number: b.number,
    posterior_mean: b.posterior_mean,
    errorRange: [b.posterior_mean - b.ci_95_low, b.ci_95_high - b.posterior_mean],
  }));

  return (
    <div className="space-y-6">
      {/* Chart */}
      <div className="bg-surface rounded-lg border border-border p-4">
        <h3 className="text-sm font-semibold mb-3">
          Top 20 — Moyennes postérieures (Beta-Binomial)
        </h3>
        <ResponsiveContainer width="100%" height={400}>
          <BarChart data={chartData}>
            <XAxis dataKey="number" tick={{ fill: "#a1a1aa", fontSize: 12 }} />
            <YAxis tick={{ fill: "#a1a1aa", fontSize: 12 }} />
            <Tooltip
              contentStyle={{
                background: "#141416",
                border: "1px solid #27272a",
                borderRadius: 6,
              }}
            />
            <Bar dataKey="posterior_mean" fill="#a855f7" radius={[4, 4, 0, 0]}>
              <ErrorBar dataKey="errorRange" stroke="#a855f7" strokeWidth={1.5} />
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Table */}
      <div className="bg-surface rounded-lg border border-border overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-border bg-surface-hover">
              <th className="px-4 py-2 text-left text-text-secondary">Numéro</th>
              <th className="px-4 py-2 text-right text-text-secondary">α</th>
              <th className="px-4 py-2 text-right text-text-secondary">β</th>
              <th className="px-4 py-2 text-right text-text-secondary">Moy. post.</th>
              <th className="px-4 py-2 text-right text-text-secondary">IC 95% bas</th>
              <th className="px-4 py-2 text-right text-text-secondary">IC 95% haut</th>
              <th className="px-4 py-2 text-right text-text-secondary">Largeur IC</th>
            </tr>
          </thead>
          <tbody>
            {sorted.map((b) => (
              <tr
                key={b.number}
                className="border-b border-border hover:bg-surface-hover"
              >
                <td className="px-4 py-2 font-mono">{b.number}</td>
                <td className="px-4 py-2 text-right font-mono">{b.alpha.toFixed(1)}</td>
                <td className="px-4 py-2 text-right font-mono">{b.beta.toFixed(1)}</td>
                <td className="px-4 py-2 text-right font-mono text-accent-purple">
                  {b.posterior_mean.toFixed(4)}
                </td>
                <td className="px-4 py-2 text-right font-mono">
                  {b.ci_95_low.toFixed(4)}
                </td>
                <td className="px-4 py-2 text-right font-mono">
                  {b.ci_95_high.toFixed(4)}
                </td>
                <td className="px-4 py-2 text-right font-mono text-text-secondary">
                  {b.ci_width.toFixed(4)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
