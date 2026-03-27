# 05 — Modèle de Données

> **Projet** : LOTO ULTIME  
> **Version** : 1.0  
> **Date** : 2026-03-27  
> **Références croisées** : [02_Architecture_Globale](02_Architecture_Globale.md) · [03_Architecture_Backend](03_Architecture_Backend.md) · [06_API_Design](06_API_Design.md)

---

## 1. Vue d'Ensemble

Le modèle de données est la fondation du système. Il est défini à deux niveaux :

| Niveau | Technologie | Rôle |
|---|---|---|
| **ORM** | SQLAlchemy 2.0 | Modèles persistés en base de données |
| **API** | Pydantic v2 | Schémas de validation, sérialisation JSON |

Les migrations sont gérées par **Alembic** pour garantir l'évolution contrôlée du schéma.

---

## 2. Diagramme Entités-Relations

```
┌─────────────────┐       ┌─────────────────┐
│   GameDefinition│       │      User        │
├─────────────────┤       ├─────────────────┤
│ id (PK)         │       │ id (PK)         │
│ name            │       │ username        │
│ slug (UNIQUE)   │       │ email (UNIQUE)  │
│ numbers_pool    │       │ hashed_password │
│ numbers_drawn   │       │ role            │
│ min_number      │       │ is_active       │
│ max_number      │       │ created_at      │
│ stars_pool      │       │ last_login      │
│ stars_drawn     │       └─────────────────┘
│ star_name       │
│ draw_frequency  │
│ historical_src  │
│ description     │
│ is_active       │
│ created_at      │
└────────┬────────┘
         │ 1
         │
         │ N
┌────────▼────────┐
│      Draw       │
├─────────────────┤       ┌─────────────────────────┐
│ id (PK)         │       │   StatisticsSnapshot    │
│ game_id (FK)    │       ├─────────────────────────┤
│ draw_date       │       │ id (PK)                 │
│ draw_number     │       │ game_id (FK)            │
│ numbers (JSON)  │       │ computed_at             │
│ stars (JSON)    │       │ draw_count              │
│ created_at      │       │ frequencies (JSON)      │
│ UNIQUE(game_id, │       │ gaps (JSON)             │
│   draw_date)    │       │ cooccurrence_matrix(JSON│
└─────────────────┘       │ temporal_trends (JSON)  │
                          │ bayesian_priors (JSON)  │
                          │ graph_metrics (JSON)    │
                          │ distribution_stats(JSON)│
                          └─────────────────────────┘

┌─────────────────────┐   ┌─────────────────────────┐
│    ScoredGrid       │   │     Portfolio            │
├─────────────────────┤   ├─────────────────────────┤
│ id (PK)             │   │ id (PK)                 │
│ game_id (FK)        │   │ game_id (FK)            │
│ numbers (JSON)      │   │ name                    │
│ stars (JSON)        │   │ strategy                │
│ total_score         │   │ grid_count              │
│ score_breakdown(JSON│   │ grids (JSON)            │
│ rank                │   │ diversity_score         │
│ method              │   │ coverage_score          │
│ computed_at         │   │ avg_grid_score          │
│ is_top              │   │ computed_at             │
│ simulation_stats    │   └─────────────────────────┘
│   (JSON)            │
└─────────────────────┘   ┌─────────────────────────┐
                          │    JobExecution          │
                          ├─────────────────────────┤
                          │ id (PK)                 │
                          │ job_name                │
                          │ game_id (FK, nullable)  │
                          │ status                  │
                          │ started_at              │
                          │ finished_at             │
                          │ duration_seconds        │
                          │ result_summary (JSON)   │
                          │ error_message           │
                          │ triggered_by            │
                          └─────────────────────────┘
```

---

## 3. Modèles SQLAlchemy (ORM)

### 3.1 Base

```python
# app/models/base.py
from datetime import datetime
from sqlalchemy import func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

class Base(DeclarativeBase):
    pass

class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    updated_at: Mapped[datetime | None] = mapped_column(
        default=None, onupdate=func.now()
    )
```

### 3.2 GameDefinition

```python
# app/models/game.py
from sqlalchemy import String, Integer, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

class GameDefinition(Base, TimestampMixin):
    __tablename__ = "game_definitions"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    slug: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    numbers_pool: Mapped[int] = mapped_column(Integer)
    numbers_drawn: Mapped[int] = mapped_column(Integer)
    min_number: Mapped[int] = mapped_column(Integer, default=1)
    max_number: Mapped[int] = mapped_column(Integer)
    stars_pool: Mapped[int | None] = mapped_column(Integer, nullable=True)
    stars_drawn: Mapped[int | None] = mapped_column(Integer, nullable=True)
    star_name: Mapped[str | None] = mapped_column(String(50), nullable=True)
    draw_frequency: Mapped[str] = mapped_column(String(50))
    historical_source: Mapped[str] = mapped_column(String(50))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relations
    draws: Mapped[list["Draw"]] = relationship(back_populates="game")
```

### 3.3 Draw

```python
# app/models/draw.py
from datetime import date
from sqlalchemy import Integer, Date, ForeignKey, JSON, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

class Draw(Base, TimestampMixin):
    __tablename__ = "draws"
    __table_args__ = (
        UniqueConstraint("game_id", "draw_date", name="uq_draw_game_date"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    game_id: Mapped[int] = mapped_column(ForeignKey("game_definitions.id"), index=True)
    draw_date: Mapped[date] = mapped_column(Date, index=True)
    draw_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    numbers: Mapped[list[int]] = mapped_column(JSON)  # [1, 7, 23, 34, 45]
    stars: Mapped[list[int] | None] = mapped_column(JSON, nullable=True)  # [3, 9]

    # Relations
    game: Mapped["GameDefinition"] = relationship(back_populates="draws")
```

### 3.4 StatisticsSnapshot

```python
# app/models/statistics.py
from datetime import datetime
from sqlalchemy import Integer, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column

class StatisticsSnapshot(Base):
    __tablename__ = "statistics_snapshots"

    id: Mapped[int] = mapped_column(primary_key=True)
    game_id: Mapped[int] = mapped_column(ForeignKey("game_definitions.id"), index=True)
    computed_at: Mapped[datetime] = mapped_column(DateTime)
    draw_count: Mapped[int] = mapped_column(Integer)
    
    # Données statistiques (stockées en JSON)
    frequencies: Mapped[dict] = mapped_column(JSON)
    # {1: {"count": 234, "relative": 0.12, "last_seen": 3}, 2: {...}, ...}
    
    gaps: Mapped[dict] = mapped_column(JSON)
    # {1: {"current_gap": 5, "max_gap": 42, "avg_gap": 8.3}, ...}
    
    cooccurrence_matrix: Mapped[dict] = mapped_column(JSON)
    # {"1-2": 45, "1-3": 38, ...}
    
    temporal_trends: Mapped[dict] = mapped_column(JSON)
    # {"windows": [{"period": "last_50", "hot": [3,7,12], "cold": [41,44]}, ...]}
    
    bayesian_priors: Mapped[dict] = mapped_column(JSON)
    # {1: {"alpha": 234, "beta": 1766, "posterior_mean": 0.117}, ...}
    
    graph_metrics: Mapped[dict] = mapped_column(JSON)
    # {"centrality": {1: 0.85, ...}, "communities": [[1,3,7], [12,23,34]], ...}
    
    distribution_stats: Mapped[dict] = mapped_column(JSON)
    # {"chi2_pvalue": 0.23, "entropy": 5.61, "uniformity_score": 0.94}
```

### 3.5 ScoredGrid

```python
# app/models/grid.py
from datetime import datetime
from sqlalchemy import Integer, Float, String, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column

class ScoredGrid(Base):
    __tablename__ = "scored_grids"

    id: Mapped[int] = mapped_column(primary_key=True)
    game_id: Mapped[int] = mapped_column(ForeignKey("game_definitions.id"), index=True)
    numbers: Mapped[list[int]] = mapped_column(JSON)
    stars: Mapped[list[int] | None] = mapped_column(JSON, nullable=True)
    
    total_score: Mapped[float] = mapped_column(Float, index=True)
    score_breakdown: Mapped[dict] = mapped_column(JSON)
    # {"frequency": 0.82, "gap": 0.71, "cooccurrence": 0.65,
    #  "structure": 0.78, "balance": 0.90, "pattern_penalty": -0.05}
    
    rank: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    method: Mapped[str] = mapped_column(String(50))
    # "genetic_algorithm", "simulated_annealing", "tabu_search", "exhaustive"
    
    computed_at: Mapped[datetime] = mapped_column(DateTime)
    is_top: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    
    simulation_stats: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    # {"monte_carlo_runs": 10000, "avg_matches": 1.23, "stability": 0.87}
```

### 3.6 Portfolio

```python
# app/models/portfolio.py
from datetime import datetime
from sqlalchemy import Integer, Float, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column

class Portfolio(Base):
    __tablename__ = "portfolios"

    id: Mapped[int] = mapped_column(primary_key=True)
    game_id: Mapped[int] = mapped_column(ForeignKey("game_definitions.id"), index=True)
    name: Mapped[str] = mapped_column(String(100))
    strategy: Mapped[str] = mapped_column(String(50))
    # "max_diversity", "max_coverage", "balanced", "min_correlation"
    
    grid_count: Mapped[int] = mapped_column(Integer)
    grids: Mapped[list[dict]] = mapped_column(JSON)
    # [{"numbers": [1,7,23,34,45], "stars": [3], "score": 0.82}, ...]
    
    diversity_score: Mapped[float] = mapped_column(Float)
    coverage_score: Mapped[float] = mapped_column(Float)
    avg_grid_score: Mapped[float] = mapped_column(Float)
    min_hamming_distance: Mapped[float | None] = mapped_column(Float, nullable=True)
    
    computed_at: Mapped[datetime] = mapped_column(DateTime)
```

### 3.7 User

```python
# app/models/user.py
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, Enum
from sqlalchemy.orm import Mapped, mapped_column
import enum

class UserRole(str, enum.Enum):
    ADMIN = "ADMIN"
    UTILISATEUR = "UTILISATEUR"
    CONSULTATION = "CONSULTATION"

class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.CONSULTATION)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_login: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
```

### 3.8 JobExecution

```python
# app/models/job.py
from datetime import datetime
from sqlalchemy import Integer, String, DateTime, Float, ForeignKey, JSON, Enum, Text
from sqlalchemy.orm import Mapped, mapped_column
import enum

class JobStatus(str, enum.Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"

class JobExecution(Base):
    __tablename__ = "job_executions"

    id: Mapped[int] = mapped_column(primary_key=True)
    job_name: Mapped[str] = mapped_column(String(100), index=True)
    game_id: Mapped[int | None] = mapped_column(
        ForeignKey("game_definitions.id"), nullable=True
    )
    status: Mapped[JobStatus] = mapped_column(Enum(JobStatus))
    started_at: Mapped[datetime] = mapped_column(DateTime)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    duration_seconds: Mapped[float | None] = mapped_column(Float, nullable=True)
    result_summary: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    triggered_by: Mapped[str] = mapped_column(String(50))
    # "scheduler", "manual:admin_username"
```

---

## 4. Schémas Pydantic (API)

### 4.1 GameDefinition

```python
# app/schemas/game.py
from pydantic import BaseModel, Field

class GameDefinitionResponse(BaseModel):
    id: int
    name: str
    slug: str
    numbers_pool: int
    numbers_drawn: int
    min_number: int
    max_number: int
    stars_pool: int | None
    stars_drawn: int | None
    star_name: str | None
    draw_frequency: str
    is_active: bool

    model_config = {"from_attributes": True}

class GameDefinitionCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    slug: str = Field(..., min_length=2, max_length=50, pattern=r"^[a-z0-9-]+$")
    numbers_pool: int = Field(..., ge=5, le=100)
    numbers_drawn: int = Field(..., ge=1, le=20)
    min_number: int = Field(1, ge=0)
    max_number: int = Field(..., ge=5, le=100)
    stars_pool: int | None = Field(None, ge=1, le=50)
    stars_drawn: int | None = Field(None, ge=1, le=10)
    star_name: str | None = None
    draw_frequency: str
    historical_source: str
    description: str | None = None
```

### 4.2 Draw

```python
# app/schemas/draw.py
from datetime import date
from pydantic import BaseModel, Field

class DrawResponse(BaseModel):
    id: int
    game_id: int
    draw_date: date
    draw_number: int | None
    numbers: list[int]
    stars: list[int] | None

    model_config = {"from_attributes": True}

class DrawCreate(BaseModel):
    draw_date: date
    draw_number: int | None = None
    numbers: list[int] = Field(..., min_length=1)
    stars: list[int] | None = None
```

### 4.3 Statistics

```python
# app/schemas/statistics.py
from datetime import datetime
from pydantic import BaseModel

class FrequencyItem(BaseModel):
    number: int
    count: int
    relative_frequency: float
    last_seen: int  # Nombre de tirages depuis dernière apparition

class GapItem(BaseModel):
    number: int
    current_gap: int
    max_gap: int
    avg_gap: float
    min_gap: int

class CooccurrenceItem(BaseModel):
    pair: tuple[int, int]
    count: int
    expected: float
    affinity: float  # count / expected

class StatisticsResponse(BaseModel):
    game_id: int
    computed_at: datetime
    draw_count: int
    frequencies: list[FrequencyItem]
    gaps: list[GapItem]
    top_cooccurrences: list[CooccurrenceItem]
    hot_numbers: list[int]
    cold_numbers: list[int]
    distribution_entropy: float
    uniformity_score: float
```

### 4.4 Grid / Scoring

```python
# app/schemas/grid.py
from datetime import datetime
from pydantic import BaseModel

class ScoreBreakdown(BaseModel):
    frequency: float
    gap: float
    cooccurrence: float
    structure: float
    balance: float
    pattern_penalty: float

class GridResponse(BaseModel):
    id: int
    numbers: list[int]
    stars: list[int] | None
    total_score: float
    score_breakdown: ScoreBreakdown
    rank: int | None
    method: str
    computed_at: datetime

    model_config = {"from_attributes": True}

class GridGenerateRequest(BaseModel):
    count: int = Field(10, ge=1, le=100)
    method: str = Field("auto", pattern=r"^(auto|genetic|annealing|tabu|hill_climbing)$")
    weights: dict[str, float] | None = None
```

### 4.5 Portfolio

```python
# app/schemas/portfolio.py
from datetime import datetime
from pydantic import BaseModel, Field

class PortfolioGridItem(BaseModel):
    numbers: list[int]
    stars: list[int] | None
    score: float

class PortfolioResponse(BaseModel):
    id: int
    game_id: int
    name: str
    strategy: str
    grid_count: int
    grids: list[PortfolioGridItem]
    diversity_score: float
    coverage_score: float
    avg_grid_score: float
    min_hamming_distance: float | None
    computed_at: datetime

    model_config = {"from_attributes": True}

class PortfolioGenerateRequest(BaseModel):
    grid_count: int = Field(10, ge=2, le=50)
    strategy: str = Field(
        "balanced",
        pattern=r"^(max_diversity|max_coverage|balanced|min_correlation)$",
    )
```

---

## 5. Structure JSON des Champs Complexes

### 5.1 frequencies (StatisticsSnapshot)

```json
{
  "1": {"count": 234, "relative": 0.117, "last_seen": 3},
  "2": {"count": 220, "relative": 0.110, "last_seen": 12},
  "...": "..."
}
```

### 5.2 cooccurrence_matrix (StatisticsSnapshot)

```json
{
  "pairs": {
    "1-2": {"count": 45, "expected": 42.3, "affinity": 1.064},
    "1-3": {"count": 38, "expected": 42.3, "affinity": 0.898},
    "...": "..."
  },
  "triplets": {
    "1-2-3": {"count": 5, "expected": 4.2, "affinity": 1.190},
    "...": "..."
  }
}
```

### 5.3 graph_metrics (StatisticsSnapshot)

```json
{
  "centrality": {
    "degree": {"1": 0.85, "2": 0.72, "...": "..."},
    "betweenness": {"1": 0.12, "2": 0.08, "...": "..."},
    "eigenvector": {"1": 0.34, "2": 0.29, "...": "..."}
  },
  "communities": [
    [1, 3, 7, 12, 23],
    [5, 8, 15, 34, 41],
    "..."
  ],
  "clustering_coefficient": 0.67,
  "graph_density": 0.42
}
```

---

## 6. Index de Base de Données

| Table | Index | Colonnes | Type |
|---|---|---|---|
| game_definitions | uq_slug | slug | UNIQUE |
| draws | ix_game_date | game_id, draw_date | UNIQUE |
| draws | ix_game_id | game_id | INDEX |
| draws | ix_draw_date | draw_date | INDEX |
| statistics_snapshots | ix_game_computed | game_id, computed_at DESC | INDEX |
| scored_grids | ix_game_score | game_id, total_score DESC | INDEX |
| scored_grids | ix_game_top | game_id, is_top | INDEX |
| users | uq_username | username | UNIQUE |
| users | uq_email | email | UNIQUE |
| job_executions | ix_job_name | job_name | INDEX |
| job_executions | ix_started | started_at DESC | INDEX |

---

## 7. Migrations Alembic

### Structure

```
alembic/
├── env.py
├── versions/
│   ├── 001_initial_schema.py
│   ├── 002_add_statistics.py
│   ├── 003_add_scored_grids.py
│   ├── 004_add_portfolios.py
│   ├── 005_add_users.py
│   ├── 006_add_job_executions.py
│   └── ...
└── script.py.mako
```

### Commandes

```bash
# Créer migration
alembic revision --autogenerate -m "description"

# Appliquer migrations
alembic upgrade head

# Revenir en arrière
alembic downgrade -1
```

---

## 8. Références

| Document | Contenu |
|---|---|
| [02_Architecture_Globale](02_Architecture_Globale.md) | Stack technique |
| [03_Architecture_Backend](03_Architecture_Backend.md) | Couche Repository |
| [06_API_Design](06_API_Design.md) | Utilisation des schémas |
| [07_Moteur_Statistique](07_Moteur_Statistique.md) | Données statistiques |

---

*Fin du document 05_Modele_Donnees.md*
