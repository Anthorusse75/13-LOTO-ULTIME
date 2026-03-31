export const SCORING_PROFILES = [
  {
    value: "equilibre",
    label: "Équilibré",
    description:
      "Donne le même poids à tous les critères. Idéal pour débuter : on ne favorise aucun axe en particulier.",
  },
  {
    value: "tendance",
    label: "Tendance",
    description:
      "Favorise les numéros « chauds » (souvent tirés récemment). Pari sur la continuité des tendances.",
  },
  {
    value: "contrarian",
    label: "Contrarian",
    description:
      "Favorise les numéros « froids » (peu tirés récemment). Pari sur un retour à la moyenne.",
  },
  {
    value: "structurel",
    label: "Structurel",
    description:
      "Met l'accent sur l'équilibre de la grille : bonne répartition pairs/impairs, dizaines, somme globale.",
  },
] as const;

export const OPTIMIZATION_METHODS = [
  {
    value: "auto",
    label: "Automatique",
    description:
      "Laisse le système choisir le meilleur algorithme selon le jeu et le nombre de grilles demandées.",
  },
  {
    value: "annealing",
    label: "Recuit simulé",
    description:
      "S'inspire du refroidissement des métaux : teste beaucoup de combinaisons au début, puis se concentre sur les meilleures. Bon compromis vitesse/qualité.",
  },
  {
    value: "genetic",
    label: "Algorithme génétique",
    description:
      "Comme la sélection naturelle : les meilleures grilles se « reproduisent » entre elles pour créer des combinaisons encore meilleures. Plus lent mais souvent meilleur.",
  },
  {
    value: "tabu",
    label: "Recherche tabou",
    description:
      "Explore intelligemment en mémorisant les combinaisons déjà testées pour ne pas tourner en rond. Bons résultats sur les petits pools.",
  },
  {
    value: "hill_climbing",
    label: "Hill climbing",
    description:
      "Le plus simple : améliore la grille pas à pas en changeant un numéro à la fois. Très rapide mais peut manquer de diversité.",
  },
] as const;

export const PORTFOLIO_STRATEGIES = [
  {
    value: "balanced",
    label: "Équilibré",
    description:
      "Compromis entre score individuel et diversité. Chaque grille est bonne tout en étant différente des autres. Recommandé pour débuter.",
  },
  {
    value: "max_diversity",
    label: "Diversité max",
    description:
      "Maximise les différences entre les grilles. Utile si vous voulez couvrir un maximum de combinaisons différentes à chaque tirage.",
  },
  {
    value: "max_coverage",
    label: "Couverture max",
    description:
      "Cherche à ce que le plus grand nombre de numéros possibles soient présents dans au moins une grille du portefeuille.",
  },
  {
    value: "min_correlation",
    label: "Corrélation min",
    description:
      "Minimise les numéros en commun entre les grilles. Si un numéro n'est pas tiré, il n'impacte qu'une seule de vos grilles.",
  },
] as const;

export const SCORE_CRITERIA = [
  {
    key: "frequency",
    label: "Fréquence",
    tooltip:
      "Mesure à quel point vos numéros sont souvent tirés dans l'historique. Par exemple, si le 7 est sorti 150 fois sur 1000 tirages, il a une fréquence élevée. Un score haut signifie que vos numéros sont des habitués des tirages.",
  },
  {
    key: "gap",
    label: "Écart",
    tooltip:
      "Regarde depuis combien de tirages chaque numéro n'est pas sorti. Par exemple, si le 23 n'est pas sorti depuis 40 tirages alors qu'il sort en moyenne tous les 15 tirages, son « retard » est élevé. Un bon score ici indique un équilibre entre numéros récents et en retard.",
  },
  {
    key: "cooccurrence",
    label: "Cooccurrence",
    tooltip:
      "Analyse les paires de numéros qui apparaissent souvent ensemble. Par exemple, si le 7 et le 12 sortent ensemble plus souvent que la moyenne, c'est une paire « forte ». Un bon score signifie que vos numéros forment des paires historiquement fréquentes.",
  },
  {
    key: "structure",
    label: "Structure",
    tooltip:
      "Vérifie que la grille est bien construite : bonne répartition entre les dizaines (pas tout entre 1-10), mix de pairs et impairs, couverture de l'ensemble du pool. Une grille 2-4-6-8-10 aurait un mauvais score ici car elle ne contient que des pairs de la même dizaine.",
  },
  {
    key: "balance",
    label: "Équilibre",
    tooltip:
      "Évalue la somme totale, la médiane et l'écart-type de vos numéros. Par exemple, une grille 1-2-3-4-5 a une somme très basse (15) alors que la moyenne des tirages est autour de 125 — son score d'équilibre serait faible.",
  },
  {
    key: "pattern_penalty",
    label: "Pénalité",
    tooltip:
      "Détecte les combinaisons « trop régulières » que beaucoup de joueurs choisissent : suites (1-2-3-4-5), multiples d'un nombre (5-10-15-20), diagonales de grille. Moins il y a de pénalité, mieux c'est — le score monte quand la grille est originale.",
  },
] as const;
