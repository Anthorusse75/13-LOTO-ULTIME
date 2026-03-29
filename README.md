# LOTO ULTIME

> Système d'analyse combinatoire avancée pour loteries — Outil d'aide à la décision basé sur les statistiques, les heuristiques et l'optimisation combinatoire.

---

## Présentation

**LOTO ULTIME** est une application web professionnelle d'analyse de tirages de loterie. Elle combine 7 moteurs statistiques, un scoring multicritères, des méta-heuristiques d'optimisation et des simulations Monte Carlo pour générer des grilles optimisées et des portefeuilles diversifiés.

### Contrainte fondamentale

> **Aucun modèle de machine learning, aucun réseau de neurones, aucune API d'IA.**  
> Uniquement : probabilités, statistiques descriptives, heuristiques, optimisation combinatoire, simulation Monte Carlo, inférence bayésienne empirique.

### Loteries supportées

| Loterie      | Configuration                          | Jours de tirage |
| ------------ | -------------------------------------- | --------------- |
| Loto FDJ     | 5 numéros / 49 + 1 complémentaire / 10 | Lun, Mer, Sam   |
| EuroMillions | 5 numéros / 50 + 2 étoiles / 12        | Mar, Ven        |

L'architecture est **game-agnostic** : toute loterie peut être ajoutée via configuration YAML.

---

## Stack Technique

### Backend
- Python 3.11+, FastAPI, SQLAlchemy 2.0, Alembic, Pydantic v2
- APScheduler, NumPy, SciPy, NetworkX
- structlog, uvicorn, httpx

### Frontend
- React 19, TypeScript 5.9, Vite 8
- Tailwind CSS v4 (dark mode par défaut)
- Recharts, D3.js, Zustand 5, TanStack Query v5

### Base de données
- SQLite (développement) / PostgreSQL 15+ (production)

---

## Architecture

Architecture hexagonale (ports & adapters) avec séparation stricte des couches :

```
API (FastAPI Routers)
  └── Services (orchestration)
        ├── Engines (calculs purs)
        └── Repositories (accès données)
              └── Models (SQLAlchemy)
```

### Moteurs

| Moteur                      | Rôle                                                                         |
| --------------------------- | ---------------------------------------------------------------------------- |
| **Statistique** (7 engines) | Fréquences, écarts, cooccurrences, tendances, distribution, bayésien, graphe |
| **Scoring**                 | Score multicritères 0-10 avec 6 critères + pénalités patterns                |
| **Optimisation**            | Recuit simulé, algorithme génétique, tabou, hill climbing, NSGA-II           |
| **Simulation**              | Monte Carlo, analyse de robustesse, validation bootstrap                     |

---

## Documentation

La documentation complète du projet se trouve dans le dossier [`docs/`](docs/) :

| #   | Document                                                                                      | Description                                        |
| --- | --------------------------------------------------------------------------------------------- | -------------------------------------------------- |
| 01  | [Vision du Projet](docs/architecture_initiale/01_Vision_Projet.md)                            | Objectifs, contraintes, périmètre                  |
| 02  | [Architecture Globale](docs/architecture_initiale/02_Architecture_Globale.md)                 | Vue système, stack technique, flux de données      |
| 03  | [Architecture Backend](docs/architecture_initiale/03_Architecture_Backend.md)                 | Couches, DI, configuration, scrapers               |
| 04  | [Architecture Frontend](docs/architecture_initiale/04_Architecture_Frontend.md)               | React SPA, routing, state management               |
| 05  | [Modèle de Données](docs/architecture_initiale/05_Modele_Donnees.md)                          | Schéma ER, modèles SQLAlchemy, migrations          |
| 06  | [API Design](docs/architecture_initiale/06_API_Design.md)                                     | Catalogue REST complet, exemples requêtes/réponses |
| 07  | [Moteur Statistique](docs/architecture_initiale/07_Moteur_Statistique.md)                     | 7 engines avec fondements mathématiques            |
| 08  | [Moteur de Scoring](docs/architecture_initiale/08_Moteur_Scoring.md)                          | Formule multicritères, profils de poids            |
| 09  | [Moteur d'Optimisation](docs/architecture_initiale/09_Moteur_Optimisation.md)                 | Méta-heuristiques, portefeuilles, Pareto           |
| 10  | [Moteur de Simulation](docs/architecture_initiale/10_Moteur_Simulation.md)                    | Monte Carlo, robustesse, validation                |
| 11  | [Scheduler et Jobs](docs/architecture_initiale/11_Scheduler_et_Jobs.md)                       | APScheduler, chaîne de jobs, retry                 |
| 12  | [Sécurité et Authentification](docs/architecture_initiale/12_Securite_et_Authentification.md) | JWT, RBAC, rate limiting, audit                    |
| 13  | [Architecture UI/UX](docs/architecture_initiale/13_Architecture_UI_UX.md)                     | Design system, wireframes, composants              |
| 14  | [Performance et Scalabilité](docs/architecture_initiale/14_Performance_et_Scalabilite.md)     | Cache, optimisations, scaling                      |
| 15  | [Observabilité](docs/architecture_initiale/15_Observabilite.md)                               | Logging structuré, métriques, health check         |
| 16  | [Stratégie de Tests](docs/architecture_initiale/16_Strategie_Tests.md)                        | Pyramide tests, fixtures, couverture ≥80%          |
| 17  | [Roadmap de Développement](docs/architecture_initiale/17_Roadmap_Developpement.md)            | 10 phases détaillées                               |
| 18  | [Checklist Globale](docs/architecture_initiale/18_Checklist_Globale.md)                       | 219 tâches atomiques à cocher                      |

---

## Installation

> **Prérequis** : Python 3.11+, Node.js 18+

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # Linux/Mac
# .venv\Scripts\activate         # Windows
pip install -e ".[dev]"
alembic upgrade head
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Variables d'environnement

Copier `.env.example` en `.env` et configurer :

```env
SECRET_KEY=your-secret-key-min-32-chars
DATABASE_URL=sqlite+aiosqlite:///./loto_ultime.db
ADMIN_INITIAL_PASSWORD=ChangeMe123!
CORS_ORIGINS=["http://localhost:5173"]
```

---

## Développement

```bash
# Tests backend
cd backend
pytest --cov=app --cov-report=html   # 395+ tests

# Tests frontend
cd frontend
npm test                              # 28+ tests (Vitest)

# Linter
cd backend && ruff check app/

# Frontend build
cd frontend
npm run build
```

### Docker

```bash
# Lancer l'application complète
docker compose up --build

# Backend uniquement
docker compose up backend
```

Le frontend est servi via Nginx (port 80), le backend via Uvicorn (port 8000).

---

## Roadmap

| Phase | Description                  | Statut     |
| ----- | ---------------------------- | ---------- |
| 1     | Architecture & Documentation | ✅ Complète |
| 2     | Fondations Backend           | ✅ Complète |
| 3     | Moteur Statistique           | ✅ Complète |
| 4     | Moteur de Scoring            | ✅ Complète |
| 5     | Moteur d'Optimisation        | ✅ Complète |
| 6     | Moteur de Simulation         | ✅ Complète |
| 7     | Interface Frontend           | ✅ Complète |
| 8     | Scheduler & Jobs             | ✅ Complète |
| 9     | Sécurité & Auth              | ✅ Complète |
| 10    | Polish & Déploiement         | 🔄 En cours |

Voir [17_Roadmap](docs/architecture_initiale/17_Roadmap_Developpement.md) et [18_Checklist](docs/architecture_initiale/18_Checklist_Globale.md) pour le détail.

---

## Licence

Projet personnel — Tous droits réservés.
