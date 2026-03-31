# 18 — Impacts API

> Analyse complète des impacts de toutes les évolutions sur l'API : endpoints, schemas, validation, compatibilité, versioning.

---

## Références croisées

- [00_Index_Evolutions](./00_Index_Evolutions.md)
- [06_Evolutions_Fonctionnelles](./06_Evolutions_Fonctionnelles.md) — Pagination, export
- [16_Impacts_Backend](./16_Impacts_Backend.md)
- [21_Impacts_Securite_Roles](./21_Impacts_Securite_Roles.md) — Rate limiting, RBAC
- [22_Impacts_Performance_Scalabilite](./22_Impacts_Performance_Scalabilite.md)

---

## 1. État actuel de l'API

### Routers existants (9)

| Router        | Préfixe               | Endpoints | Auth    |
| ------------- | --------------------- | --------- | ------- |
| `auth`        | `/api/v1/auth`        | 6         | Partiel |
| `games`       | `/api/v1/games`       | 2         | Non     |
| `draws`       | `/api/v1/draws`       | 2         | Non     |
| `grids`       | `/api/v1/grids`       | 9         | Non     |
| `statistics`  | `/api/v1/statistics`  | 9         | Non     |
| `simulations` | `/api/v1/simulations` | 4         | Non     |
| `portfolios`  | `/api/v1/portfolios`  | 2         | Non     |
| `jobs`        | `/api/v1/jobs`        | 4         | Admin   |
| `database`    | `/api/v1/database`    | 2         | Admin   |
| `health`      | `/health`             | 1         | Non     |

**Total : 41 endpoints**

---

## 2. Nouveaux routers et endpoints

### Router wheeling (doc 08) — 6 endpoints

| Méthode | Route                          | Détail                                               | Auth      |
| ------- | ------------------------------ | ---------------------------------------------------- | --------- |
| POST    | `/api/v1/wheeling/preview`     | Aperçu avant génération (grid_count, cost, coverage) | Optionnel |
| POST    | `/api/v1/wheeling/generate`    | Génération complète du système réduit                | Optionnel |
| GET     | `/api/v1/wheeling/history`     | Liste systèmes générés (user)                        | Requis    |
| GET     | `/api/v1/wheeling/{id}`        | Détail d'un système                                  | Requis    |
| DELETE  | `/api/v1/wheeling/{id}`        | Supprimer un système                                 | Requis    |
| GET     | `/api/v1/wheeling/{id}/export` | Export PDF/CSV                                       | Requis    |

### Router budget (doc 09) — 4 endpoints

| Méthode | Route                       | Détail                             | Auth      |
| ------- | --------------------------- | ---------------------------------- | --------- |
| POST    | `/api/v1/budget/optimize`   | Optimisation budget → 3 stratégies | Optionnel |
| GET     | `/api/v1/budget/plans`      | Liste plans sauvegardés            | Requis    |
| GET     | `/api/v1/budget/plans/{id}` | Détail d'un plan                   | Requis    |
| DELETE  | `/api/v1/budget/plans/{id}` | Supprimer un plan                  | Requis    |

### Router comparison (doc 10) — 1 endpoint

| Méthode | Route                        | Détail                               | Auth |
| ------- | ---------------------------- | ------------------------------------ | ---- |
| POST    | `/api/v1/comparison/compare` | Comparaison N stratégies (stateless) | Non  |

### Router history (doc 11) — 8 endpoints

| Méthode | Route                            | Détail                                             | Auth   |
| ------- | -------------------------------- | -------------------------------------------------- | ------ |
| POST    | `/api/v1/history/save`           | Sauvegarder un résultat                            | Requis |
| GET     | `/api/v1/history`                | Liste résultats sauvegardés (paginated, filtrable) | Requis |
| GET     | `/api/v1/history/{id}`           | Détail d'un résultat                               | Requis |
| POST    | `/api/v1/history/{id}/duplicate` | Dupliquer un résultat                              | Requis |
| DELETE  | `/api/v1/history/{id}`           | Supprimer un résultat                              | Requis |
| PATCH   | `/api/v1/history/{id}/favorite`  | Toggle favori                                      | Requis |
| PATCH   | `/api/v1/history/{id}/tags`      | Modifier tags                                      | Requis |
| POST    | `/api/v1/history/{id}/export`    | Export PDF/CSV/JSON                                | Requis |

### Router notifications (doc 15) — 4 endpoints

| Méthode | Route                                | Détail                          | Auth   |
| ------- | ------------------------------------ | ------------------------------- | ------ |
| GET     | `/api/v1/notifications`              | Liste notifications (paginated) | Requis |
| PATCH   | `/api/v1/notifications/{id}/read`    | Marquer comme lue               | Requis |
| POST    | `/api/v1/notifications/read-all`     | Tout marquer comme lu           | Requis |
| GET     | `/api/v1/notifications/unread-count` | Nombre non lues                 | Requis |

### Router suggestion (doc 15) — 1 endpoint

| Méthode | Route                       | Détail                           | Auth      |
| ------- | --------------------------- | -------------------------------- | --------- |
| GET     | `/api/v1/suggestions/daily` | Suggestion du jour (par game_id) | Optionnel |

---

## 3. Endpoints existants modifiés

### Grids (doc 03, 06, 11, 12)

| Endpoint                            | Modification                                                                                             |
| ----------------------------------- | -------------------------------------------------------------------------------------------------------- |
| `POST /api/v1/grids/generate`       | +paramètre `profile` (BUG-03 fix), +`game_id` obligatoire (BUG-01), +retour `explanation` (L1) optionnel |
| `GET /api/v1/grids`                 | +pagination `limit/offset` (DT-05), +filtre `game_id`                                                    |
| `PATCH /api/v1/grids/{id}/favorite` | Vérifier user_id si authentifié                                                                          |
| `PATCH /api/v1/grids/{id}/played`   | Vérifier user_id si authentifié                                                                          |

### Statistics (doc 06)

| Endpoint                             | Modification                                                          |
| ------------------------------------ | --------------------------------------------------------------------- |
| `GET /api/v1/statistics/frequencies` | +paramètre `game_id` obligatoire, +retour `star_frequencies` séparées |
| `GET /api/v1/statistics/gaps`        | +paramètre `game_id`, +retour `star_gaps`                             |
| Tous les endpoints statistics        | +`game_id` filtering (BUG-01)                                         |

### Draws (doc 06)

| Endpoint            | Modification                                          |
| ------------------- | ----------------------------------------------------- |
| `GET /api/v1/draws` | +pagination `limit/offset` (DT-05), +filtre `game_id` |

### Simulations (doc 12)

| Endpoint                               | Modification                         |
| -------------------------------------- | ------------------------------------ |
| `POST /api/v1/simulations/monte-carlo` | +retour `explanation` (L1) optionnel |
| `POST /api/v1/simulations/robustness`  | +retour `explanation` (L1) optionnel |

### Portfolios (doc 12)

| Endpoint                           | Modification                         |
| ---------------------------------- | ------------------------------------ |
| `POST /api/v1/portfolios/optimize` | +retour `explanation` (L1) optionnel |

---

## 4. Schemas Pydantic

### Nouveaux schemas

| Schema                     | Champs principaux                                                                | Doc |
| -------------------------- | -------------------------------------------------------------------------------- | --- |
| `WheelingPreviewRequest`   | game_id, selected_numbers, selected_stars?, guarantee_level                      | 08  |
| `WheelingPreviewResponse`  | grid_count, total_cost, coverage_rate, reduction_rate                            | 08  |
| `WheelingGenerateRequest`  | game_id, selected_numbers, selected_stars?, guarantee_level                      | 08  |
| `WheelingGenerateResponse` | id, grids, grid_count, total_cost, coverage_rate, reduction_rate, gain_scenarios | 08  |
| `BudgetOptimizeRequest`    | game_id, budget, objective, selected_numbers?                                    | 09  |
| `BudgetOptimizeResponse`   | recommendations[3], pareto_front                                                 | 09  |
| `BudgetRecommendation`     | strategy, grids, total_cost, expected_coverage, expected_score                   | 09  |
| `ComparisonRequest`        | game_id, strategies[{type, params}]                                              | 10  |
| `ComparisonResponse`       | results[{strategy, scores_per_axis}], summary                                    | 10  |
| `SaveResultRequest`        | type, parameters, result_data, tags?                                             | 11  |
| `SavedResultResponse`      | id, type, parameters, result_data, is_favorite, tags, created_at                 | 11  |
| `SavedResultListResponse`  | items[], total, page, page_size                                                  | 11  |
| `NotificationResponse`     | id, type, title, message, data, is_read, created_at                              | 15  |
| `NotificationListResponse` | items[], unread_count                                                            | 15  |
| `DailySuggestionResponse`  | grid, score, explanation                                                         | 15  |
| `Explanation`              | summary, interpretation?, technical?, highlights?, warnings?                     | 12  |

### Schemas modifiés

| Schema                | Modification                                                |
| --------------------- | ----------------------------------------------------------- |
| `GridGenerateRequest` | +`profile: str                                              | None` |
| `GridResponse`        | +`explanation: Explanation                                  | None` |
| `SimulationResponse`  | +`explanation: Explanation                                  | None` |
| `PortfolioResponse`   | +`explanation: Explanation                                  | None` |
| `PaginationParams`    | Nouveau schema partagé : `limit: int = 50, offset: int = 0` |

---

## 5. Pagination standardisée (DT-05)

### Pattern de pagination

```python
class PaginationParams(BaseModel):
    limit: int = Field(default=50, ge=1, le=200)
    offset: int = Field(default=0, ge=0)

class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    limit: int
    offset: int
    has_more: bool
```

### Endpoints à paginer

| Endpoint              | Actuellement | Après                |
| --------------------- | ------------ | -------------------- |
| GET /draws            | Tous         | Paginé               |
| GET /grids            | Tous         | Paginé               |
| GET /statistics       | N/A          | Déjà OK (1 snapshot) |
| GET /history          | N/A          | Paginé dès création  |
| GET /wheeling/history | N/A          | Paginé dès création  |
| GET /notifications    | N/A          | Paginé dès création  |

---

## 6. Validation renforcée

### Règles de validation par endpoint

| Endpoint           | Validation                                                                          |
| ------------------ | ----------------------------------------------------------------------------------- |
| wheeling/preview   | `len(selected_numbers) in [6..20]`, `guarantee_level in [2..k-1]`, `game_id` valide |
| wheeling/generate  | Idem preview + confirmation                                                         |
| budget/optimize    | `budget >= grid_price`, `budget <= 500` (config), `game_id` valide                  |
| comparison/compare | `len(strategies) in [2..5]`, types valides                                          |
| history/save       | `type in SaveableTypes`, `result_data` non vide                                     |

### game_id validation (BUG-01 fix)

Tous les endpoints recevant un `game_id` doivent :
1. Valider que le game_id existe dans GameDefinition
2. Utiliser la configuration du jeu (main_numbers_count, max_main_number, etc.)
3. Adapter les engines en conséquence

---

## 7. Gestion des erreurs

### Codes d'erreur normalisés

| Code HTTP | Usage                                             |
| --------- | ------------------------------------------------- |
| 400       | Paramètres invalides (budget < prix grille, etc.) |
| 401       | Non authentifié (endpoints auth requise)          |
| 403       | Accès refusé (résultat d'un autre user)           |
| 404       | Ressource non trouvée                             |
| 409       | Conflit (doublon sauvegarde)                      |
| 422       | Validation échouée (Pydantic)                     |
| 429       | Rate limit dépassé                                |
| 500       | Erreur serveur                                    |
| 504       | Timeout (calcul wheeling trop long)               |

### Format d'erreur standard

```json
{
  "detail": {
    "code": "WHEELING_TOO_MANY_NUMBERS",
    "message": "Le nombre de numéros sélectionnés dépasse la limite de 20.",
    "field": "selected_numbers"
  }
}
```

---

## 8. Rate limiting (DT-04)

| Catégorie       | Limite  | Endpoints                                                              |
| --------------- | ------- | ---------------------------------------------------------------------- |
| Lecture légère  | 100/min | GET draws, statistics, grids (list)                                    |
| Lecture lourde  | 30/min  | GET wheeling/detail, budget/detail                                     |
| Écriture légère | 30/min  | POST history/save, PATCH favorite                                      |
| Calcul intensif | 10/min  | POST grids/generate, wheeling/generate, budget/optimize, simulations/* |
| Comparaison     | 20/min  | POST comparison/compare                                                |
| Auth            | 5/min   | POST login, register                                                   |

---

## 9. Compatibilité et versioning

### Stratégie

- **Pas de breaking changes** sur les endpoints existants
- Les nouveaux champs dans les réponses sont toujours **optionnels** (`explanation: Explanation | None`)
- Les nouveaux paramètres dans les requêtes ont des **valeurs par défaut**
- Préfixe `/api/v1/` conservé pour tous les endpoints

### Migration graduelle

1. Phase P0 : Les endpoints existants fonctionnent sans changement
2. Phase A : game_id ajouté avec valeur par défaut (Loto FDJ = game_id=1)
3. Phase B : Nouveaux endpoints ajoutés sans impact sur l'existant
4. Phase C–D : explanation ajouté en retour optionnel

---

## 10. Documentation OpenAPI

### Actions

- Enrichir les docstrings FastAPI pour chaque endpoint
- Ajouter des exemples dans les schemas Pydantic (`model_config = {"json_schema_extra": {"examples": [...]}}`)
- Grouper les endpoints par tags dans OpenAPI

### Tags recommandés

```python
tags = [
    {"name": "auth", "description": "Authentification et gestion des utilisateurs"},
    {"name": "games", "description": "Configuration des loteries"},
    {"name": "draws", "description": "Tirages historiques"},
    {"name": "grids", "description": "Génération et scoring de grilles"},
    {"name": "statistics", "description": "Statistiques et analyses"},
    {"name": "simulations", "description": "Simulations Monte Carlo et robustesse"},
    {"name": "portfolios", "description": "Optimisation de portefeuille"},
    {"name": "wheeling", "description": "Systèmes réduits (covering designs)"},
    {"name": "budget", "description": "Optimisation budget"},
    {"name": "comparison", "description": "Comparaison de stratégies"},
    {"name": "history", "description": "Historique et favoris"},
    {"name": "notifications", "description": "Notifications utilisateur"},
    {"name": "suggestions", "description": "Suggestions quotidiennes"},
    {"name": "admin", "description": "Administration"},
]
```

---

## 11. Résumé quantitatif

| Métrique         | Avant         | Après         | Delta |
| ---------------- | ------------- | ------------- | ----- |
| Routers          | 9             | 14            | +5    |
| Endpoints        | 41            | 65            | +24   |
| Schemas Pydantic | ~30           | ~46           | +16   |
| Auth requis      | ~10 endpoints | ~30 endpoints | +20   |
| Rate limited     | 0             | 65            | +65   |

---

## 12. Checklist locale

- [ ] Créer router wheeling (6 endpoints)
- [ ] Créer router budget (4 endpoints)
- [ ] Créer router comparison (1 endpoint)
- [ ] Créer router history (8 endpoints)
- [ ] Créer router notifications (4 endpoints)
- [ ] Créer router suggestions (1 endpoint)
- [ ] Créer 16 nouveaux schemas Pydantic
- [ ] Modifier schemas existants (explanation optionnel)
- [ ] Implémenter PaginationParams + PaginatedResponse
- [ ] Paginer endpoints GET draws, grids
- [ ] Fix BUG-01 : game_id obligatoire partout
- [ ] Fix BUG-03 : accepter profile dans grids/generate
- [ ] Ajouter validation renforcée sur nouveaux endpoints
- [ ] Implémenter rate limiting avec slowapi
- [ ] Normaliser les codes d'erreur
- [ ] Enrichir documentation OpenAPI (tags, exemples)
- [ ] Tests API pour les 24 nouveaux endpoints

Réf. : [27_Checklist_Globale_Evolutions](./27_Checklist_Globale_Evolutions.md)
