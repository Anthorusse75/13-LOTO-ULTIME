# Migrer de HS256 à RS256 (JWT asymétrique)

## Pourquoi migrer ?

- **HS256** (symétrique) : même clé pour signer et vérifier. Pratique en mono-service, mais la clé secrète doit être partagée entre tous les services qui valident des tokens.
- **RS256** (asymétrique) : clé privée pour signer, clé publique pour vérifier. Idéal en architecture multi-service : seul l'API génère des tokens, les autres services vérifient sans jamais avoir accès à la clé privée.

---

## 1. Générer une paire de clés RSA

```bash
# Clé privée (2048 bits, protégée par passphrase optionnelle)
openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:2048 -out private.pem

# Clé publique correspondante
openssl rsa -in private.pem -pubout -out public.pem
```

> **Sécurité** : Ne commitez jamais `private.pem` dans le dépôt Git. Ajoutez-le à `.gitignore`.

---

## 2. Configurer LOTO ULTIME

### Option A — Contenu PEM dans les variables d'environnement

```bash
# .env
JWT_ALGORITHM=RS256
JWT_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nMIIEvQ...\n-----END PRIVATE KEY-----"
JWT_PUBLIC_KEY="-----BEGIN PUBLIC KEY-----\nMIIBIj...\n-----END PUBLIC KEY-----"
# SECRET_KEY reste obligatoire (utilisé pour d'autres usages)
SECRET_KEY=<votre-secret-32-caracteres-minimum>
```

> Note : remplacez les sauts de ligne par `\n` dans les variables d'environnement.

### Option B — Chemins vers les fichiers PEM

```bash
# .env
JWT_ALGORITHM=RS256
JWT_PRIVATE_KEY_PATH=/run/secrets/jwt_private.pem
JWT_PUBLIC_KEY_PATH=/run/secrets/jwt_public.pem
SECRET_KEY=<votre-secret-32-caracteres-minimum>
```

### Option C — Docker secrets

```yaml
# docker-compose.yml
services:
  backend:
    secrets:
      - jwt_private_key
      - jwt_public_key
    environment:
      JWT_ALGORITHM: RS256
      JWT_PRIVATE_KEY_PATH: /run/secrets/jwt_private_key
      JWT_PUBLIC_KEY_PATH: /run/secrets/jwt_public_key

secrets:
  jwt_private_key:
    file: ./secrets/private.pem
  jwt_public_key:
    file: ./secrets/public.pem
```

---

## 3. Rotation de clés

Contrairement à HS256, RS256 **ne supporte pas** la rotation via `PREVIOUS_SECRET_KEY`. Pour une rotation sans interruption de service :

1. Générez une nouvelle paire de clés RSA.
2. Publiez la **nouvelle clé publique** via un endpoint JWKS (voir étape suivante).
3. Redéployez le backend avec la nouvelle clé privée.
4. Les anciens tokens (signés avec l'ancienne clé privée) expireront naturellement.

---

## 4. Exposer un endpoint JWKS (optionnel, recommandé multi-service)

Si d'autres services doivent valider vos tokens de façon autonome, exposez votre clé publique au format JWKS :

```python
# À ajouter dans main.py ou dans api/v1/auth.py
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
import base64

@app.get("/.well-known/jwks.json")
async def jwks():
    """Expose la clé publique au format JWKS pour validation multi-service."""
    from app.core.config import get_settings
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives.serialization import load_pem_public_key

    settings = get_settings()
    if settings.JWT_ALGORITHM != "RS256":
        return {"keys": []}

    key = load_pem_public_key(settings.JWT_PUBLIC_KEY.encode(), backend=default_backend())
    pub_numbers = key.public_key().public_numbers()

    def _int_to_base64(n: int) -> str:
        length = (n.bit_length() + 7) // 8
        return base64.urlsafe_b64encode(n.to_bytes(length, "big")).rstrip(b"=").decode()

    return {
        "keys": [{
            "kty": "RSA",
            "use": "sig",
            "alg": "RS256",
            "kid": "loto-ultime-1",
            "n": _int_to_base64(pub_numbers.n),
            "e": _int_to_base64(pub_numbers.e),
        }]
    }
```

---

## 5. Revenir à HS256

Pour revenir à HS256, il suffit de supprimer (ou de ne pas définir) `JWT_ALGORITHM=RS256` dans `.env`.
