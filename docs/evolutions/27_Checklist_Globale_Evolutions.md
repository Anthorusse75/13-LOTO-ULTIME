# 27 — Checklist Globale des Évolutions

> Liste exhaustive de toutes les tâches atomiques, avec références croisées aux documents, phases, et statut.

---

## Références croisées

- [00_Index_Evolutions](./00_Index_Evolutions.md)
- [26_Roadmap_Evolutions](./26_Roadmap_Evolutions.md) — Planning et phases
- Chaque tâche référence son document source

---

## Convention

- **Préfixe** : indique le domaine (B = Backend, F = Frontend, DB = Database, API = API, JOB = Scheduler, SEC = Sécurité, TEST = Tests, DOC = Documentation, UX = UI/UX)
- **Phase** : P0, A, B, C, D, E
- **Statut** : ⬜ À faire | 🔄 En cours | ✅ Fait

---

## Phase P0 — Bugs critiques (Semaine 1)

| ID | Tâche | Doc | Statut |
|----|-------|-----|--------|
| B-01 | Fix BUG-01 : propager game_id dans tous les services | 03, 16 | ⬜ |
| B-02 | Fix BUG-01 : propager game_id dans tous les engines/statistics | 03, 16 | ⬜ |
| B-03 | Fix BUG-01 : propager game_id dans engines/scoring | 03, 16 | ⬜ |
| B-04 | Fix BUG-01 : propager game_id dans engines/optimization | 03, 16 | ⬜ |
| B-05 | Fix BUG-02 : corriger logique method_selector | 03, 16 | ⬜ |
| B-06 | Fix BUG-03 : vérifier endpoint grids/generate accepte profile | 03, 16 | ⬜ |
| F-01 | Fix BUG-03 : envoyer profile depuis GridsPage au API | 03, 17 | ⬜ |
| TEST-01 | Capturer snapshots SNAP-01 à SNAP-04 (avant fix) | 24 | ⬜ |
| TEST-02 | Vérifier snapshots après fix BUG-01 | 24 | ⬜ |
| TEST-03 | Vérifier snapshots après fix BUG-02 | 24 | ⬜ |
| TEST-04 | S'assurer 337 tests existants passent | 24 | ⬜ |

---

## Phase A — Quick wins techniques (Semaine 2)

| ID | Tâche | Doc | Statut |
|----|-------|-----|--------|
| DB-01 | Créer table token_blacklist + migration | 21, 19 | ⬜ |
| B-07 | Implémenter TokenBlacklistService | 21 | ⬜ |
| B-08 | Migrer blacklist mémoire → PostgreSQL | 21 | ⬜ |
| B-09 | Installer et configurer slowapi (rate limiting) | 21, 18 | ⬜ |
| B-10 | Appliquer rate limits par catégorie d'endpoint | 21, 18 | ⬜ |
| B-11 | Implémenter PaginationParams + PaginatedResponse | 18 | ⬜ |
| API-01 | Paginer GET /draws | 18 | ⬜ |
| API-02 | Paginer GET /grids | 18 | ⬜ |
| B-12 | Implémenter TTLCache pour statistiques | 22 | ⬜ |
| B-13 | Implémenter cache pour game_definitions | 22 | ⬜ |
| DB-02 | Créer index scored_grids(game_id, score) | 19, 22 | ⬜ |
| DB-03 | Créer index draws(game_id, draw_date) | 19, 22 | ⬜ |
| B-14 | Uniformiser préfixe /api/v1/ sur tous les routers | 18 | ⬜ |
| TEST-05 | Tests rate limiting (2 tests) | 25 | ⬜ |
| TEST-06 | Tests pagination (2 tests) | 25 | ⬜ |
| TEST-07 | Tests cache (2 tests) | 25 | ⬜ |
| TEST-08 | Tests blacklist (2 tests) | 25 | ⬜ |

---

## Phase B — Fondations fonctionnelles (Semaines 3–5)

### B.1–B.3 : Historique et données de base

| ID | Tâche | Doc | Statut |
|----|-------|-----|--------|
| DB-04 | Créer table game_prize_tiers + migration | 19 | ⬜ |
| DB-05 | Seed data : rangs Loto FDJ (9 rangs) | 19 | ⬜ |
| DB-06 | Seed data : rangs EuroMillions (13 rangs) | 19 | ⬜ |
| DB-07 | Seed data : rangs PowerBall, Mega, Keno | 19 | ⬜ |
| DB-08 | Créer table user_saved_results + migration | 19 | ⬜ |
| DB-09 | Ajouter user_id sur scored_grids (migration) | 19 | ⬜ |
| DB-10 | Ajouter user_id sur portfolios (migration) | 19 | ⬜ |
| B-15 | Implémenter HistoryService (save, list, detail, duplicate, delete) | 11, 16 | ⬜ |
| API-03 | Créer router history (8 endpoints) | 11, 18 | ⬜ |
| API-04 | Implémenter ownership check sur history endpoints | 21 | ⬜ |
| F-02 | Créer composant SaveButton | 11, 17 | ⬜ |
| F-03 | Créer composant ReplayButton | 11, 17 | ⬜ |
| F-04 | Créer composant SavedResultCard | 11, 17 | ⬜ |
| F-05 | Créer composant HistoryFilters | 11, 17 | ⬜ |
| F-06 | Enrichir HistoryPage avec filtres, pagination, 6 types | 11, 17 | ⬜ |
| F-07 | Créer service historyApi.ts | 11, 17 | ⬜ |
| F-08 | Créer types/history.ts | 11, 17 | ⬜ |
| F-09 | Créer hook useSaveResult() | 11, 17 | ⬜ |
| TEST-09 | Tests historique (12 tests) | 25 | ⬜ |

### B.4–B.5 : Explicabilité et aide contextuelle

| ID | Tâche | Doc | Statut |
|----|-------|-----|--------|
| B-16 | Créer engines/explainability/__init__.py | 12, 16 | ⬜ |
| B-17 | Créer grid_explainer.py | 12, 16 | ⬜ |
| B-18 | Créer portfolio_explainer.py | 12, 16 | ⬜ |
| B-19 | Créer wheeling_explainer.py | 12, 16 | ⬜ |
| B-20 | Créer simulation_explainer.py | 12, 16 | ⬜ |
| B-21 | Créer comparison_explainer.py | 12, 16 | ⬜ |
| B-22 | Créer templates.py (templates français) | 12, 16 | ⬜ |
| B-23 | Intégrer explanation dans schema GridResponse | 12, 18 | ⬜ |
| B-24 | Intégrer explanation dans schema PortfolioResponse | 12, 18 | ⬜ |
| B-25 | Intégrer explanation dans schema SimulationResponse | 12, 18 | ⬜ |
| F-10 | Créer composant ExplanationPanel | 12, 17 | ⬜ |
| F-11 | Intégrer ExplanationPanel dans GridsPage | 12, 17 | ⬜ |
| F-12 | Intégrer ExplanationPanel dans PortfolioPage | 12, 17 | ⬜ |
| F-13 | Intégrer ExplanationPanel dans SimulationPage | 12, 17 | ⬜ |
| F-14 | Créer utils/helpTexts.ts centralisé | 13, 17 | ⬜ |
| F-15 | Créer composant EmptyState enrichi | 13, 17 | ⬜ |
| F-16 | Créer composant LoadingState enrichi | 13, 17 | ⬜ |
| F-17 | Créer composant ErrorState enrichi | 13, 17 | ⬜ |
| F-18 | Enrichir tooltips sur DrawsPage | 13 | ⬜ |
| F-19 | Enrichir tooltips sur StatisticsPage | 13 | ⬜ |
| F-20 | Enrichir tooltips sur PortfolioPage | 13 | ⬜ |
| F-21 | Ajouter empty states sur pages sans données | 13 | ⬜ |
| TEST-10 | Tests explicabilité (10 tests) | 25 | ⬜ |

### B.6–B.9 : Pédagogie, design, dashboard

| ID | Tâche | Doc | Statut |
|----|-------|-----|--------|
| F-22 | PED-01 : Section « Comprendre les scores » | 14, 17 | ⬜ |
| F-23 | PED-02 : Section « Comprendre les simulations » | 14, 17 | ⬜ |
| F-24 | PED-03 : Section « Comprendre les stratégies » | 14, 17 | ⬜ |
| F-25 | PED-05 : Section « Loto vs EuroMillions » | 14, 17 | ⬜ |
| F-26 | PED-06 : Section « Limites réelles » + disclaimer | 14, 17 | ⬜ |
| F-27 | Créer composant LearnSection | 14, 17 | ⬜ |
| F-28 | Créer composant LearnTOC | 14, 17 | ⬜ |
| F-29 | Enrichir HowItWorksPage avec sections pédagogiques | 14, 17 | ⬜ |
| F-30 | Définir design tokens CSS variables | 07, 17 | ⬜ |
| F-31 | Créer composant DataTable<T> générique | 07, 17 | ⬜ |
| F-32 | Créer composant StatCard avec sparkline | 07, 17 | ⬜ |
| F-33 | Créer LatestDrawCard | 15, 17 | ⬜ |
| F-34 | Créer DailyTopGridsCard | 15, 17 | ⬜ |
| F-35 | Créer PortfolioSummaryCard | 15, 17 | ⬜ |
| F-36 | Créer StatOfTheDay | 15, 17 | ⬜ |
| F-37 | Enrichir DashboardPage avec 5 blocs | 15, 17 | ⬜ |
| DB-11 | Ajouter hot_cold_summary sur statistics_snapshots | 19, 15 | ⬜ |
| JOB-01 | Implémenter compute_hot_cold_summary | 20, 15 | ⬜ |
| JOB-02 | Implémenter pre_generate_daily_content | 20, 15 | ⬜ |

---

## Phase C — Cœur produit (Semaines 6–8)

### C.1–C.3 : Wheeling

| ID | Tâche | Doc | Statut |
|----|-------|-----|--------|
| B-26 | Créer engines/wheeling/greedy_cover.py | 08, 16 | ⬜ |
| B-27 | Créer engines/wheeling/coverage.py | 08, 16 | ⬜ |
| B-28 | Créer engines/wheeling/cost_estimator.py | 08, 16 | ⬜ |
| B-29 | Créer engines/wheeling/gain_analyzer.py | 08, 16 | ⬜ |
| B-30 | Créer engines/wheeling/engine.py | 08, 16 | ⬜ |
| B-31 | Implémenter WheelingService | 08, 16 | ⬜ |
| DB-12 | Créer table wheeling_systems + migration | 19 | ⬜ |
| API-05 | Créer router wheeling (6 endpoints) | 08, 18 | ⬜ |
| API-06 | Validation : n ≤ 20, t ∈ [2, k-1] | 08, 18, 21 | ⬜ |
| API-07 | Timeout 30s sur wheeling/generate | 22 | ⬜ |
| F-38 | Créer composant NumberGrid | 08, 17 | ⬜ |
| F-39 | Créer composant StarsGrid | 08, 17 | ⬜ |
| F-40 | Créer composant SelectionSummary | 08, 17 | ⬜ |
| F-41 | Créer composant WheelingConfig | 08, 17 | ⬜ |
| F-42 | Créer composant WheelingPreview | 08, 17 | ⬜ |
| F-43 | Créer composant WheelingResults | 08, 17 | ⬜ |
| F-44 | Créer composant CoverageMatrix | 08, 17 | ⬜ |
| F-45 | Créer composant GainScenariosTable | 08, 17 | ⬜ |
| F-46 | Créer WheelingPage + route /wheeling | 08, 17 | ⬜ |
| F-47 | Créer service wheelingApi.ts | 08, 17 | ⬜ |
| F-48 | Créer types/wheeling.ts | 08, 17 | ⬜ |
| F-49 | Créer hook useWheeling() | 08, 17 | ⬜ |
| TEST-11 | Tests wheeling unitaires (8 tests) | 25 | ⬜ |
| TEST-12 | Tests wheeling intégration (4 tests) | 25 | ⬜ |
| TEST-13 | Tests wheeling API (4 tests) | 25 | ⬜ |

### C.4 : Budget

| ID | Tâche | Doc | Statut |
|----|-------|-----|--------|
| B-32 | Créer engines/budget/optimizer.py | 09, 16 | ⬜ |
| B-33 | Créer engines/budget/strategies.py | 09, 16 | ⬜ |
| B-34 | Implémenter BudgetService | 09, 16 | ⬜ |
| DB-13 | Créer table budget_plans + migration | 19 | ⬜ |
| API-08 | Créer router budget (4 endpoints) | 09, 18 | ⬜ |
| F-50 | Créer composant BudgetInput | 09, 17 | ⬜ |
| F-51 | Créer composant ObjectiveSelector | 09, 17 | ⬜ |
| F-52 | Créer composant BudgetRecommendationCard | 09, 17 | ⬜ |
| F-53 | Créer composant BudgetResults | 09, 17 | ⬜ |
| F-54 | Créer composant GainScenarioBar | 09, 17 | ⬜ |
| F-55 | Créer BudgetPage + route /budget | 09, 17 | ⬜ |
| F-56 | Créer service budgetApi.ts | 09, 17 | ⬜ |
| F-57 | Créer types/budget.ts | 09, 17 | ⬜ |
| TEST-14 | Tests budget (10 tests) | 25 | ⬜ |

---

## Phase D — Profondeur (Semaines 9–11)

### D.1 : Comparateur

| ID | Tâche | Doc | Statut |
|----|-------|-----|--------|
| B-35 | Implémenter ComparisonService | 10, 16 | ⬜ |
| API-09 | Créer router comparison (1 endpoint) | 10, 18 | ⬜ |
| F-58 | Créer composant StrategySelector | 10, 17 | ⬜ |
| F-59 | Créer composant ComparisonTable | 10, 17 | ⬜ |
| F-60 | Créer composant ComparisonRadar | 10, 17 | ⬜ |
| F-61 | Créer composant ComparisonScatter | 10, 17 | ⬜ |
| F-62 | Créer composant ComparisonSummary | 10, 17 | ⬜ |
| F-63 | Créer ComparatorPage + route /comparator | 10, 17 | ⬜ |
| F-64 | Créer service comparisonApi.ts | 10, 17 | ⬜ |
| F-65 | Créer types/comparison.ts | 10, 17 | ⬜ |
| TEST-15 | Tests comparateur (8 tests) | 25 | ⬜ |

### D.2–D.3 : Automatisation

| ID | Tâche | Doc | Statut |
|----|-------|-----|--------|
| DB-14 | Créer table grid_draw_results + migration | 19 | ⬜ |
| JOB-03 | Implémenter check_played_grids | 20, 15 | ⬜ |
| B-36 | Implémenter logique comparaison numéros vs tirage | 15, 16 | ⬜ |
| B-37 | Implémenter determine_prize_rank (via game_prize_tiers) | 15, 16 | ⬜ |
| F-66 | Créer composant PlayedGridsResults | 15, 17 | ⬜ |
| F-67 | Créer composant NextDrawCountdown | 15, 17 | ⬜ |
| B-38 | Implémenter SuggestionService | 15, 16 | ⬜ |
| API-10 | Créer endpoint GET /suggestions/daily | 15, 18 | ⬜ |
| F-68 | Créer composant DailySuggestionCard | 15, 17 | ⬜ |
| JOB-04 | Implémenter generate_daily_suggestion | 20, 15 | ⬜ |
| JOB-05 | Étendre nightly_pipeline avec nouveaux steps | 20, 15 | ⬜ |
| TEST-16 | Tests automatisation (10 tests) | 25 | ⬜ |

### D.4 : Notifications

| ID | Tâche | Doc | Statut |
|----|-------|-----|--------|
| DB-15 | Créer table user_notifications + migration | 19 | ⬜ |
| B-39 | Implémenter NotificationService | 15, 16 | ⬜ |
| API-11 | Créer router notifications (4 endpoints) | 15, 18 | ⬜ |
| JOB-06 | Implémenter create_grid_result_notifications | 20, 15 | ⬜ |
| JOB-07 | Implémenter create_new_draw_notifications | 20, 15 | ⬜ |
| JOB-08 | Implémenter cleanup_notifications | 20, 15 | ⬜ |
| F-69 | Créer composant NotificationBell | 15, 17 | ⬜ |
| F-70 | Créer composant NotificationDropdown | 15, 17 | ⬜ |
| F-71 | Créer service notificationApi.ts | 15, 17 | ⬜ |
| F-72 | Créer hook useNotifications() | 15, 17 | ⬜ |
| F-73 | Créer types/notification.ts | 15, 17 | ⬜ |

### D.5 : Mode expert/simplifié

| ID | Tâche | Doc | Statut |
|----|-------|-----|--------|
| F-74 | Ajouter displayMode dans settingsStore | 07, 17 | ⬜ |
| F-75 | Créer hook useDisplayMode() | 07, 17 | ⬜ |
| F-76 | Créer composant ModeToggle | 07, 17 | ⬜ |
| F-77 | Appliquer mode conditionnel sur StatisticsPage | 07 | ⬜ |
| F-78 | Appliquer mode conditionnel sur GridsPage | 07 | ⬜ |

---

## Phase E — Premium (Semaines 12–14)

| ID | Tâche | Doc | Statut |
|----|-------|-----|--------|
| F-79 | PED-04 : Section « Systèmes réduits » (pédagogie) | 14 | ⬜ |
| F-80 | PED-07 : Section « Coûts et compromis » | 14 | ⬜ |
| F-81 | Enrichir GlossaryPage avec liens vers sections | 14 | ⬜ |
| F-82 | Restructurer Sidebar par catégories | 07 | ⬜ |
| F-83 | Ajouter breadcrumbs | 07 | ⬜ |
| F-84 | Implémenter thème clair (light mode) | 07 | ⬜ |
| F-85 | Ajouter theme dans settingsStore | 07 | ⬜ |
| F-86 | Responsive amélioré (sm/md breakpoints) | 07 | ⬜ |
| F-87 | Onboarding tour enrichi | 07 | ⬜ |
| B-40 | Implémenter star scoring séparé | 06, 05 | ⬜ |
| B-41 | Multi-format export (PDF, CSV, JSON) dans ExportMenu | 06, 16 | ⬜ |
| F-88 | Créer composant ExportMenu | 06, 17 | ⬜ |
| F-89 | Code splitting React.lazy pour Wheeling, Budget, Comparator | 22 | ⬜ |
| JOB-09 | Implémenter cleanup_anonymous_data | 20 | ⬜ |
| DB-16 | Créer tous les index secondaires (migration finale) | 19 | ⬜ |
| DOC-01 | Créer RUNBOOK_DEPLOYMENT.md | 23 | ⬜ |
| DOC-02 | Créer RUNBOOK_ROLLBACK.md | 23 | ⬜ |
| DOC-03 | Configurer feature flags | 23 | ⬜ |

### Observabilité (Phase E)

| ID | Tâche | Doc | Statut |
|----|-------|-----|--------|
| OBS-01 | Ajouter métriques Prometheus pour wheeling, budget, comparison | 23 | ⬜ |
| OBS-02 | Créer dashboard Grafana : Wheeling | 23 | ⬜ |
| OBS-03 | Créer dashboard Grafana : Pipeline étendu | 23 | ⬜ |
| OBS-04 | Créer dashboard Grafana : Cache | 23 | ⬜ |
| OBS-05 | Configurer alertes critiques | 23 | ⬜ |
| OBS-06 | Configurer alertes warning | 23 | ⬜ |
| OBS-07 | Ajouter logs structurés pour nouveaux modules | 23 | ⬜ |

---

## Résumé quantitatif

| Domaine | Tâches |
|---------|--------|
| Backend (B-xx) | 41 |
| Frontend (F-xx) | 89 |
| Database (DB-xx) | 16 |
| API (API-xx) | 11 |
| Scheduler (JOB-xx) | 9 |
| Tests (TEST-xx) | 16 groupes (~74 tests) |
| Documentation (DOC-xx) | 3 |
| Observabilité (OBS-xx) | 7 |
| Sécurité (inclus dans B/API) | — |
| **Total tâches** | **~192** |

---

## Compteurs de progression

| Phase | Tâches | Faites | % |
|-------|--------|--------|---|
| P0 | 11 | 0 | 0% |
| A | 17 | 0 | 0% |
| B | 40 | 0 | 0% |
| C | 39 | 0 | 0% |
| D | 34 | 0 | 0% |
| E | 26 + 7 obs | 0 | 0% |
| **Total** | **~174** | **0** | **0%** |
