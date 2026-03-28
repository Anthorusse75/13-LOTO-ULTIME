# 02 — Architecture Globale

> **Projet** : LOTO ULTIME  
> **Version** : 1.0  
> **Date** : 2026-03-27  
> **Références croisées** : [01_Vision](01_Vision_Projet.md) · [03_Backend](03_Architecture_Backend.md) · [04_Frontend](04_Architecture_Frontend.md) · [05_Modele](05_Modele_Donnees.md) · [06_API](06_API_Design.md)

---

## 1. Vue d'Ensemble

LOTO ULTIME est un système client-serveur composé de couches indépendantes communiquant via une API HTTP REST. L'architecture suit les principes **hexagonal / ports & adapters** pour garantir la testabilité et l'extensibilité.

```
┌──────────────────────────────────────────────────────────────────┐
│                         FRONTEND (SPA)                           │
│          React / TypeScript · Dark Mode · Graphiques             │
└──────────────────────┬───────────────────────────────────────────┘
                       │ HTTPS / REST API
┌──────────────────────▼───────────────────────────────────────────┐
│                        API GATEWAY (FastAPI)                      │
│         Routing · Auth · Rate Limiting · Validation              │
├──────────────────────────────────────────────────────────────────┤
│                       SERVICE LAYER                               │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌────────────┐ │
│  │ Draw Service │ │ Stats Svc   │ │ Grid Svc    │ │ Portfolio  │ │
│  │             │ │             │ │             │ │ Svc        │ │
│  └──────┬──────┘ └──────┬──────┘ └──────┬──────┘ └─────┬──────┘ │
├─────────┼───────────────┼───────────────┼───────────────┼────────┤
│         │          ENGINE LAYER         │               │        │
│  ┌──────▼──────┐ ┌──────▼──────┐ ┌──────▼──────┐ ┌─────▼──────┐ │
│  │ Moteur      │ │ Moteur      │ │ Moteur      │ │ Moteur     │ │
│  │ Statistique │ │ Scoring     │ │ Optimisation│ │ Simulation │ │
│  │ [doc 07]    │ │ [doc 08]    │ │ [doc 09]    │ │ [doc 10]   │ │
│  └──────┬──────┘ └──────┬──────┘ └──────┬──────┘ └─────┬──────┘ │
├─────────┼───────────────┼───────────────┼───────────────┼────────┤
│         │         DATA ACCESS LAYER     │               │        │
│  ┌──────▼───────────────▼───────────────▼───────────────▼──────┐ │
│  │                    Repository Pattern                        │ │
│  │              SQLAlchemy ORM · Alembic Migrations             │ │
│  └──────────────────────┬───────────────────────────────────────┘ │
├──────────────────────────┼───────────────────────────────────────┤
│  ┌──────────────────────▼───────────────────────────────────────┐ │
│  │                    PostgreSQL / SQLite                        │ │
│  │           (SQLite dev · PostgreSQL prod/docker)              │ │
│  └──────────────────────────────────────────────────────────────┘ │
├──────────────────────────────────────────────────────────────────┤
│                       SCHEDULER LAYER                            │
│           APScheduler · Jobs · Cron · Retry · Locking           │
│                        [doc 11]                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

## 2. Principes Architecturaux

### 2.1 Architecture Hexagonale (Ports & Adapters)

```
          ┌─────────────────────────┐
          │      DOMAINE MÉTIER     │
          │  (Moteurs, Scoring,     │
          │   Modèles, Règles)      │
          └─────┬──────────┬────────┘
                │          │
         ┌──────▼──┐  ┌───▼───────┐
         │  PORTS  │  │  PORTS    │
         │ ENTRANTS│  │ SORTANTS  │
         │ (API,   │  │ (DB,      │
         │  CLI)   │  │  HTTP,    │
         │         │  │  Files)   │
         └─────────┘  └──────────┘
```

**Règle d'or** : Le domaine métier ne dépend d'aucune infrastructure. Les dépendances pointent vers l'intérieur.

### 2.2 Principes SOLID appliqués

| Principe | Application |
|---|---|
| **S** — Single Responsibility | Chaque moteur a une responsabilité unique |
| **O** — Open/Closed | Ajout de jeux/algorithmes par configuration/extension |
| **L** — Liskov Substitution | Interfaces communes pour les stratégies d'optimisation |
| **I** — Interface Segregation | Ports API séparés par domaine fonctionnel |
| **D** — Dependency Inversion | Services injectés, pas instanciés directement |

### 2.3 Séparation des responsabilités

| Couche | Responsabilité | Ne fait PAS |
|---|---|---|
| Frontend | Affichage, interaction | Calcul métier |
| API | Routing, validation, sérialisation | Logique métier complexe |
| Services | Orchestration, coordination | Accès direct DB |
| Moteurs | Calcul pur | I/O, persistance |
| Repositories | Accès données | Logique métier |
| Scheduler | Planification, exécution jobs | Calcul direct |

---

## 3. Stack Technologique

### 3.1 Backend

| Composant | Technologie | Justification |
|---|---|---|
| Langage | **Python 3.11+** | Écosystème scientifique, lisibilité |
| Framework web | **FastAPI** | Async, auto-doc OpenAPI, performant |
| ORM | **SQLAlchemy 2.0** | Mature, flexible, typage |
| Migrations | **Alembic** | Standard SQLAlchemy |
| BDD dev | **SQLite** | Zéro config, fichier local |
| BDD prod | **PostgreSQL 15+** | Robuste, performant |
| Scheduler | **APScheduler** | Python natif, persistant |
| Calcul scientifique | **NumPy, SciPy** | Référence calcul numérique |
| Graphes | **NetworkX** | Analyse graphes Python |
| Validation | **Pydantic v2** | Validation données, sérialisation |
| Auth | **python-jose (JWT)** | Tokens stateless |
| Hash passwords | **passlib[bcrypt]** | Standard sécurité |
| HTTP client | **httpx** | Async, moderne |
| Tests | **pytest** | Standard Python |

### 3.2 Frontend

| Composant | Technologie | Justification |
|---|---|---|
| Framework | **React 18+** | Écosystème riche, composants |
| Langage | **TypeScript** | Typage statique, maintenabilité |
| UI Kit | **Shadcn/ui + Tailwind CSS** | Moderne, dark mode natif |
| Graphiques | **Recharts / D3.js** | Visualisations interactives |
| State | **Zustand** | Léger, simple |
| HTTP | **Axios / TanStack Query** | Cache, retry, invalidation |
| Routing | **React Router v6** | Standard React |
| Build | **Vite** | Rapide, ESM natif |

### 3.3 Outillage

| Outil | Usage |
|---|---|
| **Ruff** | Linter + formatter Python |
| **mypy** | Vérification types statiques |
| **ESLint + Prettier** | Lint/format frontend |
| **pre-commit** | Hooks git |
| **Docker / Docker Compose** | Déploiement futur |

---

## 4. Organisation du Code Source

```
loto-ultime/
├── docs/                          # Documentation (ce dossier)
│   ├── 01_Vision_Projet.md
│   ├── 02_Architecture_Globale.md
│   ├── ...
│   └── 18_Checklist_Globale.md
│
├── backend/                       # Application backend Python
│   ├── alembic/                   # Migrations de base de données
│   │   ├── versions/
│   │   └── env.py
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                # Point d'entrée FastAPI
│   │   ├── config.py              # Configuration (Pydantic Settings)
│   │   ├── dependencies.py        # Injection de dépendances
│   │   │
│   │   ├── models/                # Modèles SQLAlchemy (ORM)
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── game.py            # GameDefinition
│   │   │   ├── draw.py            # Draw (tirage)
│   │   │   ├── statistics.py      # StatisticsSnapshot
│   │   │   ├── grid.py            # Grid, GridScore
│   │   │   ├── portfolio.py       # Portfolio
│   │   │   ├── user.py            # User, Role
│   │   │   └── job.py             # JobExecution
│   │   │
│   │   ├── schemas/               # Schémas Pydantic (API)
│   │   │   ├── __init__.py
│   │   │   ├── game.py
│   │   │   ├── draw.py
│   │   │   ├── statistics.py
│   │   │   ├── grid.py
│   │   │   ├── portfolio.py
│   │   │   ├── user.py
│   │   │   ├── auth.py
│   │   │   └── job.py
│   │   │
│   │   ├── repositories/          # Accès données (pattern Repository)
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── draw_repository.py
│   │   │   ├── game_repository.py
│   │   │   ├── statistics_repository.py
│   │   │   ├── grid_repository.py
│   │   │   ├── portfolio_repository.py
│   │   │   ├── user_repository.py
│   │   │   └── job_repository.py
│   │   │
│   │   ├── services/              # Couche service (orchestration)
│   │   │   ├── __init__.py
│   │   │   ├── draw_service.py
│   │   │   ├── statistics_service.py
│   │   │   ├── scoring_service.py
│   │   │   ├── grid_service.py
│   │   │   ├── portfolio_service.py
│   │   │   ├── simulation_service.py
│   │   │   ├── auth_service.py
│   │   │   └── job_service.py
│   │   │
│   │   ├── engines/               # Moteurs de calcul (domaine pur)
│   │   │   ├── __init__.py
│   │   │   ├── statistics/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── frequency.py
│   │   │   │   ├── gaps.py
│   │   │   │   ├── cooccurrence.py
│   │   │   │   ├── temporal.py
│   │   │   │   ├── distribution.py
│   │   │   │   └── bayesian.py
│   │   │   │
│   │   │   ├── scoring/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── scorer.py
│   │   │   │   ├── criteria/
│   │   │   │   │   ├── frequency_score.py
│   │   │   │   │   ├── gap_score.py
│   │   │   │   │   ├── cooccurrence_score.py
│   │   │   │   │   ├── structure_score.py
│   │   │   │   │   ├── balance_score.py
│   │   │   │   │   └── pattern_penalty.py
│   │   │   │   └── weights.py
│   │   │   │
│   │   │   ├── optimization/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── simulated_annealing.py
│   │   │   │   ├── genetic_algorithm.py
│   │   │   │   ├── tabu_search.py
│   │   │   │   ├── hill_climbing.py
│   │   │   │   ├── multi_objective.py
│   │   │   │   └── portfolio_optimizer.py
│   │   │   │
│   │   │   ├── simulation/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── monte_carlo.py
│   │   │   │   └── robustness.py
│   │   │   │
│   │   │   └── graph/
│   │   │       ├── __init__.py
│   │   │       ├── cooccurrence_graph.py
│   │   │       ├── centrality.py
│   │   │       └── community.py
│   │   │
│   │   ├── api/                   # Routes API (FastAPI Routers)
│   │   │   ├── __init__.py
│   │   │   ├── v1/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── games.py
│   │   │   │   ├── draws.py
│   │   │   │   ├── statistics.py
│   │   │   │   ├── grids.py
│   │   │   │   ├── portfolios.py
│   │   │   │   ├── simulation.py
│   │   │   │   ├── jobs.py
│   │   │   │   ├── auth.py
│   │   │   │   └── admin.py
│   │   │   └── deps.py
│   │   │
│   │   ├── scrapers/              # Récupération tirages externes
│   │   │   ├── __init__.py
│   │   │   ├── base_scraper.py
│   │   │   ├── fdj_loto_scraper.py
│   │   │   └── euromillions_scraper.py
│   │   │
│   │   ├── scheduler/             # Planification des tâches
│   │   │   ├── __init__.py
│   │   │   ├── scheduler.py
│   │   │   └── jobs/
│   │   │       ├── __init__.py
│   │   │       ├── fetch_draws.py
│   │   │       ├── compute_statistics.py
│   │   │       ├── compute_scoring.py
│   │   │       ├── compute_top_grids.py
│   │   │       └── optimize_portfolio.py
│   │   │
│   │   └── core/                  # Utilitaires transversaux
│   │       ├── __init__.py
│   │       ├── security.py        # JWT, hashing
│   │       ├── logging.py         # Configuration logs
│   │       ├── exceptions.py      # Exceptions personnalisées
│   │       └── game_definitions.py # Configs jeux (YAML/JSON)
│   │
│   ├── tests/                     # Tests backend
│   │   ├── conftest.py
│   │   ├── unit/
│   │   │   ├── engines/
│   │   │   ├── services/
│   │   │   └── repositories/
│   │   ├── integration/
│   │   │   ├── api/
│   │   │   └── scheduler/
│   │   └── fixtures/
│   │       └── sample_draws.json
│   │
│   ├── game_configs/              # Fichiers configuration jeux
│   │   ├── loto_fdj.yaml
│   │   └── euromillions.yaml
│   │
│   ├── alembic.ini
│   ├── pyproject.toml
│   └── requirements.txt
│
├── frontend/                      # Application frontend React
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── hooks/
│   │   ├── services/
│   │   ├── stores/
│   │   ├── types/
│   │   └── utils/
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   └── tailwind.config.ts
│
├── docker/                        # Configuration Docker (futur)
│   ├── Dockerfile.backend
│   ├── Dockerfile.frontend
│   └── docker-compose.yml
│
├── .env.example
├── .gitignore
├── README.md
└── Makefile
```

---

## 5. Flux de Données Principaux

### 5.1 Flux d'ingestion des tirages

```
Source externe (FDJ/EuroMillions)
        │
        ▼
   Scraper (httpx)
        │
        ▼
   Validation (Pydantic)
        │
        ▼
   Repository → DB (SQLAlchemy)
        │
        ▼
   Event: NEW_DRAW_INGESTED
        │
        ├──▶ Recalcul statistiques
        ├──▶ Recalcul scoring
        ├──▶ Recalcul top grilles
        └──▶ Recalcul portefeuille
```

### 5.2 Flux de génération de grilles

```
Requête utilisateur (API)
        │
        ▼
   Grid Service
        │
        ├──▶ Charge statistiques courantes
        ├──▶ Charge configuration jeu
        │
        ▼
   Moteur Scoring (évalue)
        │
        ▼
   Moteur Optimisation (explore)
        │
        ├──▶ Recuit simulé
        ├──▶ Algorithme génétique
        ├──▶ Recherche tabou
        │
        ▼
   Top N grilles scorées
        │
        ▼
   Moteur Simulation (valide)
        │
        ▼
   Résultat → API → Frontend
```

### 5.3 Flux du scheduler

```
APScheduler (cron trigger)
        │
        ▼
   Job: fetch_draws
        │
        ├──▶ Vérifie nouveaux tirages
        ├──▶ Télécharge si nouveau
        ├──▶ Valide données
        ├──▶ Stocke en DB
        │
        ▼
   Job: compute_statistics
        │
        ├──▶ Fréquences
        ├──▶ Gaps
        ├──▶ Cooccurrences
        ├──▶ Analyse temporelle
        │
        ▼
   Job: compute_scoring → compute_top_grids → optimize_portfolio
```

---

## 6. Communication Inter-Modules

### 6.1 Injection de dépendances

FastAPI utilise son système de `Depends()` pour injecter :

- Session de base de données
- Repositories
- Services
- Utilisateur courant (authentifié)
- Configuration jeu

### 6.2 Pattern de communication

| Source | Destination | Mécanisme |
|---|---|---|
| Frontend → Backend | API REST (HTTP/JSON) | Requêtes HTTP |
| API → Service | Appel direct (Python) | Injection dépendances |
| Service → Moteur | Appel direct (Python) | Passage objets domaine |
| Service → Repository | Appel direct (Python) | Injection dépendances |
| Scheduler → Service | Appel direct (Python) | Même process |
| Scraper → Source externe | HTTP GET | httpx async |

---

## 7. Stratégie de Persistance

### 7.1 Développement

- **SQLite** : fichier local `loto_ultime.db`
- Zéro configuration serveur
- Migrations Alembic compatibles

### 7.2 Production / Docker

- **PostgreSQL 15+**
- Connection pooling
- Même modèles, même migrations

### 7.3 Abstraction

Le `Repository Pattern` garantit que le code métier ne dépend jamais directement de la base de données.

→ Détails : [05_Modele_Donnees](05_Modele_Donnees.md)

---

## 8. Sécurité Transversale

| Couche | Mécanisme | Détail dans |
|---|---|---|
| API | JWT Bearer tokens | [12](12_Securite_et_Authentification.md) |
| API | Rate limiting | [12](12_Securite_et_Authentification.md) |
| API | CORS configuré | [12](12_Securite_et_Authentification.md) |
| Données | Validation Pydantic | [06](06_API_Design.md) |
| Auth | bcrypt + JWT | [12](12_Securite_et_Authentification.md) |
| Rôles | RBAC (Admin/User/Read) | [12](12_Securite_et_Authentification.md) |

---

## 9. Dockerisation Future

L'architecture est conçue pour être dockerisée sans modification du code :

```yaml
# docker-compose.yml (futur)
services:
  db:
    image: postgres:15
    volumes: [pgdata:/var/lib/postgresql/data]
    
  backend:
    build: ./docker/Dockerfile.backend
    depends_on: [db]
    environment:
      DATABASE_URL: postgresql://...
    
  frontend:
    build: ./docker/Dockerfile.frontend
    depends_on: [backend]
    
  scheduler:
    build: ./docker/Dockerfile.backend
    command: python -m app.scheduler
    depends_on: [db]
```

**Prérequis pour la dockerisation** :
- Configuration externalisée via variables d'environnement
- Pas de chemins codés en dur
- Health checks sur chaque service
- Volumes pour la persistance

→ Détails : [14_Performance_et_Scalabilite](14_Performance_et_Scalabilite.md)

---

## 10. Références

| Document | Contenu |
|---|---|
| [01_Vision_Projet](01_Vision_Projet.md) | Contexte et objectifs |
| [03_Architecture_Backend](03_Architecture_Backend.md) | Détail architecture serveur |
| [04_Architecture_Frontend](04_Architecture_Frontend.md) | Détail architecture client |
| [05_Modele_Donnees](05_Modele_Donnees.md) | Modèles, schémas, BDD |
| [06_API_Design](06_API_Design.md) | Spécification API REST |
| [14_Performance_et_Scalabilite](14_Performance_et_Scalabilite.md) | Docker, scaling |

---

*Fin du document 02_Architecture_Globale.md*
