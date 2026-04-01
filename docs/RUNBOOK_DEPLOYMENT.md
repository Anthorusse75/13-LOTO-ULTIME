# RUNBOOK — Déploiement LOTO ULTIME

## Pré-requis

| Élément | Détail |
|---------|--------|
| Python | 3.12+ |
| Node.js | 20 LTS+ |
| PostgreSQL | 15+ |
| Redis | 7+ (optionnel, cache) |

## Variables d'environnement

```env
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/loto_ultime
SECRET_KEY=<random-64-chars>
ALLOWED_ORIGINS=https://loto-ultime.example.com
FDJ_API_BASE_URL=https://www.fdj.fr
REDIS_URL=redis://localhost:6379/0
```

## 1. Préparation

```bash
# Cloner le dépôt
git clone https://github.com/Anthorusse75/13-LOTO-ULTIME.git
cd 13-LOTO-ULTIME

# Vérifier la branche
git checkout main && git pull origin main
```

## 2. Backend

```bash
cd backend

# Créer / activer le venv
python -m venv .venv
source .venv/bin/activate      # Linux
# .venv\Scripts\activate       # Windows

# Installer les dépendances
pip install -r requirements.txt

# Appliquer les migrations
alembic upgrade head

# Lancer les tests
python -m pytest tests/unit/ -q --tb=short

# Démarrer le serveur
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## 3. Frontend

```bash
cd frontend

# Installer les dépendances
npm ci

# Build de production
npm run build

# Les fichiers statiques sont dans dist/
# Servir avec Nginx, Caddy, ou tout serveur statique
```

## 4. Nginx (exemple)

```nginx
server {
    listen 443 ssl http2;
    server_name loto-ultime.example.com;

    # Frontend
    root /var/www/loto-ultime/frontend/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    # API proxy
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Métriques Prometheus (accès restreint)
    location /metrics {
        proxy_pass http://127.0.0.1:8000/metrics;
        allow 10.0.0.0/8;
        deny all;
    }
}
```

## 5. Scheduler (APScheduler)

Le scheduler démarre automatiquement avec l'application FastAPI.
Jobs principaux :
- **nightly_pipeline** : 02h00 UTC — scraping + stats + scoring + portfolio + notifications
- **cleanup_anonymous_data** : inclus dans le pipeline nightly

Vérifier les logs :
```bash
journalctl -u loto-ultime -f | grep scheduler
```

## 6. Vérification post-déploiement

```bash
# Health check
curl -s https://loto-ultime.example.com/api/v1/health | jq .

# Vérifier les métriques
curl -s http://localhost:8000/metrics | head -20

# Vérifier les migrations
cd backend && alembic current
```

## 7. Checklist déploiement

- [ ] Variables d'environnement configurées
- [ ] `alembic upgrade head` exécuté sans erreur
- [ ] Tests backend passent (491+)
- [ ] Build frontend sans erreur TypeScript
- [ ] Health check retourne `200 OK`
- [ ] Scheduler fonctionne (logs visibles)
- [ ] HTTPS actif
- [ ] CORS configuré correctement
