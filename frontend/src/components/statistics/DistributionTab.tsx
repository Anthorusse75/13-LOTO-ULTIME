import { useDistribution } from "@/hooks/useStatistics";
import LoadingSpinner from "@/components/common/LoadingSpinner";
import { CheckCircle, XCircle } from "lucide-react";

export default function DistributionTab() {
  const { data: dist, isLoading } = useDistribution();

  if (isLoading) return <LoadingSpinner />;
  if (!dist)
    return <p className="text-text-secondary">Aucune donnée de distribution disponible.</p>;

  return (
    <div className="space-y-6">
      {/* Summary cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard label="Entropie" value={dist.entropy.toFixed(4)} />
        <StatCard label="Entropie max" value={dist.max_entropy.toFixed(4)} />
        <StatCard
          label="Uniformité"
          value={`${(dist.uniformity_score * 100).toFixed(1)}%`}
        />
        <div className="bg-surface rounded-lg border border-border p-4">
          <p className="text-xs text-text-secondary">Test Chi-2</p>
          <div className="flex items-center gap-2 mt-1">
            {dist.is_uniform ? (
              <CheckCircle size={16} className="text-accent-green" />
            ) : (
              <XCircle size={16} className="text-accent-red" />
            )}
            <span className="font-mono text-sm">
              p={dist.chi2_pvalue.toFixed(4)}
            </span>
          </div>
          <p className="text-xs text-text-secondary mt-1">
            χ²={dist.chi2_statistic.toFixed(2)}
          </p>
        </div>
      </div>

      {/* Sum stats */}
      <div className="bg-surface rounded-lg border border-border p-4">
        <h3 className="text-sm font-semibold mb-3">Statistiques des sommes</h3>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4 text-sm">
          <StatCard label="Moyenne" value={dist.sum_stats.mean.toFixed(1)} />
          <StatCard label="Écart-type" value={dist.sum_stats.std.toFixed(1)} />
          <StatCard label="Min" value={String(dist.sum_stats.min)} />
          <StatCard label="Max" value={String(dist.sum_stats.max)} />
          <StatCard label="Médiane" value={dist.sum_stats.median.toFixed(1)} />
        </div>
      </div>

      {/* Even/Odd */}
      <div className="bg-surface rounded-lg border border-border p-4">
        <h3 className="text-sm font-semibold mb-3">Distribution Pair/Impair</h3>
        <div className="grid grid-cols-2 gap-4 text-sm">
          <StatCard
            label="Pairs (moy)"
            value={dist.even_odd_distribution.mean_even.toFixed(2)}
          />
          <StatCard
            label="Impairs (moy)"
            value={dist.even_odd_distribution.mean_odd.toFixed(2)}
          />
        </div>
      </div>

      {/* Decades */}
      <div className="bg-surface rounded-lg border border-border p-4">
        <h3 className="text-sm font-semibold mb-3">Distribution par décade</h3>
        <div className="flex flex-wrap gap-3">
          {Object.entries(dist.decades).map(([decade, count]) => (
            <div
              key={decade}
              className="bg-surface-hover rounded-md px-3 py-2 text-sm"
            >
              <span className="text-text-secondary">{decade}:</span>{" "}
              <span className="font-mono">{count}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function StatCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="bg-surface rounded-lg border border-border p-4">
      <p className="text-xs text-text-secondary">{label}</p>
      <p className="font-mono text-lg mt-1">{value}</p>
    </div>
  );
}
