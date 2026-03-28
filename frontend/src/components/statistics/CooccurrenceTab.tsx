import { useMemo } from "react";
import { useCooccurrences } from "@/hooks/useStatistics";
import LoadingSpinner from "@/components/common/LoadingSpinner";

export default function CooccurrenceTab() {
  const { data: cooccurrences, isLoading } = useCooccurrences();

  const sortedPairs = useMemo(() => {
    if (!cooccurrences) return [];
    return [...cooccurrences.pairs]
      .sort((a, b) => b.affinity - a.affinity);
  }, [cooccurrences]);

  if (isLoading) return <LoadingSpinner />;
  if (!cooccurrences)
    return <p className="text-text-secondary">Aucune donnée de cooccurrence disponible.</p>;

  const topPairs = sortedPairs.slice(0, 20);
  const bottomPairs = sortedPairs.slice(-20).reverse();

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top affinities */}
        <div className="bg-surface rounded-lg border border-border p-4">
          <h3 className="text-sm font-semibold mb-3 text-accent-green">
            Top 20 — Affinités fortes
          </h3>
          <div className="space-y-1">
            {topPairs.map((p) => (
              <div
                key={p.pair}
                className="flex items-center justify-between px-2 py-1.5 rounded hover:bg-surface-hover text-sm"
              >
                <span className="font-mono">{p.pair}</span>
                <div className="flex items-center gap-4">
                  <span className="text-text-secondary">{p.count}×</span>
                  <span className="font-mono text-accent-green w-16 text-right">
                    {p.affinity.toFixed(3)}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Bottom affinities */}
        <div className="bg-surface rounded-lg border border-border p-4">
          <h3 className="text-sm font-semibold mb-3 text-accent-red">
            Bottom 20 — Affinités faibles
          </h3>
          <div className="space-y-1">
            {bottomPairs.map((p) => (
              <div
                key={p.pair}
                className="flex items-center justify-between px-2 py-1.5 rounded hover:bg-surface-hover text-sm"
              >
                <span className="font-mono">{p.pair}</span>
                <div className="flex items-center gap-4">
                  <span className="text-text-secondary">{p.count}×</span>
                  <span className="font-mono text-accent-red w-16 text-right">
                    {p.affinity.toFixed(3)}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Summary */}
      <div className="bg-surface rounded-lg border border-border p-4">
        <h3 className="text-sm font-semibold mb-2">Résumé</h3>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4 text-sm">
          <div>
            <span className="text-text-secondary">Paires totales</span>
            <p className="font-mono">{cooccurrences.pairs.length}</p>
          </div>
          <div>
            <span className="text-text-secondary">Fréquence attendue</span>
            <p className="font-mono">{cooccurrences.expected_pair_count.toFixed(2)}</p>
          </div>
          <div>
            <span className="text-text-secondary">Taille matrice</span>
            <p className="font-mono">{cooccurrences.matrix_shape.join("×")}</p>
          </div>
        </div>
      </div>
    </div>
  );
}
