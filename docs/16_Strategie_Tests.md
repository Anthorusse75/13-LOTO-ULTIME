# 16 — Stratégie de Tests

> **Projet** : LOTO ULTIME  
> **Version** : 1.0  
> **Date** : 2026-03-27  
> **Références croisées** : [03_Backend](03_Architecture_Backend.md) · [04_Frontend](04_Architecture_Frontend.md) · [07_Statistique](07_Moteur_Statistique.md) · [08_Scoring](08_Moteur_Scoring.md) · [11_Scheduler](11_Scheduler_et_Jobs.md)

---

## 1. Objectifs

| Objectif | Cible |
|---|---|
| Couverture globale | ≥ 80% |
| Couverture moteurs (engines) | ≥ 95% |
| Couverture API | ≥ 90% |
| Tests avant chaque commit | Obligatoire (pre-commit hook) |
| Temps total suite de tests | < 60s |

---

## 2. Pyramide de Tests

```
        ╱╲
       ╱  ╲       E2E (frontend)
      ╱    ╲      ~5 tests
     ╱──────╲
    ╱        ╲    Intégration (API + DB)
   ╱          ╲   ~50 tests
  ╱────────────╲
 ╱              ╲  Unitaires (engines, services, utils)
╱________________╲ ~200+ tests
```

| Niveau | Ratio | Scope | Vitesse |
|---|---|---|---|
| Unitaire | 70% | Fonctions pures, engines, utils | < 1s chacun |
| Intégration | 25% | API endpoints, DB, services | < 5s chacun |
| E2E | 5% | Parcours utilisateur complet | < 30s chacun |

---

## 3. Stack de Test

| Outil | Usage |
|---|---|
| **pytest** | Framework de test principal |
| **pytest-asyncio** | Support async/await |
| **pytest-cov** | Couverture de code |
| **httpx** | Client HTTP pour tests API (AsyncClient) |
| **factory-boy** | Factories pour données de test |
| **faker** | Génération de données aléatoires |
| **freezegun** | Mock du temps (dates) |

---

## 4. Organisation des Tests

```
backend/
└── tests/
    ├── conftest.py                  # Fixtures globales
    ├── factories.py                 # Factories (factory-boy)
    ├── unit/
    │   ├── engines/
    │   │   ├── test_frequency.py
    │   │   ├── test_gap.py
    │   │   ├── test_cooccurrence.py
    │   │   ├── test_temporal.py
    │   │   ├── test_distribution.py
    │   │   ├── test_bayesian.py
    │   │   └── test_graph.py
    │   ├── scoring/
    │   │   ├── test_criteria.py
    │   │   ├── test_scorer.py
    │   │   └── test_weights.py
    │   ├── optimization/
    │   │   ├── test_simulated_annealing.py
    │   │   ├── test_genetic.py
    │   │   ├── test_tabu.py
    │   │   ├── test_portfolio_optimizer.py
    │   │   └── test_multi_objective.py
    │   ├── simulation/
    │   │   ├── test_monte_carlo.py
    │   │   └── test_robustness.py
    │   ├── services/
    │   │   ├── test_draw_service.py
    │   │   ├── test_statistics_service.py
    │   │   ├── test_grid_service.py
    │   │   └── test_portfolio_service.py
    │   └── utils/
    │       ├── test_validators.py
    │       └── test_math_utils.py
    ├── integration/
    │   ├── api/
    │   │   ├── test_auth.py
    │   │   ├── test_games.py
    │   │   ├── test_draws.py
    │   │   ├── test_statistics.py
    │   │   ├── test_grids.py
    │   │   ├── test_portfolios.py
    │   │   ├── test_simulation.py
    │   │   └── test_jobs.py
    │   ├── repositories/
    │   │   ├── test_draw_repository.py
    │   │   ├── test_user_repository.py
    │   │   └── test_grid_repository.py
    │   └── scrapers/
    │       └── test_fdj_scraper.py
    └── e2e/
        └── test_full_workflow.py
```

---

## 5. Fixtures (conftest.py)

```python
# tests/conftest.py
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from httpx import AsyncClient, ASGITransport

from app.main import create_app
from app.models.base import Base
from app.core.config import Settings

# ── Base de données de test (SQLite en mémoire) ──

@pytest.fixture(scope="session")
def test_settings():
    return Settings(
        DATABASE_URL="sqlite+aiosqlite:///:memory:",
        SECRET_KEY="test-secret-key-minimum-32-chars-long",
        ADMIN_INITIAL_PASSWORD="TestAdmin123",
    )

@pytest_asyncio.fixture
async def db_engine(test_settings):
    engine = create_async_engine(test_settings.DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

@pytest_asyncio.fixture
async def db_session(db_engine):
    session_factory = async_sessionmaker(db_engine, expire_on_commit=False)
    async with session_factory() as session:
        yield session
        await session.rollback()

# ── Client HTTP de test ──

@pytest_asyncio.fixture
async def app(test_settings):
    return create_app(settings=test_settings)

@pytest_asyncio.fixture
async def client(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

# ── Utilisateurs de test ──

@pytest_asyncio.fixture
async def admin_token(client):
    response = await client.post("/api/v1/auth/login", json={
        "username": "admin",
        "password": "TestAdmin123",
    })
    return response.json()["access_token"]

@pytest_asyncio.fixture
async def admin_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}
```

---

## 6. Factories

```python
# tests/factories.py
import factory
from datetime import date, datetime
from app.models.draw import Draw
from app.models.game_definition import GameDefinition

class GameDefinitionFactory(factory.Factory):
    class Meta:
        model = GameDefinition
    
    slug = factory.Sequence(lambda n: f"game-{n}")
    name = factory.LazyAttribute(lambda o: o.slug.replace("-", " ").title())
    main_numbers_count = 5
    main_numbers_max = 49
    complementary_count = 1
    complementary_max = 10
    draw_days = ["monday", "wednesday", "saturday"]
    source_url = "https://example.com"
    is_active = True

class DrawFactory(factory.Factory):
    class Meta:
        model = Draw
    
    game_id = 1
    draw_number = factory.Sequence(lambda n: n + 1)
    draw_date = factory.LazyFunction(date.today)
    main_numbers = factory.LazyFunction(lambda: [5, 12, 23, 34, 45])
    complementary_numbers = factory.LazyFunction(lambda: [3])
    jackpot = 2_000_000

def generate_draws(n: int = 100, max_num: int = 49, count: int = 5) -> list[list[int]]:
    """Génère n tirages aléatoires pour les tests."""
    import random
    random.seed(42)
    return [sorted(random.sample(range(1, max_num + 1), count)) for _ in range(n)]
```

---

## 7. Tests Unitaires — Exemples

### 7.1 Test FrequencyEngine

```python
# tests/unit/engines/test_frequency.py
import pytest
import numpy as np
from app.engines.frequency import FrequencyEngine

class TestFrequencyEngine:
    def setup_method(self):
        self.engine = FrequencyEngine()
    
    def test_compute_basic(self):
        draws = np.array([[1, 2, 3, 4, 5], [1, 2, 6, 7, 8]])
        result = self.engine.compute(draws, max_num=10)
        
        assert result[1] == 2  # Numéro 1 apparaît 2 fois
        assert result[6] == 1  # Numéro 6 apparaît 1 fois
        assert result[9] == 0  # Numéro 9 apparaît 0 fois
    
    def test_relative_frequency(self):
        draws = np.array([[1, 2, 3, 4, 5]] * 10)
        result = self.engine.compute_relative(draws, max_num=5)
        
        for num in range(1, 6):
            assert result[num] == pytest.approx(1.0)
    
    def test_empty_draws(self):
        draws = np.array([]).reshape(0, 5)
        result = self.engine.compute(draws, max_num=49)
        
        assert all(v == 0 for v in result.values())
    
    def test_frequency_ratio(self):
        draws = np.array([[1, 2, 3, 4, 5]] * 50 + [[6, 7, 8, 9, 10]] * 50)
        result = self.engine.compute_ratio(draws, max_num=10, n_draws=100)
        
        theoretical = 5 / 10  # 0.5
        for num in range(1, 11):
            assert result[num] == pytest.approx(1.0, abs=0.01)
```

### 7.2 Test GapEngine

```python
# tests/unit/engines/test_gap.py
import pytest
from app.engines.gap import GapEngine

class TestGapEngine:
    def setup_method(self):
        self.engine = GapEngine()
    
    def test_current_gap(self):
        """Le numéro 5 n'est pas sorti depuis 3 tirages."""
        draws = [
            [1, 2, 3, 4, 5],   # Tirage le plus ancien
            [6, 7, 8, 9, 10],
            [11, 12, 13, 14, 15],
            [16, 17, 18, 19, 20],
        ]
        result = self.engine.compute_current_gap(draws, max_num=20)
        
        assert result[5] == 3   # 3 tirages sans le 5
        assert result[20] == 0  # Dernier tirage
    
    def test_max_gap(self):
        draws = [
            [1, 2, 3, 4, 5],
            [6, 7, 8, 9, 10],
            [6, 7, 8, 9, 10],
            [6, 7, 8, 9, 10],
            [1, 2, 3, 4, 5],
        ]
        result = self.engine.compute_max_gap(draws, max_num=10)
        
        assert result[1] == 3  # Gap de 3 tirages entre deux apparitions
    
    def test_expected_gap(self):
        """Écart théorique pour Loto 5/49."""
        expected = self.engine.theoretical_gap(n=49, k=5)
        assert expected == pytest.approx(49 / 5 - 1, abs=0.01)
```

### 7.3 Test Scoring

```python
# tests/unit/scoring/test_scorer.py
import pytest
from app.engines.scoring import GridScorer
from app.engines.scoring.criteria import FrequencyScoreCriterion

class TestGridScorer:
    def test_score_range(self):
        """Le score est toujours entre 0 et 10."""
        scorer = GridScorer(weights={"frequency": 1.0})
        stats = {"frequency_ratios": {i: 1.0 for i in range(1, 50)}}
        
        for _ in range(100):
            grid = sorted(random.sample(range(1, 50), 5))
            score = scorer.score(grid, stats)
            assert 0 <= score <= 10
    
    def test_weights_affect_score(self):
        """Des poids différents produisent des scores différents."""
        stats = create_mock_stats()
        grid = [5, 12, 23, 34, 45]
        
        scorer1 = GridScorer(weights={"frequency": 1.0, "gap": 0.0})
        scorer2 = GridScorer(weights={"frequency": 0.0, "gap": 1.0})
        
        score1 = scorer1.score(grid, stats)
        score2 = scorer2.score(grid, stats)
        
        assert score1 != score2
    
    def test_penalty_reduces_score(self):
        """Les grilles avec patterns sont pénalisées."""
        stats = create_mock_stats()
        
        normal_grid = [5, 12, 23, 34, 45]
        consecutive_grid = [1, 2, 3, 4, 5]  # Pattern consécutif
        
        scorer = GridScorer(default_weights())
        
        assert scorer.score(normal_grid, stats) > scorer.score(consecutive_grid, stats)
```

### 7.4 Test Monte Carlo

```python
# tests/unit/simulation/test_monte_carlo.py
import pytest
from app.engines.simulation import MonteCarloSimulator

class TestMonteCarloSimulator:
    def test_convergence(self):
        """Les probabilités convergent vers les valeurs théoriques."""
        sim = MonteCarloSimulator(seed=42)
        grid = [5, 12, 23, 34, 45]
        
        result = sim.simulate(
            grid=grid,
            n_simulations=100_000,
            main_max=49,
            main_count=5,
        )
        
        # P(0 bons) théorique ≈ 0.5269
        assert result.distribution[0] == pytest.approx(0.5269, abs=0.01)
    
    def test_reproducibility(self):
        """Même seed = même résultat."""
        sim1 = MonteCarloSimulator(seed=42)
        sim2 = MonteCarloSimulator(seed=42)
        
        r1 = sim1.simulate([1, 2, 3, 4, 5], 10_000, 49, 5)
        r2 = sim2.simulate([1, 2, 3, 4, 5], 10_000, 49, 5)
        
        assert r1.distribution == r2.distribution
    
    def test_all_matches_sum_to_one(self):
        """La somme des probabilités = 1."""
        sim = MonteCarloSimulator(seed=42)
        result = sim.simulate([1, 2, 3, 4, 5], 10_000, 49, 5)
        
        total = sum(result.distribution.values())
        assert total == pytest.approx(1.0, abs=0.001)
```

---

## 8. Tests d'Intégration — Exemples

### 8.1 Test API Auth

```python
# tests/integration/api/test_auth.py
import pytest
from httpx import AsyncClient

class TestAuthAPI:
    @pytest.mark.asyncio
    async def test_login_success(self, client: AsyncClient):
        response = await client.post("/api/v1/auth/login", json={
            "username": "admin",
            "password": "TestAdmin123",
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    @pytest.mark.asyncio
    async def test_login_wrong_password(self, client: AsyncClient):
        response = await client.post("/api/v1/auth/login", json={
            "username": "admin",
            "password": "WrongPassword",
        })
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_protected_endpoint_without_token(self, client: AsyncClient):
        response = await client.get("/api/v1/games")
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_protected_endpoint_with_token(
        self, client: AsyncClient, admin_headers
    ):
        response = await client.get("/api/v1/games", headers=admin_headers)
        assert response.status_code == 200
```

### 8.2 Test API Draws

```python
# tests/integration/api/test_draws.py
import pytest

class TestDrawsAPI:
    @pytest.mark.asyncio
    async def test_create_draw(self, client, admin_headers, test_game_id):
        response = await client.post(
            f"/api/v1/draws",
            headers=admin_headers,
            json={
                "game_id": test_game_id,
                "draw_number": 1,
                "draw_date": "2025-03-24",
                "main_numbers": [5, 12, 23, 34, 45],
                "complementary_numbers": [3],
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["main_numbers"] == [5, 12, 23, 34, 45]
    
    @pytest.mark.asyncio
    async def test_create_draw_invalid_numbers(self, client, admin_headers, test_game_id):
        response = await client.post(
            f"/api/v1/draws",
            headers=admin_headers,
            json={
                "game_id": test_game_id,
                "draw_number": 2,
                "draw_date": "2025-03-25",
                "main_numbers": [5, 12, 23, 34, 55],  # 55 > 49
                "complementary_numbers": [3],
            },
        )
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_list_draws_pagination(self, client, admin_headers, test_game_id):
        # Créer plusieurs tirages...
        response = await client.get(
            f"/api/v1/draws?game_id={test_game_id}&limit=10&offset=0",
            headers=admin_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
```

### 8.3 Test Repository

```python
# tests/integration/repositories/test_draw_repository.py
import pytest
from app.repositories.draw import DrawRepository
from tests.factories import DrawFactory

class TestDrawRepository:
    @pytest.mark.asyncio
    async def test_create_and_get(self, db_session):
        repo = DrawRepository(db_session)
        draw = DrawFactory(game_id=1, draw_number=1)
        
        created = await repo.create(draw)
        assert created.id is not None
        
        fetched = await repo.get(created.id)
        assert fetched.draw_number == 1
        assert fetched.main_numbers == [5, 12, 23, 34, 45]
    
    @pytest.mark.asyncio
    async def test_get_by_game_ordered(self, db_session):
        repo = DrawRepository(db_session)
        # Créer 3 tirages
        for i in range(3):
            draw = DrawFactory(game_id=1, draw_number=i + 1)
            await repo.create(draw)
        
        draws = await repo.get_by_game(game_id=1, limit=10, offset=0)
        assert len(draws) == 3
        # Vérifie l'ordre décroissant par date
        assert draws[0].draw_number >= draws[1].draw_number
```

---

## 9. Validation Mathématique

Tests spéciaux pour vérifier la rigueur mathématique :

```python
# tests/unit/engines/test_math_validation.py
import pytest
from scipy.special import comb

class TestMathematicalCorrectness:
    def test_hypergeometric_probabilities(self):
        """Vérifier les probabilités hypergéométriques du Loto 5/49."""
        N = 49  # Boules totales
        K = 5   # Boules tirées
        n = 5   # Boules jouées
        
        probs = {}
        for k in range(K + 1):
            probs[k] = (comb(K, k) * comb(N - K, n - k)) / comb(N, n)
        
        assert sum(probs.values()) == pytest.approx(1.0)
        assert probs[5] == pytest.approx(1 / comb(49, 5))  # ~5.2e-8
    
    def test_chi2_uniform_distribution(self):
        """Chi-2 ne rejette pas l'uniformité d'une vraie uniforme."""
        from scipy.stats import chisquare
        import numpy as np
        
        np.random.seed(42)
        observed = np.random.multinomial(10000, [1/49]*49)
        stat, pvalue = chisquare(observed)
        
        assert pvalue > 0.05  # Ne pas rejeter H0
    
    def test_entropy_bounds(self):
        """Entropie de Shannon bornée entre 0 et log2(N)."""
        import numpy as np
        
        N = 49
        max_entropy = np.log2(N)
        
        # Distribution uniforme → entropie maximale
        uniform = np.ones(N) / N
        H = -np.sum(uniform * np.log2(uniform))
        assert H == pytest.approx(max_entropy, abs=0.001)
        
        # Distribution dégénérée → entropie = 0
        degenerate = np.zeros(N)
        degenerate[0] = 1.0
        H = -np.sum(degenerate[degenerate > 0] * np.log2(degenerate[degenerate > 0]))
        assert H == pytest.approx(0.0)
```

---

## 10. Configuration pytest

```ini
# pytest.ini
[pytest]
testpaths = tests
asyncio_mode = auto
markers =
    slow: Tests lents (>5s)
    integration: Tests d'intégration (DB requise)
    e2e: Tests end-to-end
addopts = 
    -v
    --tb=short
    --strict-markers
    -x
```

```ini
# .coveragerc
[run]
source = app
omit =
    app/main.py
    app/core/config.py
    */migrations/*

[report]
exclude_lines =
    pragma: no cover
    if TYPE_CHECKING:
    raise NotImplementedError
fail_under = 80
show_missing = true
```

---

## 11. Commandes

```bash
# Tous les tests
pytest

# Tests unitaires uniquement
pytest tests/unit/

# Tests d'intégration uniquement
pytest tests/integration/

# Avec couverture
pytest --cov=app --cov-report=html

# Tests d'un module spécifique
pytest tests/unit/engines/test_frequency.py -v

# Exclure les tests lents
pytest -m "not slow"

# Mode watch (pytest-watch)
ptw -- tests/unit/
```

---

## 12. Références

| Document | Contenu |
|---|---|
| [03_Architecture_Backend](03_Architecture_Backend.md) | Structure testée |
| [07_Moteur_Statistique](07_Moteur_Statistique.md) | Formules à valider |
| [08_Moteur_Scoring](08_Moteur_Scoring.md) | Scoring à tester |
| [10_Moteur_Simulation](10_Moteur_Simulation.md) | Convergence Monte Carlo |
| [04_Architecture_Frontend](04_Architecture_Frontend.md) | Structure frontend (tests E2E) |
| [11_Scheduler_et_Jobs](11_Scheduler_et_Jobs.md) | Jobs à tester (intégration) |

---

*Fin du document 16_Strategie_Tests.md*
