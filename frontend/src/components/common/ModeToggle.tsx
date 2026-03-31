import { useDisplayMode } from "@/hooks/useDisplayMode";
import { Eye, Microscope } from "lucide-react";

export default function ModeToggle() {
  const { isExpert, toggleDisplayMode } = useDisplayMode();

  return (
    <button
      onClick={toggleDisplayMode}
      className="flex items-center gap-2 px-3 py-1.5 rounded-lg border border-surface-border bg-surface-overlay text-sm transition-colors hover:bg-surface-hover"
      title={isExpert ? "Passer en mode simplifié" : "Passer en mode expert"}
    >
      {isExpert ? (
        <>
          <Microscope size={16} className="text-accent-blue" />
          <span className="text-text-secondary">Expert</span>
        </>
      ) : (
        <>
          <Eye size={16} className="text-accent-green" />
          <span className="text-text-secondary">Simple</span>
        </>
      )}
    </button>
  );
}
