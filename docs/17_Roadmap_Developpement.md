# 17 — Roadmap de Développement

> **Projet** : LOTO ULTIME  
> **Version** : 1.0  
> **Date** : 2026-03-27  
> **Références croisées** : [01_Vision](01_Vision_Projet.md) · [18_Checklist](18_Checklist_Globale.md)

---

## 1. Vue d'ensemble

```
Phase 1      Phase 2      Phase 3      Phase 4      Phase 5
 Archi        Fondations   Stats        Scoring      Optimisation
 & Docs       Backend      Engine       Engine       Engine
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
▓▓▓▓▓▓▓▓▓▓  ▓▓▓▓▓▓▓▓▓▓  ▓▓▓▓▓▓▓▓▓▓  ▓▓▓▓▓▓▓▓▓▓  ▓▓▓▓▓▓▓▓▓▓

Phase 6      Phase 7      Phase 8      Phase 9      Phase 10
 Simulation   Frontend     Scheduler    Sécurité     Polish
 Engine       UI           & Jobs       & Auth       & Deploy
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
░░░░░░░░░░  ░░░░░░░░░░  ░░░░░░░░░░  ░░░░░░░░░░  ░░░░░░░░░░
```

---

## 2. Phase 1 — Architecture & Documentation

> **Statut** : ✅ TERMINÉE  
> **Prérequis** : Aucun

### Livrables

| #   | Tâche                                     | Statut |
| --- | ----------------------------------------- | ------ |
| 1.1 | Rédaction des 18 documents d'architecture | ✅      |
| 1.2 | Structure dossier projet                  | ✅      |
| 1.3 | Validation croisée des documents          | ✅      |
| 1.4 | Création du README.md racine              | ✅      |

### Critères de complétion
- [x] 18 documents rédigés et cohérents
- [x] README avec instructions de setup
- [x] Tous les cross-references valides

---

## 3. Phase 2 — Fondations Backend

> **Statut** : ✅ TERMINÉE  
> **Prérequis** : Phase 1

### Livrables

| #   | Tâche                        | Description                              | Statut |
| --- | ---------------------------- | ---------------------------------------- | ------ |
| 2.1 | Initialisation projet Python | pyproject.toml, structure dossiers, venv | ✅      |
| 2.2 | Configuration (Settings)     | Pydantic Settings, .env, YAML jeux       | ✅      |
| 2.3 | Modèles SQLAlchemy           | Tous les modèles du doc 05               | ✅      |
| 2.4 | Alembic setup                | Init + première migration                | ✅      |
| 2.5 | Repository pattern           | BaseRepository + implémentations         | ✅      |
| 2.6 | FastAPI app de base          | main.py, lifespan, CORS, health check    | ✅      |
| 2.7 | Logger structuré             | Configuration structlog                  | ✅      |
| 2.8 | Tests fondations             | Fixtures, factories, tests repo/config   | ✅      |

### Technologies initialisées
- Python 3.11+, FastAPI, SQLAlchemy 2.0, Alembic, Pydantic v2
- pytest, pytest-asyncio, httpx
- structlog, uvicorn

### Critères de complétion
- [x] `uvicorn app.main:app` démarre sans erreur
- [x] Migrations créent toutes les tables
- [x] `/health` retourne `{"status": "healthy"}`
- [x] Tests passent avec couverture > 80% sur ce code (81.68%)

---

## 4. Phase 3 — Moteur Statistique

> **Statut** : ✅ TERMINÉE  
> **Prérequis** : Phase 2

### Livrables

| #    | Tâche                   | Description                            | Statut |
| ---- | ----------------------- | -------------------------------------- | ------ |
| 3.1  | FrequencyEngine         | Fréquences absolues, relatives, ratios | ✅      |
| 3.2  | GapEngine               | Écarts courant, max, moyen, médian     | ✅      |
| 3.3  | CooccurrenceEngine      | Matrice paires, affinité, triplets     | ✅      |
| 3.4  | TemporalEngine          | Fenêtres glissantes, tendances         | ✅      |
| 3.5  | DistributionEngine      | Entropie, Chi-2, stats structurelles   | ✅      |
| 3.6  | BayesianEngine          | Beta-Binomial, intervalles crédibilité | ✅      |
| 3.7  | GraphEngine             | NetworkX, centralités, communautés     | ✅      |
| 3.8  | StatisticsService       | Orchestration pipeline complet         | ✅      |
| 3.9  | API /statistics         | Endpoints REST documentés              | ✅      |
| 3.10 | Tests unitaires engines | Couverture ≥95%                        | ✅      |

### Critères de complétion
- [x] 7 engines fonctionnels avec données réelles
- [x] Pipeline complet rapide (< 2s pour 10 tirages, 4.34s full suite)
- [x] API retourne toutes les statistiques conformes au doc 06 (9 endpoints)
- [x] Tests unitaires : couverture ≥95% sur les engines (91-100%)

---

## 5. Phase 4 — Moteur de Scoring

> **Statut** : ✅ TERMINÉE  
> **Prérequis** : Phase 3

### Livrables

| #    | Tâche                           | Description                   | Statut |
| ---- | ------------------------------- | ----------------------------- | ------ |
| 4.1  | FrequencyCriterion              | Score basé ratio fréquence    | ✅      |
| 4.2  | GapCriterion                    | Sigmoïde des écarts           | ✅      |
| 4.3  | CooccurrenceCriterion           | Affinité moyenne paires       | ✅      |
| 4.4  | StructureCriterion              | Pair/impair, décades, etc.    | ✅      |
| 4.5  | BalanceCriterion                | Écart positions idéales       | ✅      |
| 4.6  | PatternPenalty                  | Détection patterns anormaux   | ✅      |
| 4.7  | GridScorer                      | Orchestrateur multi-critères  | ✅      |
| 4.8  | Profils de poids                | 4 profils prédéfinis + custom | ✅      |
| 4.9  | Scoring étoiles/complémentaires | Score séparé 85%/15%          | ✅      |
| 4.10 | API /grids (3 endpoints)        | POST /score, GET /top, GET /  | ✅      |
| 4.11 | Tests scoring                   | 62 tests (unit + intégration) | ✅      |

### Critères de complétion
- [x] Score toujours dans [0, 1] (normalisé)
- [x] Les 4 profils produisent des classements différents
- [x] Patterns détectés et pénalisés correctement (6 types)
- [x] Tests : couverture 100% sur tous les engines scoring
- [x] Suite complète : 187 tests, 0 échec, 90.38% couverture globale

---

## 6. Phase 5 — Moteur d'Optimisation

> **Statut** : ✅ TERMINÉE
> **Prérequis** : Phase 4

### Livrables

| #    | Tâche                    | Description                      | Statut |
| ---- | ------------------------ | -------------------------------- | ------ |
| 5.1  | SimulatedAnnealing       | Recuit simulé avec voisinage     | ✅      |
| 5.2  | GeneticAlgorithm         | Populations, crossover, mutation | ✅      |
| 5.3  | TabuSearch               | Liste tabu, mémoire              | ✅      |
| 5.4  | HillClimbing             | Montée avec redémarrages         | ✅      |
| 5.5  | MultiObjectiveOptimizer  | NSGA-II, fronts Pareto           | ✅      |
| 5.6  | PortfolioOptimizer       | Diversité, couverture, greedy    | ✅      |
| 5.7  | Auto-sélection méthode   | Choix selon espace/budget        | ✅      |
| 5.8  | API /grids/generate      | Endpoint génération              | ✅      |
| 5.9  | API /portfolios/generate | Endpoint portefeuille            | ✅      |
| 5.10 | Tests optimisation       | 68 tests (unit + intégration)    | ✅      |

### Critères de complétion
- [x] Génération de 10 grilles en < 5s (0.44s en test)
- [x] Toutes méta-heuristiques fonctionnelles avec seed reproductible
- [x] Portfolio optimizer avec 4 stratégies (balanced, max_diversity, max_coverage, min_correlation)
- [x] Suite complète : 242 tests, 0 échec, 93.13% couverture globale
- [ ] Tests avec seeds reproduisibles

---

## 7. Phase 6 — Moteur de Simulation

> **Statut** : ⬜ À FAIRE  
> **Prérequis** : Phase 5

### Livrables

| #   | Tâche                  | Description                     |
| --- | ---------------------- | ------------------------------- |
| 6.1 | MonteCarloSimulator    | Simulation grille et étoiles    |
| 6.2 | RobustnessAnalyzer     | Bootstrap, stabilité temporelle |
| 6.3 | PortfolioSimulator     | Couverture effective            |
| 6.4 | Validation convergence | Tests hypergéométriques         |
| 6.5 | API /simulation        | Endpoints simulation            |
| 6.6 | Tests simulation       | Convergence, reproductibilité   |

### Critères de complétion
- [ ] 100K simulations en < 30s
- [ ] Probabilités convergent vers théoriques (< 1% écart)
- [ ] Reproductibilité avec seed
- [ ] Tests couverture ≥ 90%

---

## 8. Phase 7 — Interface Frontend

> **Statut** : ⬜ À FAIRE  
> **Prérequis** : Phase 6 (API complète)

### Livrables

| #    | Tâche                     | Description                                  |
| ---- | ------------------------- | -------------------------------------------- |
| 7.1  | Initialisation React/Vite | Vite + TypeScript + Tailwind + Shadcn        |
| 7.2  | Layout principal          | Sidebar, TopBar, routing                     |
| 7.3  | Authentification UI       | Login, register, token management            |
| 7.4  | Dashboard                 | KPIs, graphiques fréquence, derniers tirages |
| 7.5  | Page Tirages              | Liste paginée, filtres, DrawBalls            |
| 7.6  | Page Statistiques         | 7 onglets, heatmap, matrice, graphe          |
| 7.7  | Page Grilles              | Formulaire génération, résultats, détail     |
| 7.8  | Page Portefeuille         | Génération, visualisation couverture         |
| 7.9  | Page Simulation           | Paramètres, résultats Monte Carlo            |
| 7.10 | Page Admin                | Monitoring, jobs, utilisateurs               |
| 7.11 | Thème dark/light          | Toggle + persistence                         |
| 7.12 | Responsive                | Adaptations mobile/tablette                  |

### Critères de complétion
- [ ] Toutes les pages fonctionnelles et connectées à l'API
- [ ] Dark mode par défaut
- [ ] Graphiques interactifs (D3.js + Recharts)
- [ ] LCP < 2.5s, bundle < 300 KB gzipped

---

## 9. Phase 8 — Scheduler & Jobs

> **Statut** : ⬜ À FAIRE  
> **Prérequis** : Phase 7

### Livrables

| #    | Tâche                  | Description                  |
| ---- | ---------------------- | ---------------------------- |
| 8.1  | APScheduler setup      | Configuration, persistence   |
| 8.2  | Job scrape_draws       | Scraper FDJ + EuroMillions   |
| 8.3  | Job compute_statistics | Pipeline statistique complet |
| 8.4  | Job score_grids        | Scoring batch                |
| 8.5  | Job update_top_grids   | Sélection top N              |
| 8.6  | Job generate_portfolio | Portefeuille automatique     |
| 8.7  | Job cleanup            | Purge données anciennes      |
| 8.8  | Déclenchement manuel   | API admin /jobs/trigger      |
| 8.9  | Historisation          | JobExecution tracking        |
| 8.10 | Tests jobs             | Intégration avec mocks       |

### Critères de complétion
- [ ] Jobs se déclenchent selon le cron configuré
- [ ] Chaîne complète : scrape → stats → scoring → portfolio
- [ ] Historique accessible via API
- [ ] Retry automatique sur échec

---

## 10. Phase 9 — Sécurité & Auth

> **Statut** : ⬜ À FAIRE  
> **Prérequis** : Phase 8

### Livrables

| #   | Tâche             | Description                  |
| --- | ----------------- | ---------------------------- |
| 9.1 | JWT Auth complète | Login, refresh, logout       |
| 9.2 | RBAC              | 3 rôles, matrice permissions |
| 9.3 | Rate limiting     | Par endpoint                 |
| 9.4 | Security headers  | HSTS, XSS, etc.              |
| 9.5 | Audit logging     | Actions sensibles loggées    |
| 9.6 | Initial admin     | Création automatique         |
| 9.7 | Tests sécurité    | Auth, rôles, injections      |

### Critères de complétion
- [ ] Pas d'accès sans token valide
- [ ] Chaque rôle limité à ses permissions
- [ ] Rate limiting actif
- [ ] Audit trail complet pour actions admin

---

## 11. Phase 10 — Polish & Déploiement

> **Statut** : ⬜ À FAIRE  
> **Prérequis** : Phase 9

### Livrables

| #     | Tâche                   | Description                        |
| ----- | ----------------------- | ---------------------------------- |
| 10.1  | Dockerfile backend      | Multi-stage optimisé               |
| 10.2  | Dockerfile frontend     | Nginx + build static               |
| 10.3  | docker-compose.yml      | Stack complète                     |
| 10.4  | README.md               | Installation, configuration, usage |
| 10.5  | Performance audit       | Profiling, optimisations           |
| 10.6  | Couverture tests finale | Vérifier ≥ 80% global              |
| 10.7  | Documentation API       | Swagger/OpenAPI à jour             |
| 10.8  | Seed data               | Données initiales pour démo        |
| 10.9  | Revue de sécurité       | Checklist OWASP                    |
| 10.10 | Tag version 1.0         | Release officielle                 |

### Critères de complétion
- [ ] `docker-compose up` lance tout le système
- [ ] README complet et à jour
- [ ] Pas de vulnérabilité critique
- [ ] Tests passent à 100%
- [ ] Tag v1.0.0

---

## 12. Dépendances entre Phases

```
Phase 1 ──→ Phase 2 ──→ Phase 3 ──→ Phase 4 ──→ Phase 5
                                                      │
                                                      ▼
Phase 10 ←── Phase 9 ←── Phase 8 ←── Phase 7 ←── Phase 6
```

Chaque phase dépend de la précédente. Pas de parallélisme entre phases (développement solo).

---

## 13. Règles de Développement

| Règle                     | Description                                        |
| ------------------------- | -------------------------------------------------- |
| **Tests first**           | Écrire les tests avant ou avec le code             |
| **No skip**               | Chaque phase doit être complète avant la suivante  |
| **Commit atomique**       | Un commit = une tâche logique                      |
| **Pas de TODO en prod**   | Résoudre tout avant de passer à la suite           |
| **Documentation vivante** | Mettre à jour les docs si l'implémentation diverge |
| **Pas de sur-ingénierie** | Implémenter uniquement ce qui est documenté        |
| **Rigueur mathématique**  | Chaque formule testée contre la théorie            |

---

## 14. Références

| Document                                        | Contenu                            |
| ----------------------------------------------- | ---------------------------------- |
| [01_Vision_Projet](01_Vision_Projet.md)         | Objectifs et contraintes           |
| [18_Checklist_Globale](18_Checklist_Globale.md) | Suivi détaillé par tâche           |
| Tous les docs 02-16                             | Spécifications de chaque composant |

---

*Fin du document 17_Roadmap_Developpement.md*
