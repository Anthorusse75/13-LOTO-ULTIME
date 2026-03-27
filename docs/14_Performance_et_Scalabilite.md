# 14 — Performance et Scalabilité

> **Projet** : LOTO ULTIME  
> **Version** : 1.0  
> **Date** : 2026-03-27  
> **Références croisées** : [02_Architecture](02_Architecture_Globale.md) · [03_Backend](03_Architecture_Backend.md) · [07_Statistique](07_Moteur_Statistique.md) · [11_Scheduler](11_Scheduler_et_Jobs.md)

---

## 1. Objectifs de Performance

### 1.1 Temps de Réponse API

| Catégorie | Endpoint type | Cible p50 | Cible p95 | Max absolu |
|---|---|---|---|---|
| Lecture simple | GET /games, GET /draws/:id | < 50ms | < 100ms | 200ms |
| Liste paginée | GET /draws, GET /grids/top | < 100ms | < 200ms | 500ms |
| Statistiques | GET /statistics/* | < 200ms | < 500ms | 1s |
| Calcul léger | POST /grids/score | < 500ms | < 1s | 2s |
| Génération | POST /grids/generate | < 5s | < 15s | 30s |
| Simulation | POST /simulation | < 10s | < 30s | 60s |
| Stats complètes | POST /statistics/recompute | < 30s | < 60s | 120s |

### 1.2 Frontend

| Métrique | Cible |
|---|---|
| First Contentful Paint | < 1.5s |
| Largest Contentful Paint | < 2.5s |
| Time to Interactive | < 3.5s |
| Bundle size (gzipped) | < 300 KB |
| Re-render dashboard | < 200ms |

### 1.3 Jobs Scheduler

| Job | Cible | Max |
|---|---|---|
| Scraping tirages | < 10s | 30s |
| Calcul statistiques complet | < 30s | 120s |
| Scoring 1000 grilles | < 15s | 60s |
| Simulation 100K tirages | < 30s | 120s |

---

## 2. Stratégie de Cache

### 2.1 Architecture Cache

```
Client (Browser Cache)
  │
  ▼
React (TanStack Query Cache)     ← staleTime / gcTime
  │
  ▼
API FastAPI
  │
  ├── Cache applicatif (in-memory)  ← TTL-based dict
  │
  └── Base de données
         └── Snapshots pré-calculés  ← StatisticsSnapshot
```

### 2.2 Cache Frontend (TanStack Query)

```typescript
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000,     // 5 min avant re-fetch
      gcTime: 30 * 60 * 1000,        // 30 min en mémoire
      refetchOnWindowFocus: false,
      retry: 2,
    },
  },
});

// Cache spécifique par type de données
const CACHE_CONFIG = {
  games:      { staleTime: 60 * 60 * 1000 },    // 1h (quasi-statique)
  draws:      { staleTime: 10 * 60 * 1000 },     // 10 min
  statistics: { staleTime: 15 * 60 * 1000 },     // 15 min
  grids:      { staleTime: 0 },                   // Toujours frais
  simulation: { staleTime: 0 },                   // Jamais caché
};
```

### 2.3 Cache Backend (In-Memory)

```python
from datetime import datetime, timedelta
from typing import Any
import threading

class TTLCache:
    """Cache simple en mémoire avec TTL."""
    
    def __init__(self):
        self._store: dict[str, tuple[Any, datetime]] = {}
        self._lock = threading.Lock()
    
    def get(self, key: str) -> Any | None:
        with self._lock:
            if key in self._store:
                value, expiry = self._store[key]
                if datetime.utcnow() < expiry:
                    return value
                del self._store[key]
        return None
    
    def set(self, key: str, value: Any, ttl: timedelta) -> None:
        with self._lock:
            self._store[key] = (value, datetime.utcnow() + ttl)
    
    def invalidate(self, pattern: str) -> None:
        with self._lock:
            keys_to_delete = [k for k in self._store if pattern in k]
            for k in keys_to_delete:
                del self._store[k]

# Singleton
cache = TTLCache()
```

### 2.4 Politique d'Invalidation

| Événement | Invalidation |
|---|---|
| Nouveau tirage scraped | `statistics:*`, `draws:*` |
| Statistiques recalculées | `statistics:*` |
| Grilles régénérées | `grids:*`, `portfolios:*` |
| Configuration jeu modifiée | Tout le cache du jeu |

---

## 3. Optimisations Base de Données

### 3.1 Index

| Table | Index | Type | Raison |
|---|---|---|---|
| draws | `(game_id, draw_date)` | UNIQUE | Requêtes par jeu+date |
| draws | `(game_id, draw_number)` | UNIQUE | Lookup par numéro |
| statistics_snapshots | `(game_id, computed_at)` | INDEX | Dernières stats |
| scored_grids | `(game_id, score DESC)` | INDEX | Top grilles |
| scored_grids | `(game_id, created_at)` | INDEX | Grilles récentes |
| portfolios | `(game_id, created_at)` | INDEX | Derniers portefeuilles |
| job_executions | `(job_name, started_at)` | INDEX | Historique jobs |
| users | `(username)` | UNIQUE | Login |
| users | `(email)` | UNIQUE | Unicité email |

### 3.2 Requêtes Optimisées

```python
# Éviter le N+1 : eager loading
async def get_draws_with_game(
    self, game_id: int, limit: int, offset: int
) -> list[Draw]:
    stmt = (
        select(Draw)
        .where(Draw.game_id == game_id)
        .order_by(Draw.draw_date.desc())
        .limit(limit)
        .offset(offset)
    )
    result = await self.session.execute(stmt)
    return result.scalars().all()

# Pagination cursor-based pour gros volumes
async def get_draws_cursor(
    self, game_id: int, after_date: date | None, limit: int
) -> list[Draw]:
    stmt = select(Draw).where(Draw.game_id == game_id)
    if after_date:
        stmt = stmt.where(Draw.draw_date < after_date)
    stmt = stmt.order_by(Draw.draw_date.desc()).limit(limit)
    result = await self.session.execute(stmt)
    return result.scalars().all()
```

### 3.3 Pré-calcul (StatisticsSnapshot)

Les statistiques sont pré-calculées par le scheduler et stockées en JSON :

```
1. Job scrape → Nouveau tirage
2. Job compute_statistics → Recalcul complet
3. Résultats → StatisticsSnapshot (JSON blob)
4. API GET /statistics → Lecture du snapshot (rapide)
```

Avantage : l'API ne fait que **lire** un document JSON, aucun calcul en temps réel.

---

## 4. Optimisations Calcul

### 4.1 NumPy Vectorisation

```python
# ❌ Lent : boucle Python
def frequency_slow(draws: list[list[int]], max_num: int) -> dict:
    freq = {}
    for draw in draws:
        for num in draw:
            freq[num] = freq.get(num, 0) + 1
    return freq

# ✅ Rapide : NumPy vectorisé
def frequency_fast(draws: np.ndarray, max_num: int) -> np.ndarray:
    return np.bincount(draws.ravel(), minlength=max_num + 1)[1:]

# Benchmark ~100x plus rapide pour 2000 tirages
```

### 4.2 Matrice de Cooccurrences Vectorisée

```python
def cooccurrence_matrix(draws: np.ndarray, max_num: int) -> np.ndarray:
    n = max_num + 1
    binary = np.zeros((len(draws), n), dtype=np.int8)
    for i, draw in enumerate(draws):
        binary[i, draw] = 1
    # M^T × M = matrice de cooccurrences
    return binary.T @ binary
```

### 4.3 Parallélisme des Moteurs Statistiques

```python
import asyncio

async def compute_all_statistics(draws, game_def):
    """Lance tous les moteurs en parallèle (I/O-like avec pre-loaded data)."""
    tasks = [
        frequency_engine.compute(draws, game_def),
        gap_engine.compute(draws, game_def),
        cooccurrence_engine.compute(draws, game_def),
        temporal_engine.compute(draws, game_def),
        distribution_engine.compute(draws, game_def),
        bayesian_engine.compute(draws, game_def),
        graph_engine.compute(draws, game_def),
    ]
    results = await asyncio.gather(*tasks)
    return merge_results(results)
```

### 4.4 Optimisation Méta-heuristiques

| Technique | Impact |
|---|---|
| Évaluation incrémentale | Ne recalculer que le delta après mutation |
| Pré-calcul lookup tables | Paires affinité, gaps → dict O(1) |
| Elagage précoce | Arrêter si convergé (plateau > N itérations) |
| Population sizing | Adapter la taille au budget temps |

---

## 5. Scalabilité

### 5.1 Profils d'utilisation

| Profil | Utilisateurs | Jeux | Tirages/jeu | Description |
|---|---|---|---|---|
| Dev/Local | 1 | 2 | ~2000 | SQLite, un seul utilisateur |
| Production légère | 1-5 | 2-4 | ~5000 | PostgreSQL, usage familial |
| Production standard | 5-20 | 5+ | ~10000 | Docker, usage associatif |

### 5.2 Limites Actuelles (v1)

| Ressource | Limite | Raison |
|---|---|---|
| Tirages/jeu | 10 000 | Au-delà, calcul stats > 60s |
| Grilles/génération | 100 | Mémoire + temps |
| Simulation tirages | 1 000 000 | Temps CPU |
| Utilisateurs simultanés | 20 | Single process uvicorn |
| Taille snapshot JSON | 5 MB | Mémoire |

### 5.3 Strategies de Scale (futur)

```
Phase 1 (v1) : Monolithe
  uvicorn --workers 1

Phase 2 (v2) : Multi-workers
  uvicorn --workers 4 (1 worker / core)
  + PostgreSQL connection pool

Phase 3 (v3) : Docker
  docker-compose:
    - nginx (reverse proxy)
    - api (2-4 replicas)
    - postgres
    - redis (cache partagé)
    - scheduler (1 instance)
```

---

## 6. Monitoring Performance

### 6.1 Middleware de Timing

```python
import time
import structlog

logger = structlog.get_logger()

@app.middleware("http")
async def timing_middleware(request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    duration_ms = (time.perf_counter() - start) * 1000
    
    logger.info(
        "http.request",
        method=request.method,
        path=request.url.path,
        status=response.status_code,
        duration_ms=round(duration_ms, 2),
    )
    
    response.headers["X-Response-Time"] = f"{duration_ms:.2f}ms"
    return response
```

### 6.2 Endpoint Health Check

```python
@router.get("/health")
async def health_check(session = Depends(get_session)):
    checks = {}
    
    # Check DB
    try:
        await session.execute(text("SELECT 1"))
        checks["database"] = "ok"
    except Exception:
        checks["database"] = "error"
    
    # Check cache
    cache.set("health", True, timedelta(seconds=10))
    checks["cache"] = "ok" if cache.get("health") else "error"
    
    status = "healthy" if all(v == "ok" for v in checks.values()) else "degraded"
    return {"status": status, "checks": checks}
```

---

## 7. Bonnes Pratiques

| Catégorie | Règle |
|---|---|
| SQL | Toujours paginer, jamais `SELECT *` sans LIMIT |
| Cache | TTL approprié, invalider proactivement |
| NumPy | Vectoriser toute opération sur tableaux |
| JSON | Stocker les blobs pré-sérialisés dans les snapshots |
| Frontend | Code-splitting par route, lazy load des charts |
| Images | Aucune (application data-only) |
| API | Compression gzip activée |
| Async | `asyncio.gather` pour les tâches parallèles |

---

## 8. Références

| Document | Contenu |
|---|---|
| [02_Architecture_Globale](02_Architecture_Globale.md) | Architecture système |
| [03_Architecture_Backend](03_Architecture_Backend.md) | Configuration uvicorn |
| [07_Moteur_Statistique](07_Moteur_Statistique.md) | Calculs à optimiser |
| [15_Observabilite](15_Observabilite.md) | Métriques à surveiller |
| [11_Scheduler_et_Jobs](11_Scheduler_et_Jobs.md) | Performance des jobs |

---

*Fin du document 14_Performance_et_Scalabilite.md*
