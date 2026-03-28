# 3. Analyse Détaillée de l'Architecture

## 3.1 Vue d'ensemble

L'architecture de LOTO ULTIME suit un pattern **layered architecture** classique, adapté à une application web analytique avec un backend Python/FastAPI et un frontend React/TypeScript. Cette approche est le bon choix pour ce type de projet : suffisamment structurée pour maintenir la séparation des responsabilités, suffisamment simple pour ne pas ajouter de complexité inutile.

```
┌─────────────────────────────────────────────────┐
│                   Frontend                       │
│   React 18 + TypeScript + Tailwind v4           │  Port 5173
│   TanStack Query v5 + Zustand + Axios           │
└─────────────────────┬───────────────────────────┘
                      │ HTTP/JSON (CORS)
┌─────────────────────▼───────────────────────────┐
│              API REST (FastAPI)                   │
│   34 endpoints, JWT auth, rate limiting          │  Port 8000
├──────────────────────────────────────────────────┤
│              Services (logique métier)            │
│   StatisticsService, GridService, SimService     │
├──────────────────────────────────────────────────┤
│              Repositories (accès données)         │
│   Generic BaseRepository<T>, 7 repositories      │
├──────────────────────────────────────────────────┤
│              Engines (calculs)                    │
│   7 stats + 6 scoring + 5 optim + 2 simulation  │
├──────────────────────────────────────────────────┤
│              Models (SQLAlchemy ORM)              │
│   User, Draw, GameDefinition, ScoredGrid, etc.  │
├──────────────────────────────────────────────────┤
│              Database (SQLite + aiosqlite)        │
│   loto_ultime.db                                 │
└──────────────────────────────────────────────────┘
```

---

## 3.2 Points forts de l'architecture

### Séparation des responsabilités bien exécutée

Chaque couche a un rôle clair et ne déborde pas sur les autres :

- **Routes API** : Décodent la requête HTTP, délèguent au service, formatent la réponse. Elles ne contiennent aucune logique métier.
- **Services** : Orchestrent les interactions entre repositories et engines. Un service peut appeler plusieurs repositories et plusieurs engines pour produire un résultat.
- **Repositories** : Encapsulent les requêtes SQLAlchemy. Aucune logique métier, uniquement du CRUD et des requêtes spécialisées.
- **Engines** : Fonctions pures (ou quasi-pures) qui reçoivent des données en entrée et produisent des résultats en sortie. Pas de dépendance à la base de données.

Cette séparation est essentielle parce qu'elle rend chaque couche **testable indépendamment**. Les engines peuvent être testés avec des matrices numpy synthétiques, les services peuvent être testés avec des mocks de repositories, et les routes peuvent être testées avec des clients HTTP.

### Asynchronisme de bout en bout

L'utilisation de `aiosqlite` comme driver, d'`AsyncSession` pour la couche ORM, de `httpx.AsyncClient` pour les requêtes HTTP externes et d'`AsyncIOScheduler` pour le scheduling crée un pipeline entièrement non-bloquant. C'est un investissement technique significatif qui :

- Permet à FastAPI de servir d'autres requêtes pendant qu'une requête attend la base de données ou un appel HTTP
- Prépare l'application à gérer un nombre raisonnable de requêtes concurrentes
- Évite les problèmes de threading qui sont fréquents avec SQLite

### Configuration centralisée et typée

L'utilisation de `pydantic-settings` pour la configuration est un excellent choix :

```python
class Settings(BaseSettings):
    SECRET_KEY: str = Field(..., min_length=32)  # Validation automatique
    JWT_EXPIRATION_MINUTES: int = 60              # Type-safe
    CORS_ORIGINS: list[str] = ["http://localhost:5173"]  # Listes supportées
```

Chaque paramètre est typé, validé et documentable. Le pattern `env_file` permet de charger un `.env` tout en supportant les variables d'environnement système pour le déploiement.

### Hiérarchie d'exceptions métier

La création d'exceptions spécifiques au domaine (`GameNotFoundError`, `DrawAlreadyExistsError`, `InsufficientDataError`, etc.) mappées à des codes HTTP dans `main.py` est un pattern mature :

```python
@app.exception_handler(GameNotFoundError)
async def game_not_found_handler(request, exc):
    return JSONResponse(status_code=404, content={"detail": str(exc)})
```

Cela évite les `raise HTTPException` dispersés dans le code métier et centralise le mapping erreur → HTTP.

---

## 3.3 Points faibles et risques architecturaux

### 3.3.1 🔧 Résolution de configuration jeu — BUG CRITIQUE

**Constat** : La fonction `_get_game_config()` utilisée dans les routes `grids.py`, `portfolios.py` et `simulations.py` itère sur les configurations de jeux et retourne **la première trouvée**, sans jamais vérifier le `game_id` passé en paramètre d'URL.

```python
def _get_game_config(game_id: int):
    configs = list(_game_configs.values())
    for cfg in configs:
        return cfg  # ← RETOURNE TOUJOURS LE PREMIER
    raise HTTPException(status_code=404, detail="Game not found")
```

**Impact** : Toutes les opérations de grille, portefeuille et simulation utilisent systématiquement la configuration du Loto FDJ, même quand l'URL contient `/games/2/grids/generate` (EuroMillions). Le pool de numéros (1-49 vs 1-50), le nombre d'étoiles (1 vs 2) et les règles sont incorrects.

**Classement** : 🔧 Correction critique — le bug invalide le support multi-loteries.

**Correction attendue** : Charger les configs indexées par `game_id` (pas par slug), ou résoudre via un repository lookup dans chaque route.

### 3.3.2 ⚠️ Absence de couche DTO explicite

Les routes API retournent directement les modèles ORM (ou des dicts) sans passer par des schémas Pydantic de réponse dédiés. Par exemple, `StatisticsSnapshot` est retourné tel quel depuis le repository.

**Pourquoi c'est un problème** :
- Si le modèle ORM évolue (ajout de colonnes internes), les réponses API changent automatiquement, potentiellement en cassant les clients
- Les champs internes (IDs séquentiels, timestamps internes) sont exposés sans filtrage
- La documentation OpenAPI/Swagger reflète la structure ORM, pas le contrat API

**Classement** : 📈 Amélioration — pas critique aujourd'hui avec un seul client frontend, mais nécessaire avant toute ouverture de l'API à des tiers.

### 3.3.3 ⚠️ Absence de couche d'offloading pour les calculs lourds

Les opérations de calcul intensif (statistiques complètes, génération de 10 grilles optimisées, simulation de 10 000 Monte Carlo) s'exécutent **sur le thread principal d'asyncio**. Bien que les engines soient synchrones (calculs numpy/scipy), ils bloquent la boucle d'événements pendant leur exécution.

**Pourquoi c'est un problème** :
- Un seul utilisateur peut lancer un `/statistics/recompute` qui bloque le serveur pendant 10-30 secondes
- Pendant ce temps, aucune autre requête n'est traitée
- Le health check peut timeout et le scheduler peut manquer un trigger

**Solution recommandée** :
- À court terme : Utiliser `asyncio.to_thread()` ou `run_in_executor()` pour les calculs CPU-bound
- À moyen terme : Migrer vers Celery ou ARQ pour les tâches lourdes avec file d'attente
- À long terme : Séparer les workers de calcul du serveur API

**Classement** : 📈 Amélioration importante — pas bloquant avec un seul utilisateur, critique dès que plusieurs utilisateurs concurrents.

### 3.3.4 ⚠️ Gestion des sessions ORM inconsistante

Le pattern de gestion de session utilisé dans les jobs est atypique :

```python
async for session in get_session():
    # ... travail ...
    await session.commit()
    break  # ← Sort de la boucle après le premier tour
```

Ce `async for ... break` est un contournement pour utiliser le générateur asynchrone `get_session()` en dehors du contexte FastAPI `Depends`. Il fonctionne mais :
- Il n'est pas idiomatique
- Le `break` masque l'intention
- Si le commit échoue, la session n'est pas correctement fermée

**Solution** : Créer un context manager explicite `async with get_managed_session() as session:` pour les usages hors-API.

**Classement** : 📈 Amélioration — pas de bug avéré mais fragilité structurelle.

### 3.3.5 ⚠️ Pas de migration de schéma

Le projet n'utilise pas Alembic (ou un outil équivalent) pour les migrations de base de données. Le schéma est créé par `Base.metadata.create_all()` au démarrage. Cela signifie que :
- Toute modification de modèle nécessite de supprimer et recréer la base
- L'historique des tirages (1642 entrées) est perdu à chaque changement de schéma
- En production, les évolutions de modèle sont impossibles sans downtime et perte de données

**Classement** : 📈 Amélioration structurante — indispensable avant toute mise en production.

---

## 3.4 Architecture frontend

### Structure des composants

```
src/
├── pages/           8 pages (Dashboard, Draws, Statistics, Grids, Portfolio, Simulation, Admin, Login)
├── components/
│   ├── auth/        RequireAuth, RequireRole
│   ├── common/      LoadingSpinner, ErrorBoundary, DrawBalls, ScoreBar, NumberHeatmap, StatusBadge, Disclaimer
│   ├── draws/       (vide ou minimal)
│   ├── grids/       (vide ou minimal)
│   ├── layout/      Header, Sidebar
│   └── statistics/  FrequencyTab, GapTab, CooccurrenceTab, DistributionTab, BayesianTab, GraphTab, TemporalTab
├── hooks/           useAuth, useDraws, useGames, useGlobalStats, useGrids, useJobs, usePortfolio, useSimulation, useStatistics
├── services/        api.ts, authService.ts
├── stores/          authStore.ts, settingsStore.ts
├── types/           api.ts (types centralisés)
└── utils/           (minimal)
```

**Points forts** :
- Découpage clair pages/composants/hooks/services/stores
- Custom hooks avec TanStack Query pour le data fetching (cache automatique, refetch, invalidation)
- Zustand pour l'état global (léger, pas de boilerplate Redux)
- Typage TypeScript sur toute la surface

**Points faibles** :
- Composants de pages trop volumineux (AdminPage fait ~500 lignes avec 3 panels imbriqués)
- Pas de composants réutilisables pour les patterns récurrents (cards, tables, tabs)
- Pas de design system formel / storybook

**Classement** : 📈 Amélioration — le frontend est fonctionnel mais gagnerait en maintenabilité avec une extraction des composants composites.

---

## 3.5 Architecture des données

### Modèle relationnel

```
GameDefinition (id, name, slug, numbers_pool, stars_pool, ...)
    ├─ Draw (id, game_id FK, draw_date, numbers[], stars[])
    ├─ StatisticsSnapshot (id, game_id FK, computed_at, frequencies JSON, gaps JSON, ...)
    ├─ ScoredGrid (id, game_id FK, numbers[], total_score, score_breakdown JSON, ...)
    ├─ Portfolio (id, game_id FK, strategy, grids JSON, diversity_score, ...)
    └─ JobExecution (id, game_id FK nullable, job_name, status, ...)

User (id, username, email, hashed_password, role, is_active, last_login)
```

**Points forts** :
- Clé étrangère systématique vers `GameDefinition` pour le multi-loteries
- Colonnes JSON pour les données structurées complexes (scores, grilles, statistiques)
- Contrainte d'unicité sur `(game_id, draw_date)` pour éviter les doublons de tirages
- Enum SQLAlchemy pour `UserRole` et `JobStatus`

**Points faibles** :
- Pas d'index explicites sur les colonnes fréquemment filtrées (`game_id`, `draw_date`, `computed_at`)
- Le JSON opaque dans `StatisticsSnapshot` rend impossible les requêtes SQL sur les statistiques individuelles
- Pas de partition ou d'archivage automatique des vieux snapshots (le cleanup supprime après 30 jours mais sans archivage)

**Classement** : 📈 Amélioration — ajouter des index est rapide et impactant sur les performances.

---

## 3.6 Synthèse architecturale

| Aspect | Verdict | Action requise |
|--------|---------|----------------|
| Layered architecture | ✅ Solide | Aucune |
| Async de bout en bout | ✅ Bon choix | Aucune |
| Configuration typée | ✅ Excellente | Aucune |
| Exception hierarchy | ✅ Propre | Aucune |
| Game config resolution | 🔴 Bug critique | Corriger immédiatement |
| Couche DTO | ⚠️ Absente | Ajouter des schémas Pydantic response |
| Offloading calculs CPU | ⚠️ Manquant | `asyncio.to_thread()` minimum |
| Gestion sessions jobs | ⚠️ Fragile | Context manager dédié |
| Migrations DB | ⚠️ Absentes | Intégrer Alembic |
| Index DB | ⚠️ Manquants | Ajouter sur colonnes filtrées |
| Design system frontend | ⚠️ Absent | Extraire composants réutilisables |

L'architecture est une des forces du projet. Les corrections nécessaires sont ciblées et n'imposent pas de refactoring structurel. Le bug de résolution `game_config` est le seul point véritablement critique à résoudre en priorité.
