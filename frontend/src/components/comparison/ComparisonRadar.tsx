import type { StrategyMetrics } from "@/types/comparison";
import { useMemo } from "react";
import {
  PolarAngleAxis,
  PolarGrid,
  PolarRadiusAxis,
  Radar,
  RadarChart,
  ResponsiveContainer,
  Legend,
  Tooltip,
} from "recharts";

const AXES = [
  { key: "avg_score", label: "Score" },
  { key: "diversity", label: "Diversité" },
  { key: "coverage", label: "Couverture" },
  { key: "robustness", label: "Robustesse" },
];

const COLORS = ["#3B82F6", "#10B981", "#F59E0B", "#EF4444", "#8B5CF6"];

interface Props {
  strategies: StrategyMetrics[];
}

export default function ComparisonRadar({ strategies }: Props) {
  const data = useMemo(() => {
    return AXES.map((axis) => {
      const row: Record<string, string | number> = { metric: axis.label };
      const values = strategies.map(
        (s) => (s[axis.key as keyof StrategyMetrics] as number) ?? 0,
      );
      const maxVal = Math.max(...values, 0.001);
      strategies.forEach((s) => {
        const raw = (s[axis.key as keyof StrategyMetrics] as number) ?? 0;
        // Normalize to 0-100 for radar chart
        row[s.label] = maxVal > 0 ? Math.round((raw / maxVal) * 100) : 0;
      });
      return row;
    });
  }, [strategies]);

  if (strategies.length === 0) return null;

  return (
    <div className="rounded-xl border border-border-primary bg-bg-secondary p-4">
      <h3 className="text-sm font-semibold text-text-primary mb-3">
        Profil radar
      </h3>
      <ResponsiveContainer width="100%" height={320}>
        <RadarChart data={data}>
          <PolarGrid stroke="var(--color-border-primary)" />
          <PolarAngleAxis
            dataKey="metric"
            tick={{ fill: "var(--color-text-secondary)", fontSize: 12 }}
          />
          <PolarRadiusAxis
            angle={90}
            domain={[0, 100]}
            tick={{ fill: "var(--color-text-secondary)", fontSize: 10 }}
          />
          {strategies.map((s, idx) => (
            <Radar
              key={s.label}
              name={s.label}
              dataKey={s.label}
              stroke={COLORS[idx % COLORS.length]}
              fill={COLORS[idx % COLORS.length]}
              fillOpacity={0.15}
              strokeWidth={2}
            />
          ))}
          <Tooltip
            contentStyle={{
              backgroundColor: "var(--color-bg-primary)",
              border: "1px solid var(--color-border-primary)",
              borderRadius: "8px",
              color: "var(--color-text-primary)",
            }}
          />
          <Legend
            wrapperStyle={{ fontSize: 12, color: "var(--color-text-secondary)" }}
          />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  );
}
