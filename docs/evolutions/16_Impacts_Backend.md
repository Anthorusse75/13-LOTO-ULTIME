# 16 — Impacts Backend

> Analyse complète des impacts de toutes les évolutions sur le backend : services, engines, modèles, repositories, configuration.

---

## Références croisées

- [00_Index_Evolutions](./00_Index_Evolutions.md)
- [03_Audit_Existant_et_Ecarts](./03_Audit_Existant_et_Ecarts.md) — Bugs et dettes techniques
- [05_Evolutions_Algorithmiques](./05_Evolutions_Algorithmiques.md)
- [06_Evolutions_Fonctionnelles](./06_Evolutions_Fonctionnelles.md)
- [18_Impacts_API](./18_Impacts_API.md) — Vue API
- [19_Impacts_Base_De_Donnees](./19_Impacts_Base_De_Donnees.md) — Vue DB

---

## 1. État actuel du backend

### Structure existante

```
backend/
├── app/
│   ├── main.py                  # FastAPI app, startup, CORS, routers
│   ├── config.py                # Settings (Pydantic BaseSettings)
│   ├── database.py              # AsyncSession, engine, get_db
│   ├── models/                  # 7 modèles SQLAlchemy
│   │   ├── user.py              # User (ADMIN, UTILISATEUR, CONSULTATION)
│   │   ├── game.py              # GameDefinition
│   │   ├── draw.py              # Draw
│   │   ├── grid.py              # ScoredGrid
│   │   ├── statistics.py        # StatisticsSnapshot
│   │   ├── portfolio.py         # Portfolio
│   │   └── job.py               # JobExecution
│   ├── schemas/                 # Pydantic v2 schemas
│   ├── routers/                 # 9 routers (41 endpoints)
│   ├── services/                # Services métier
│   ├── engines/                 # Moteurs algorithmiques
│   │   ├── statistics/          # 7 analyseurs
│   │   ├── scoring/             # 6 critères + scorer
│   │   ├── optimization/        # 5 algorithmes + portfolio
│   │   └── simulation/          # Monte Carlo, Robustness
│   ├── scheduler/               # 9 jobs APScheduler
│   ├── scrapers/                # 5 scrapers (1 par loterie)
│   └── tests/                   # 337 tests
```

### Métriques existantes

| Métrique | Valeur |
|----------|--------|
| Modèles SQLAlchemy | 7 |
| Schemas Pydantic | ~30 |
| Routers | 9 |
| Endpoints | 41 |
| Services | ~8 |
| Engines | ~20 modules |
| Tests | 337 |

---

## 2. Nouveaux modèles SQLAlchemy

| Modèle | Source (doc) | Table | Colonnes principales |
|--------|-------------|-------|---------------------|
| `GamePrizeTier` | 08 | `game_prize_tiers` | game_id, rank, name, match_numbers, match_stars, avg_prize, probability |
| `WheelingSystem` | 08 | `wheeling_systems` | user_id, game_id, selected_numbers, selected_stars, guarantee_level, grids(JSON), grid_count, total_cost, coverage_rate, reduction_rate |
| `BudgetPlan` | 09 | `budget_plans` | user_id, game_id, budget, objective, selected_numbers, recommendations(JSON), chosen_strategy |
| `UserSavedResult` | 11 | `user_saved_results` | user_id, type, parameters(JSON), result_data(JSON), is_favorite, tags |
| `GridDrawResult` | 15 | `grid_draw_results` | scored_grid_id, draw_id, matched_numbers, matched_stars, match_count, prize_rank, estimated_prize |
| `UserNotification` | 15 | `user_notifications` | user_id, type, title, message, data(JSON), is_read |

**Total modèles** : 7 existants + 6 nouveaux = **13 modèles**

### Colonnes ajoutées sur modèles existants

| Modèle | Colonne | Type | Doc |
|--------|---------|------|-----|
| `ScoredGrid` | `user_id` | FK nullable | 11 |
| `Portfolio` | `user_id` | FK nullable | 11 |
| `StatisticsSnapshot` | `hot_cold_summary` | JSON nullable | 15 |

---

## 3. Nouveaux modules engines/

### engines/wheeling/ (doc 08)

```
engines/wheeling/
├── __init__.py
├── greedy_cover.py       # Algorithme greedy Set Cover
├── coverage.py           # Calcul matrice de couverture
├── cost_estimator.py     # Estimation coûts
├── gain_analyzer.py      # Scénarios de gains conditionnels
└── engine.py             # Orchestrateur WheelingEngine
```

### engines/explainability/ (doc 12)

```
engines/explainability/
├── __init__.py
├── grid_explainer.py       # Explication d'une grille
├── portfolio_explainer.py  # Explication d'un portefeuille
├── wheeling_explainer.py   # Explication d'un système réduit
├── simulation_explainer.py # Explication d'une simulation
├── comparison_explainer.py # Explication d'une comparaison
└── templates.py            # Templates textuels (français)
```

### engines/budget/ (doc 09)

```
engines/budget/
├── __init__.py
├── optimizer.py          # BudgetOptimizer (Pareto 3 stratégies)
└── strategies.py         # TopStrategy, PortfolioStrategy, WheelingStrategy
```

---

## 4. Nouveaux services

| Service | Doc | Méthodes principales |
|---------|-----|---------------------|
| `WheelingService` | 08 | `preview()`, `generate()`, `list_history()`, `get_detail()`, `delete()` |
| `BudgetService` | 09 | `optimize()`, `list_plans()`, `get_plan()` |
| `ComparisonService` | 10 | `compare()` (stateless, pas de stockage) |
| `HistoryService` | 11 | `save()`, `list()`, `detail()`, `duplicate()`, `delete()` |
| `ExplainabilityService` | 12 | `explain_grid()`, `explain_portfolio()`, `explain_wheeling()`, `explain_simulation()`, `explain_comparison()` |
| `SuggestionService` | 15 | `get_daily_suggestion()` |
| `NotificationService` | 15 | `list()`, `mark_read()`, `mark_all_read()`, `unread_count()`, `create()` |

**Total services** : ~8 existants + 7 nouveaux = **~15 services**

---

## 5. Corrections de bugs (impacts backend)

### BUG-01 : Multi-lottery game_id non fonctionnel (doc 03)

**Fichiers impactés** :
- `services/grid_service.py` — Passer game_id à tous les appels engines
- `services/statistics_service.py` — Filtrer par game_id
- `engines/scoring/scorer.py` — Recevoir game_id, adapter les bornes
- `engines/statistics/*.py` — Tous les analyseurs doivent filtrer par game_id
- `engines/optimization/*.py` — Adapter aux paramètres du jeu sélectionné

**Effort** : 3–5 jours (transversal, beaucoup de fichiers)

### BUG-02 : method_selector toujours "genetic" (doc 03)

**Fichier** : `engines/optimization/method_selector.py`
**Fix** : Corriger la logique de sélection (conditions inversées ou jamais atteintes)
**Effort** : 0.5 jour

### BUG-03 : Profil scoring non envoyé à l'API (doc 03)

**Fichier** : Frontend principalement (cf. doc 17), mais côté backend vérifier que le endpoint `/grids/generate` accepte bien le paramètre `profile`.
**Effort** : 0.5 jour (côté backend)

---

## 6. Dettes techniques à corriger

### DT-01 : Pas de versioning API

**Action** : Préfixer tous les routers avec `/api/v1/` (déjà partiellement fait, uniformiser).

### DT-02 : Token blacklist en mémoire

**Action** : Migrer `token_blacklist: set` vers une table `TokenBlacklist` ou Redis.
**Recommandation** : Table PostgreSQL avec TTL auto (job cleanup).

### DT-03 : Pas de cache applicatif

**Action** : Ajouter un mécanisme de cache in-process pour les statistiques (qui changent 1x/jour max).
**Options** : `cachetools.TTLCache` ou Redis si disponible.

### DT-04 : Pas de rate limiting granulaire

**Action** : Ajouter `slowapi` avec rate limits différenciés par route.

### DT-05 : Pas de pagination sur les listes

**Action** : Ajouter pagination (limit/offset) sur `/draws`, `/grids`, `/statistics`, et tous les nouveaux endpoints.

---

## 7. Fichiers de configuration impactés

| Fichier | Changements |
|---------|-------------|
| `config.py` | Nouvelles variables : `WHEELING_MAX_NUMBERS`, `BUDGET_MAX`, `NOTIFICATION_RETENTION_DAYS` |
| `main.py` | Nouveaux routers : wheeling, budget, comparison, history, notifications, suggestions |
| `database.py` | Import nouveaux modèles |
| `requirements.txt` | `slowapi` (rate limiting), `cachetools` (cache) |

---

## 8. Matrice évolutions × fichiers backend

| Évolution | Modèles | Engines | Services | Routers | Schemas | Tests |
|-----------|---------|---------|----------|---------|---------|-------|
| Wheeling (08) | +2 | +5 fichiers | +1 | +1 (6 endpoints) | +4 | +16 |
| Budget (09) | +1 | +2 fichiers | +1 | +1 (4 endpoints) | +3 | +10 |
| Comparateur (10) | — | — | +1 | +1 (1 endpoint) | +2 | +8 |
| Historique (11) | +1, +2 cols | — | +1 | +1 (8 endpoints) | +3 | +12 |
| Explicabilité (12) | — | +6 fichiers | +1 | intégré | +1 | +10 |
| Tooltips (13) | — | — | — | — | — | — |
| Pédagogie (14) | — | — | — | — | — | — |
| Automatisation (15) | +2 | — | +2 | +1 (5 endpoints) | +3 | +10 |

**Total estimé** : +6 modèles, +13 fichiers engines, +7 services, +5 routers (+24 endpoints), +16 schemas, +66 tests

---

## 9. Risques backend

| Risque | Impact | Mitigation |
|--------|--------|------------|
| Explosion du nombre de fichiers | Complexité accrue | Respecter la structure existante, éviter les fichiers monolithiques |
| Couplage entre services | Maintenance difficile | Injection de dépendances, interfaces claires |
| Régression multi-lottery | Casse du scoring existant | Tests de non-régression avant/après BUG-01 fix |
| Performance engines wheeling | Lenteur n>15 | Borner à n≤20, timeout, cache des résultats |

---

## 10. Checklist locale

- [ ] Corriger BUG-01 : propager game_id dans tous les services et engines
- [ ] Corriger BUG-02 : fix method_selector
- [ ] Corriger BUG-03 : vérifier endpoint accepte profile
- [ ] DT-01 : Uniformiser préfixe /api/v1/
- [ ] DT-02 : Migrer token_blacklist vers PostgreSQL
- [ ] DT-03 : Ajouter cachetools pour statistiques
- [ ] DT-04 : Ajouter slowapi rate limiting
- [ ] DT-05 : Ajouter pagination limit/offset
- [ ] Créer 6 nouveaux modèles SQLAlchemy
- [ ] Créer engines/wheeling/ (5 fichiers)
- [ ] Créer engines/explainability/ (6 fichiers)
- [ ] Créer engines/budget/ (2 fichiers)
- [ ] Créer 7 nouveaux services
- [ ] Créer 5 nouveaux routers
- [ ] Créer ~16 nouveaux schemas Pydantic
- [ ] Ajouter ~66 tests pour les nouvelles fonctionnalités
- [ ] Mettre à jour config.py avec nouvelles variables
- [ ] Mettre à jour main.py avec nouveaux routers
- [ ] Mettre à jour requirements.txt

Réf. : [27_Checklist_Globale_Evolutions](./27_Checklist_Globale_Evolutions.md)
