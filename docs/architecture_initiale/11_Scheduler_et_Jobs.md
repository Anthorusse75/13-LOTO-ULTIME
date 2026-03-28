# 11 — Scheduler et Jobs

> **Projet** : LOTO ULTIME  
> **Version** : 1.0  
> **Date** : 2026-03-27  
> **Références croisées** : [03_Backend](03_Architecture_Backend.md) · [05_Modele](05_Modele_Donnees.md) · [09_Optimisation](09_Moteur_Optimisation.md) · [15_Observabilite](15_Observabilite.md)

---

## 1. Rôle du Scheduler

Le scheduler automatise l'ensemble des tâches de fond nécessaires au maintien du système à jour :

- Récupération des nouveaux tirages
- Recalcul des statistiques
- Recalcul des scores et classements
- Recalcul des portefeuilles optimisés
- Nettoyage des données obsolètes

Le backend doit fonctionner comme un **service autonome** qui maintient les données à jour **sans intervention humaine**.

---

## 2. Technologie

**APScheduler** (Advanced Python Scheduler) avec :
- **Job stores** : SQLAlchemy (persistance des jobs)
- **Triggers** : Cron, Interval, Date
- **Executors** : ThreadPool (pour tâches sync) / AsyncIO (pour tâches async)

---

## 3. Architecture

```
┌───────────────────────────────────────────────┐
│              Scheduler (APScheduler)           │
│                                               │
│  ┌─────────────────────────────────────────┐  │
│  │            Job Store (DB)               │  │
│  │  Persiste l'état des jobs planifiés     │  │
│  └─────────────────────────────────────────┘  │
│                                               │
│  ┌─────────┐ ┌─────────┐ ┌──────────────┐   │
│  │ Trigger │ │ Trigger │ │   Trigger    │   │
│  │  Cron   │ │Interval │ │    Date      │   │
│  └────┬────┘ └────┬────┘ └──────┬───────┘   │
│       │           │              │            │
│  ┌────▼───────────▼──────────────▼──────────┐ │
│  │              Executor                     │ │
│  │  ThreadPoolExecutor (max_workers=4)       │ │
│  └────┬──────────────────────────────────────┘ │
│       │                                        │
│  ┌────▼──────────────────────────────────────┐ │
│  │              Job Functions                 │ │
│  │  fetch_draws · compute_stats · scoring    │ │
│  │  compute_top · optimize_portfolio         │ │
│  └────────────────────────────────────────────┘ │
└───────────────────────────────────────────────┘
```

---

## 4. Jobs Définis

### 4.1 Catalogue des Jobs

| Job | ID | Fréquence | Dépendances | Description |
|---|---|---|---|---|
| Récupération Loto | `fetch_loto` | Lun/Mer/Sam 22h | Aucune | Récupère les tirages Loto FDJ |
| Récupération EuroMillions | `fetch_euromillions` | Mar/Ven 22h | Aucune | Récupère les tirages EuroMillions |
| Recalcul statistiques | `compute_stats` | Après chaque fetch | `fetch_*` | Recalcule toutes les stats |
| Recalcul scoring | `compute_scoring` | Après stats | `compute_stats` | Recalcule les scores des grilles |
| Recalcul top grilles | `compute_top_grids` | Après scoring | `compute_scoring` | Met à jour le top 10 |
| Optimisation portefeuille | `optimize_portfolio` | Après top grilles | `compute_top_grids` | Recalcule les portefeuilles |
| Nettoyage | `cleanup` | Quotidien 3h | Aucune | Supprime les snapshots anciens |

### 4.2 Chaîne de dépendance

```
fetch_loto ──┐
             ├──▶ compute_stats ──▶ compute_scoring ──▶ compute_top_grids ──▶ optimize_portfolio
fetch_euro ──┘
```

---

## 5. Implémentation

### 5.1 Configuration du Scheduler

```python
# app/scheduler/scheduler.py
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor

def setup_scheduler(settings) -> AsyncIOScheduler:
    jobstores = {
        "default": SQLAlchemyJobStore(url=settings.DATABASE_URL.replace("+aiosqlite", "")),
    }
    executors = {
        "default": ThreadPoolExecutor(max_workers=4),
    }
    job_defaults = {
        "coalesce": True,       # Fusionner les exécutions manquées
        "max_instances": 1,     # Une seule instance par job
        "misfire_grace_time": 3600,  # 1h de grâce
    }
    
    scheduler = AsyncIOScheduler(
        jobstores=jobstores,
        executors=executors,
        job_defaults=job_defaults,
    )
    
    _register_jobs(scheduler, settings)
    
    return scheduler
```

### 5.2 Enregistrement des Jobs

```python
def _register_jobs(scheduler: AsyncIOScheduler, settings):
    from app.scheduler.jobs.fetch_draws import fetch_draws_job
    from app.scheduler.jobs.compute_statistics import compute_stats_job
    from app.scheduler.jobs.compute_scoring import compute_scoring_job
    from app.scheduler.jobs.compute_top_grids import compute_top_grids_job
    from app.scheduler.jobs.optimize_portfolio import optimize_portfolio_job
    
    # Loto FDJ : lundi, mercredi, samedi à 22h
    scheduler.add_job(
        fetch_draws_job,
        "cron",
        id="fetch_loto",
        day_of_week="mon,wed,sat",
        hour=22,
        minute=0,
        args=["loto-fdj"],
        replace_existing=True,
    )
    
    # EuroMillions : mardi, vendredi à 22h
    scheduler.add_job(
        fetch_draws_job,
        "cron",
        id="fetch_euromillions",
        day_of_week="tue,fri",
        hour=22,
        minute=0,
        args=["euromillions"],
        replace_existing=True,
    )
    
    # Recalcul statistiques : tous les jours à 23h
    scheduler.add_job(
        compute_stats_job,
        "cron",
        id="compute_stats",
        hour=23,
        minute=0,
        replace_existing=True,
    )
    
    # Recalcul scoring : tous les jours à 23h30
    scheduler.add_job(
        compute_scoring_job,
        "cron",
        id="compute_scoring",
        hour=23,
        minute=30,
        replace_existing=True,
    )
    
    # Top grilles : tous les jours à 23h45
    scheduler.add_job(
        compute_top_grids_job,
        "cron",
        id="compute_top_grids",
        hour=23,
        minute=45,
        replace_existing=True,
    )
    
    # Optimisation portefeuille : quotidien 0h00
    scheduler.add_job(
        optimize_portfolio_job,
        "cron",
        id="optimize_portfolio",
        hour=0,
        minute=0,
        replace_existing=True,
    )
```

### 5.3 Structure d'un Job

```python
# app/scheduler/jobs/fetch_draws.py
import structlog
from datetime import datetime
from app.models.job import JobStatus

logger = structlog.get_logger()

async def fetch_draws_job(game_slug: str):
    """Job de récupération des tirages pour un jeu donné."""
    job_execution = JobExecution(
        job_name=f"fetch_draws_{game_slug}",
        game_id=None,  # Résolu dans le job
        status=JobStatus.RUNNING,
        started_at=datetime.utcnow(),
        triggered_by="scheduler",
    )
    
    try:
        logger.info("fetch_draws.start", game_slug=game_slug)
        
        # Résoudre le jeu
        game = await game_repo.get_by_slug(game_slug)
        job_execution.game_id = game.id
        
        # Récupérer les tirages
        scraper = get_scraper(game_slug)
        last_draw = await draw_repo.get_latest(game.id)
        since = last_draw.draw_date if last_draw else None
        
        new_draws = await scraper.fetch_latest_draws(since_date=since)
        
        # Valider et sauvegarder
        saved_count = 0
        for raw_draw in new_draws:
            validated = validator.validate(raw_draw, game)
            if not await draw_repo.exists(game.id, validated.draw_date):
                await draw_repo.create(validated.to_model(game.id))
                saved_count += 1
        
        job_execution.status = JobStatus.SUCCESS
        job_execution.result_summary = {
            "fetched": len(new_draws),
            "saved": saved_count,
            "duplicates": len(new_draws) - saved_count,
        }
        
        logger.info(
            "fetch_draws.success",
            game_slug=game_slug,
            saved=saved_count,
        )
    
    except Exception as e:
        job_execution.status = JobStatus.FAILED
        job_execution.error_message = str(e)
        logger.error("fetch_draws.failed", game_slug=game_slug, error=str(e))
    
    finally:
        job_execution.finished_at = datetime.utcnow()
        job_execution.duration_seconds = (
            job_execution.finished_at - job_execution.started_at
        ).total_seconds()
        await job_repo.create(job_execution)
```

---

## 6. Exécution Manuelle

Les jobs peuvent être déclenchés manuellement via l'API :

```
POST /api/v1/jobs/{job_name}/trigger
```

Le système vérifie qu'aucune instance du même job n'est en cours (verrouillage).

```python
async def trigger_job_manually(job_name: str, triggered_by: str):
    """Déclenche un job manuellement."""
    # Vérifier qu'aucune instance n'est en cours
    running = await job_repo.get_running(job_name)
    if running:
        raise JobAlreadyRunningError(f"Job {job_name} est déjà en cours")
    
    # Modifier triggered_by
    # ... exécuter le job
```

---

## 7. Reprise sur Échec

### 7.1 Stratégie de retry

| Tentative | Délai | Action |
|---|---|---|
| 1ère | Immédiat | Réexécution automatique |
| 2ème | 5 min | Réexécution avec délai |
| 3ème | 30 min | Réexécution avec délai |
| 4ème+ | — | Abandon, alerte admin |

### 7.2 Implémentation

```python
MAX_RETRIES = 3
RETRY_DELAYS = [0, 300, 1800]  # secondes

async def execute_with_retry(job_func, *args, **kwargs):
    for attempt in range(MAX_RETRIES):
        try:
            return await job_func(*args, **kwargs)
        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                delay = RETRY_DELAYS[attempt]
                logger.warning(
                    "job.retry",
                    attempt=attempt + 1,
                    delay=delay,
                    error=str(e),
                )
                await asyncio.sleep(delay)
            else:
                logger.error("job.max_retries_exceeded", error=str(e))
                raise
```

---

## 8. Verrouillage de Concurrence

Empêcher l'exécution simultanée du même job :

```python
# Utilisation de max_instances=1 dans APScheduler
# + vérification en base avant exécution manuelle

job_defaults = {
    "max_instances": 1,
    "coalesce": True,
}
```

---

## 9. Historisation

Chaque exécution de job est enregistrée dans la table `job_executions` :

```
id | job_name         | game_id | status  | started_at          | finished_at         | duration_s | triggered_by
1  | fetch_loto       | 1       | SUCCESS | 2026-03-27 22:00:01 | 2026-03-27 22:00:05 | 4.2        | scheduler
2  | compute_stats    | null    | SUCCESS | 2026-03-27 23:00:01 | 2026-03-27 23:00:28 | 27.1       | scheduler
3  | fetch_euro       | 2       | FAILED  | 2026-03-27 22:00:01 | 2026-03-27 22:00:03 | 2.1        | scheduler
```

Retention : 90 jours (configurable).

---

## 10. Monitoring

→ Détails : [15_Observabilite](15_Observabilite.md)

Le scheduler expose :
- État de chaque job planifié
- Prochaine exécution prévue
- Dernière exécution + résultat
- Statistiques (temps moyen, taux d'échec)

---

## 11. Références

| Document | Contenu |
|---|---|
| [03_Architecture_Backend](03_Architecture_Backend.md) | Intégration backend |
| [05_Modele_Donnees](05_Modele_Donnees.md) | Table JobExecution |
| [06_API_Design](06_API_Design.md) | Endpoints jobs |
| [15_Observabilite](15_Observabilite.md) | Monitoring jobs |
| [09_Moteur_Optimisation](09_Moteur_Optimisation.md) | Génération optimisée (job) |
| [16_Strategie_Tests](16_Strategie_Tests.md) | Tests d'intégration jobs |

---

*Fin du document 11_Scheduler_et_Jobs.md*
