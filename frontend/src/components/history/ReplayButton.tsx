import type { ResultType } from "@/types/history";
import { PlayCircle } from "lucide-react";
import { useNavigate } from "react-router-dom";

interface ReplayButtonProps {
  resultType: ResultType;
  parameters: Record<string, unknown>;
  gameId?: number;
}

const ROUTE_MAP: Record<ResultType, string> = {
  grid: "/grids",
  portfolio: "/portfolio",
  simulation: "/simulation",
  comparison: "/simulation",
  wheeling: "/wheeling",
  budget_plan: "/budget",
};

export default function ReplayButton({
  resultType,
  parameters,
  gameId,
}: ReplayButtonProps) {
  const navigate = useNavigate();

  const handleReplay = () => {
    const route = ROUTE_MAP[resultType] ?? "/grids";
    const searchParams = new URLSearchParams();
    if (gameId) searchParams.set("gameId", String(gameId));
    Object.entries(parameters).forEach(([key, value]) => {
      if (value !== null && value !== undefined) {
        searchParams.set(key, String(value));
      }
    });
    const qs = searchParams.toString();
    navigate(qs ? `${route}?${qs}` : route);
  };

  return (
    <button
      onClick={handleReplay}
      className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-md bg-accent-blue/10 text-accent-blue hover:bg-accent-blue/20 transition-colors"
    >
      <PlayCircle size={14} />
      Rejouer
    </button>
  );
}
