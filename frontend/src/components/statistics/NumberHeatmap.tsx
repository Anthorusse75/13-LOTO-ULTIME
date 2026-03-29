import { useMemo } from "react";

interface NumberHeatmapProps {
  data: Record<number, number>;
  minNumber: number;
  maxNumber: number;
  colorScale?: "frequency" | "gap" | "score";
  onNumberClick?: (num: number) => void;
}

export default function NumberHeatmap({
  data,
  minNumber,
  maxNumber,
  colorScale = "frequency",
  onNumberClick,
}: NumberHeatmapProps) {
  const { values, minVal, maxVal } = useMemo(() => {
    const vals = Object.values(data);
    return {
      values: vals,
      minVal: Math.min(...vals),
      maxVal: Math.max(...vals),
    };
  }, [data]);

  const getColor = (value: number) => {
    if (values.length === 0 || maxVal === minVal) return "bg-surface-hover";
    const ratio = (value - minVal) / (maxVal - minVal);
    if (colorScale === "gap") {
      // Inverted: higher gap = more red
      if (ratio >= 0.7) return "bg-accent-red/80";
      if (ratio >= 0.4) return "bg-accent-amber/80";
      return "bg-accent-green/80";
    }
    // frequency/score: higher = more green
    if (ratio >= 0.7) return "bg-accent-green/80";
    if (ratio >= 0.4) return "bg-accent-amber/80";
    return "bg-accent-red/80";
  };

  const numbers = Array.from(
    { length: maxNumber - minNumber + 1 },
    (_, i) => i + minNumber
  );

  return (
    <div className="flex flex-wrap gap-1.5">
      {numbers.map((n) => {
        const val = data[n];
        return (
          <button
            key={n}
            onClick={() => onNumberClick?.(n)}
            className={`w-10 h-10 rounded-md flex items-center justify-center font-mono text-sm transition-colors ${
              val !== undefined
                ? `${getColor(val)} text-white`
                : "bg-surface text-text-secondary"
            } hover:ring-1 hover:ring-accent-blue`}
            aria-label={val !== undefined ? `Numéro ${n} : ${val.toFixed(3)}` : `Numéro ${n} : N/A`}
            aria-pressed={undefined}
          >
            {n}
          </button>
        );
      })}
    </div>
  );
}
