# 4. Analyse Détaillée du Backend

## 4.1 API REST

### Surface d'API

L'API expose **34 endpoints** répartis en 8 domaines fonctionnels :

| Domaine    | Endpoints     | Auth requise                                     | Calcul intensif           |
| ---------- | ------------- | ------------------------------------------------ | ------------------------- |
| Auth       | 5             | Partiel (login/register publics avec rate limit) | Non                       |
| Games      | 2             | Non                                              | Non                       |
| Draws      | 2             | Non                                              | Non                       |
| Statistics | 8 + recompute | Partiel (bayesian/graph protégés)                | **Oui (recompute)**       |
| Grids      | 4             | Utilisateur                                      | **Oui (generate, score)** |
| Portfolios | 1             | Utilisateur                                      | **Oui**                   |
| Simulation | 4             | Utilisateur                                      | **Oui**                   |
| Jobs       | 4             | Admin                                            | **Oui (trigger)**         |

**Verdict** : La couverture fonctionnelle est excellente. L'API couvre l'intégralité de la chaîne d'analyse.

### Problèmes identifiés sur l'API

#### 🔧 Rate limiting insuffisant sur les endpoints de calcul

Seuls les endpoints d'authentification sont rate-limités (`5/min` login, `3/min` register). Les endpoints de calcul intensif n'ont aucune protection :

- `POST /statistics/recompute` — Lance le pipeline complet des 7 moteurs statistiques. Un utilisateur malveillant peut appeler cet endpoint en boucle et saturer le CPU du serveur.
- `POST /grids/generate` — Génère et optimise N grilles avec un algorithme métaheuristique. Selon la méthode, cela peut prendre 10+ secondes.
- `POST /simulation/monte-carlo` — Lance 10 000 simulations par défaut.

**Conséquence** : Un seul utilisateur peut rendre l'application inutilisable pour les autres en lançant des calculs répétés.

**Recommandation** :
- Ajouter un rate limit de `2/min` sur tous les endpoints de calcul intensif
- Implémenter un système de file d'attente pour les tâches longues (retourner un `202 Accepted` avec un ID de tâche, puis poll pour le résultat)

**Classement** : 🔧 Correction importante

#### 🔧 Pas d'endpoints de suppression ni de modification

L'API ne propose **aucun endpoint DELETE** et **aucun endpoint PATCH**. Concrètement :
- Un administrateur ne peut pas supprimer une grille, un portefeuille ou un snapshot
- Un utilisateur ne peut pas modifier son profil (email, mot de passe)
- Il n'existe aucun moyen de nettoyer les données depuis l'interface

Le cleanup automatique via le scheduler supprime les vieux jobs et snapshots, mais les grilles et portefeuilles s'accumulent indéfiniment.

**Classement** : 📈 Amélioration nécessaire

#### ⚠️ Pagination incomplète

Seul l'endpoint `GET /draws` implémente la pagination (offset/limit avec un maximum de 500). Les autres endpoints list retournent toutes les données sans limite :
- `GET /grids/top` — Retourne jusqu'à 100 grilles (acceptable)
- `GET /jobs` — Paginé (50 par défaut, max 200) ✅
- `GET /statistics/cooccurrences` — Retourne top N (50 par défaut, max 500) ✅

Le problème se posera quand les tables contiendront des milliers d'entrées après plusieurs mois d'exécution.

**Classement** : 📈 Amélioration

---

## 4.2 Services métier

### StatisticsService

Le service d'orchestration des statistiques est bien conçu :

```python
class StatisticsService:
    def __init__(self, draw_repo, stats_repo):
        self._engines = {
            "frequency": FrequencyEngine(),
            "gaps": GapEngine(),
            # ... 7 engines
        }
    
    async def compute_all(self, game_id, game):
        draws = await self._draw_repo.get_numbers_matrix(game_id)
        results = {}
        for name, engine in self._engines.items():
            results[name] = engine.compute(draws, game)
        # Persist snapshot
```

**Forces** :
- Pipeline séquentiel clair et traçable
- Chaque engine est isolé — un échec est tracé individuellement
- Le check `n_draws < MIN_DRAWS_REQUIRED` évite les calculs absurdes

**Faiblesses** :
- Les engines sont instanciés à chaque création de `StatisticsService`. Comme les engines sont stateless, ils pourraient être des singletons ou des fonctions de classe.
- Le pipeline est all-or-nothing : si un engine échoue, aucun résultat n'est sauvegardé. Un mode dégradé (sauvegarder les résultats partiels) serait plus résilient.
- Aucune parallélisation : les 7 engines s'exécutent séquentiellement alors qu'ils sont indépendants. Un `asyncio.gather()` avec `to_thread()` pourrait réduire le temps de calcul.

**Classement** : 📈 Amélioration (parallélisation, mode dégradé)

### GridService

Le service de grilles délègue correctement au `GridScorer` et aux optimiseurs :

**Force** : Support de 4 méthodes d'optimisation + auto-sélection
**Faiblesse** : L'auto-sélection est bugée (toujours `"genetic"` — voir section 5)

### SimulationService

Le service de simulation est complet avec 4 opérations distinctes :
1. Monte Carlo sur une grille unique
2. Monte Carlo sur un portefeuille
3. Analyse de stabilité (bootstrap)
4. Comparaison avec des grilles aléatoires

**Force** : Couverture fonctionnelle complète
**Faiblesse** : Les 10 000 simulations Monte Carlo (défaut) tournent sur le thread principal

---

## 4.3 Repositories

### Pattern générique

Le `BaseRepository[T]` offre des opérations CRUD génériques :

```python
class BaseRepository(Generic[T]):
    async def get(self, id: int) -> T | None
    async def get_all(self, **filters) -> list[T]
    async def create(self, entity: T) -> T
    async def update(self, entity: T) -> T
    async def delete(self, entity: T) -> None
    async def count(self, **filters) -> int
```

**Problème de performance dans `count()`** :

```python
async def count(self, **filters) -> int:
    stmt = select(self._model_class).filter_by(**filters)
    result = await self._session.execute(stmt)
    return len(result.scalars().all())  # ← Charge TOUS les enregistrements en mémoire
```

Cette implémentation charge la totalité des enregistrements pour les compter. Pour une table de 1000 tirages, c'est acceptable. Pour une table de 100 000 grilles accumulées sur un an, c'est une fuite mémoire.

**Correction** :
```python
async def count(self, **filters) -> int:
    stmt = select(func.count()).select_from(self._model_class).filter_by(**filters)
    result = await self._session.execute(stmt)
    return result.scalar_one()
```

**Classement** : 🔧 Correction importante

### Repositories spécialisés

Les 7 repositories spécialisés ajoutent des requêtes pertinentes :
- `DrawRepository.get_numbers_matrix()` — Convertit les tirages en matrice numpy pour les engines ✅
- `DrawRepository.exists(game_id, draw_date)` — Évite les doublons d'import ✅
- `GridRepository.get_top_grids(game_id, limit)` — Tri par score descendant ✅
- `UserRepository.get_by_email()` — Recherche case-insensitive avec `func.lower()` ✅

---

## 4.4 Scheduler et Jobs

### Configuration du scheduler

Le scheduler APScheduler est correctement configuré avec 8 jobs cron :

| Job                | Schedule         | Durée estimée |
| ------------------ | ---------------- | ------------- |
| fetch_loto         | Lun/Mer/Sam 22h  | ~5s           |
| fetch_euromillions | Mar/Ven 22h      | ~5s           |
| compute_stats      | Quotidien 23h    | 10-30s        |
| compute_scoring    | Quotidien 23h30  | 5-15s         |
| compute_top_grids  | Quotidien 23h45  | 30-120s       |
| optimize_portfolio | Quotidien 0h00   | 30-120s       |
| cleanup            | Quotidien 3h     | <1s           |
| health_check       | Toutes les 30min | <1s           |

**Forces** :
- `coalesce=True` et `max_instances=1` évitent les exécutions multiples
- `misfire_grace_time=3600` donne une heure de marge en cas de retard
- Le scheduling est cohérent : fetch → stats → scoring → top grids → portfolio (pipeline séquentiel par timing)

**Faiblesses** :

#### ⚠️ Pas de chaînage explicite entre les jobs

Le pipeline nightly repose sur des intervalles de temps (23h → 23h30 → 23h45 → 0h) plutôt que sur un chaînage explicite. Si `compute_stats` prend plus de 30 minutes (par exemple avec beaucoup plus de tirages dans le futur), `compute_scoring` démarrera sans avoir les statistiques à jour.

**Solution** : Implémenter un job orchestrateur qui lance les étapes séquentiellement, ou utiliser un mécanisme de dépendance.

**Classement** : 📈 Amélioration structurante

#### ⚠️ Pas de timezone explicite

```python
scheduler.add_job(
    fetch_draws_job,
    "cron",
    hour=22,
    minute=0,
    # ← Pas de timezone= argument
)
```

Le scheduler utilise le fuseau horaire système. En production (serveur cloud), ce sera probablement UTC, ce qui décalera les horaires de fetch par rapport aux tirages FDJ (heure de Paris).

**Classement** : 🔧 Correction à faire avant déploiement

### Runner avec retry

Le système de retry est bien conçu :

```
Tentative 1 → Échec → Attente 0s
Tentative 2 → Échec → Attente 5s
Tentative 3 → Échec → Job marqué FAILED
```

**Forces** :
- Chaque tentative est loggée individuellement
- Le status final est toujours persisté en base
- La durée totale est calculée correctement

**Faiblesses** :
- Aucun timeout : un job qui boucle indéfiniment n'est jamais tué
- Le health check détecte les jobs « collés » après 1h, mais ne les tue pas

**Classement** : 📈 Amélioration — ajouter un `asyncio.wait_for(timeout=300)` par défaut

---

## 4.5 Scrapers et ingestion

### FDJ Loto Scraper

Le scraper Loto FDJ télécharge un fichier ZIP contenant un CSV depuis l'API STO de la FDJ. L'implémentation est solide :

- Timeout configurable (httpx)
- Follow redirects activé
- User-Agent personnalisé
- Extraction ZIP en mémoire (pas de fichier temporaire)
- Parsing CSV avec `DictReader` (robuste aux changements d'ordre de colonnes)
- UTF-8 BOM handling (`utf-8-sig`)
- Validation de chaque ligne avec `DrawValidator`
- Compteurs détaillés (fetched, saved, duplicates, errors)

**Faiblesse principale** : L'URL de l'API FDJ est hardcodée dans le code source :
```python
FDJ_LOTO_ZIP_URL = "https://www.sto.api.fdj.fr/anonymous/service-draw-info/v3/..."
```

Si FDJ change cette URL (ce qui arrive), il faut modifier le code et redéployer. Cette URL devrait être dans la configuration.

**Classement** : 📈 Amélioration

### EuroMillions Scraper

Identique au scraper Loto sauf pour le parsing des colonnes (2 étoiles au lieu de 1 numéro chance). Le code est dupliqué à ~95%.

**Recommandation** : Factoriser dans une classe de base `FDJBaseScraper` qui accepte un mapping de colonnes en paramètre.

**Classement** : 📈 Amélioration (refactoring, pas de bug)

---

## 4.6 Authentification et sécurité

### Implémentation JWT

L'authentification est bien implémentée :
- **Hashage bcrypt** avec sel automatique
- **JWT HS256** avec séparation access token (60 min) / refresh token (7 jours)
- **Champ `type`** dans le payload JWT pour distinguer access et refresh
- **RBAC 3 niveaux** : ADMIN > UTILISATEUR > CONSULTATION
- **Rate limiting** : 5/min sur login, 3/min sur register
- **Headers de sécurité** : X-Content-Type-Options, X-Frame-Options, X-XSS-Protection

### Points d'attention

| Aspect                | État                  | Risque                                       |
| --------------------- | --------------------- | -------------------------------------------- |
| Complexité password   | ❌ Aucune validation   | Un mot de passe vide est accepté             |
| Révocation de token   | ❌ Pas de blacklist    | Un token volé est valide jusqu'à expiration  |
| Vérification email    | ❌ Absente             | N'importe quelle adresse est acceptée        |
| Brute-force refresh   | ⚠️ Non limité          | Le endpoint `/refresh` n'a pas de rate limit |
| Admin password en dur | ⚠️ Default dans config | `ChangeMe123!` dans le code source           |

**Classement** :
- Complexité password : 🔧 Correction importante
- Révocation token : 📈 Amélioration (criticité dépend du déploiement)
- Les autres : 📈 Améliorations pour la production

---

## 4.7 Logging et observabilité

### Forces

L'utilisation de **structlog** est un excellent choix. Le logging est :
- **Structuré** (key-value pairs, pas de strings formatés)
- **Contextualisé** (request_id propagé via contextvars)
- **Hiérarchisé** (par module : `auth`, `jobs`, `statistics`, etc.)
- **Configurable** (JSON output pour la production, human-readable pour le dev)

Le middleware de timing ajoute `X-Process-Time-Ms` à chaque réponse, ce qui permet un monitoring basique des performances.

### Faiblesses

- **Pas de métriques** : Aucune intégration Prometheus/StatsD pour le monitoring quantitatif
- **Pas d'alerting** : Le health check détecte les problèmes mais ne notifie personne
- **Pas de tracing distribué** : Si un jour l'application est décomposée en microservices, le tracing sera absent

**Classement** : 📈 Amélioration pour la production (pas prioritaire en développement)

---

## 4.8 Synthèse backend

| Composant               | Qualité | Action prioritaire                      |
| ----------------------- | ------- | --------------------------------------- |
| API REST (34 endpoints) | ★★★★☆   | Rate limiting sur calculs               |
| Services (3 services)   | ★★★★☆   | Paralléliser les engines                |
| Repositories (7 + base) | ★★★☆☆   | Corriger count(), ajouter index         |
| Scheduler (8 jobs)      | ★★★★☆   | Timezone, chaînage explicite            |
| Runner + retry          | ★★★★☆   | Ajouter timeout                         |
| Scrapers                | ★★★★☆   | Externaliser URLs, factoriser           |
| Auth                    | ★★★★☆   | Password complexity, rate limit refresh |
| Logging                 | ★★★★☆   | Métriques pour production               |

Le backend est **la partie la plus mature du projet**. Les corrections identifiées sont ciblées et ne remettent pas en cause l'architecture globale. Le bug de résolution `game_config` reste le problème critique numéro un à adresser.
