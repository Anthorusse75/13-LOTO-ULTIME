import type { StrategyConfig } from "@/types/comparison";
import {
  Crown,
  Dices,
  Layers,
  type LucideIcon,
  Minus,
  Plus,
  Sliders,
  Trophy,
  Wrench,
  X,
} from "lucide-react";
import { useState } from "react";

const STRATEGY_TYPES: {
  value: string;
  label: string;
  description: string;
  icon: LucideIcon;
  color: string;
  bg: string;
  border: string;
}[] = [
  {
    value: "top",
    label: "Top scoring",
    description: "Grilles les mieux notées par le moteur statistique",
    icon: Trophy,
    color: "text-amber-400",
    bg: "bg-amber-500/10",
    border: "border-amber-500/30",
  },
  {
    value: "portfolio",
    label: "Portefeuille",
    description: "Portefeuille optimisé pour la diversification",
    icon: Layers,
    color: "text-emerald-400",
    bg: "bg-emerald-500/10",
    border: "border-emerald-500/30",
  },
  {
    value: "random",
    label: "Aléatoire",
    description: "Grilles aléatoires pour servir de référence",
    icon: Dices,
    color: "text-gray-400",
    bg: "bg-gray-500/10",
    border: "border-gray-500/30",
  },
  {
    value: "wheeling",
    label: "Système réduit",
    description: "Couverture combinatoire optimale (wheeling)",
    icon: Crown,
    color: "text-purple-400",
    bg: "bg-purple-500/10",
    border: "border-purple-500/30",
  },
  {
    value: "profile",
    label: "Profil",
    description: "Profil de scoring spécifique (tendance, contrarian…)",
    icon: Sliders,
    color: "text-sky-400",
    bg: "bg-sky-500/10",
    border: "border-sky-500/30",
  },
  {
    value: "method",
    label: "Méthode",
    description: "Méta-heuristique spécifique (recuit, génétique…)",
    icon: Wrench,
    color: "text-rose-400",
    bg: "bg-rose-500/10",
    border: "border-rose-500/30",
  },
];

const PROFILES = [
  { value: "equilibre", label: "Équilibré" },
  { value: "tendance", label: "Tendance" },
  { value: "contrarian", label: "Contrarian" },
  { value: "structurel", label: "Structurel" },
];

const METHODS = [
  { value: "annealing", label: "Recuit simulé" },
  { value: "genetic", label: "Génétique" },
  { value: "tabu", label: "Tabou" },
  { value: "hill_climbing", label: "Hill climbing" },
];

interface Props {
  strategies: StrategyConfig[];
  onChange: (strategies: StrategyConfig[]) => void;
  maxStrategies?: number;
}

export default function StrategySelector({
  strategies,
  onChange,
  maxStrategies = 5,
}: Props) {
  const [showAdd, setShowAdd] = useState(false);

  const addStrategy = (type: StrategyConfig["type"]) => {
    if (strategies.length >= maxStrategies) return;
    const newStrat: StrategyConfig = { type, count: 10 };
    if (type === "profile") newStrat.profile = "equilibre";
    if (type === "method") newStrat.method = "annealing";
    onChange([...strategies, newStrat]);
    setShowAdd(false);
  };

  const removeStrategy = (idx: number) => {
    onChange(strategies.filter((_, i) => i !== idx));
  };

  const updateStrategy = (idx: number, patch: Partial<StrategyConfig>) => {
    onChange(strategies.map((s, i) => (i === idx ? { ...s, ...patch } : s)));
  };

  const getMeta = (type: string) =>
    STRATEGY_TYPES.find((t) => t.value === type) ?? STRATEGY_TYPES[0];

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-text-primary">
          Stratégies sélectionnées
        </h3>
        <span className="text-xs font-medium text-text-secondary rounded-full bg-surface-hover px-2.5 py-0.5">
          {strategies.length} / {maxStrategies}
        </span>
      </div>

      {/* Selected strategies */}
      <div className="space-y-2">
        {strategies.map((strat, idx) => {
          const meta = getMeta(strat.type);
          const Icon = meta.icon;
          return (
            <div
              key={idx}
              className={`group relative flex items-center gap-4 rounded-xl border ${meta.border} ${meta.bg} p-4 transition-all hover:shadow-md`}
            >
              {/* Icon */}
              <div
                className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-lg ${meta.bg} ${meta.color}`}
              >
                <Icon size={20} />
              </div>

              {/* Content */}
              <div className="flex-1 min-w-0 space-y-2">
                <div className="flex items-baseline gap-2">
                  <span className="text-sm font-semibold text-text-primary">
                    {meta.label}
                  </span>
                  <span className="text-xs text-text-secondary hidden sm:inline">
                    {meta.description}
                  </span>
                </div>

                <div className="flex items-center gap-4 flex-wrap">
                  {/* Grid count stepper */}
                  <div className="flex items-center gap-1.5">
                    <span className="text-xs text-text-secondary">Grilles</span>
                    <div className="inline-flex items-center rounded-lg border border-border-primary bg-bg-primary overflow-hidden">
                      <button
                        onClick={() =>
                          updateStrategy(idx, {
                            count: Math.max(1, (strat.count ?? 10) - 1),
                          })
                        }
                        className="px-2 py-1 text-text-secondary hover:bg-surface-hover hover:text-text-primary transition-colors"
                        aria-label="Moins"
                      >
                        <Minus size={12} />
                      </button>
                      <input
                        type="number"
                        min={1}
                        max={50}
                        value={strat.count ?? 10}
                        onChange={(e) =>
                          updateStrategy(idx, {
                            count: Number(e.target.value) || 10,
                          })
                        }
                        className="w-10 bg-transparent text-center text-sm font-semibold text-text-primary outline-none tabular-nums [appearance:textfield] [&::-webkit-inner-spin-button]:appearance-none [&::-webkit-outer-spin-button]:appearance-none"
                      />
                      <button
                        onClick={() =>
                          updateStrategy(idx, {
                            count: Math.min(50, (strat.count ?? 10) + 1),
                          })
                        }
                        className="px-2 py-1 text-text-secondary hover:bg-surface-hover hover:text-text-primary transition-colors"
                        aria-label="Plus"
                      >
                        <Plus size={12} />
                      </button>
                    </div>
                  </div>

                  {/* Profile selector */}
                  {strat.type === "profile" && (
                    <div className="flex items-center gap-1.5">
                      <span className="text-xs text-text-secondary">
                        Profil
                      </span>
                      <select
                        value={strat.profile ?? "equilibre"}
                        onChange={(e) =>
                          updateStrategy(idx, { profile: e.target.value })
                        }
                        className="rounded-lg border border-border-primary bg-bg-primary px-2.5 py-1 text-xs font-medium text-text-primary outline-none focus:border-accent-blue transition-colors"
                      >
                        {PROFILES.map((p) => (
                          <option key={p.value} value={p.value}>
                            {p.label}
                          </option>
                        ))}
                      </select>
                    </div>
                  )}

                  {/* Method selector */}
                  {strat.type === "method" && (
                    <div className="flex items-center gap-1.5">
                      <span className="text-xs text-text-secondary">
                        Méthode
                      </span>
                      <select
                        value={strat.method ?? "annealing"}
                        onChange={(e) =>
                          updateStrategy(idx, { method: e.target.value })
                        }
                        className="rounded-lg border border-border-primary bg-bg-primary px-2.5 py-1 text-xs font-medium text-text-primary outline-none focus:border-accent-blue transition-colors"
                      >
                        {METHODS.map((m) => (
                          <option key={m.value} value={m.value}>
                            {m.label}
                          </option>
                        ))}
                      </select>
                    </div>
                  )}
                </div>
              </div>

              {/* Remove button */}
              <button
                onClick={() => removeStrategy(idx)}
                className="rounded-lg p-1.5 text-text-secondary opacity-0 group-hover:opacity-100 hover:text-accent-red hover:bg-red-500/10 transition-all"
                aria-label="Retirer cette stratégie"
              >
                <X size={16} />
              </button>
            </div>
          );
        })}
      </div>

      {/* Add strategy */}
      {strategies.length < maxStrategies && (
        <div>
          {!showAdd ? (
            <button
              onClick={() => setShowAdd(true)}
              className="flex w-full items-center justify-center gap-2 rounded-xl border-2 border-dashed border-border-primary py-3 text-sm font-medium text-text-secondary hover:border-accent-blue hover:text-accent-blue hover:bg-accent-blue/5 transition-all"
            >
              <Plus size={16} />
              Ajouter une stratégie
            </button>
          ) : (
            <div className="rounded-xl border border-border-primary bg-bg-primary/50 p-3 space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-text-secondary uppercase tracking-wider">
                  Choisir une stratégie
                </span>
                <button
                  onClick={() => setShowAdd(false)}
                  className="rounded-lg p-1 text-text-secondary hover:text-text-primary hover:bg-surface-hover transition-colors"
                >
                  <X size={14} />
                </button>
              </div>
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
                {STRATEGY_TYPES.filter(
                  (t) =>
                    !strategies.some(
                      (s) =>
                        s.type === t.value &&
                        t.value !== "profile" &&
                        t.value !== "method",
                    ),
                ).map((t) => {
                  const Icon = t.icon;
                  return (
                    <button
                      key={t.value}
                      onClick={() =>
                        addStrategy(t.value as StrategyConfig["type"])
                      }
                      className={`flex flex-col items-center gap-2 rounded-xl border ${t.border} p-3 text-center hover:${t.bg} hover:shadow-md transition-all group/card`}
                    >
                      <div
                        className={`flex h-9 w-9 items-center justify-center rounded-lg ${t.bg} ${t.color} transition-transform group-hover/card:scale-110`}
                      >
                        <Icon size={18} />
                      </div>
                      <div>
                        <div className="text-sm font-semibold text-text-primary">
                          {t.label}
                        </div>
                        <div className="text-[11px] text-text-secondary leading-tight mt-0.5">
                          {t.description}
                        </div>
                      </div>
                    </button>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
