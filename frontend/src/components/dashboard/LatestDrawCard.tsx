import DrawBalls from "@/components/draws/DrawBalls";
import { formatDate } from "@/utils/formatters";
import { Calendar } from "lucide-react";
import type { Draw } from "@/types/draw";

interface LatestDrawCardProps {
  draw: Draw | undefined;
}

export default function LatestDrawCard({ draw }: LatestDrawCardProps) {
  return (
    <div className="bg-surface rounded-lg border border-border p-4">
      <div className="flex items-center gap-2 mb-3">
        <Calendar size={16} className="text-accent-blue" />
        <h3 className="text-sm font-semibold">Dernier tirage</h3>
      </div>
      {draw ? (
        <div className="space-y-2">
          <DrawBalls numbers={draw.numbers} stars={draw.stars} size="sm" />
          <p className="text-xs text-text-secondary">
            {formatDate(draw.draw_date)}
            {draw.draw_number && ` — #${draw.draw_number}`}
          </p>
        </div>
      ) : (
        <p className="text-sm text-text-secondary">Aucun tirage disponible</p>
      )}
    </div>
  );
}
