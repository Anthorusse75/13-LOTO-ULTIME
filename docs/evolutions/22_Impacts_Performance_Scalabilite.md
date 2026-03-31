# 22 — Impacts Performance / Scalabilité

> Analyse complète des impacts de toutes les évolutions sur les performances, la latence, la scalabilité, le cache, l'async et le volume de données.

---

## Références croisées

- [00_Index_Evolutions](./00_Index_Evolutions.md)
- [14_Performance_et_Scalabilite](../14_Performance_et_Scalabilite.md) — Perf actuelle
- [05_Evolutions_Algorithmiques](./05_Evolutions_Algorithmiques.md) — Complexités
- [08_Evolution_Systeme_Reduit_Wheeling](./08_Evolution_Systeme_Reduit_Wheeling.md) — Bornes wheeling
- [19_Impacts_Base_De_Donnees](./19_Impacts_Base_De_Donnees.md) — Indexation
- [20_Impacts_Scheduler_Jobs](./20_Impacts_Scheduler_Jobs.md) — Durée pipeline

---

## 1. Baseline de performance actuel

### Temps de réponse mesurés (approx.)

| Endpoint | Temps moyen | P95 |
|----------|-------------|-----|
| GET /draws | ~50ms | ~100ms |
| GET /statistics | ~80ms | ~150ms |
| POST /grids/generate (10 grilles) | ~500ms | ~1.5s |
| POST /simulations/monte-carlo (1000 iter) | ~2s | ~5s |
| POST /portfolios/optimize (genetic) | ~3s | ~8s |
| Nightly pipeline complet | ~3 min | ~5 min |

### Infrastructure

- **Serveur** : 1 instance Docker, 2 CPU, 4GB RAM (192.168.0.94)
- **Base** : PostgreSQL 16 (même machine)
- **Pas de cache applicatif**
- **Pas de CDN**

---

## 2. Nouveaux endpoints et leur complexité

### Wheeling (doc 08)

| Opération | Complexité | Temps estimé |
|-----------|-----------|-------------|
| Preview (n=10, k=5, t=3) | O(C(n,t) × k) | ~100ms |
| Preview (n=15, k=5, t=3) | O(C(15,3) × 5) = O(2275) | ~500ms |
| Preview (n=20, k=5, t=3) | O(C(20,3) × 5) = O(5700) | ~1s |
| Generate (n=10, greedy) | ~100ms | ~200ms total |
| Generate (n=15, greedy) | ~500ms | ~1s total |
| Generate (n=20, greedy) | ~2s | ~3s total |
| Generate (n=20, k=5, t=4) | Potentiellement lent | **~5-10s** |

**Borne** : n ≤ 20 imposé côté validation. Au-delà, le temps explose (combinatoire).

### Budget (doc 09)

| Opération | Complexité | Temps estimé |
|-----------|-----------|-------------|
| optimize (3 stratégies) | 3 × scoring + 1 wheeling potentiel | ~2-5s |

### Comparaison (doc 10)

| Opération | Complexité | Temps estimé |
|-----------|-----------|-------------|
| compare (3 stratégies, 8 axes) | 3 × (scoring + simulation légère) | ~3-8s |

### Check played grids (doc 15)

| Volume | Opération | Temps estimé |
|--------|-----------|-------------|
| 100 grilles jouées | 100 comparaisons vs 1 tirage | ~200ms |
| 1000 grilles jouées | 1000 comparaisons | ~1s |

---

## 3. Points chauds identifiés

### 3.1 — Wheeling génération (critique)

**Problème** : Pour n=20, t=4, le nombre de t-subsets à couvrir = C(20,4) = 4845. Le greedy doit itérer sur C(20,5) = 15504 combos candidats par itération.

**Mitigations** :
1. **Borne stricte** : n ≤ 20, t ≤ k-1
2. **Timeout** : 30 secondes max, retourner résultat partiel si timeout
3. **Cache** : Stocker les résultats fréquents (même paramètres → même résultat déterministe)
4. **Algorithme** : Greedy avec heuristiques d'élagage, pas d'ILP en phase C

### 3.2 — Comparateur de stratégies

**Problème** : Compare N stratégies × 8 axes. Si une stratégie inclut simulation Monte Carlo (1000 itérations), le temps explose.

**Mitigations** :
1. **Simulation allégée** : 100 itérations seulement pour le comparateur (vs 1000 normal)
2. **Timeout par stratégie** : 5s max
3. **Caching intermédiaire** : Si une stratégie a déjà été évaluée récemment (même paramètres), réutiliser

### 3.3 — Pipeline nocturne étendu

**Problème** : 11 étapes au lieu de 5. Risque de dépasser le créneau nocturne.

**Mitigations** :
1. **Parallélisation** : check_played_grids et pre_generate sont indépendants → lancer en parallèle
2. **Monitoring** : Alerter si pipeline > 10 min
3. **Optimization** : Batch processing pour check_played_grids

---

## 4. Stratégie de cache (DT-03)

### Cache in-process (cachetools)

| Donnée cachée | TTL | Clé | Taille max |
|---------------|-----|-----|-----------|
| StatisticsSnapshot (dernier par game) | 1h | `stats:{game_id}` | 5 entries |
| GameDefinition (actives) | 24h | `games:active` | 1 entry |
| GamePrizeTier (par game) | 24h | `prize_tiers:{game_id}` | 5 entries |
| Top grilles du jour | 1h | `top_grids:{game_id}` | 5 entries |
| Daily suggestion | 1h | `suggestion:{game_id}` | 5 entries |

### Implémentation

```python
from cachetools import TTLCache

# Cache global
stats_cache = TTLCache(maxsize=5, ttl=3600)
games_cache = TTLCache(maxsize=1, ttl=86400)
prize_tiers_cache = TTLCache(maxsize=5, ttl=86400)

async def get_statistics_cached(db: AsyncSession, game_id: int):
    key = f"stats:{game_id}"
    if key in stats_cache:
        return stats_cache[key]
    result = await get_latest_snapshot(db, game_id)
    stats_cache[key] = result
    return result
```

### Invalidation

- Après `compute_statistics` → vider `stats_cache`
- Après `pre_generate_daily_content` → vider `top_grids` et `suggestion`
- Pas besoin d'invalidation cross-instance (1 seule instance)

---

## 5. Async et concurrence

### État actuel

- Tous les endpoints sont `async def`
- SQLAlchemy 2.0 async avec `AsyncSession`
- uvicorn avec workers configurable

### Risques de concurrence

| Scénario | Risque | Mitigation |
|----------|--------|------------|
| 2 requêtes generate simultanées | CPU spike | Rate limiting 10/min |
| Pipeline nocturne + requête utilisateur | Contention DB | Pipeline utilise sa propre session |
| Cache write simultané | Données incohérentes | TTLCache est thread-safe |

---

## 6. Volume de données et croissance

### Projections à 6 mois

| Table | Volume 6 mois | Taille estimée |
|-------|---------------|---------------|
| draws | +1000 lignes (5 jeux × ~200 tirages) | ~500 KB |
| scored_grids | +50000 (génération quotidienne) | ~50 MB |
| wheeling_systems | +2000 | ~10 MB (grids JSON volumineux) |
| user_saved_results | +10000 | ~20 MB |
| grid_draw_results | +20000 | ~5 MB |
| user_notifications | ~5000 (purgé à 30j) | ~2 MB |
| statistics_snapshots | +1000 | ~50 MB (matrices JSON) |

**Total estimé** : ~140 MB en 6 mois. Pas de problème de volume.

### Requêtes les plus coûteuses

| Requête | Fréquence | Coût |
|---------|-----------|------|
| SELECT scored_grids ORDER BY score DESC LIMIT 10 | Chaque visite dashboard | Moyen (index) |
| SELECT statistics_snapshots WHERE game_id=? ORDER BY computed_at DESC LIMIT 1 | Chaque page stats | Léger (cache) |
| SELECT user_saved_results WHERE user_id=? ORDER BY created_at DESC | Chaque visite historique | Moyen (index) |

---

## 7. Optimisations recommandées par phase

### Phase A (quick wins)

| Action | Impact | Effort |
|--------|--------|--------|
| Ajouter index sur scored_grids(game_id, score) | -50% temps GET grids | 0.25j |
| Ajouter index sur draws(game_id, draw_date) | -30% temps GET draws | 0.25j |
| Implémenter cache stats (TTLCache) | -80% temps GET stats | 0.5j |
| Implémenter pagination (DT-05) | Éviter full scan | 0.5j |

### Phase B

| Action | Impact | Effort |
|--------|--------|--------|
| Cache games et prize_tiers | -90% temps sur données statiques | 0.25j |
| Cache top grilles quotidiennes | Dashboard instantané | 0.25j |

### Phase C

| Action | Impact | Effort |
|--------|--------|--------|
| Timeout wheeling 30s | Éviter blocage serveur | 0.25j |
| Borne n≤20 validation | Prévenir explosion combinatoire | Inclus dans validation |

### Phase D

| Action | Impact | Effort |
|--------|--------|--------|
| Simulation allégée pour comparateur | 10× plus rapide | 0.25j |
| Paralléliser pipeline steps indépendants | -30% durée pipeline | 0.5j |

---

## 8. Métriques de performance à suivre

| Métrique | Outil | Seuil alerte |
|----------|-------|-------------|
| Latence P95 par endpoint | Prometheus + Grafana | > 2s (lecture), > 10s (calcul) |
| Temps pipeline nocturne | job_executions | > 10 min |
| Hit rate cache | Logs applicatifs | < 50% |
| Connexions DB actives | pg_stat_activity | > 20 |
| CPU utilisation | Docker stats | > 80% sustained |
| Mémoire | Docker stats | > 3.5 GB |

---

## 9. Frontend performance

### Bundle size

| Action | Impact |
|--------|--------|
| React.lazy pour nouvelles pages | Chunk splitting automatique |
| Recharts import sélectif | Réduire taille charts |
| Tailwind CSS purge (déjà en place) | Pas de changement |

### Estimations taille bundle

| Module | Taille estimée |
|--------|---------------|
| WheelingPage + composants | ~30 KB gzip |
| BudgetPage + composants | ~20 KB gzip |
| ComparatorPage + composants | ~25 KB gzip |
| Dashboard enrichi | +15 KB gzip |
| Total ajouté | ~90 KB gzip |

---

## 10. Checklist locale

- [ ] Ajouter index sur scored_grids(game_id, score)
- [ ] Ajouter index sur draws(game_id, draw_date)
- [ ] Implémenter TTLCache pour statistiques
- [ ] Implémenter cache pour game_definitions et prize_tiers
- [ ] Implémenter cache pour top grilles quotidiennes
- [ ] Ajouter pagination sur GET draws et GET grids
- [ ] Ajouter timeout 30s sur wheeling/generate
- [ ] Validation n≤20 sur wheeling
- [ ] Simulation allégée (100 iter) pour comparateur
- [ ] Paralléliser steps indépendants du pipeline
- [ ] Code splitting React.lazy pour nouvelles pages
- [ ] Configurer métriques Prometheus pour nouveaux endpoints
- [ ] Dashboard Grafana : ajouter panels pour wheeling, budget, comparaison
- [ ] Test de charge : 10 requêtes wheeling simultanées

Réf. : [27_Checklist_Globale_Evolutions](./27_Checklist_Globale_Evolutions.md)
