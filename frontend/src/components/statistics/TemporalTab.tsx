import { useTemporal } from "@/hooks/useStatistics";
import LoadingSpinner from "@/components/common/LoadingSpinner";
import { TrendingUp, TrendingDown, Minus } from "lucide-react";

export default function TemporalTab() {
  const { data: temporal, isLoading } = useTemporal();

  if (isLoading) return <LoadingSpinner />;
  if (!temporal)
    return <p className="text-text-secondary">Aucune donnée temporelle disponible.</p>;

  return (
    <div className="space-y-6">
      {/* Windows */}
      {temporal.windows.map((w) => (
        <div
          key={w.window_size}
          className="bg-surface rounded-lg border border-border p-4"
        >
          <h3 className="text-sm font-semibold mb-3">
            Fenêtre : {w.window_size} derniers tirages
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <h4 className="text-xs text-accent-green flex items-center gap-1 mb-2">
                <TrendingUp size={14} /> Hot numbers
              </h4>
              <div className="space-y-1">
                {w.hot_numbers.map((n) => (
                  <div
                    key={n.number}
                    className="flex items-center justify-between text-sm px-2 py-1 rounded hover:bg-surface-hover"
                  >
                    <span className="font-mono">{n.number}</span>
                    <div className="flex gap-3">
                      <span className="font-mono">{n.freq.toFixed(3)}</span>
                      <span
                        className={`font-mono text-xs ${
                          n.delta > 0 ? "text-accent-green" : "text-accent-red"
                        }`}
                      >
                        {n.delta > 0 ? "+" : ""}
                        {n.delta.toFixed(3)}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
            <div>
              <h4 className="text-xs text-accent-red flex items-center gap-1 mb-2">
                <TrendingDown size={14} /> Cold numbers
              </h4>
              <div className="space-y-1">
                {w.cold_numbers.map((n) => (
                  <div
                    key={n.number}
                    className="flex items-center justify-between text-sm px-2 py-1 rounded hover:bg-surface-hover"
                  >
                    <span className="font-mono">{n.number}</span>
                    <div className="flex gap-3">
                      <span className="font-mono">{n.freq.toFixed(3)}</span>
                      <span
                        className={`font-mono text-xs ${
                          n.delta > 0 ? "text-accent-green" : "text-accent-red"
                        }`}
                      >
                        {n.delta > 0 ? "+" : ""}
                        {n.delta.toFixed(3)}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      ))}

      {/* Momentum */}
      {Object.keys(temporal.momentum).length > 0 && (
        <div className="bg-surface rounded-lg border border-border p-4">
          <h3 className="text-sm font-semibold mb-3">Momentum (régression linéaire)</h3>
          <div className="flex flex-wrap gap-2">
            {Object.entries(temporal.momentum)
              .sort(([, a], [, b]) => Math.abs(b) - Math.abs(a))
              .slice(0, 20)
              .map(([num, val]) => (
                <div
                  key={num}
                  className={`flex items-center gap-1 px-2 py-1 rounded text-xs font-mono ${
                    val > 0.01
                      ? "bg-accent-green/10 text-accent-green"
                      : val < -0.01
                        ? "bg-accent-red/10 text-accent-red"
                        : "bg-surface-hover text-text-secondary"
                  }`}
                >
                  {val > 0.01 ? (
                    <TrendingUp size={12} />
                  ) : val < -0.01 ? (
                    <TrendingDown size={12} />
                  ) : (
                    <Minus size={12} />
                  )}
                  {num}: {val > 0 ? "+" : ""}
                  {val.toFixed(4)}
                </div>
              ))}
          </div>
        </div>
      )}
    </div>
  );
}
