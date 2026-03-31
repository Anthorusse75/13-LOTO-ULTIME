# 21 — Impacts Sécurité / Rôles

> Analyse complète des impacts de toutes les évolutions sur la sécurité, l'authentification, les rôles, la validation, le rate limiting.

---

## Références croisées

- [00_Index_Evolutions](./00_Index_Evolutions.md)
- [12_Securite_et_Authentification](../12_Securite_et_Authentification.md) — Sécurité actuelle
- [03_Audit_Existant_et_Ecarts](./03_Audit_Existant_et_Ecarts.md) — DT-02 token blacklist, DT-04 rate limiting
- [18_Impacts_API](./18_Impacts_API.md) — Endpoints et rate limiting

---

## 1. État actuel de la sécurité

### Authentification

| Composant          | Implémentation                  |
| ------------------ | ------------------------------- |
| Système            | JWT (access + refresh tokens)   |
| Stockage tokens    | Côté client (localStorage)      |
| Blacklist          | En mémoire Python (set) — DT-02 |
| Expiration access  | 30 min                          |
| Expiration refresh | 7 jours                         |
| Hash passwords     | bcrypt                          |

### Rôles existants

| Rôle           | Permissions                                 |
| -------------- | ------------------------------------------- |
| `ADMIN`        | Tout (y compris /jobs, /database)           |
| `UTILISATEUR`  | Lecture + écriture (grilles, favoris, etc.) |
| `CONSULTATION` | Lecture seule                               |

### Endpoints protégés actuels

| Endpoint             | Protection                       |
| -------------------- | -------------------------------- |
| `/api/v1/auth/*`     | Partiel (login/register publics) |
| `/api/v1/jobs/*`     | Admin seulement                  |
| `/api/v1/database/*` | Admin seulement                  |
| Reste                | Ouvert (pas d'auth requise)      |

---

## 2. Impacts des évolutions sur la sécurité

### 2.1 — Endpoints nécessitant une authentification

**Nouvelle règle** : Tout endpoint qui écrit ou lit des données utilisateur personnelles nécessite l'authentification.

| Catégorie           | Endpoints                       | Auth requise                 |
| ------------------- | ------------------------------- | ---------------------------- |
| Wheeling génération | POST generate                   | Optionnel (anonyme possible) |
| Wheeling historique | GET history, GET detail, DELETE | **Requis**                   |
| Budget              | POST optimize                   | Optionnel                    |
| Budget historique   | GET plans, GET plan, DELETE     | **Requis**                   |
| Historique/Favoris  | Tous les 8 endpoints            | **Requis**                   |
| Notifications       | Tous les 4 endpoints            | **Requis**                   |
| Suggestions         | GET daily                       | Optionnel (enrichi si auth)  |
| Comparaison         | POST compare                    | Non (stateless)              |

### 2.2 — Propriété des ressources (ownership)

**Principe** : Un utilisateur ne peut accéder qu'à SES propres ressources.

```python
async def verify_ownership(
    resource_user_id: int | None,
    current_user: User,
) -> None:
    if resource_user_id is not None and resource_user_id != current_user.id:
        if current_user.role != UserRole.ADMIN:
            raise HTTPException(status_code=403, detail="Accès refusé")
```

**Endpoints impactés** :
- GET/DELETE wheeling/{id} → vérifier user_id
- GET/DELETE budget/plans/{id} → vérifier user_id
- GET/DELETE/PATCH history/{id} → vérifier user_id
- GET/PATCH notifications/{id} → vérifier user_id

### 2.3 — Matrice rôles × fonctionnalités

| Fonctionnalité       | ADMIN | UTILISATEUR | CONSULTATION | Anonyme       |
| -------------------- | ----- | ----------- | ------------ | ------------- |
| Lire tirages/stats   | ✅     | ✅           | ✅            | ✅             |
| Générer grilles      | ✅     | ✅           | ❌            | ✅ (limité)    |
| Wheeling preview     | ✅     | ✅           | ✅            | ✅             |
| Wheeling generate    | ✅     | ✅           | ❌            | ✅ (non sauvé) |
| Wheeling historique  | ✅     | ✅ (own)     | ❌            | ❌             |
| Budget optimize      | ✅     | ✅           | ❌            | ✅ (non sauvé) |
| Comparaison          | ✅     | ✅           | ✅            | ✅             |
| Sauvegarder résultat | ✅     | ✅           | ❌            | ❌             |
| Historique/Favoris   | ✅     | ✅ (own)     | ❌            | ❌             |
| Notifications        | ✅     | ✅ (own)     | ❌            | ❌             |
| Dashboard enrichi    | ✅     | ✅           | ✅            | Partiel       |
| Admin DB/Jobs        | ✅     | ❌           | ❌            | ❌             |

---

## 3. DT-02 : Migration token blacklist

### Problème actuel

```python
# Actuel : en mémoire, perdu au redémarrage
token_blacklist: set[str] = set()
```

### Solution : Table PostgreSQL

```sql
CREATE TABLE token_blacklist (
    id SERIAL PRIMARY KEY,
    jti VARCHAR(64) UNIQUE NOT NULL,    -- JWT ID
    expires_at TIMESTAMPTZ NOT NULL,     -- Expiration du token
    blacklisted_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_blacklist_jti ON token_blacklist(jti);
CREATE INDEX idx_blacklist_expires ON token_blacklist(expires_at);
```

### Service de blacklist

```python
class TokenBlacklistService:
    async def blacklist_token(self, db: AsyncSession, jti: str, expires_at: datetime):
        entry = TokenBlacklist(jti=jti, expires_at=expires_at)
        db.add(entry)
        await db.commit()
    
    async def is_blacklisted(self, db: AsyncSession, jti: str) -> bool:
        result = await db.execute(
            select(TokenBlacklist).where(TokenBlacklist.jti == jti)
        )
        return result.scalar_one_or_none() is not None
    
    async def cleanup_expired(self, db: AsyncSession):
        await db.execute(
            delete(TokenBlacklist).where(
                TokenBlacklist.expires_at < datetime.utcnow()
            )
        )
        await db.commit()
```

### Job de purge

Ajouter à `cleanup` : `cleanup_expired_tokens()` — supprimer les tokens expirés.

---

## 4. DT-04 : Rate limiting

### Implémentation avec slowapi

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

# Appliquer par route
@router.post("/generate")
@limiter.limit("10/minute")
async def generate_grids(request: Request, ...):
    ...
```

### Limites par catégorie

| Catégorie         | Limite  | Endpoints                                                         |
| ----------------- | ------- | ----------------------------------------------------------------- |
| Auth              | 5/min   | login, register                                                   |
| Calcul intensif   | 10/min  | grids/generate, wheeling/generate, budget/optimize, simulations/* |
| Lecture           | 100/min | draws, statistics, grids (list)                                   |
| Écriture légère   | 30/min  | history/save, favorite toggle                                     |
| Lecture détaillée | 30/min  | wheeling/detail, budget/detail                                    |
| Comparaison       | 20/min  | comparison/compare                                                |

### Gestion des dépassements

```python
# Réponse 429
{
    "detail": {
        "code": "RATE_LIMIT_EXCEEDED",
        "message": "Trop de requêtes. Veuillez patienter avant de réessayer.",
        "retry_after": 60  # secondes
    }
}
```

---

## 5. Validation des entrées

### Règles de validation renforcées

| Champ                 | Validation                                                | Raison               |
| --------------------- | --------------------------------------------------------- | -------------------- |
| `selected_numbers`    | Chaque num ∈ [1, max_main_number], len ∈ [6, 20], uniques | Injection, bornes    |
| `selected_stars`      | Chaque num ∈ [1, max_star_number], uniques                | Injection, bornes    |
| `guarantee_level`     | ∈ [2, main_numbers_count - 1]                             | Bornes mathématiques |
| `budget`              | > 0, ≤ 500                                                | Bornes raisonnables  |
| `tags`                | Chaque tag: str, len ≤ 50, max 10 tags                    | Anti-spam            |
| `name` (saved result) | str, len ≤ 200                                            | Anti-spam            |
| `game_id`             | Exists in game_definitions, is_active=true                | Intégrité            |

### Protection XSS

Tous les champs texte retournés (notification.title, notification.message, tags) doivent être échappés côté frontend. Pas de `dangerouslySetInnerHTML`.

### Protection injection SQL

Pas de risque direct (SQLAlchemy ORM), mais vérifier qu'aucune requête raw n'est utilisée avec des paramètres non échappés.

---

## 6. Données sensibles

### Données à protéger

| Donnée                 | Protection                             |
| ---------------------- | -------------------------------------- |
| Mots de passe          | bcrypt (déjà en place)                 |
| Tokens JWT             | HTTPS uniquement, expiration courte    |
| Historique utilisateur | Accessible uniquement par propriétaire |
| Email utilisateur      | Pas exposé dans les API publiques      |

### RGPD minimal

- Droit à la suppression : supprimer user → CASCADE sur notifications, saved_results
- Pas de collecte de données personnelles au-delà de username/email/password
- Pas de tracking externe ni analytics tierces

---

## 7. Sécurité du scheduler

### Risques

| Risque                                                | Mitigation                                   |
| ----------------------------------------------------- | -------------------------------------------- |
| Job crée des notifications pour des users inexistants | FK constraint user_id                        |
| Job notification storm                                | Limiter à 1 notif par type par user par jour |
| Scraper manipulé (faux tirages)                       | Vérifier source_url, comparer avec cache     |

---

## 8. Résumé des actions

| Action                                       | Priorité | Phase | Effort    |
| -------------------------------------------- | -------- | ----- | --------- |
| Migrer token_blacklist vers PostgreSQL       | P1       | A     | 1 jour    |
| Implémenter rate limiting (slowapi)          | P1       | A     | 1 jour    |
| Ajouter ownership check sur endpoints        | P1       | B     | 0.5 jour  |
| Mettre auth requise sur endpoints personnels | P1       | B     | 0.5 jour  |
| Validation entrées wheeling/budget           | P1       | C     | 0.5 jour  |
| Cleanup expired tokens job                   | P2       | A     | 0.25 jour |
| Matrice rôles complète                       | P2       | B     | 0.5 jour  |

---

## 9. Checklist locale

- [ ] DT-02 : Créer table token_blacklist + migration
- [ ] DT-02 : Implémenter TokenBlacklistService
- [ ] DT-02 : Migrer blacklist en mémoire → PostgreSQL
- [ ] DT-02 : Job cleanup_expired_tokens
- [ ] DT-04 : Installer et configurer slowapi
- [ ] DT-04 : Appliquer rate limits par catégorie d'endpoint
- [ ] DT-04 : Implémenter réponse 429 avec retry_after
- [ ] Ajouter auth obligatoire sur endpoints historique/favoris
- [ ] Ajouter auth obligatoire sur endpoints notifications
- [ ] Ajouter auth obligatoire sur endpoints wheeling historique
- [ ] Implémenter verify_ownership sur GET/DELETE/PATCH
- [ ] Validation entrées : selected_numbers bornes
- [ ] Validation entrées : budget bornes
- [ ] Validation entrées : tags anti-spam
- [ ] Vérifier protection XSS sur champs texte retournés
- [ ] Vérifier aucune requête raw SQL avec paramètres non échappés
- [ ] Documenter matrice rôles × fonctionnalités

Réf. : [27_Checklist_Globale_Evolutions](./27_Checklist_Globale_Evolutions.md)
