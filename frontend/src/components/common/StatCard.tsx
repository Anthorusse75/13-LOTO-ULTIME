interface StatCardProps {
  title: string;
  icon: React.ReactNode;
  value: React.ReactNode;
  sub: string;
  trend?: "up" | "down" | "neutral";
  sparklineData?: number[];
}

export default function StatCard({
  title,
  icon,
  value,
  sub,
  trend,
  sparklineData,
}: StatCardProps) {
  const trendColor =
    trend === "up"
      ? "text-accent-green"
      : trend === "down"
        ? "text-accent-red"
        : "text-text-secondary";

  return (
    <div className="bg-surface rounded-lg border border-border p-4">
      <div className="flex items-center gap-2 mb-2">
        {icon}
        <span className="text-xs text-text-secondary">{title}</span>
      </div>
      <div className={`text-lg font-semibold ${trendColor}`}>{value}</div>
      <p className="text-xs text-text-secondary mt-1">{sub}</p>
      {sparklineData && sparklineData.length > 1 && (
        <div className="mt-2 flex items-end gap-px h-6">
          {sparklineData.map((v, i) => {
            const max = Math.max(...sparklineData);
            const h = max > 0 ? (v / max) * 100 : 0;
            return (
              <div
                key={i}
                className="flex-1 bg-accent-blue/40 rounded-t-sm"
                style={{ height: `${h}%` }}
              />
            );
          })}
        </div>
      )}
    </div>
  );
}
