# 12 — Sécurité et Authentification

> **Projet** : LOTO ULTIME  
> **Version** : 1.0  
> **Date** : 2026-03-27  
> **Références croisées** : [03_Backend](03_Architecture_Backend.md) · [06_API_Design](06_API_Design.md) · [04_Frontend](04_Architecture_Frontend.md)

---

## 1. Principes de Sécurité

| Principe | Application |
|---|---|
| Defense in depth | Multiples couches de protection |
| Least privilege | Chaque rôle n'a accès qu'au strict nécessaire |
| Secure by default | Pas d'accès sans authentification |
| No trust | Valider toutes les entrées, même internes |

---

## 2. Authentification

### 2.1 Mécanisme : JWT (JSON Web Tokens)

```
1. Client envoie username + password → POST /auth/login
2. Backend vérifie credentials
3. Backend retourne JWT signé
4. Client inclut JWT dans chaque requête : Authorization: Bearer <token>
5. Backend vérifie et décode le token
```

### 2.2 Structure du Token

```json
{
  "header": {
    "alg": "HS256",
    "typ": "JWT"
  },
  "payload": {
    "sub": "1",
    "username": "admin",
    "role": "ADMIN",
    "exp": 1711584000,
    "iat": 1711580400,
    "jti": "unique-token-id"
  }
}
```

### 2.3 Configuration

| Paramètre | Valeur | Description |
|---|---|---|
| Algorithme | HS256 | HMAC-SHA256 |
| Expiration | 60 min | Durée de validité |
| Secret | `SECRET_KEY` (env) | Clé de signature (≥ 32 chars) |
| Refresh | Token séparé | Durée 7 jours |

### 2.4 Implémentation

```python
# app/core/security.py
from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext
import secrets

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, secret_key: str, expires_delta: timedelta) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "jti": secrets.token_urlsafe(16),
    })
    return jwt.encode(to_encode, secret_key, algorithm="HS256")

def decode_token(token: str, secret_key: str) -> dict:
    return jwt.decode(token, secret_key, algorithms=["HS256"])
```

### 2.5 Dépendance FastAPI

```python
# app/api/deps.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    user_repo: UserRepository = Depends(get_user_repository),
    settings: Settings = Depends(get_settings),
) -> User:
    try:
        payload = decode_token(credentials.credentials, settings.SECRET_KEY)
        user_id = int(payload["sub"])
    except (JWTError, KeyError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide",
        )
    
    user = await user_repo.get(user_id)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Utilisateur inactif ou inexistant",
        )
    
    return user
```

---

## 3. Autorisation (RBAC)

### 3.1 Rôles

| Rôle | Description | Niveau |
|---|---|---|
| **ADMIN** | Accès complet, gestion système | 3 |
| **UTILISATEUR** | Accès stats + grilles + portefeuilles | 2 |
| **CONSULTATION** | Lecture seule : stats, tirages | 1 |

### 3.2 Matrice de Permissions

| Ressource | CONSULTATION | UTILISATEUR | ADMIN |
|---|:---:|:---:|:---:|
| GET /games | ✅ | ✅ | ✅ |
| GET /draws | ✅ | ✅ | ✅ |
| GET /statistics | ✅ | ✅ | ✅ |
| GET /statistics/bayesian | ❌ | ✅ | ✅ |
| GET /statistics/graph | ❌ | ✅ | ✅ |
| GET /grids/top | ❌ | ✅ | ✅ |
| POST /grids/generate | ❌ | ✅ | ✅ |
| POST /grids/score | ❌ | ✅ | ✅ |
| GET /portfolios | ❌ | ✅ | ✅ |
| POST /portfolios/generate | ❌ | ✅ | ✅ |
| POST /simulation | ❌ | ✅ | ✅ |
| POST /draws (ajout manuel) | ❌ | ❌ | ✅ |
| POST /draws/fetch | ❌ | ❌ | ✅ |
| POST /statistics/recompute | ❌ | ❌ | ✅ |
| * /jobs | ❌ | ❌ | ✅ |
| * /admin | ❌ | ❌ | ✅ |
| POST /games | ❌ | ❌ | ✅ |
| PUT /games | ❌ | ❌ | ✅ |
| DELETE * | ❌ | ❌ | ✅ |

### 3.3 Implémentation

```python
from functools import wraps
from app.models.user import UserRole

def require_role(minimum_role: UserRole):
    """Dépendance FastAPI pour vérifier le rôle minimum."""
    ROLE_HIERARCHY = {
        UserRole.CONSULTATION: 1,
        UserRole.UTILISATEUR: 2,
        UserRole.ADMIN: 3,
    }
    
    async def role_checker(current_user: User = Depends(get_current_user)):
        if ROLE_HIERARCHY[current_user.role] < ROLE_HIERARCHY[minimum_role]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Accès réservé au rôle {minimum_role.value} minimum",
            )
        return current_user
    
    return role_checker

# Utilisation dans un router
@router.post("/games", dependencies=[Depends(require_role(UserRole.ADMIN))])
async def create_game(...):
    ...
```

---

## 4. Gestion des Mots de Passe

### 4.1 Règles

| Règle | Valeur |
|---|---|
| Longueur minimale | 8 caractères |
| Complexité | Au moins 1 majuscule, 1 minuscule, 1 chiffre |
| Hachage | bcrypt (facteur coût = 12) |
| Stockage | Hash seul, jamais le mot de passe en clair |

### 4.2 Validation

```python
# app/schemas/auth.py
import re
from pydantic import BaseModel, field_validator

class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    
    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Le mot de passe doit contenir au moins 8 caractères")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Le mot de passe doit contenir au moins une majuscule")
        if not re.search(r"[a-z]", v):
            raise ValueError("Le mot de passe doit contenir au moins une minuscule")
        if not re.search(r"\d", v):
            raise ValueError("Le mot de passe doit contenir au moins un chiffre")
        return v
```

---

## 5. Protection API

### 5.1 Rate Limiting

Limiter le nombre de requêtes par utilisateur/IP :

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.middleware("http")
async def rate_limit_middleware(request, call_next):
    # 60 requêtes par minute par IP
    ...
```

| Endpoint | Limite |
|---|---|
| POST /auth/login | 5/min |
| POST /auth/register | 3/min |
| GET /* | 60/min |
| POST /grids/generate | 10/min |
| POST /simulation | 5/min |

### 5.2 CORS

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,  # Liste blanche
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)
```

### 5.3 Validation des Entrées

Toutes les entrées sont validées par Pydantic :
- Types stricts
- Bornes numériques (min/max)
- Patterns regex pour slugs et identifiants
- Longueurs maximales pour les chaînes

### 5.4 En-têtes de sécurité

```python
@app.middleware("http")
async def security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response
```

### 5.5 Protection contre les injections

- **SQL Injection** : Impossible grâce à SQLAlchemy ORM (requêtes paramétrées)
- **XSS** : Pas de rendu HTML côté backend (API JSON only)
- **CSRF** : Non applicable (API stateless, JWT Bearer)
- **Path Traversal** : Pas d'accès fichier basé sur l'entrée utilisateur

---

## 6. Gestion du Premier Utilisateur

Au premier démarrage, si aucun utilisateur n'existe, le système crée un administrateur :

```python
async def create_initial_admin(settings: Settings, user_repo: UserRepository):
    """Crée le premier admin au démarrage si aucun utilisateur n'existe."""
    count = await user_repo.count()
    if count == 0:
        admin = User(
            username="admin",
            email=settings.ADMIN_EMAIL or "admin@loto-ultime.local",
            hashed_password=hash_password(settings.ADMIN_INITIAL_PASSWORD),
            role=UserRole.ADMIN,
            is_active=True,
        )
        await user_repo.create(admin)
        logger.info("initial_admin.created", username="admin")
```

Le mot de passe initial est défini via variable d'environnement `ADMIN_INITIAL_PASSWORD` et **doit être changé** au premier login.

---

## 7. Audit Trail

Journaliser les actions sensibles :

| Action | Données logguées |
|---|---|
| Login réussi | username, IP, timestamp |
| Login échoué | username, IP, timestamp |
| Création utilisateur | username, rôle, créateur |
| Modification rôle | ancien_rôle → nouveau_rôle, modificateur |
| Déclenchement job | job_name, utilisateur |
| Accès admin | endpoint, utilisateur |

---

## 8. Références

| Document | Contenu |
|---|---|
| [03_Architecture_Backend](03_Architecture_Backend.md) | Middleware, dépendances |
| [04_Architecture_Frontend](04_Architecture_Frontend.md) | Stockage JWT côté client |
| [06_API_Design](06_API_Design.md) | Endpoints auth |
| [15_Observabilite](15_Observabilite.md) | Logs d'audit |

---

*Fin du document 12_Securite_et_Authentification.md*
