import { useState, useCallback } from "react";
import { Sliders, RotateCcw } from "lucide-react";
import InfoTooltip from "@/components/common/InfoTooltip";

// ─── Weight keys mirror the backend scoring criteria ────────────────────────
type WeightKey = "frequency" | "gap" | "cooccurrence" | "structure" | "balance" | "penalty";

const CRITERIA: Array<{ key: WeightKey; label: string; description: string }> = [
  {
    key: "frequency",
    label: "Fréquence",
    description: "Importance des numéros fréquemment tirés dans l'historique.",
  },
  {
    key: "gap",
    label: "Écart (retard)",
    description: "Importance des numéros en retard par rapport à leur moyenne d'apparition.",
  },
  {
    key: "cooccurrence",
    label: "Co-occurrence",
    description: "Importance des paires de numéros qui apparaissent souvent ensemble.",
  },
  {
    key: "structure",
    label: "Structure",
    description: "Répartition par dizaines, parité et couverture du pool de numéros.",
  },
  {
    key: "balance",
    label: "Équilibre",
    description: "Somme totale de la grille comparée à la somme moyenne historique.",
  },
  {
    key: "penalty",
    label: "Pénalité (patterns)",
    description: "Pénalise les grilles avec des patterns trop simplistes (consécutifs, même dizaine).",
  },
];

// Default equal weights
const DEFAULT_WEIGHTS: Record<WeightKey, number> = {
  frequency: 0.25,
  gap: 0.25,
  cooccurrence: 0.15,
  structure: 0.15,
  balance: 0.10,
  penalty: 0.10,
};

interface CustomWeightsEditorProps {
  /** Called whenever weights change. Null when profile mode is active (no custom weights). */
  onChange: (weights: Record<WeightKey, number> | null) => void;
}

export default function CustomWeightsEditor({ onChange }: CustomWeightsEditorProps) {
  const [enabled, setEnabled] = useState(false);
  const [weights, setWeights] = useState<Record<WeightKey, number>>({ ...DEFAULT_WEIGHTS });

  const total = Object.values(weights).reduce((s, v) => s + v, 0);
  const isValid = Math.abs(total - 1.0) < 0.01;

  const handleChange = useCallback(
    (key: WeightKey, value: number) => {
      const next = { ...weights, [key]: value };
      setWeights(next);
      if (enabled) {
        onChange(next);
      }
    },
    [weights, enabled, onChange],
  );

  const handleToggle = (checked: boolean) => {
    setEnabled(checked);
    onChange(checked ? weights : null);
  };

  const handleReset = () => {
    setWeights({ ...DEFAULT_WEIGHTS });
    if (enabled) onChange({ ...DEFAULT_WEIGHTS });
  };

  return (
    <div className="border border-border rounded-xl p-4 space-y-3">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Sliders className="w-4 h-4 text-primary" aria-hidden="true" />
          <span className="font-semibold text-sm">Poids personnalisés</span>
          <InfoTooltip text="Remplacez le profil prédéfini par vos propres pondérations pour chaque critère de scoring." />
        </div>
        <label className="flex items-center gap-2 cursor-pointer select-none">
          <span className="text-xs text-muted-foreground">Activer</span>
          <button
            role="switch"
            aria-checked={enabled}
            onClick={() => handleToggle(!enabled)}
            className={`relative inline-flex h-5 w-9 items-center rounded-full transition-colors focus-visible:outline focus-visible:outline-2 focus-visible:outline-primary ${
              enabled ? "bg-primary" : "bg-muted"
            }`}
            aria-label="Activer les poids personnalisés"
          >
            <span
              className={`inline-block h-4 w-4 transform rounded-full bg-white shadow transition-transform ${
                enabled ? "translate-x-4" : "translate-x-0.5"
              }`}
            />
          </button>
        </label>
      </div>

      {enabled && (
        <div className="space-y-3" aria-live="polite">
          {CRITERIA.map(({ key, label, description }) => (
            <div key={key} className="space-y-1">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-1 text-sm font-medium">
                  {label}
                  <InfoTooltip text={description} />
                </div>
                <span className="text-sm tabular-nums text-muted-foreground">
                  {(weights[key] * 100).toFixed(0)}%
                </span>
              </div>
              <input
                type="range"
                min={0}
                max={1}
                step={0.01}
                value={weights[key]}
                onChange={(e) => handleChange(key, parseFloat(e.target.value))}
                className="w-full accent-primary h-1.5"
                aria-label={`Poids ${label}`}
                aria-valuemin={0}
                aria-valuemax={100}
                aria-valuenow={Math.round(weights[key] * 100)}
                aria-valuetext={`${(weights[key] * 100).toFixed(0)}%`}
              />
            </div>
          ))}

          {/* Total indicator */}
          <div
            className={`flex items-center justify-between text-xs rounded-lg px-3 py-2 ${
              isValid
                ? "bg-green-500/10 text-green-600"
                : "bg-red-500/10 text-red-500"
            }`}
            role="status"
            aria-live="polite"
          >
            <span>Total</span>
            <span className="font-mono font-bold">
              {(total * 100).toFixed(0)}% {isValid ? "✓" : "— doit être 100%"}
            </span>
          </div>

          {/* Reset */}
          <button
            onClick={handleReset}
            className="flex items-center gap-1.5 text-xs text-muted-foreground hover:text-foreground transition-colors"
            aria-label="Réinitialiser les poids par défaut"
          >
            <RotateCcw className="w-3 h-3" aria-hidden="true" />
            Réinitialiser
          </button>
        </div>
      )}
    </div>
  );
}
