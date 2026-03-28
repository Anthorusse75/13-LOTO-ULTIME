# 15 — Observabilité

> **Projet** : LOTO ULTIME  
> **Version** : 1.0  
> **Date** : 2026-03-27  
> **Références croisées** : [03_Backend](03_Architecture_Backend.md) · [11_Scheduler](11_Scheduler_et_Jobs.md) · [14_Performance](14_Performance_et_Scalabilite.md)

---

## 1. Principes

| Pilier | Outil | Usage |
|---|---|---|
| **Logs** | structlog | Journalisation structurée JSON |
| **Métriques** | Compteurs internes + endpoint /metrics | Suivi quantitatif |
| **Health** | Endpoint /health | État du système |
| **Audit** | Logs dédiés | Traçabilité des actions sensibles |

---

## 2. Logging Structuré

### 2.1 Configuration structlog

```python
# app/core/logging.py
import structlog
import logging
import sys

def setup_logging(log_level: str = "INFO", json_output: bool = True):
    """Configure structlog pour le projet."""
    
    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.UnicodeDecoder(),
    ]
    
    if json_output:
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer(colors=True))
    
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level.upper()),
    )
```

### 2.2 Format des Logs

**Mode JSON (production)** :
```json
{
  "event": "http.request",
  "method": "GET",
  "path": "/api/v1/statistics/loto-fdj",
  "status": 200,
  "duration_ms": 45.23,
  "user_id": 1,
  "timestamp": "2025-03-27T14:30:00.123Z",
  "level": "info",
  "logger": "api"
}
```

**Mode console (développement)** :
```
2025-03-27 14:30:00 [info     ] http.request    method=GET path=/api/v1/statistics/loto-fdj status=200 duration_ms=45.23
```

### 2.3 Contexte par Requête

```python
# Middleware : injecter request_id et user dans le contexte
import uuid

@app.middleware("http")
async def logging_context_middleware(request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(
        request_id=request_id,
    )
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response
```

### 2.4 Niveaux de Log par Module

| Module | Niveau | Exemples |
|---|---|---|
| `api` | INFO | Requêtes HTTP, erreurs client |
| `service` | INFO | Opérations métier, résultats |
| `engine` | DEBUG | Détails calculs statistiques |
| `repository` | DEBUG | Requêtes SQL (dev uniquement) |
| `scheduler` | INFO | Démarrage/fin jobs, erreurs |
| `scraper` | INFO | Tirages récupérés, validations |
| `security` | WARNING | Échecs auth, accès refusés |

---

## 3. Métriques

### 3.1 Compteurs Internes

```python
# app/core/metrics.py
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict
import threading

@dataclass
class MetricsCollector:
    """Collecteur de métriques in-process."""
    _counters: dict[str, int] = field(default_factory=lambda: defaultdict(int))
    _gauges: dict[str, float] = field(default_factory=dict)
    _histograms: dict[str, list[float]] = field(
        default_factory=lambda: defaultdict(list)
    )
    _lock: threading.Lock = field(default_factory=threading.Lock)
    _start_time: datetime = field(default_factory=datetime.utcnow)
    
    def increment(self, name: str, value: int = 1):
        with self._lock:
            self._counters[name] += value
    
    def gauge(self, name: str, value: float):
        with self._lock:
            self._gauges[name] = value
    
    def observe(self, name: str, value: float):
        with self._lock:
            self._histograms[name].append(value)
            # Garder les 1000 dernières observations
            if len(self._histograms[name]) > 1000:
                self._histograms[name] = self._histograms[name][-1000:]
    
    def snapshot(self) -> dict:
        with self._lock:
            return {
                "uptime_seconds": (datetime.utcnow() - self._start_time).total_seconds(),
                "counters": dict(self._counters),
                "gauges": dict(self._gauges),
                "histograms": {
                    name: {
                        "count": len(values),
                        "avg": sum(values) / len(values) if values else 0,
                        "min": min(values) if values else 0,
                        "max": max(values) if values else 0,
                    }
                    for name, values in self._histograms.items()
                },
            }

metrics = MetricsCollector()
```

### 3.2 Métriques Collectées

| Catégorie | Métrique | Type | Description |
|---|---|---|---|
| HTTP | `http.requests.total` | Counter | Nombre total de requêtes |
| HTTP | `http.requests.status.{code}` | Counter | Requêtes par code status |
| HTTP | `http.request.duration_ms` | Histogram | Temps de réponse |
| Auth | `auth.login.success` | Counter | Logins réussis |
| Auth | `auth.login.failure` | Counter | Logins échoués |
| Jobs | `job.{name}.success` | Counter | Jobs réussis |
| Jobs | `job.{name}.failure` | Counter | Jobs échoués |
| Jobs | `job.{name}.duration_ms` | Histogram | Durée des jobs |
| Engine | `engine.statistics.duration_ms` | Histogram | Durée calcul stats |
| Engine | `engine.scoring.duration_ms` | Histogram | Durée scoring |
| Engine | `engine.generation.duration_ms` | Histogram | Durée génération |
| DB | `db.queries.total` | Counter | Requêtes SQL |
| Cache | `cache.hits` | Counter | Cache hits |
| Cache | `cache.misses` | Counter | Cache misses |
| System | `active_users` | Gauge | Tokens valides actifs |

### 3.3 Endpoint /metrics

```python
@router.get("/metrics", dependencies=[Depends(require_role(UserRole.ADMIN))])
async def get_metrics():
    return metrics.snapshot()
```

Réponse :
```json
{
  "uptime_seconds": 86432.5,
  "counters": {
    "http.requests.total": 15234,
    "http.requests.status.200": 14892,
    "http.requests.status.401": 23,
    "http.requests.status.500": 2,
    "auth.login.success": 45,
    "auth.login.failure": 3,
    "job.scrape_draws.success": 128,
    "cache.hits": 8934,
    "cache.misses": 2341
  },
  "gauges": {
    "active_users": 3
  },
  "histograms": {
    "http.request.duration_ms": {
      "count": 1000,
      "avg": 87.4,
      "min": 2.1,
      "max": 4523.0
    }
  }
}
```

---

## 4. Health Check

### 4.1 Endpoint /health

```python
@router.get("/health")
async def health_check(
    session = Depends(get_session),
    settings: Settings = Depends(get_settings),
):
    checks = {}
    overall_status = "healthy"
    
    # Base de données
    try:
        await session.execute(text("SELECT 1"))
        checks["database"] = {"status": "ok"}
    except Exception as e:
        checks["database"] = {"status": "error", "detail": str(e)}
        overall_status = "unhealthy"
    
    # Scheduler
    try:
        from app.scheduler import scheduler
        running = scheduler.running
        checks["scheduler"] = {
            "status": "ok" if running else "warning",
            "running": running,
        }
        if not running:
            overall_status = "degraded"
    except Exception:
        checks["scheduler"] = {"status": "unknown"}
    
    # Dernier scraping
    try:
        last_job = await job_repo.get_last_execution("scrape_draws")
        if last_job:
            hours_ago = (datetime.utcnow() - last_job.completed_at).total_seconds() / 3600
            checks["last_scrape"] = {
                "status": "ok" if hours_ago < 48 else "warning",
                "hours_ago": round(hours_ago, 1),
            }
    except Exception:
        checks["last_scrape"] = {"status": "unknown"}
    
    return {
        "status": overall_status,
        "version": settings.APP_VERSION,
        "checks": checks,
        "timestamp": datetime.utcnow().isoformat(),
    }
```

### 4.2 Réponse

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "checks": {
    "database": { "status": "ok" },
    "scheduler": { "status": "ok", "running": true },
    "last_scrape": { "status": "ok", "hours_ago": 2.3 }
  },
  "timestamp": "2025-03-27T14:30:00.000Z"
}
```

---

## 5. Logging des Jobs

### 5.1 Décorateur de Job

```python
import functools
import time

def log_job_execution(job_name: str):
    """Décorateur pour logger l'exécution d'un job."""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            logger = structlog.get_logger("scheduler")
            logger.info("job.started", job=job_name)
            start = time.perf_counter()
            
            try:
                result = await func(*args, **kwargs)
                duration = (time.perf_counter() - start) * 1000
                
                metrics.increment(f"job.{job_name}.success")
                metrics.observe(f"job.{job_name}.duration_ms", duration)
                
                logger.info(
                    "job.completed",
                    job=job_name,
                    duration_ms=round(duration, 2),
                    result=str(result)[:200],
                )
                return result
                
            except Exception as e:
                duration = (time.perf_counter() - start) * 1000
                metrics.increment(f"job.{job_name}.failure")
                
                logger.error(
                    "job.failed",
                    job=job_name,
                    duration_ms=round(duration, 2),
                    error=str(e),
                    exc_info=True,
                )
                raise
        
        return wrapper
    return decorator

# Usage
@log_job_execution("scrape_draws")
async def scrape_draws_job(game_slug: str):
    ...
```

---

## 6. Logging d'Audit

### 6.1 Actions Auditées

```python
# app/core/audit.py
audit_logger = structlog.get_logger("audit")

async def audit_log(
    action: str,
    user_id: int | None,
    detail: dict | None = None,
    ip_address: str | None = None,
):
    audit_logger.info(
        "audit.action",
        action=action,
        user_id=user_id,
        detail=detail or {},
        ip_address=ip_address,
    )
```

### 6.2 Points d'Audit

| Action | Quand | Données |
|---|---|---|
| `auth.login` | Login réussi | username, IP |
| `auth.login_failed` | Login échoué | username tenté, IP |
| `auth.logout` | Déconnexion | user_id |
| `user.created` | Création utilisateur | username, rôle, créateur |
| `user.role_changed` | Modification rôle | ancien→nouveau, modificateur |
| `user.deactivated` | Désactivation | user_id, administrateur |
| `job.manual_trigger` | Job lancé manuellement | job_name, user_id |
| `game.created` | Ajout d'un jeu | game_slug, admin |
| `game.modified` | Modification config jeu | game_slug, champs modifiés |
| `admin.cache_cleared` | Vidage cache | admin_id |
| `admin.stats_recomputed` | Recalcul forcé | game_slug, admin_id |

---

## 7. Alertes (Futur)

### 7.1 Conditions d'Alerte

| Condition | Sévérité | Action |
|---|---|---|
| Health check unhealthy | CRITIQUE | Log ERROR + notification |
| Job échoué 3x consécutives | HAUTE | Log ERROR |
| Temps réponse p95 > 5s | MOYENNE | Log WARNING |
| Login échoué > 10/min | HAUTE | Log WARNING + rate limit |
| Espace disque < 10% | HAUTE | Log WARNING |
| Scheduler arrêté | CRITIQUE | Log ERROR |

### 7.2 Implémentation log-based (v1)

En v1, les alertes sont simplement des logs de niveau ERROR/WARNING. Un monitoring externe (tail logs, grep) peut être configuré.

```python
# Vérification périodique (job scheduler)
async def check_system_health():
    logger = structlog.get_logger("monitor")
    
    # Vérifier le dernier scraping
    last_scrape = await job_repo.get_last_execution("scrape_draws")
    if last_scrape:
        hours = (datetime.utcnow() - last_scrape.completed_at).total_seconds() / 3600
        if hours > 48:
            logger.warning("alert.stale_data", hours_since_scrape=round(hours, 1))
    
    # Vérifier les échecs de jobs
    recent_failures = await job_repo.count_failures_since(
        timedelta(hours=24)
    )
    if recent_failures > 5:
        logger.error("alert.job_failures", count=recent_failures, period="24h")
```

---

## 8. Fichiers de Log

### 8.1 Rotation

| Fichier | Contenu | Rotation | Rétention |
|---|---|---|---|
| `app.log` | Tous les logs | 10 MB | 30 jours |
| `audit.log` | Logs d'audit uniquement | 5 MB | 90 jours |
| `error.log` | Niveau ERROR+ | 5 MB | 90 jours |

### 8.2 Configuration logrotate (production)

```python
# Alternative Python : RotatingFileHandler
import logging.handlers

file_handler = logging.handlers.RotatingFileHandler(
    "logs/app.log",
    maxBytes=10 * 1024 * 1024,  # 10 MB
    backupCount=30,
)
```

---

## 9. Dashboard de Monitoring (Frontend)

Page Admin > Monitoring :

```
┌──────────────────────────────────────────────────────────┐
│  Monitoring Système                                      │
├──────────────────────────────────────────────────────────┤
│  Status: ● Healthy    Uptime: 3j 14h 22m                │
│                                                          │
│  ┌─ Requêtes (24h) ───────┐ ┌─ Jobs (24h) ────────────┐│
│  │  Total: 1,523           │ │  Réussis: 12            ││
│  │  Erreurs: 2 (0.13%)    │ │  Échoués: 0             ││
│  │  Temps moyen: 87ms     │ │  En attente: 3          ││
│  └─────────────────────────┘ └──────────────────────────┘│
│                                                          │
│  ┌─ Dernières exécutions jobs ──────────────────────────┐│
│  │  scrape_draws     ✅ 2h ago   (8.2s)               ││
│  │  compute_stats    ✅ 1h ago   (24.5s)              ││
│  │  score_grids      ✅ 1h ago   (12.1s)              ││
│  │  update_top       ✅ 45m ago  (3.4s)               ││
│  └──────────────────────────────────────────────────────┘│
└──────────────────────────────────────────────────────────┘
```

---

## 10. Références

| Document | Contenu |
|---|---|
| [03_Architecture_Backend](03_Architecture_Backend.md) | Middleware, configuration |
| [11_Scheduler_et_Jobs](11_Scheduler_et_Jobs.md) | Jobs à monitorer |
| [12_Securite](12_Securite_et_Authentification.md) | Audit trail |
| [14_Performance](14_Performance_et_Scalabilite.md) | Métriques de perf |

---

*Fin du document 15_Observabilite.md*
