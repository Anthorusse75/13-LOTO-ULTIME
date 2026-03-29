# Architecture des moteurs algorithmiques

## Vue d'ensemble

Loto Ultime utilise une architecture en couches : une API FastAPI orchestre des moteurs algorithmiques spécialisés qui opèrent sur des matrices NumPy de tirages.

---

## Diagramme de flux — Pipeline statistique

```mermaid
flowchart TD
    A[GET /statistics/*] --> B{Snapshot en cache?}
    B -- Oui --> C[StatisticsRepository.get_latest]
    B -- Non --> D[POST /statistics/recompute]
    D --> E[StatisticsService.compute_all]

    E --> F[DrawRepository.get_numbers_matrix]
    F --> G[np.ndarray N×K tirages]
    G --> H1[FrequencyEngine]
    G --> H2[GapEngine]
    G --> H3[CooccurrenceEngine]
    G --> H4[TemporalEngine]
    G --> H5[DistributionEngine]
    G --> H6[BayesianEngine]
    G --> H7[GraphEngine]

    H1 --> I[StatisticsSnapshot]
    H2 --> I
    H3 --> I
    H4 --> I
    H5 --> I
    H6 --> I
    H7 --> I
    I --> J[StatisticsRepository.create]
    C --> K[Réponse API]
    J --> K
```

---

## Diagramme de flux — Pipeline de scoring

```mermaid
flowchart TD
    A[POST /grids/generate\nou\nPOST /grids/score] --> B[OptimizationService]
    B --> C{Méthode?}

    C -- genetic --> D[GeneticOptimizer]
    C -- bayesian --> E[BayesianOptimizer]
    C -- simulated_annealing --> F[SimulatedAnnealingOptimizer]
    C -- mcts --> G[MCTSOptimizer]
    C -- random --> H[RandomSampler]
    C -- auto --> I[AutoSelector\nchoisit selon le profil]

    D --> J[ScoringEngine]
    E --> J
    F --> J
    G --> J
    H --> J
    I --> J

    J --> K{Score breakdown}
    K --> K1[frequency_score\nFréquence historique des numéros]
    K --> K2[gap_score\nÉcart depuis dernière apparition]
    K --> K3[cooccurrence_score\nPaires de numéros fréquentes]
    K --> K4[structure_score\nPlage haut/bas, parité]
    K --> K5[balance_score\nDistribution uniforme]
    K --> K6[pattern_penalty\nPénalité si motif trop régulier]

    K1 --> L[total_score ∈ 0..1]
    K2 --> L
    K3 --> L
    K4 --> L
    K5 --> L
    K6 --> L

    L --> M[GridScoreResponse]
    M --> N[Persistance dans scored_grids\nsi endpoint /generate]
```

---

## Diagramme de flux — Pipeline de simulation

```mermaid
flowchart TD
    A[POST /simulation/*] --> B{Type de simulation}
    B -- monte-carlo --> C[MonteCarloEngine\nnp.random hypergéométrique\nN fois]
    B -- stability --> D[BootstrapEngine\nré-échantillonnage\ndes tirages historiques]
    B -- compare-random --> E[CompareRandomEngine\ngénère N grilles aléatoires\net calcule percentile + z-score]
    B -- portfolio --> F[PortfolioService\ngénère M grilles optimisées\npuis simule chacune]

    C --> G[MonteCarloResult\nmatch_distribution, avg_matches]
    D --> H[StabilityResult\nmean_score, std, cv, ci_95]
    E --> I[ComparisonResult\ngrid_score, percentile, z_score]
    F --> J[PortfolioResult\ngrilles + synthèse]
```

---

## Couches de l'application

```
┌─────────────────────────────────────────────────────────┐
│                    API Layer (FastAPI)                    │
│  /api/v1/games/{id}/statistics  grids  simulation  ...   │
├─────────────────────────────────────────────────────────┤
│                  Service Layer                           │
│  StatisticsService  ScoringService  SimulationService    │
│  GridService  AuthService  PortfolioService              │
├─────────────────────────────────────────────────────────┤
│                 Engine Layer (NumPy/SciPy)               │
│  FrequencyEngine  GapEngine  CooccurrenceEngine          │
│  TemporalEngine  DistributionEngine  BayesianEngine      │
│  GraphEngine  ScoringEngine  Optimizers (genetic, ...)   │
├─────────────────────────────────────────────────────────┤
│              Repository Layer (SQLAlchemy)               │
│  DrawRepository  GridRepository  StatisticsRepository    │
│  GameRepository  UserRepository                          │
├─────────────────────────────────────────────────────────┤
│                 Data Layer (SQLite + Alembic)            │
│  draws  scored_grids  statistics_snapshots  users  games │
└─────────────────────────────────────────────────────────┘
```

---

## Moteurs statistiques — Détail

| Moteur | Entrée | Sortie | Algorithme |
|--------|--------|--------|------------|
| `FrequencyEngine` | matrice N×K | `{num: {count, relative}}` | comptage + normalisation |
| `GapEngine` | matrice N×K | `{num: {current_gap, avg_gap, max_gap}}` | scan inverse |
| `CooccurrenceEngine` | matrice N×K | matrice Co-occurrence K×K | co-occurrence binaire |
| `TemporalEngine` | matrice N×K | tendances sur fenêtres 10/30/100 | fréquences glissantes |
| `DistributionEngine` | matrice N×K | entropie, score d'uniformité | chi², entropie de Shannon |
| `BayesianEngine` | matrice N×K | priors Beta-Binomial par numéro | mise à jour bayésienne |
| `GraphEngine` | matrice N×K | centralité, communautés | NetworkX + Louvain |

---

## Optimiseurs — Comparaison

| Méthode | Complexité | Points forts | Cas d'usage |
|---------|------------|--------------|-------------|
| `genetic` | O(N·G·P) | Explore l'espace global | Grilles très optimisées |
| `bayesian` | O(N·iter) | Utilise les priors statistiques | Favorise les numéros historiques |
| `simulated_annealing` | O(N·T) | Échappe aux optima locaux | Équilibre exploration/exploitation |
| `mcts` | O(N·sqrt) | Arbre de décision stochastique | Grandes plages de numéros |
| `random` | O(1) | Rapide, baseline | Référence de comparaison |
| `auto` | dépend du profil | Sélection automatique | Usage général |

---

## Flux de données — Frontend ↔ Backend

```
React/TanStack Query
       │
       ▼
  axios (api.ts)         ← JWT Bearer token
       │
       ▼
FastAPI /api/v1/...
       │
       ├── Depend: get_current_user (JWT decode)
       ├── Depend: get_game_config  (DB → YAML)
       │
       ▼
Service Layer
       │
       ▼
Repository + Engine
       │
       ▼
SQLite (loto_ultime.db)
```
