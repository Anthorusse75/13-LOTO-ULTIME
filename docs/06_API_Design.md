# 06 — API Design

> **Projet** : LOTO ULTIME  
> **Version** : 1.0  
> **Date** : 2026-03-27  
> **Références croisées** : [03_Backend](03_Architecture_Backend.md) · [04_Frontend](04_Architecture_Frontend.md) · [05_Modele](05_Modele_Donnees.md) · [12_Securite](12_Securite_et_Authentification.md)

---

## 1. Principes de Design

| Principe | Application |
|---|---|
| REST | Ressources nommées, verbes HTTP, codes retour standards |
| Versionnée | Préfixe `/api/v1/` |
| Auto-documentée | OpenAPI 3.1 (Swagger UI intégré FastAPI) |
| Paginée | Paramètres `skip` + `limit` sur les listes |
| Filtrée | Query parameters pour filtrage |
| Sécurisée | JWT Bearer token sur toutes les routes protégées |
| Cohérente | Réponses JSON uniformes, codes d'erreur normalisés |

---

## 2. Base URL

```
Development : http://localhost:8000/api/v1
Production  : https://api.loto-ultime.example/api/v1
```

Documentation interactive : `http://localhost:8000/docs` (Swagger UI)

---

## 3. Authentification

Toutes les routes (sauf `/auth/login` et `/auth/register`) requièrent un token JWT.

```
Authorization: Bearer <jwt_token>
```

→ Détails : [12_Securite_et_Authentification](12_Securite_et_Authentification.md)

---

## 4. Catalogue des Endpoints

### 4.1 Auth — `/api/v1/auth`

| Méthode | Endpoint | Description | Rôle min. |
|---|---|---|---|
| POST | `/auth/login` | Authentification, retourne JWT | Public |
| POST | `/auth/register` | Création compte (si autorisé) | Public/Admin |
| GET | `/auth/me` | Profil utilisateur courant | Tous |
| PUT | `/auth/me` | Mise à jour profil | Tous |
| POST | `/auth/refresh` | Renouvellement token | Tous |

#### POST `/auth/login`

```json
// Request
{
  "username": "admin",
  "password": "secret"
}

// Response 200
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "role": "ADMIN"
  }
}

// Response 401
{
  "detail": "Identifiants invalides"
}
```

---

### 4.2 Games — `/api/v1/games`

| Méthode | Endpoint | Description | Rôle min. |
|---|---|---|---|
| GET | `/games` | Liste des jeux disponibles | CONSULTATION |
| GET | `/games/{game_id}` | Détail d'un jeu | CONSULTATION |
| POST | `/games` | Créer un jeu | ADMIN |
| PUT | `/games/{game_id}` | Modifier un jeu | ADMIN |
| DELETE | `/games/{game_id}` | Désactiver un jeu | ADMIN |

#### GET `/games`

```json
// Response 200
[
  {
    "id": 1,
    "name": "Loto FDJ",
    "slug": "loto-fdj",
    "numbers_pool": 49,
    "numbers_drawn": 5,
    "min_number": 1,
    "max_number": 49,
    "stars_pool": 10,
    "stars_drawn": 1,
    "star_name": "numéro chance",
    "draw_frequency": "lun/mer/sam",
    "is_active": true
  },
  {
    "id": 2,
    "name": "EuroMillions",
    "slug": "euromillions",
    "numbers_pool": 50,
    "numbers_drawn": 5,
    "min_number": 1,
    "max_number": 50,
    "stars_pool": 12,
    "stars_drawn": 2,
    "star_name": "étoile",
    "draw_frequency": "mar/ven",
    "is_active": true
  }
]
```

---

### 4.3 Draws — `/api/v1/games/{game_id}/draws`

| Méthode | Endpoint | Description | Rôle min. |
|---|---|---|---|
| GET | `/games/{game_id}/draws` | Liste tirages (paginée) | CONSULTATION |
| GET | `/games/{game_id}/draws/latest` | Dernier tirage | CONSULTATION |
| GET | `/games/{game_id}/draws/{draw_id}` | Détail tirage | CONSULTATION |
| POST | `/games/{game_id}/draws` | Ajouter tirage manuellement | ADMIN |
| POST | `/games/{game_id}/draws/fetch` | Déclencher récupération | ADMIN |

#### GET `/games/{game_id}/draws`

Query params :
- `skip` (int, default 0)
- `limit` (int, default 50, max 200)
- `from_date` (date, optional)
- `to_date` (date, optional)

```json
// Response 200
{
  "items": [
    {
      "id": 1523,
      "game_id": 1,
      "draw_date": "2026-03-25",
      "draw_number": 2891,
      "numbers": [3, 12, 23, 34, 47],
      "stars": [7]
    }
  ],
  "total": 4200,
  "skip": 0,
  "limit": 50
}
```

---

### 4.4 Statistics — `/api/v1/games/{game_id}/statistics`

| Méthode | Endpoint | Description | Rôle min. |
|---|---|---|---|
| GET | `/games/{game_id}/statistics` | Statistiques courantes | CONSULTATION |
| GET | `/games/{game_id}/statistics/frequencies` | Fréquences détaillées | CONSULTATION |
| GET | `/games/{game_id}/statistics/gaps` | Retards détaillés | CONSULTATION |
| GET | `/games/{game_id}/statistics/cooccurrences` | Cooccurrences | CONSULTATION |
| GET | `/games/{game_id}/statistics/temporal` | Tendances temporelles | CONSULTATION |
| GET | `/games/{game_id}/statistics/bayesian` | Estimations bayésiennes | UTILISATEUR |
| GET | `/games/{game_id}/statistics/graph` | Métriques de graphe | UTILISATEUR |
| GET | `/games/{game_id}/statistics/distribution` | Distributions | CONSULTATION |
| POST | `/games/{game_id}/statistics/recompute` | Forcer recalcul | ADMIN |

#### GET `/games/{game_id}/statistics`

```json
// Response 200
{
  "game_id": 1,
  "computed_at": "2026-03-27T10:30:00Z",
  "draw_count": 4200,
  "frequencies": [
    {"number": 7, "count": 580, "relative_frequency": 0.138, "last_seen": 1},
    {"number": 3, "count": 565, "relative_frequency": 0.134, "last_seen": 0}
  ],
  "gaps": [
    {"number": 41, "current_gap": 23, "max_gap": 45, "avg_gap": 9.5, "min_gap": 1}
  ],
  "hot_numbers": [3, 7, 12, 23, 34],
  "cold_numbers": [41, 44, 48],
  "distribution_entropy": 5.61,
  "uniformity_score": 0.94
}
```

#### GET `/games/{game_id}/statistics/cooccurrences`

Query params :
- `top_n` (int, default 50) — Nombre de paires à retourner
- `type` (string, "pairs" | "triplets", default "pairs")

```json
// Response 200
{
  "type": "pairs",
  "items": [
    {"pair": [7, 23], "count": 89, "expected": 42.3, "affinity": 2.104},
    {"pair": [3, 12], "count": 75, "expected": 42.3, "affinity": 1.773}
  ]
}
```

#### GET `/games/{game_id}/statistics/graph`

```json
// Response 200
{
  "nodes": [
    {"id": 1, "degree_centrality": 0.85, "betweenness": 0.12, "community": 0},
    {"id": 2, "degree_centrality": 0.72, "betweenness": 0.08, "community": 1}
  ],
  "edges": [
    {"source": 1, "target": 7, "weight": 89},
    {"source": 1, "target": 12, "weight": 75}
  ],
  "communities": [[1, 3, 7, 12], [5, 8, 15, 34]],
  "graph_density": 0.42,
  "clustering_coefficient": 0.67
}
```

---

### 4.5 Grids — `/api/v1/games/{game_id}/grids`

| Méthode | Endpoint | Description | Rôle min. |
|---|---|---|---|
| GET | `/games/{game_id}/grids/top` | Top N grilles | UTILISATEUR |
| POST | `/games/{game_id}/grids/generate` | Générer nouvelles grilles | UTILISATEUR |
| POST | `/games/{game_id}/grids/score` | Scorer une grille donnée | UTILISATEUR |
| GET | `/games/{game_id}/grids/{grid_id}` | Détail grille + scoring | UTILISATEUR |

#### GET `/games/{game_id}/grids/top`

Query params :
- `limit` (int, default 10, max 100)
- `method` (string, optional) — Filtrer par méthode

```json
// Response 200
[
  {
    "id": 42,
    "numbers": [3, 7, 23, 34, 45],
    "stars": [7],
    "total_score": 0.847,
    "score_breakdown": {
      "frequency": 0.82,
      "gap": 0.71,
      "cooccurrence": 0.65,
      "structure": 0.78,
      "balance": 0.90,
      "pattern_penalty": -0.05
    },
    "rank": 1,
    "method": "genetic_algorithm",
    "computed_at": "2026-03-27T10:30:00Z"
  }
]
```

#### POST `/games/{game_id}/grids/generate`

```json
// Request
{
  "count": 10,
  "method": "auto",
  "weights": {
    "frequency": 1.0,
    "gap": 0.8,
    "cooccurrence": 0.6,
    "structure": 0.5,
    "balance": 0.7,
    "pattern_penalty": 0.3
  }
}

// Response 200
{
  "grids": [ /* liste de GridResponse */ ],
  "computation_time_ms": 2340,
  "method_used": "genetic_algorithm",
  "generations": 500
}
```

#### POST `/games/{game_id}/grids/score`

```json
// Request
{
  "numbers": [5, 12, 23, 34, 47],
  "stars": [3]
}

// Response 200
{
  "numbers": [5, 12, 23, 34, 47],
  "stars": [3],
  "total_score": 0.723,
  "score_breakdown": {
    "frequency": 0.75,
    "gap": 0.68,
    "cooccurrence": 0.55,
    "structure": 0.82,
    "balance": 0.85,
    "pattern_penalty": -0.02
  },
  "percentile": 72.3,
  "explanation": {
    "frequency": "3 numéros dans le top 30% fréquence",
    "gap": "Le numéro 47 a un retard de 15 tirages",
    "cooccurrence": "La paire 12-34 a une affinité de 1.4",
    "structure": "Bonne répartition pair/impair (3/2)",
    "balance": "Distribution uniforme dans les décades",
    "pattern_penalty": "Motif 5-12 (écart constant -7) légèrement pénalisé"
  }
}
```

---

### 4.6 Portfolios — `/api/v1/games/{game_id}/portfolios`

| Méthode | Endpoint | Description | Rôle min. |
|---|---|---|---|
| GET | `/games/{game_id}/portfolios` | Liste des portefeuilles | UTILISATEUR |
| GET | `/games/{game_id}/portfolios/{id}` | Détail portefeuille | UTILISATEUR |
| POST | `/games/{game_id}/portfolios/generate` | Générer portefeuille optimisé | UTILISATEUR |
| DELETE | `/games/{game_id}/portfolios/{id}` | Supprimer portefeuille | ADMIN |

#### POST `/games/{game_id}/portfolios/generate`

```json
// Request
{
  "grid_count": 10,
  "strategy": "balanced"
}

// Response 200
{
  "id": 5,
  "name": "balanced_20260327_1030",
  "strategy": "balanced",
  "grid_count": 10,
  "grids": [
    {"numbers": [3, 7, 23, 34, 45], "stars": [7], "score": 0.847},
    {"numbers": [5, 12, 28, 36, 49], "stars": [3], "score": 0.812}
  ],
  "diversity_score": 0.92,
  "coverage_score": 0.78,
  "avg_grid_score": 0.81,
  "min_hamming_distance": 3.0,
  "computed_at": "2026-03-27T10:35:00Z"
}
```

---

### 4.7 Simulation — `/api/v1/games/{game_id}/simulation`

| Méthode | Endpoint | Description | Rôle min. |
|---|---|---|---|
| POST | `/games/{game_id}/simulation/monte-carlo` | Lancer simulation MC | UTILISATEUR |
| GET | `/games/{game_id}/simulation/{sim_id}` | Résultats simulation | UTILISATEUR |

#### POST `/games/{game_id}/simulation/monte-carlo`

```json
// Request
{
  "grids": [
    {"numbers": [3, 7, 23, 34, 45], "stars": [7]}
  ],
  "num_simulations": 10000,
  "seed": 42
}

// Response 200
{
  "simulation_id": "mc_20260327_103500",
  "num_simulations": 10000,
  "seed": 42,
  "results": [
    {
      "grid": {"numbers": [3, 7, 23, 34, 45], "stars": [7]},
      "avg_matches": 1.23,
      "match_distribution": {
        "0": 3245,
        "1": 4012,
        "2": 2100,
        "3": 540,
        "4": 95,
        "5": 8
      },
      "star_match_distribution": {"0": 9100, "1": 900},
      "stability_score": 0.87,
      "expected_value_ratio": 0.45
    }
  ],
  "computation_time_ms": 1560
}
```

---

### 4.8 Jobs — `/api/v1/jobs`

| Méthode | Endpoint | Description | Rôle min. |
|---|---|---|---|
| GET | `/jobs` | Liste des exécutions de jobs | ADMIN |
| GET | `/jobs/{job_id}` | Détail exécution | ADMIN |
| POST | `/jobs/{job_name}/trigger` | Déclencher job manuellement | ADMIN |
| POST | `/jobs/{job_id}/cancel` | Annuler job en cours | ADMIN |
| GET | `/jobs/schedule` | Planning des jobs | ADMIN |

---

### 4.9 Admin — `/api/v1/admin`

| Méthode | Endpoint | Description | Rôle min. |
|---|---|---|---|
| GET | `/admin/users` | Liste utilisateurs | ADMIN |
| POST | `/admin/users` | Créer utilisateur | ADMIN |
| PUT | `/admin/users/{id}` | Modifier utilisateur | ADMIN |
| DELETE | `/admin/users/{id}` | Désactiver utilisateur | ADMIN |
| GET | `/admin/system/health` | Health check | ADMIN |
| GET | `/admin/system/metrics` | Métriques système | ADMIN |

---

## 5. Réponses d'Erreur Standard

```json
// 400 - Validation
{
  "detail": [
    {
      "loc": ["body", "numbers"],
      "msg": "La grille doit contenir exactement 5 numéros",
      "type": "value_error"
    }
  ]
}

// 401 - Non authentifié
{
  "detail": "Token manquant ou invalide"
}

// 403 - Non autorisé
{
  "detail": "Accès réservé aux administrateurs"
}

// 404 - Non trouvé
{
  "detail": "Jeu non trouvé : id=99"
}

// 409 - Conflit
{
  "detail": "Ce tirage existe déjà pour cette date"
}

// 429 - Rate limited
{
  "detail": "Trop de requêtes. Réessayez dans 30 secondes."
}

// 500 - Erreur interne
{
  "detail": "Erreur interne du serveur",
  "request_id": "req_abc123"
}
```

---

## 6. Pagination Standard

Toutes les listes paginées utilisent le format :

```json
{
  "items": [ /* ... */ ],
  "total": 4200,
  "skip": 0,
  "limit": 50,
  "has_more": true
}
```

---

## 7. Références

| Document | Contenu |
|---|---|
| [03_Architecture_Backend](03_Architecture_Backend.md) | Implémentation routers |
| [04_Architecture_Frontend](04_Architecture_Frontend.md) | Consommation API |
| [05_Modele_Donnees](05_Modele_Donnees.md) | Schémas Pydantic |
| [12_Securite_et_Authentification](12_Securite_et_Authentification.md) | JWT, RBAC |

---

*Fin du document 06_API_Design.md*
