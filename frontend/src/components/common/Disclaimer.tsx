import { AlertTriangle } from "lucide-react";

export default function Disclaimer() {
  return (
    <div className="flex items-start gap-2 p-3 rounded-md bg-accent-amber/10 border border-accent-amber/30 text-xs text-accent-amber">
      <AlertTriangle size={14} className="mt-0.5 flex-shrink-0" />
      <span>
        Ce logiciel est un outil d'analyse statistique. Il ne garantit aucun gain.
        Les jeux de hasard restent aléatoires. Jouez responsablement.
      </span>
    </div>
  );
}
