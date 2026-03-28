export const SCORING_PROFILES = [
  { value: "equilibre", label: "Équilibré" },
  { value: "tendance", label: "Tendance" },
  { value: "contrarian", label: "Contrarian" },
  { value: "structurel", label: "Structurel" },
] as const;

export const OPTIMIZATION_METHODS = [
  { value: "auto", label: "Automatique" },
  { value: "annealing", label: "Recuit simulé" },
  { value: "genetic", label: "Algorithme génétique" },
  { value: "tabu", label: "Recherche tabou" },
  { value: "hill_climbing", label: "Hill climbing" },
] as const;

export const PORTFOLIO_STRATEGIES = [
  { value: "balanced", label: "Équilibré" },
  { value: "max_diversity", label: "Diversité max" },
  { value: "max_coverage", label: "Couverture max" },
  { value: "min_correlation", label: "Corrélation min" },
] as const;

export const SCORE_CRITERIA = [
  { key: "frequency", label: "Fréquence" },
  { key: "gap", label: "Écart" },
  { key: "cooccurrence", label: "Cooccurrence" },
  { key: "structure", label: "Structure" },
  { key: "balance", label: "Équilibre" },
  { key: "pattern_penalty", label: "Pénalité" },
] as const;
