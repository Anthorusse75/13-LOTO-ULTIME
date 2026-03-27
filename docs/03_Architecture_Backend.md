# 03 — Architecture Backend

> **Projet** : LOTO ULTIME  
> **Version** : 1.0  
> **Date** : 2026-03-27  
> **Références croisées** : [02_Architecture_Globale](02_Architecture_Globale.md) · [05_Modele_Donnees](05_Modele_Donnees.md) · [06_API_Design](06_API_Design.md) · [07_Moteur_Statistique](07_Moteur_Statistique.md) · [11_Scheduler](11_Scheduler_et_Jobs.md) · [12_Securite](12_Securite_et_Authentification.md)

---

## 1. Rôle du Backend

Le backend est le **cœur du système**. Il est responsable de :

| Responsabilité | Description |
|---|---|
| Ingestion | Récupération et validation des tirages depuis sources externes |
| Stockage | Persistance des tirages, statistiques, grilles, utilisateurs |
| Calcul | Exécution des moteurs statistique, scoring, optimisation, simulation |
| Exposition | API REST pour le frontend et clients tiers |
| Planification | Scheduler pour l'automatisation des tâches |
| Sécurité | Authentification JWT, autorisation RBAC |
| Journalisation | Logs structurés, traçabilité des opérations |

---

## 2. Stack Technique Détaillée

```
Python 3.11+
├── FastAPI          — Framework web async
├── SQLAlchemy 2.0   — ORM avec support async
├── Alembic          — Migrations BDD
├── Pydantic v2      — Validation & sérialisation
├── APScheduler      — Planification tâches
├── NumPy 1.26+      — Calcul matriciel
├── SciPy 1.12+      — Statistiques, optimisation
├── NetworkX 3.2+    — Analyse de graphes
├── httpx            — Client HTTP async
├── python-jose      — JWT
├── passlib[bcrypt]  — Hachage mots de passe
├── uvicorn          — Serveur ASGI
├── structlog        — Logging structuré
└── pytest           — Tests
```

---

## 3. Architecture en Couches

### 3.1 Vue des couches

```
┌─────────────────────────────────────────┐
│            API Layer (Routers)          │  ← Reçoit HTTP, retourne JSON
│  Validation entrée · Sérialisation     │
├─────────────────────────────────────────┤
│           Service Layer                 │  ← Orchestre la logique
│  Coordination · Transactions · Events  │
├─────────────────────────────────────────┤
│           Engine Layer                  │  ← Calcul pur
│  Stats · Scoring · Optim · Simulation  │
├─────────────────────────────────────────┤
│          Repository Layer               │  ← Accès données
│  CRUD · Queries · Aggregations         │
├─────────────────────────────────────────┤
│           Model Layer                   │  ← Définition données
│  SQLAlchemy Models · Pydantic Schemas  │
├─────────────────────────────────────────┤
│          Infrastructure                 │  ← Transversal
│  DB · Config · Logging · Security      │
└─────────────────────────────────────────┘
```

### 3.2 Règles de dépendance

```
API → Service → {Engine, Repository}
                Engine → (rien, calcul pur)
                Repository → Model → DB

Interdit :
  API → Repository (directement)
  API → Engine (directement)
  Engine → Repository
  Repository → Service
```

---

## 4. Couche API (Routers)

### 4.1 Structure

```python
# app/api/v1/__init__.py
from fastapi import APIRouter
from .games import router as games_router
from .draws import router as draws_router
from .statistics import router as statistics_router
from .grids import router as grids_router
from .portfolios import router as portfolios_router
from .simulation import router as simulation_router
from .jobs import router as jobs_router
from .auth import router as auth_router
from .admin import router as admin_router

api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(games_router, prefix="/games", tags=["Games"])
api_v1_router.include_router(draws_router, prefix="/draws", tags=["Draws"])
# ... etc.
```

### 4.2 Responsabilités d'un router

```python
# Exemple : app/api/v1/draws.py
@router.get("/{game_id}/draws", response_model=list[DrawResponse])
async def list_draws(
    game_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
    draw_service: DrawService = Depends(get_draw_service),
):
    """Liste les tirages avec pagination."""
    return await draw_service.get_draws(game_id, skip=skip, limit=limit)
```

**Un router** :
- Déclare la route HTTP
- Valide les entrées (Pydantic, Query params)
- Vérifie l'authentification/autorisation
- Appelle le service approprié
- Retourne la réponse sérialisée

**Un router ne fait PAS** :
- De calcul métier
- D'accès direct à la base de données
- De logique conditionnelle complexe

---

## 5. Couche Service

### 5.1 Rôle

La couche service **orchestre** les opérations entre repositories et moteurs de calcul.

### 5.2 Services principaux

| Service | Responsabilité |
|---|---|
| `DrawService` | Gestion tirages : import, validation, stockage |
| `StatisticsService` | Déclenchement calculs statistiques, stockage résultats |
| `ScoringService` | Calcul scores de grilles via moteur scoring |
| `GridService` | Génération et évaluation de grilles |
| `PortfolioService` | Optimisation de portefeuilles de grilles |
| `SimulationService` | Lancement simulations Monte Carlo |
| `AuthService` | Authentification, gestion utilisateurs |
| `JobService` | Gestion des jobs scheduler |

### 5.3 Pattern d'un service

```python
class StatisticsService:
    def __init__(
        self,
        draw_repo: DrawRepository,
        stats_repo: StatisticsRepository,
        game_repo: GameRepository,
        frequency_engine: FrequencyEngine,
        gap_engine: GapEngine,
        cooccurrence_engine: CooccurrenceEngine,
        temporal_engine: TemporalEngine,
    ):
        self._draw_repo = draw_repo
        self._stats_repo = stats_repo
        self._game_repo = game_repo
        self._frequency_engine = frequency_engine
        self._gap_engine = gap_engine
        self._cooccurrence_engine = cooccurrence_engine
        self._temporal_engine = temporal_engine

    async def compute_full_statistics(self, game_id: int) -> StatisticsSnapshot:
        """Recalcule toutes les statistiques pour un jeu."""
        game = await self._game_repo.get(game_id)
        draws = await self._draw_repo.get_all(game_id)
        
        numbers_matrix = self._extract_numbers(draws)
        
        frequencies = self._frequency_engine.compute(numbers_matrix, game)
        gaps = self._gap_engine.compute(numbers_matrix, game)
        cooccurrences = self._cooccurrence_engine.compute(numbers_matrix, game)
        temporal = self._temporal_engine.compute(numbers_matrix, game)
        
        snapshot = StatisticsSnapshot(
            game_id=game_id,
            computed_at=datetime.utcnow(),
            frequencies=frequencies,
            gaps=gaps,
            cooccurrences=cooccurrences,
            temporal=temporal,
        )
        
        await self._stats_repo.save_snapshot(snapshot)
        return snapshot
```

---

## 6. Couche Engine (Moteurs de Calcul)

### 6.1 Principes

Les moteurs sont des **classes de calcul pur** :
- Aucune dépendance sur l'infrastructure (pas de DB, pas d'I/O)
- Entrée : données numériques (NumPy arrays, listes)
- Sortie : résultats structurés (dataclasses, dicts)
- Testables unitairement sans mock

### 6.2 Arbre des moteurs

```
engines/
├── statistics/          → [doc 07]
│   ├── frequency.py     # Fréquences absolues et relatives
│   ├── gaps.py          # Retards (écart depuis dernier tirage)
│   ├── cooccurrence.py  # Matrices de cooccurrence
│   ├── temporal.py      # Tendances temporelles
│   ├── distribution.py  # Distributions statistiques
│   └── bayesian.py      # Estimation bayésienne
│
├── scoring/             → [doc 08]
│   ├── scorer.py        # Orchestrateur scoring multicritère
│   ├── criteria/        # Critères individuels
│   │   ├── frequency_score.py
│   │   ├── gap_score.py
│   │   ├── cooccurrence_score.py
│   │   ├── structure_score.py
│   │   ├── balance_score.py
│   │   └── pattern_penalty.py
│   └── weights.py       # Gestion des poids
│
├── optimization/        → [doc 09]
│   ├── simulated_annealing.py
│   ├── genetic_algorithm.py
│   ├── tabu_search.py
│   ├── hill_climbing.py
│   ├── multi_objective.py
│   └── portfolio_optimizer.py
│
├── simulation/          → [doc 10]
│   ├── monte_carlo.py
│   └── robustness.py
│
└── graph/               → [doc 07, section graphes]
    ├── cooccurrence_graph.py
    ├── centrality.py
    └── community.py
```

### 6.3 Interface commune des moteurs

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
import numpy as np

@dataclass
class GameConfig:
    """Configuration minimale du jeu pour les moteurs."""
    name: str
    numbers_pool: int
    numbers_drawn: int
    min_number: int
    max_number: int
    stars_pool: int | None = None
    stars_drawn: int | None = None

class BaseStatisticsEngine(ABC):
    """Interface commune pour tous les moteurs statistiques."""
    
    @abstractmethod
    def compute(self, draws: np.ndarray, game: GameConfig) -> dict:
        """Calcule les statistiques à partir des tirages."""
        ...
    
    @abstractmethod
    def get_name(self) -> str:
        """Nom du moteur pour logging/traçabilité."""
        ...
```

---

## 7. Couche Repository

### 7.1 Rôle

Abstraction de l'accès aux données. Chaque repository encapsule les requêtes SQL pour une entité.

### 7.2 Pattern

```python
class BaseRepository(Generic[T]):
    def __init__(self, session: AsyncSession, model_class: type[T]):
        self._session = session
        self._model_class = model_class

    async def get(self, id: int) -> T | None:
        return await self._session.get(self._model_class, id)

    async def get_all(self, **filters) -> list[T]:
        stmt = select(self._model_class).filter_by(**filters)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def create(self, entity: T) -> T:
        self._session.add(entity)
        await self._session.flush()
        return entity

    async def delete(self, entity: T) -> None:
        await self._session.delete(entity)
```

### 7.3 Repository spécialisé

```python
class DrawRepository(BaseRepository[Draw]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Draw)

    async def get_latest(self, game_id: int, limit: int = 1) -> list[Draw]:
        stmt = (
            select(Draw)
            .where(Draw.game_id == game_id)
            .order_by(Draw.draw_date.desc())
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_numbers_matrix(self, game_id: int) -> np.ndarray:
        """Retourne tous les numéros comme matrice NumPy (N tirages × K numéros)."""
        stmt = (
            select(Draw.numbers)
            .where(Draw.game_id == game_id)
            .order_by(Draw.draw_date.asc())
        )
        result = await self._session.execute(stmt)
        rows = result.scalars().all()
        return np.array(rows)
```

---

## 8. Configuration

### 8.1 Configuration applicative

```python
# app/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Application
    APP_NAME: str = "LOTO ULTIME"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Base de données
    DATABASE_URL: str = "sqlite+aiosqlite:///./loto_ultime.db"
    
    # Sécurité
    SECRET_KEY: str  # Obligatoire, pas de défaut
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 60
    
    # Scheduler
    SCHEDULER_ENABLED: bool = True
    FETCH_DRAWS_CRON: str = "0 22 * * 1,3,6"  # Loto: lun/mer/sam 22h
    
    # Scraper
    FDJ_BASE_URL: str = "https://www.fdj.fr"
    EUROMILLIONS_BASE_URL: str = "https://www.fdj.fr"
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:5173"]
    
    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}
```

### 8.2 Configuration des jeux (YAML)

```yaml
# game_configs/loto_fdj.yaml
name: "Loto FDJ"
slug: "loto-fdj"
numbers_pool: 49
numbers_drawn: 5
min_number: 1
max_number: 49
stars_pool: 10
stars_drawn: 1
star_name: "numéro chance"
draw_frequency: "lun/mer/sam"
historical_source: "fdj"
description: "Loto Français - Française des Jeux"
```

```yaml
# game_configs/euromillions.yaml
name: "EuroMillions"
slug: "euromillions"
numbers_pool: 50
numbers_drawn: 5
min_number: 1
max_number: 50
stars_pool: 12
stars_drawn: 2
star_name: "étoile"
draw_frequency: "mar/ven"
historical_source: "euromillions"
description: "EuroMillions - Loterie européenne"
```

---

## 9. Point d'Entrée

```python
# app/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import Settings
from app.api.v1 import api_v1_router
from app.core.logging import setup_logging
from app.scheduler.scheduler import setup_scheduler

settings = Settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    setup_logging()
    scheduler = setup_scheduler(settings)
    if settings.SCHEDULER_ENABLED:
        scheduler.start()
    yield
    # Shutdown
    if settings.SCHEDULER_ENABLED:
        scheduler.shutdown()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_v1_router)
```

---

## 10. Injection de Dépendances

```python
# app/dependencies.py
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base import get_session
from app.repositories.draw_repository import DrawRepository
from app.repositories.game_repository import GameRepository
from app.repositories.statistics_repository import StatisticsRepository
from app.services.draw_service import DrawService
from app.services.statistics_service import StatisticsService
from app.engines.statistics.frequency import FrequencyEngine
from app.engines.statistics.gaps import GapEngine
from app.engines.statistics.cooccurrence import CooccurrenceEngine
from app.engines.statistics.temporal import TemporalEngine

async def get_db() -> AsyncSession:
    async with get_session() as session:
        yield session

def get_draw_repository(session: AsyncSession = Depends(get_db)) -> DrawRepository:
    return DrawRepository(session)

def get_draw_service(
    draw_repo: DrawRepository = Depends(get_draw_repository),
    game_repo: GameRepository = Depends(get_game_repository),
) -> DrawService:
    return DrawService(draw_repo, game_repo)

def get_statistics_service(
    draw_repo: DrawRepository = Depends(get_draw_repository),
    stats_repo: StatisticsRepository = Depends(get_statistics_repository),
    game_repo: GameRepository = Depends(get_game_repository),
) -> StatisticsService:
    return StatisticsService(
        draw_repo=draw_repo,
        stats_repo=stats_repo,
        game_repo=game_repo,
        frequency_engine=FrequencyEngine(),
        gap_engine=GapEngine(),
        cooccurrence_engine=CooccurrenceEngine(),
        temporal_engine=TemporalEngine(),
    )
```

---

## 11. Gestion des Erreurs

### 11.1 Exceptions personnalisées

```python
# app/core/exceptions.py
class LotoUltimeError(Exception):
    """Exception de base du projet."""
    pass

class GameNotFoundError(LotoUltimeError):
    """Jeu non trouvé."""
    pass

class DrawAlreadyExistsError(LotoUltimeError):
    """Tirage déjà présent en base."""
    pass

class InvalidDrawDataError(LotoUltimeError):
    """Données de tirage invalides."""
    pass

class InsufficientDataError(LotoUltimeError):
    """Pas assez de données pour le calcul."""
    pass

class EngineComputationError(LotoUltimeError):
    """Erreur dans un moteur de calcul."""
    pass

class AuthenticationError(LotoUltimeError):
    """Erreur d'authentification."""
    pass

class AuthorizationError(LotoUltimeError):
    """Accès non autorisé."""
    pass
```

### 11.2 Handlers globaux

```python
# Enregistrés dans main.py
@app.exception_handler(GameNotFoundError)
async def game_not_found_handler(request, exc):
    return JSONResponse(status_code=404, content={"detail": str(exc)})

@app.exception_handler(AuthenticationError)
async def auth_error_handler(request, exc):
    return JSONResponse(status_code=401, content={"detail": str(exc)})

@app.exception_handler(AuthorizationError)
async def authz_error_handler(request, exc):
    return JSONResponse(status_code=403, content={"detail": str(exc)})
```

---

## 12. Scrapers (Récupération des Tirages)

### 12.1 Architecture

```python
# app/scrapers/base_scraper.py
from abc import ABC, abstractmethod

class BaseScraper(ABC):
    """Interface pour les scrapers de tirages."""
    
    @abstractmethod
    async def fetch_latest_draws(self, since_date: date | None = None) -> list[RawDraw]:
        """Récupère les tirages depuis la source."""
        ...
    
    @abstractmethod
    async def fetch_historical_draws(self) -> list[RawDraw]:
        """Récupère l'historique complet."""
        ...
    
    @abstractmethod
    def get_game_slug(self) -> str:
        """Identifiant du jeu associé."""
        ...
```

### 12.2 Validation des données

Chaque tirage récupéré passe par une validation stricte :

```python
@dataclass
class RawDraw:
    draw_date: date
    numbers: list[int]
    stars: list[int] | None
    draw_number: int | None

class DrawValidator:
    def validate(self, raw: RawDraw, game: GameConfig) -> ValidatedDraw:
        # Vérification nombre de numéros
        assert len(raw.numbers) == game.numbers_drawn
        # Vérification plage
        for n in raw.numbers:
            assert game.min_number <= n <= game.max_number
        # Vérification unicité
        assert len(set(raw.numbers)) == len(raw.numbers)
        # Vérification étoiles si applicable
        if game.stars_pool:
            assert raw.stars is not None
            assert len(raw.stars) == game.stars_drawn
        return ValidatedDraw(...)
```

---

## 13. Logging Structuré

```python
# app/core/logging.py
import structlog

def setup_logging():
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.dev.ConsoleRenderer(),  # dev
            # structlog.processors.JSONRenderer(),  # prod
        ],
        logger_factory=structlog.PrintLoggerFactory(),
    )
```

→ Détails : [15_Observabilite](15_Observabilite.md)

---

## 14. Références

| Document | Contenu |
|---|---|
| [02_Architecture_Globale](02_Architecture_Globale.md) | Vue d'ensemble |
| [05_Modele_Donnees](05_Modele_Donnees.md) | Modèles ORM et schémas |
| [06_API_Design](06_API_Design.md) | Spécification complète API |
| [07_Moteur_Statistique](07_Moteur_Statistique.md) | Détail moteur stats |
| [11_Scheduler_et_Jobs](11_Scheduler_et_Jobs.md) | Jobs automatisés |
| [12_Securite_et_Authentification](12_Securite_et_Authentification.md) | Auth et sécurité |
| [16_Strategie_Tests](16_Strategie_Tests.md) | Tests backend |

---

*Fin du document 03_Architecture_Backend.md*
