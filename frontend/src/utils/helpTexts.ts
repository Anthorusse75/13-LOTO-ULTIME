/**
 * Help texts for tooltips across the application.
 * Organized by page/section for easy lookup.
 */

export const HELP_TEXTS = {
  // ── Grid page ──
  grid: {
    totalScore:
      "Note globale de 0 à 10 combinant fréquence, écart, co-occurrence, structure, équilibre et pénalité. Plus c'est haut, meilleure est la qualité statistique.",
    frequency:
      "Mesure si les numéros choisis correspondent aux numéros les plus fréquents dans l'historique.",
    gap:
      "Évalue les écarts (retards) des numéros — un numéro qui n'est pas sorti depuis longtemps a un écart élevé.",
    cooccurrence:
      "Vérifie si les paires de numéros de la grille sont historiquement associées (sortent souvent ensemble).",
    structure:
      "Analyse la répartition structurelle : dizaines, terminaisons, somme totale.",
    balance:
      "Équilibre pair/impair et haut/bas — une bonne grille a un mix des deux.",
    patternPenalty:
      "Pénalité pour les patterns trop réguliers (suites, multiples, etc.) rarement observés dans les vrais tirages.",
  },

  // ── Portfolio page ──
  portfolio: {
    diversity:
      "Mesure à quel point vos grilles sont différentes. 100% = toutes uniques, 0% = toutes identiques.",
    coverage:
      "Pourcentage de numéros du jeu présents dans au moins une grille de votre portefeuille.",
    hammingDistance:
      "Nombre minimum de numéros différents entre deux grilles du portefeuille. Plus c'est élevé, meilleure est la diversité.",
    avgScore:
      "Moyenne des scores individuels des grilles du portefeuille.",
  },

  // ── Simulation page ──
  simulation: {
    monteCarlo:
      "Simule N tirages aléatoires et compte combien de vos numéros seraient sortis. Pas une prédiction, mais une estimation statistique.",
    avgMatches:
      "Nombre moyen de numéros correspondants sur l'ensemble des simulations.",
    expectedMatches:
      "Nombre théorique de correspondances calculé par la loi hypergéométrique.",
    stability:
      "Indice de robustesse du score : 1.0 = parfaitement stable, <0.5 = très instable selon l'échantillon.",
    percentile:
      "Position de votre grille par rapport aux grilles aléatoires. 95% signifie que vous battez 95% des grilles tirées au hasard.",
    zScore:
      "Écart standardisé par rapport à la moyenne des grilles aléatoires. >2 = significativement meilleur.",
  },

  // ── Dashboard ──
  dashboard: {
    hotNumbers: "Numéros les plus fréquents dans l'historique récent.",
    coldNumbers: "Numéros les moins fréquents ou les plus absents récemment.",
    pipeline: "État du système automatique qui met à jour les données chaque nuit.",
  },
} as const;
