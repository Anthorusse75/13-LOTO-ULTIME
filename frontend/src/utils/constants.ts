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
  {
    key: "frequency",
    label: "Fréquence",
    tooltip:
      "Mesure à quel point les numéros choisis sont fréquemment tirés dans l'historique.",
  },
  {
    key: "gap",
    label: "Écart",
    tooltip:
      "Évalue le retard actuel des numéros par rapport à leur moyenne d'apparition.",
  },
  {
    key: "cooccurrence",
    label: "Cooccurrence",
    tooltip: "Analyse les paires de numéros qui apparaissent souvent ensemble.",
  },
  {
    key: "structure",
    label: "Structure",
    tooltip:
      "Vérifie la répartition par dizaines, parité et couverture du pool.",
  },
  {
    key: "balance",
    label: "Équilibre",
    tooltip:
      "Évalue l'équilibre global de la grille (somme, écart-type, médiane).",
  },
  {
    key: "pattern_penalty",
    label: "Pénalité",
    tooltip:
      "Malus appliqué si les numéros suivent des motifs trop réguliers (suites, multiples).",
  },
] as const;
