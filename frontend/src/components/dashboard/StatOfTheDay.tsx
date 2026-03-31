import { Sparkles } from "lucide-react";

export interface StatHighlight {
  icon: React.ReactNode;
  label: string;
  value: string | number;
  detail: string;
  color?: string; // tailwind text color class
}

interface StatOfTheDayProps {
  items: StatHighlight[];
}

export default function StatOfTheDay({ items }: StatOfTheDayProps) {
  return (
    <div className="bg-gradient-to-br from-accent-blue/10 to-accent-purple/10 rounded-lg border border-accent-blue/20 p-4 flex flex-col">
      <div className="flex items-center gap-2 mb-3">
        <Sparkles size={16} className="text-accent-amber" />
        <h3 className="text-sm font-semibold">Stat du jour</h3>
      </div>
      <div className="flex-1 space-y-3">
        {items.map((item, i) => (
          <div key={i} className="flex items-start gap-3">
            <div className="mt-0.5 shrink-0">{item.icon}</div>
            <div className="min-w-0 flex-1">
              <div className="flex items-baseline gap-2">
                <span
                  className={`text-lg font-bold ${item.color ?? "text-accent-blue"}`}
                >
                  {item.value}
                </span>
                <span className="text-xs text-text-secondary truncate">
                  {item.label}
                </span>
              </div>
              <p className="text-xs text-text-secondary">{item.detail}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
