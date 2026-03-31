# 20 — Impacts Scheduler / Jobs

> Analyse complète des impacts de toutes les évolutions sur le scheduler APScheduler, les jobs existants et les nouveaux jobs à créer.

---

## Références croisées

- [00_Index_Evolutions](./00_Index_Evolutions.md)
- [11_Scheduler_et_Jobs](../11_Scheduler_et_Jobs.md) — Scheduler actuel
- [15_Evolution_Automatisation_Produit](./15_Evolution_Automatisation_Produit.md)
- [16_Impacts_Backend](./16_Impacts_Backend.md)
- [19_Impacts_Base_De_Donnees](./19_Impacts_Base_De_Donnees.md) — Purges

---

## 1. État actuel du scheduler

### Jobs existants (9)

```
┌─────────────────────────────────────────────────┐
│  nightly_pipeline (orchestrateur, 01:00)        │
│  ┌──────────────────┐                           │
│  │ fetch_draws      │  23:00 (ou via pipeline)  │
│  │ compute_stats    │  après fetch              │
│  │ compute_scoring  │  après stats              │
│  │ compute_top      │  après scoring            │
│  │ optimize_portf   │  après top                │
│  └──────────────────┘                           │
├─────────────────────────────────────────────────┤
│  health_check          │  toutes les 5 min      │
│  backup_db             │  02:00                  │
│  cleanup               │  03:00                  │
└─────────────────────────────────────────────────┘
```

### Système de tracking

Chaque exécution est tracée dans `job_executions` : status, durée, erreur.

---

## 2. Modifications du pipeline nocturne

### Pipeline étendu

```
fetch_draws         (23:00 ou 01:00 via pipeline)
    │
    ├── compute_statistics
    │       │
    │       └── compute_hot_cold_summary   ← NOUVEAU
    │
    ├── compute_scoring
    │       │
    │       ├── compute_top_grids
    │       │
    │       └── pre_generate_daily_content  ← NOUVEAU
    │               │
    │               └── generate_daily_suggestion  ← NOUVEAU
    │
    ├── optimize_portfolio
    │
    ├── check_played_grids                  ← NOUVEAU
    │       │
    │       └── create_grid_result_notifications  ← NOUVEAU
    │
    └── create_new_draw_notifications       ← NOUVEAU
```

---

## 3. Nouveaux jobs

### JOB-01 : compute_hot_cold_summary

**Déclencheur** : Après `compute_statistics`  
**Fréquence** : Quotidien (pipeline)  
**Action** : Extraire top 5 numéros chauds et top 5 froids depuis StatisticsSnapshot, stocker dans `hot_cold_summary` (JSON).

```python
async def compute_hot_cold_summary(db: AsyncSession, game_id: int):
    snapshot = await get_latest_snapshot(db, game_id)
    freqs = snapshot.frequencies  # {num: count}
    sorted_nums = sorted(freqs.items(), key=lambda x: x[1], reverse=True)
    hot = sorted_nums[:5]
    cold = sorted_nums[-5:]
    snapshot.hot_cold_summary = {"hot": hot, "cold": cold}
    await db.commit()
```

**Effort** : 0.5 jour  
**Phase** : B

### JOB-02 : pre_generate_daily_content

**Déclencheur** : Après `compute_scoring`  
**Fréquence** : Quotidien (pipeline)  
**Action** : Marquer les top 10 grilles par jeu avec un tag `daily_top`, le portefeuille optimal avec `daily_optimal`.

```python
async def pre_generate_daily_content(db: AsyncSession, game_id: int):
    # 1. Récupérer top 10 grilles par score
    top_grids = await get_top_scored_grids(db, game_id, limit=10)
    # 2. Marquer/stocker pour le dashboard
    # (via champ generation_method = "daily_top" ou via user_saved_results system)
    ...
```

**Effort** : 0.5 jour  
**Phase** : B

### JOB-03 : generate_daily_suggestion

**Déclencheur** : Après `pre_generate_daily_content`  
**Fréquence** : Quotidien (pipeline)  
**Action** : Générer une grille suggestion par jeu actif, avec explication L1.

**Effort** : 0.5 jour  
**Phase** : D

### JOB-04 : check_played_grids

**Déclencheur** : Après `fetch_draws`  
**Fréquence** : Quotidien (pipeline)  
**Action** :
1. Récupérer toutes les `scored_grids` avec `is_played = true`
2. Pour chaque grille, comparer avec le dernier tirage du même `game_id`
3. Calculer `matched_numbers`, `matched_stars`, `match_count`, `star_match_count`
4. Déterminer `prize_rank` via `game_prize_tiers`
5. Insérer dans `grid_draw_results`

```python
async def check_played_grids(db: AsyncSession, game_id: int):
    latest_draw = await get_latest_draw(db, game_id)
    if not latest_draw:
        return
    
    played_grids = await get_played_grids_unchecked(db, game_id, latest_draw.id)
    
    for grid in played_grids:
        matched = set(grid.main_numbers) & set(latest_draw.main_numbers)
        matched_stars = set(grid.star_numbers or []) & set(latest_draw.star_numbers or [])
        
        prize_rank = await determine_prize_rank(
            db, game_id, len(matched), len(matched_stars)
        )
        
        result = GridDrawResult(
            scored_grid_id=grid.id,
            draw_id=latest_draw.id,
            matched_numbers=list(matched),
            matched_stars=list(matched_stars),
            match_count=len(matched),
            star_match_count=len(matched_stars),
            prize_rank=prize_rank.rank if prize_rank else None,
            estimated_prize=prize_rank.avg_prize if prize_rank else 0.0,
        )
        db.add(result)
    
    await db.commit()
```

**Effort** : 1 jour  
**Phase** : B

### JOB-05 : create_grid_result_notifications

**Déclencheur** : Après `check_played_grids`  
**Fréquence** : Quotidien (pipeline)  
**Action** : Pour chaque `grid_draw_result` créé, générer une notification pour le user_id associé.

```python
async def create_grid_result_notifications(db: AsyncSession):
    # Récupérer les résultats créés aujourd'hui avec user_id
    results = await get_todays_grid_results_with_users(db)
    
    for result in results:
        if result.user_id:
            notification = UserNotification(
                user_id=result.user_id,
                type="grid_result",
                title=f"Résultat de votre grille",
                message=f"{result.match_count} numéro(s) trouvé(s)"
                    + (f", gain estimé : {result.estimated_prize}€" if result.prize_rank else ""),
                data={"grid_id": result.scored_grid_id, "draw_id": result.draw_id},
            )
            db.add(notification)
    
    await db.commit()
```

**Effort** : 0.5 jour  
**Phase** : D

### JOB-06 : create_new_draw_notifications

**Déclencheur** : Après `fetch_draws` (si nouveau tirage trouvé)  
**Fréquence** : Quotidien (pipeline)  
**Action** : Créer une notification "Nouveau tirage disponible" pour tous les utilisateurs actifs.

**Effort** : 0.5 jour  
**Phase** : D

### JOB-07 : cleanup_notifications

**Déclencheur** : Indépendant  
**Fréquence** : Quotidien (03:00, avec cleanup existant)  
**Action** : Supprimer les notifications lues datant de plus de 30 jours.

```python
async def cleanup_notifications(db: AsyncSession):
    cutoff = datetime.utcnow() - timedelta(days=30)
    await db.execute(
        delete(UserNotification).where(
            UserNotification.is_read == True,
            UserNotification.created_at < cutoff,
        )
    )
    await db.commit()
```

**Effort** : 0.25 jour  
**Phase** : D

### JOB-08 : cleanup_anonymous_data

**Déclencheur** : Indépendant  
**Fréquence** : Quotidien (03:00, avec cleanup existant)  
**Action** : Supprimer les wheeling_systems et budget_plans anonymes (user_id IS NULL) datant de plus de 7 jours.

**Effort** : 0.25 jour  
**Phase** : C

---

## 4. Modifications des jobs existants

### fetch_draws

| Aspect | Avant | Après |
|--------|-------|-------|
| Jeux scrapés | Tous les jeux actifs | Inchangé |
| Post-action | Déclenche pipeline | Déclenche pipeline + create_new_draw_notifications |
| Multi-lottery | Fonctionne déjà | Vérifier BUG-01 n'impacte pas |

### compute_statistics

| Aspect | Avant | Après |
|--------|-------|-------|
| Post-action | Fin | + compute_hot_cold_summary |
| Multi-lottery | Vérifier game_id | BUG-01 fix |

### compute_scoring

| Aspect | Avant | Après |
|--------|-------|-------|
| Post-action | compute_top | + pre_generate_daily_content after top |
| BUG-02 | method_selector broken | Fix method_selector |

### cleanup

| Aspect | Avant | Après |
|--------|-------|-------|
| Scope | Données anciennes | + cleanup_notifications + cleanup_anonymous_data |

---

## 5. Configuration scheduler étendu

```python
# Nouveau pipeline étendu
NIGHTLY_PIPELINE = [
    ("fetch_draws", {}),
    ("compute_statistics", {}),
    ("compute_hot_cold_summary", {}),
    ("compute_scoring", {}),
    ("compute_top_grids", {}),
    ("pre_generate_daily_content", {}),
    ("check_played_grids", {}),
    ("create_grid_result_notifications", {}),  # Phase D
    ("create_new_draw_notifications", {}),     # Phase D
    ("generate_daily_suggestion", {}),         # Phase D
    ("optimize_portfolio", {}),
]

STANDALONE_JOBS = [
    ("health_check", "interval", {"minutes": 5}),
    ("backup_db", "cron", {"hour": 2}),
    ("cleanup", "cron", {"hour": 3}),          # inclut notifications + anonymous
]
```

---

## 6. Monitoring et alertes

### Métriques à surveiller

| Métrique | Seuil alerte | Action |
|----------|-------------|--------|
| Pipeline total duration | > 10 min | Investiguer job le plus lent |
| check_played_grids duration | > 2 min | Optimiser requête / index |
| fetch_draws failures | 2 consécutifs | Vérifier scraper / site FDJ |
| notification count/day | > 1000 | Vérifier boucle infinie |

### Logging

Chaque nouveau job doit :
1. Logger le début et la fin
2. Enregistrer dans `job_executions`
3. Loguer le nombre d'éléments traités

---

## 7. Résumé quantitatif

| Métrique | Avant | Après | Delta |
|----------|-------|-------|-------|
| Jobs total | 9 | 17 | +8 |
| Pipeline steps | 5 | 11 | +6 |
| Standalone jobs | 4 | 4 | 0 (cleanup étendu) |
| Durée pipeline estimée | ~3 min | ~5–7 min | +2–4 min |

---

## 8. Risques

| Risque | Impact | Mitigation |
|--------|--------|------------|
| Pipeline trop long (>10 min) | Résultats pas prêts au matin | Paralléliser jobs indépendants |
| Job check_played_grids sur beaucoup de grilles | Lenteur | Index + batch processing |
| Notification storm au déploiement initial | UX | Ne pas backfill les notifications |
| Échec nightly_pipeline casse tout le flux | Critique | Chaque step indépendante, retry, continue on error |

---

## 9. Checklist locale

- [ ] JOB-01 : Implémenter compute_hot_cold_summary
- [ ] JOB-02 : Implémenter pre_generate_daily_content
- [ ] JOB-03 : Implémenter generate_daily_suggestion
- [ ] JOB-04 : Implémenter check_played_grids
- [ ] JOB-05 : Implémenter create_grid_result_notifications
- [ ] JOB-06 : Implémenter create_new_draw_notifications
- [ ] JOB-07 : Implémenter cleanup_notifications
- [ ] JOB-08 : Implémenter cleanup_anonymous_data
- [ ] Étendre nightly_pipeline avec les 6 nouveaux steps
- [ ] Étendre cleanup avec notifications + anonymous
- [ ] Ajouter logging et tracking dans job_executions pour tous les nouveaux jobs
- [ ] Configurer monitoring / alertes seuils
- [ ] Tester pipeline complet en local
- [ ] Vérifier que les jobs échouent gracieusement (continue on error)

Réf. : [27_Checklist_Globale_Evolutions](./27_Checklist_Globale_Evolutions.md)
