interface DrawBallsProps {
  numbers: number[];
  stars?: number[] | null;
  size?: "sm" | "md" | "lg";
  highlight?: number[];
}

const sizeMap = {
  sm: "w-7 h-7 text-xs",
  md: "w-9 h-9 text-sm",
  lg: "w-12 h-12 text-base",
};

export default function DrawBalls({
  numbers,
  stars,
  size = "md",
  highlight,
}: DrawBallsProps) {
  const sizeClass = sizeMap[size];
  const isHighlighted = (n: number) => highlight?.includes(n);

  return (
    <div className="flex items-center gap-1.5 flex-wrap">
      {numbers.map((n) => (
        <div
          key={n}
          className={`${sizeClass} rounded-full font-mono font-medium flex items-center justify-center ${
            isHighlighted(n)
              ? "bg-accent-green text-white ring-2 ring-accent-green/50"
              : "bg-accent-blue text-white"
          }`}
        >
          {n}
        </div>
      ))}
      {stars?.map((s) => (
        <div
          key={`star-${s}`}
          className={`${sizeClass} rounded-full font-mono font-medium flex items-center justify-center bg-accent-purple text-white`}
        >
          {s}
        </div>
      ))}
    </div>
  );
}
