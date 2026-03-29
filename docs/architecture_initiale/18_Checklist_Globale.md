# 18 — Checklist Globale

> **Projet** : LOTO ULTIME  
> **Version** : 2.0 — Audit profond vérifié  
> **Date** : 2026-03-29  
> **Méthode** : Chaque case cochée a été vérifiée par lecture du code source, exécution des tests, et vérification des fichiers.  
> **Références croisées** : [17_Roadmap](17_Roadmap_Developpement.md) · [01_Vision](01_Vision_Projet.md)

---

## Mode d'emploi

Cette checklist est **atomique** : chaque ligne = une tâche vérifiable.  
Cocher `[x]` au fur et à mesure de l'avancement.  
⚠️ = élément vérifié avec réserve (détail en commentaire).

---

## Phase 1 — Architecture & Documentation

- [x] 01_Vision_Projet.md rédigé
- [x] 02_Architecture_Globale.md rédigé
- [x] 03_Architecture_Backend.md rédigé
- [x] 04_Architecture_Frontend.md rédigé
- [x] 05_Modele_Donnees.md rédigé
- [x] 06_API_Design.md rédigé
- [x] 07_Moteur_Statistique.md rédigé
- [x] 08_Moteur_Scoring.md rédigé
- [x] 09_Moteur_Optimisation.md rédigé
- [x] 10_Moteur_Simulation.md rédigé
- [x] 11_Scheduler_et_Jobs.md rédigé
- [x] 12_Securite_et_Authentification.md rédigé
- [x] 13_Architecture_UI_UX.md rédigé
- [x] 14_Performance_et_Scalabilite.md rédigé
- [x] 15_Observabilite.md rédigé
- [x] 16_Strategie_Tests.md rédigé
- [x] 17_Roadmap_Developpement.md rédigé
- [x] 18_Checklist_Globale.md rédigé
- [x] README.md racine créé
- [ ] Cross-references validées entre tous les documents ⚠️ **README.md pointe vers `docs/01_Vision_Projet.md` mais fichiers réels dans `docs/architecture_initiale/` — liens cassés**

---

## Phase 2 — Fondations Backend

### 2.1 Initialisation projet
- [x] Répertoire `backend/` créé
- [x] `pyproject.toml` configuré (dependencies + dev-dependencies)
- [x] Environnement virtuel créé
- [x] Dépendances installées
- [x] Structure de dossiers conforme au doc 02

### 2.2 Configuration
- [x] `app/core/config.py` — Pydantic BaseSettings (HS256 + RS256, 25+ settings)
- [ ] `.env.example` avec toutes les variables ⚠️ **18 vars présentes mais ~6 manquantes** (JWT_ALGORITHM, FDJ_BASE_URL, EUROMILLIONS_BASE_URL, RATE_LIMIT_PER_MINUTE, PREVIOUS_SECRET_KEY, JWT_PRIVATE/PUBLIC_KEY) **+ nom incorrect ACCESS_TOKEN_EXPIRE_MINUTES ≠ JWT_EXPIRATION_MINUTES**
- [x] `game_configs/loto_fdj.yaml` créé (5/49 + 1/10)
- [x] `game_configs/euromillions.yaml` créé (5/50 + 2/12)
- [x] `game_configs/keno.yaml` créé (16/70)
- [x] `game_configs/mega_millions.yaml` créé (5/70 + 1/25)
- [x] `game_configs/powerball.yaml` créé (5/69 + 1/26)
- [x] Configuration testée (unit test — `test_config.py`)

### 2.3 Base de données
- [x] `app/models/base.py` — DeclarativeBase
- [x] `app/models/game.py` — GameDefinition
- [x] `app/models/draw.py` — Draw
- [x] `app/models/statistics.py` — StatisticsSnapshot
- [x] `app/models/grid.py` — ScoredGrid
- [x] `app/models/portfolio.py` — Portfolio
- [x] `app/models/user.py` — User + UserRole enum
- [x] `app/models/job.py` — JobExecution + JobStatus enum
- [x] Alembic initialisé
- [x] Migration initiale créée et testée (SQLite)
- [ ] Migration testée (PostgreSQL) → reporté Phase 10

### 2.4 Repositories
- [x] `app/repositories/base.py` — BaseRepository[T] générique
- [x] `app/repositories/game_repository.py` — GameRepository
- [x] `app/repositories/draw_repository.py` — DrawRepository
- [x] `app/repositories/statistics_repository.py` — StatisticsRepository
- [x] `app/repositories/grid_repository.py` — GridRepository
- [x] `app/repositories/portfolio_repository.py` — PortfolioRepository
- [x] `app/repositories/user_repository.py` — UserRepository
- [x] `app/repositories/job_repository.py` — JobRepository
- [x] Tests d'intégration repositories

### 2.5 Application FastAPI
- [x] `app/main.py` — create_app() avec lifespan
- [x] CORS middleware configuré
- [x] Timing middleware
- [x] Security headers middleware
- [x] Logging context middleware
- [x] `/health` endpoint fonctionnel
- [x] `/docs` (Swagger) accessible
- [x] structlog configuré (JSON + console)
- [x] Tests de démarrage application

---

## Phase 3 — Moteur Statistique

### 3.1 Engines
- [x] `app/engines/statistics/frequency.py` — FrequencyEngine
- [x] Tests FrequencyEngine
- [x] `app/engines/statistics/gap.py` — GapEngine
- [x] Tests GapEngine
- [x] `app/engines/statistics/cooccurrence.py` — CooccurrenceEngine
- [x] Tests CooccurrenceEngine
- [x] `app/engines/statistics/temporal.py` — TemporalEngine
- [x] Tests TemporalEngine
- [x] `app/engines/statistics/distribution.py` — DistributionEngine
- [x] Tests DistributionEngine
- [x] `app/engines/statistics/bayesian.py` — BayesianEngine
- [x] Tests BayesianEngine
- [x] `app/engines/statistics/graph.py` — GraphEngine
- [x] Tests GraphEngine
- 59 tests engines statistiques, tous passants. Couverture par engine non mesurée individuellement.

### 3.2 Service & API
- [x] `app/services/statistics.py` — StatisticsService (pipeline 7 engines, MIN_DRAWS=10)
- [x] Tests StatisticsService (3 tests service)
- [x] `app/api/v1/statistics.py` — 9 endpoints REST (8 GET + 1 POST recompute)
- [x] Tests intégration API /statistics ⚠️ **2 tests échouent actuellement (307 redirect trailing slash)**
- [x] Pipeline complet rapide (10 tirages < 2s)
- [x] Validation mathématique (Chi-2, hypergéométrique)

---

## Phase 4 — Moteur de Scoring

### 4.1 Critères
- [x] `app/engines/scoring/frequency_criterion.py`
- [x] `app/engines/scoring/gap_criterion.py`
- [x] `app/engines/scoring/cooccurrence_criterion.py`
- [x] `app/engines/scoring/structure_criterion.py`
- [x] `app/engines/scoring/balance_criterion.py`
- [x] `app/engines/scoring/pattern_penalty.py`
- [x] Tests unitaires chaque critère (49 tests scoring)

### 4.2 Scorer & API
- [x] `app/engines/scoring/scorer.py` — GridScorer (4 profils + custom + stars)
- [x] Profils de poids (4 prédéfinis + custom)
- [x] Scoring étoiles/complémentaires
- [x] Tests scorer
- [x] `app/services/grid.py` — GridService (12 méthodes)
- [x] `app/api/v1/grids.py` — 9 endpoints (score, generate, top, CRUD, favorite, played)
- [x] Tests intégration API

---

## Phase 5 — Moteur d'Optimisation

### 5.1 Méta-heuristiques
- [x] `app/engines/optimization/simulated_annealing.py`
- [x] `app/engines/optimization/genetic.py`
- [x] `app/engines/optimization/tabu.py`
- [x] `app/engines/optimization/hill_climbing.py`
- [x] `app/engines/optimization/multi_objective.py`
- [x] 45 tests optimisation, tous passants

### 5.2 Portfolio & API
- [x] `app/engines/optimization/portfolio.py` — PortfolioOptimizer (4 stratégies : balanced, max_diversity, max_coverage, min_correlation)
- [x] Tests PortfolioOptimizer
- [x] Auto-sélection de méthode (`method_selector.py`)
- [x] `app/api/v1/grids.py` — POST /grids/generate
- [x] `app/api/v1/portfolios.py` — 2 endpoints (POST generate + DELETE)
- [x] Tests intégration API
- [x] Génération 10 grilles < 5s

---

## Phase 6 — Moteur de Simulation

### 6.1 Engines
- [x] `app/engines/simulation/monte_carlo.py` — MonteCarloSimulator + SimulationResult + PortfolioSimulationResult
- [x] Tests convergence Monte Carlo (hypergéométrique)
- [x] `app/engines/simulation/robustness.py` — RobustnessAnalyzer + StabilityResult + ComparisonResult
- [x] Tests stabilité bootstrap
- [x] Simulation portefeuille (couverture effective)
- [x] Validation hypergéométrique (scipy.stats.hypergeom)
- 24 tests simulation, tous passants

### 6.2 Service & API
- [x] `app/services/simulation.py` — SimulationService (4 méthodes : grid, portfolio, stability, compare)
- [x] `app/api/v1/simulations.py` — 4 endpoints (monte-carlo, portfolio, stability, compare-random)
- [x] Tests intégration API
- [x] Reproductibilité seed confirmée

---

## Phase 7 — Interface Frontend

### 7.1 Setup
- [x] Projet Vite 8 + **React 19** + TypeScript 5.9 ⚠️ React 19, pas 18 comme prévu initialement
- [x] Tailwind CSS v4.2 configuré (dark mode via @custom-variant dark)
- [x] Composants custom Tailwind (Shadcn/ui non utilisé — remplacé par composants maison)
- [x] Axios instance avec intercepteur JWT ⚠️ **Intercepteur request (Bearer token) + response (401→logout). PAS de refresh token automatique — un 401 déconnecte l'utilisateur.**
- [x] TanStack Query configuré (staleTime 5min, retry 1, refetchOnWindowFocus: false)
- [x] Zustand stores (auth + game + settings) avec persist middleware
- [x] React Router v6.30 avec guards auth (RequireAuth + RequireRole hiérarchie 3 niveaux)

### 7.2 Layout
- [x] Sidebar navigation (collapse/expand, 11 nav items, icônes Lucide, mobile drawer, touche Escape)
- [x] TopBar/Header (game selector dropdown `<select>`, theme toggle Sun/Moon)
- [x] Layout responsive (MainLayout flex + `<Outlet>` + ErrorBoundary + AiCoach + OnboardingTour + skip-link)

### 7.3 Pages (13 pages vérifiées, toutes avec contenu réel)
- [x] LoginPage — formulaire email/password (react-hook-form + zod)
- [x] DashboardPage — 6 KPIs + bar chart fréquences Recharts + top 5 grilles + 5 derniers tirages
- [x] DrawsPage — liste paginée avec DrawBalls + contrôles pagination
- [x] StatisticsPage — **8 onglets** (7 base + StarsTab dynamique si étoiles) :
  - [x] Fréquences : NumberHeatmap + top 10 bar chart + bottom 10 + table complète
  - [x] Écarts : alertes critiques (gap > 2× expected) + bar chart top 20 + table
  - [x] Cooccurrences : top 20 + bottom 20 paires affinité (listes triées, **pas de matrice D3**)
  - [x] Tendances : fenêtres temporelles (hot/cold per window) + momentum régression linéaire
  - [x] Distribution : entropy, Chi-2 (statistic + p-value), sommes (mean/std/min/max/median), pairs/impairs, décades
  - [x] Bayésien : bar chart postérieures Recharts (top 20) + table α, β, posterior_mean, IC 95%
  - [x] Graphe : D3.js force-directed + communautés Louvain + zoom/pan/drag + sizing par degré
  - [x] Étoiles : fréquences étoiles/numéros chance (dynamique, visible si jeu a des étoiles)
- [x] GridsPage (176 lignes) — formulaire génération (méthode, count, profil) + liste résultats + ScoreBar × 6 critères
- [x] PortfolioPage — génération (stratégie + count) + KPIs (diversité, couverture, hamming) + NumberHeatmap
- [x] SimulationPage — 3 onglets : Monte Carlo, Stabilité bootstrap, Comparaison aléatoire + Recharts
- [x] FavoritesPage (176 lignes) — page dédiée grilles favorites
- [x] HistoryPage (353 lignes) — comparaison grilles vs tirages passés
- [x] GlossaryPage (147 lignes) — glossaire termes statistiques
- [x] HowItWorksPage (90 lignes) — page pédagogique
- [x] AdminPage — **5 onglets** : overview (status cards), jobs (trigger + historique), users (liste + création), games, settings
- [x] NotFoundPage (21 lignes) — page 404

### 7.4 Composants
- [x] DrawBalls (numéros bleu + étoiles violet, 3 tailles sm/md/lg, highlights, role="group" + aria-label)
- [x] ScoreBar (barre gradient vert/ambre/rouge, role="progressbar", aria-valuenow, poids + InfoTooltip)
- [x] NumberHeatmap (grille colorée, 3 échelles : frequency/gap/score, Tailwind opacity classes)
- [ ] CooccurrenceMatrix (D3.js heatmap complète) → **non implémenté, CooccurrenceTab affiche des listes texte triées**
- [x] NetworkGraph (GraphTab — D3.js force-directed, d3.zoom, d3.drag, communautés Louvain, sizing par degré, schemeTableau10)
- [x] Toast notifications (Sonner, position bottom-right, theme dark, richColors, closeButton)

### 7.5 Qualité
- [x] Dark mode par défaut + toggle (class-based .dark/.light, persist localStorage via settingsStore, onRehydrateStorage)
- [ ] LCP < 2.5s → non mesuré (web-vitals non installé)
- [x] Bundle < 300 KB gzipped — 238 KB gzip JS + 5 KB gzip CSS ✅
- [ ] Navigation clavier complète → partiel (focus-visible, aria-labels sur composants clés, mais pas de skip-nav complet sur toutes les pages)
- [ ] Code-splitting lazy routes → **non fait** — toutes les pages importées statiquement dans App.tsx, pas de React.lazy()

### 7.6 Tests frontend
- [x] 7 fichiers test unitaires Vitest (28 tests) ⚠️ **1 test échoue actuellement** (LoadingSpinner default message)
- [x] 4 specs E2E Playwright (admin, grids, login-statistics, simulation)
- [x] 9 fichiers types, 9 fichiers services, 6 hooks custom

---

## Phase 8 — Scheduler & Jobs

- [x] APScheduler configuré et démarré dans le lifespan (AsyncIOScheduler, Europe/Paris, coalesce=True, max_instances=1)
- [x] Nightly pipeline orchestrateur (`nightly_pipeline.py` — cron 22:00, chaîne fetch→stats→scoring→top→portfolio)
- [x] Job `fetch_draws` (Loto FDJ) — scraper CSV ZIP FDJ
- [x] Job `fetch_draws` (EuroMillions) — scraper CSV ZIP FDJ
- [x] Job `fetch_draws` (Keno) — scraper CSV ZIP FDJ (16 boules)
- [x] Scraper FDJ Loto fonctionnel (httpx, CSV parsing, validation) — couverture 85%
- [x] Scraper EuroMillions fonctionnel — couverture 93%
- [ ] Scraper Keno fonctionnel ⚠️ **code existe mais couverture 26% — non testé en profondeur**
- [x] Scraper Mega Millions implémenté (JSON API US) ⚠️ **couverture 21% — tests minimaux**
- [x] Scraper Powerball implémenté (JSON API US) ⚠️ **couverture 21% — tests minimaux**
- [x] Job `compute_statistics` (chaîné après scraping)
- [x] Job `compute_scoring`
- [x] Job `compute_top_grids`
- [x] Job `optimize_portfolio`
- [x] Job `cleanup_old_data` (cron 03:00 — grids >30j, portfolios >30j, jobs >90j, stats >30j)
- [x] Job `check_system_health` (every 30 min)
- [x] Job `backup_db` (weekly dimanche 04:00)
- [x] Déclenchement manuel via API admin (4 endpoints : trigger, list, history, status)
- [x] Historisation dans JobExecution (PENDING→RUNNING→SUCCESS/FAILED)
- [x] Retry automatique (MAX_RETRIES=3, delays [0, 5, 30]s dans runner.py)
- [x] Verrouillage concurrence (max_instances=1 via APScheduler)

---

## Phase 9 — Sécurité & Auth

- [x] `app/core/security.py` — hash_password (bcrypt), verify_password, create_access_token, create_refresh_token, decode_access_token (supporte HS256 + RS256 + rotation de clé)
- [x] POST /auth/login fonctionnel (rate limited **20/min** via slowapi)
- [x] POST /auth/register fonctionnel (admin only, rate limited 3/min)
- [x] POST /auth/refresh fonctionnel (rotation JTI + blacklist ancien token)
- [x] POST /auth/logout fonctionnel (révocation refresh token via blacklist)
- [x] GET /auth/me — info utilisateur courant
- [x] GET /auth/users — liste utilisateurs (admin only)
- [x] Dépendance `get_current_user` (JWT decode + type="access" + user lookup + check active)
- [x] Dépendance `require_role` (hiérarchie CONSULTATION=1 < UTILISATEUR=2 < ADMIN=3)
- [x] RBAC appliqué sur tous les endpoints (jobs=ADMIN, grids/portfolios/simulations=UTILISATEUR, recompute=ADMIN, games/draws/stats basiques=public)
- [x] Security headers middleware (X-Content-Type-Options, X-Frame-Options: DENY, X-XSS-Protection, Referrer-Policy, Permissions-Policy, HSTS production)
- [x] Validation mot de passe (min 8 car., 1 majuscule, 1 minuscule, 1 chiffre)
- [x] Création admin initial au démarrage (`_seed_admin()` dans lifespan, ADMIN_EMAIL + ADMIN_INITIAL_PASSWORD)
- [x] Token blacklist implémenté (`token_blacklist.py`) ⚠️ **en mémoire uniquement — perdu au redémarrage du serveur**
- [x] Audit logging des actions sensibles (structlog)
- [x] Tests auth (23 tests : login, token, rôles, refresh, validation, admin seed)
- [x] Frontend: RequireAuth guard + RequireRole pour admin
- [x] Frontend: page Admin > Utilisateurs (liste + création)
- [x] Frontend: sidebar conditionnel (admin link masqué pour non-admin)
- [x] Frontend: logout + user info dans sidebar

---

## Phase 10 — Polish & Déploiement

### 10.1 Conteneurisation
- [ ] Dockerfile backend multi-stage ⚠️ **Existe mais single-stage** (`FROM python:3.12-slim AS base` — 1 seul FROM, pas de build séparé)
- [x] Dockerfile frontend multi-stage Nginx (node:22-alpine AS build → nginx:alpine, 2 FROM)
- [x] docker-compose.yml (4 services : backend, frontend, Prometheus, Grafana + 3 volumes)
- [x] .dockerignore (backend + frontend)

### 10.2 CI/CD
- [x] `.github/workflows/ci.yml` — Lint (ruff + ESLint) + Tests + Coverage
- [x] `.github/workflows/deploy.yml` — Build Docker (GHCR) + Déploiement

### 10.3 Documentation
- [ ] README.md complet ⚠️ **Existe (180 lignes, sections installation/config/usage/docker/roadmap) mais liens docs cassés** (`docs/01_Vision.md` au lieu de `docs/architecture_initiale/01_Vision.md`)
- [ ] CONTRIBUTING.md — **absent**
- [ ] `.env.example` complet ⚠️ **18 vars mais ~6 manquantes** + nom `ACCESS_TOKEN_EXPIRE_MINUTES` ≠ `JWT_EXPIRATION_MINUTES` dans config.py

### 10.4 Qualité & Performance
- [ ] Performance audit (profiling endpoints lents) — non fait
- [ ] Optimisations identifiées appliquées — non fait
- [ ] Couverture tests globale ≥ 80% — **76.97% actuellement** (3673 statements, 846 manqués). Seuil configuré à 80%, échoue.
- [x] Swagger/OpenAPI à jour (auto-généré par FastAPI, /docs accessible)

### 10.5 Données & Migration
- [x] Seed games (5 jeux) + seed admin au démarrage (lifespan `_seed_games()` + `_seed_admin()`)
- [ ] Seed data tirages pour démo — pas de tirages pré-chargés depuis un clean install
- [ ] Migration testée (PostgreSQL) — jamais testé sur PostgreSQL

### 10.6 Sécurité & Release
- [ ] Revue sécurité OWASP Top 10 — non fait formellement
- [x] Données sensibles dans .env uniquement (SECRET_KEY, ADMIN_INITIAL_PASSWORD, DB URL)
- [ ] Tag git v1.0.0 — **aucun tag git** 
- [ ] Changelog v1.0.0 — **aucun fichier CHANGELOG**

---

## Récapitulatif

| Phase                           | Tâches  | Fait    | Statut                     |
| ------------------------------- | ------- | ------- | -------------------------- |
| 1. Architecture & Documentation | 20      | 19/20   | 🟡 95% (cross-refs cassées) |
| 2. Fondations Backend           | 36      | 34/36   | 🟡 94% (.env.example + PG)  |
| 3. Moteur Statistique           | 18      | 18/18   | ✅ Complète                 |
| 4. Moteur de Scoring            | 13      | 13/13   | ✅ Complète                 |
| 5. Moteur d'Optimisation        | 13      | 13/13   | ✅ Complète                 |
| 6. Moteur de Simulation         | 10      | 10/10   | ✅ Complète                 |
| 7. Interface Frontend           | 49      | 43/49   | 🟡 88% (6 manquants)        |
| 8. Scheduler & Jobs             | 21      | 20/21   | 🟡 95% (Keno scraper)       |
| 9. Sécurité & Auth              | 20      | 20/20   | ✅ Complète                 |
| 10. Polish & Déploiement        | 19      | 7/19    | 🔴 37%                      |
| **TOTAL**                       | **219** | **197** | **90%**                    |

### État global mesuré (2026-03-29)

- **Backend** : 425 tests, 420 passants, 5 échouent (307 redirects trailing slash)
- **Frontend** : 28 tests Vitest, 27 passants, 1 échoue (LoadingSpinner)
- **Couverture backend** : **76.97%** (seuil 80% non atteint)
- **Scrapers peu testés** : keno 26%, mega_millions 21%, powerball 21%
- **Pas de tag git**, pas de CHANGELOG, pas de CONTRIBUTING.md
- **Liens docs cassés** dans README.md

### Problèmes à corriger en priorité

1. ❌ 5 tests backend échouent (307 trailing slash dans tests intégration)
2. ❌ 1 test frontend échoue (LoadingSpinner default message)
3. ❌ Couverture 76.97% < 80% requis
4. ❌ Liens README.md cassés (`docs/` → `docs/architecture_initiale/`)
5. ❌ `.env.example` incomplet + nom variable incorrect
6. ❌ Backend Dockerfile single-stage (devrait être multi-stage)
7. ⚠️ Token blacklist en mémoire (perdu au redémarrage)
8. ⚠️ Axios intercepteur : pas de refresh token, 401 = déconnexion directe
9. ⚠️ Pas de code-splitting (React.lazy) dans le frontend

---

*Fin du document 18_Checklist_Globale.md — v2.0 audit profond*
