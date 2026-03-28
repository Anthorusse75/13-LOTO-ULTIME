interface ScoreBarProps {
  value: number;
  max?: number;
  label: string;
  weight?: number;
}

export default function ScoreBar({
  value,
  max = 1,
  label,
  weight,
}: ScoreBarProps) {
  const pct = Math.min((value / max) * 100, 100);

  const getColor = (v: number) => {
    if (v >= 0.7) return "bg-accent-green";
    if (v >= 0.4) return "bg-accent-amber";
    return "bg-accent-red";
  };

  return (
    <div className="flex items-center gap-3 text-sm">
      <span className="w-28 text-text-secondary truncate">{label}</span>
      <div className="flex-1 h-2.5 bg-border rounded-full overflow-hidden">
        <div
          className={`h-full rounded-full transition-all duration-500 ${getColor(value / max)}`}
          style={{ width: `${pct}%` }}
        />
      </div>
      <span className="w-12 text-right font-mono text-text-primary">
        {(value * 10).toFixed(1)}
      </span>
      {weight !== undefined && (
        <span className="w-14 text-right text-text-secondary text-xs">
          ×{weight.toFixed(2)}
        </span>
      )}
    </div>
  );
}
