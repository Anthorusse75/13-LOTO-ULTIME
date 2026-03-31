import type { StrategyMetrics } from "@/types/comparison";
import { useMemo } from "react";
import {
  CartesianGrid,
  ResponsiveContainer,
  Scatter,
  ScatterChart,
  Tooltip,
  XAxis,
  YAxis,
  ZAxis,
  Cell,
} from "recharts";

const COLORS = ["#3B82F6", "#10B981", "#F59E0B", "#EF4444", "#8B5CF6"];

interface Props {
  strategies: StrategyMetrics[];
}

export default function ComparisonScatter({ strategies }: Props) {
  const data = useMemo(() => {
    return strategies
      .filter((s) => s.cost > 0)
      .map((s, idx) => ({
        name: s.label,
        cost: s.cost,
        score: s.avg_score ?? 0,
        coverage: (s.coverage ?? 0) * 100,
        idx,
      }));
  }, [strategies]);

  if (data.length < 2) return null;

  return (
    <div className="rounded-xl border border-border-primary bg-bg-secondary p-4">
      <h3 className="text-sm font-semibold text-text-primary mb-3">
        Coût vs Score moyen
      </h3>
      <ResponsiveContainer width="100%" height={300}>
        <ScatterChart margin={{ top: 10, right: 20, bottom: 10, left: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border-primary)" />
          <XAxis
            dataKey="cost"
            name="Coût (€)"
            type="number"
            tick={{ fill: "var(--color-text-secondary)", fontSize: 11 }}
            label={{
              value: "Coût (€)",
              position: "insideBottom",
              offset: -5,
              fill: "var(--color-text-secondary)",
              fontSize: 11,
            }}
          />
          <YAxis
            dataKey="score"
            name="Score"
            type="number"
            tick={{ fill: "var(--color-text-secondary)", fontSize: 11 }}
            label={{
              value: "Score moyen",
              angle: -90,
              position: "insideLeft",
              fill: "var(--color-text-secondary)",
              fontSize: 11,
            }}
          />
          <ZAxis dataKey="coverage" range={[100, 400]} name="Couverture (%)" />
          <Tooltip
            contentStyle={{
              backgroundColor: "var(--color-bg-primary)",
              border: "1px solid var(--color-border-primary)",
              borderRadius: "8px",
              color: "var(--color-text-primary)",
            }}
            formatter={(value, name) => {
              const v = typeof value === "number" ? value : Number(value ?? 0);
              const n = String(name);
              if (n === "Coût (€)") return [v.toFixed(2) + " €", n];
              if (n === "Score") return [v.toFixed(4), n];
              if (n === "Couverture (%)") return [v.toFixed(1) + "%", n];
              return [String(value), n];
            }}
            labelFormatter={(_, payload) => {
              const item = payload?.[0]?.payload;
              return item?.name ?? "";
            }}
          />
          <Scatter data={data}>
            {data.map((entry) => (
              <Cell
                key={entry.name}
                fill={COLORS[entry.idx % COLORS.length]}
              />
            ))}
          </Scatter>
        </ScatterChart>
      </ResponsiveContainer>
      <div className="flex flex-wrap gap-3 mt-2 justify-center">
        {data.map((entry) => (
          <div key={entry.name} className="flex items-center gap-1.5 text-xs text-text-secondary">
            <div
              className="w-3 h-3 rounded-full"
              style={{ backgroundColor: COLORS[entry.idx % COLORS.length] }}
            />
            {entry.name}
          </div>
        ))}
      </div>
    </div>
  );
}
