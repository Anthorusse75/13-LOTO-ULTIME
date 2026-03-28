# 10. Analyse Détaillée de la Robustesse Produit

La robustesse d'un produit se mesure à sa capacité à fonctionner correctement dans des conditions variées, à résister aux erreurs, à se remettre des pannes, et à maintenir une qualité constante dans le temps. Cette section évalue LOTO ULTIME sous cet angle.

---

## 10.1 Tests automatisés

### Couverture actuelle

**337 tests passants** répartis en :

| Catégorie | Nombre approximatif | Couverture |
|-----------|-------------------|------------|
| Moteurs statistiques | ~70 | ✅ Les 7 moteurs testés |
| Moteurs de scoring | ~50 | ✅ Tous les critères |
| Moteurs d'optimisation | ~60 | ✅ Les 5 algorithmes |
| Simulation | ~30 | ✅ Monte Carlo + robustesse |
| Authentification | 23 | ✅ Login, register, refresh, RBAC |
| API intégration | ~50 | ✅ Routes principales |
| Repositories | ~30 | ⚠️ CRUD basique |
| Configuration | ~10 | ✅ Settings validation |
| Scrapers | ~15 | ✅ Parsing CSV |

**Points forts** :
- Les moteurs algorithmiques (le cœur du produit) sont bien testés
- Les tests d'intégration API vérifient le pipeline complet
- L'authentification a une couverture dédiée incluant les cas d'erreur

**Lacunes identifiées** :

1. **Pas de tests multi-loteries** : Aucun test ne vérifie que les opérations EuroMillions produisent des résultats différents de celles du Loto. Le bug `_get_game_config()` aurait été détecté immédiatement avec un tel test.

2. **Pas de tests de non-régression** : Si le scoring d'une grille connue change après une modification d'engine, rien ne l'alerte. Des tests « golden file » (résultat attendu figé) seraient utiles.

3. **Pas de tests de performance** : Aucun test ne vérifie que la génération de 10 grilles prend moins de X secondes, ou que la simulation de 10 000 itérations ne dépasse pas un seuil de temps.

4. **Pas de tests E2E** : Le frontend n'a aucun test (ni unitaire, ni E2E). Un parcours Playwright vérifiant « login → statistiques → génération → simulation » rattraperait beaucoup de problèmes d'intégration.

**Classement** :
- Tests multi-loteries : 🔧 Correction critique (aurait prévenu le bug principal)
- Tests non-régression : 📈 Amélioration importante
- Tests de performance : 📈 Amélioration
- Tests E2E : 📈 Amélioration (moyen terme)

---

## 10.2 Gestion des erreurs

### Backend

La gestion des erreurs backend est **globalement bonne** :

| Couche | Mécanisme | Verdict |
|--------|-----------|---------|
| Routes API | Exception handlers dans main.py | ✅ 7 types d'exceptions mappés |
| Services | try/except dans le pipeline | ✅ Engines isolés |
| Scheduler | Retry 3× avec backoff | ✅ Robuste |
| Scrapers | HTTP errors + validation errors | ✅ Compteurs d'erreurs |
| Auth | Exceptions spécifiques | ✅ Messages en français |

**Points faibles** :
- Le `GraphEngine` masque les erreurs de convergence eigenvector (retourne des zéros au lieu de signaler)
- Le `StatisticsService` est all-or-nothing : un engine en échec annule tous les résultats
- Pas de circuit breaker sur les appels HTTP aux scrapers FDJ

### Frontend

La gestion des erreurs frontend est **inégale** :

| Composant | Erreur réseau | Erreur 4xx | Erreur 5xx | État vide |
|-----------|--------------|-----------|-----------|-----------|
| Draws | ✅ ErrorBoundary | ✅ Toast | ✅ Toast | ✅ Message |
| Statistics | ✅ | ✅ | ✅ | ⚠️ « Run /recompute first » (technique) |
| Grids | ✅ | ✅ | ✅ | ✅ Message |
| Portfolio | ✅ | ✅ | ✅ | ⚠️ Pas de state pré-génération |
| Simulation | ✅ | ✅ | ✅ | ⚠️ Pas d'aide si pas de stats |
| Admin Jobs | ✅ | ✅ | ✅ | ⚠️ Pas de message « aucun historique » |

**Le toast d'erreur automatique** via l'intercepteur Axios est un bon filet de sécurité. Mais les messages d'erreur sont souvent techniques (« detail: Insufficient data for computation ») au lieu d'être orientés utilisateur (« Pas assez de tirages pour effectuer le calcul. Lancez l'importation des données dans l'administration. »).

**Classement** : 📈 Amélioration (messages d'erreur user-friendly)

---

## 10.3 Résilience des données

### Intégrité référentielle

La base de données maintient une intégrité correcte :
- FK constraints sur `game_id` dans tous les modèles
- Contrainte d'unicité `(game_id, draw_date)` pour éviter les doublons de tirages
- Enum SQLAlchemy pour les statuts et rôles

**Risque** : SQLite ne force pas les FK constraints par défaut. Il faut explicitement exécuter `PRAGMA foreign_keys = ON;` à chaque connexion. Le code actuel ne semble pas faire cela.

**Classement** : 🔧 Correction (activer PRAGMA foreign_keys)

### Accumulation de données

Certaines tables accumulent des données sans nettoyage :

| Table | Ajouts quotidiens | Nettoyage | Projection 1 an |
|-------|-------------------|-----------|-----------------|
| Draw | 3-5 par semaine | ❌ Jamais (voulu) | ~250 nouvelles lignes |
| StatisticsSnapshot | 2/jour (1 par jeu) | ✅ >30 jours supprimés | ~60 conservées |
| ScoredGrid | 10/jour (top grids) + user requests | ❌ Jamais | ~3,650+ grilles |
| Portfolio | 8/jour (4 stratégies × 2 jeux) | ❌ Jamais | ~2,920 portefeuilles |
| JobExecution | 10/jour | ✅ >90 jours supprimés | ~900 conservées |

Sans nettoyage, la table `ScoredGrid` atteindra **10 000+ entrées en 3 ans** et la table `Portfolio` **9 000+ entrées**. Pour SQLite, c'est gérable en volume mais les requêtes `get_all()` sans pagination deviendront lentes.

**Classement** : 📈 Amélioration importante (ajouter un cleanup des vieilles grilles et portfolios)

### Corruption de données

SQLite est vulnérable à la corruption en cas de crash pendant une écriture. Le projet utilise WAL mode via aiosqlite (recommandé), ce qui réduit le risque. Cependant :
- Pas de backup automatique de la base
- Pas de mécanisme de recovery
- La base contient 1642 tirages importés : une perte nécessiterait un re-import complet

**Classement** : 📈 Amélioration (backup automatique hebdomadaire)

---

## 10.4 Cohérence du pipeline

Le pipeline nightly (fetch → stats → scoring → top grids → portfolio) repose sur des intervalles de temps plutôt que sur un chaînage explicite :

```
22h00  fetch_loto / fetch_euromillions
23h00  compute_stats
23h30  compute_scoring (dépend de stats)
23h45  compute_top_grids (dépend de scoring)
00h00  optimize_portfolio (dépend de grids)
```

**Risque** : Si `compute_stats` prend plus de 30 minutes (imaginable avec l'ajout de moteurs plus complexes), `compute_scoring` démarre sans les nouvelles statistiques. Il utilise alors le snapshot précédent, ce qui crée une **incohérence temporelle** : les grilles sont scorées sur des statistiques périmées d'un jour.

**Aujourd'hui** : Le risque est faible car les calculs prennent ~10-30s au total. Mais avec la montée en complexité prévue (plus de moteurs, plus de données), le risque augmente.

**Solution** : Un job orchestrateur qui exécute les étapes séquentiellement :

```python
async def nightly_pipeline():
    await compute_stats_job()
    await compute_scoring_job()
    await compute_top_grids_job()
    await optimize_portfolio_job()
```

**Classement** : 📈 Amélioration structurante

---

## 10.5 Disponibilité et recovery

### Démarrage de l'application

Le démarrage suit un ordre correct :
1. Init logging
2. Init database (create tables)
3. Seed games (YAML → DB)
4. Seed admin user
5. Start scheduler
6. Serve API

**Risques au démarrage** :
- Si la base est verrouillée (autre processus), le démarrage échoue sans retry
- Si le réseau est down au moment du fetch, le scraper échoue (mais le retry du runner rattrape)
- Si les fichiers YAML de config sont corrompus, le seed échoue avec une erreur non descriptive

### Arrêt propre

Le shutdown est correct :
1. Scheduler arrêté (`shutdown(wait=False)`)
2. Database fermée

Mais `wait=False` signifie que les jobs en cours sont interrompus brutalement. Si un job est en train de commiter des données, le commit peut être partiel.

**Classement** : 📈 Amélioration modérée (ajouter un graceful shutdown avec timeout)

---

## 10.6 Monitoring et alerting

### État actuel

| Capacité | Implémenté | Moyen |
|----------|-----------|-------|
| Logging structuré | ✅ | structlog |
| Request tracing | ✅ | X-Request-ID |
| Timing des requêtes | ✅ | X-Process-Time-Ms header |
| Health check | ✅ | Endpoint + job périodique |
| Détection stale data | ✅ | > 7 jours sans tirage |
| Détection stuck jobs | ✅ | > 1h running |
| **Métriques Prometheus** | ❌ | - |
| **Alerting** | ❌ | - |
| **Dashboard monitoring** | ❌ | - |
| **Log aggregation** | ❌ | - |

**Pour un produit personnel en développement**, le niveau actuel est suffisant. Les logs structurés et le health check couvrent les besoins de diagnostic.

**Pour une mise en production**, il manquerait :
- Export Prometheus avec compteurs de requêtes, latences P50/P95/P99, erreurs 5xx
- Alerting (email ou webhook) quand le health check détecte un problème
- Dashboard Grafana ou similaire

**Classement** : 📈 Amélioration pour la production (pas prioritaire maintenant)

---

## 10.7 Synthèse robustesse

| Aspect | Score | Verdict |
|--------|-------|---------|
| Tests automatisés | 4/5 | Bonne couverture, manque multi-loteries + E2E |
| Gestion d'erreurs backend | 4/5 | Solide, quelques silences masqués |
| Gestion d'erreurs frontend | 3/5 | Toast automatique mais messages techniques |
| Intégrité données | 3/5 | FK correctes, PRAGMA FK non activé |
| Accumulation données | 2/5 | Grilles et portfolios non nettoyés |
| Cohérence pipeline | 3/5 | Timing-based, pas de chaînage |
| Recovery | 3/5 | Retry sur jobs, pas sur startup |
| Monitoring | 3/5 | Logs + health check, pas de métriques |
| **Score global** | **3.1/5** | **Correct pour du dev, insuffisant pour production** |

Le produit est robuste pour un environnement de développement mono-utilisateur. Les investissements prioritaires pour la prochaine étape sont :
1. Tests multi-loteries (prévention de bugs critiques)
2. Nettoyage des données accumulées
3. Orchestration pipeline séquentielle
4. PRAGMA foreign_keys activé
