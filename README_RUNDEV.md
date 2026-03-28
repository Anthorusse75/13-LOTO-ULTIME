# Commandes de lancement — Développement

> Toutes les commandes se lancent **depuis la racine du projet**.

---

## Backend (FastAPI + Uvicorn)

### Installation (une seule fois)

```bash
python -m venv backend/.venv
backend/.venv/Scripts/pip install -e "backend/.[dev]"
```

### Lancer en local (localhost uniquement)

```bash
backend/.venv/Scripts/uvicorn app.main:app --reload --host 127.0.0.1 --port 8000 --app-dir backend
```

→ http://127.0.0.1:8000
→ Swagger : http://127.0.0.1:8000/docs

### Lancer accessible depuis l'extérieur (réseau local / tunnel)

```bash
backend/.venv/Scripts/uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 --app-dir backend
```

→ http://<IP_MACHINE>:8000

### Tests

```bash
backend/.venv/Scripts/python -m pytest backend -v --cov=app --cov-report=term-missing --rootdir=backend
```

### Migrations (Alembic)

```bash
(cd backend && .venv/Scripts/alembic upgrade head)
```

---

## Frontend (React + Vite)

### Installation (une seule fois)

```bash
npm --prefix frontend install
```

### Lancer en local (localhost uniquement)

```bash
npm --prefix frontend run dev
```

→ http://localhost:5173

### Lancer accessible depuis l'extérieur

```bash
npm --prefix frontend run dev -- --host 0.0.0.0
```

→ http://<IP_MACHINE>:5173

### Build production

```bash
npm --prefix frontend run build
npm --prefix frontend run preview -- --host 0.0.0.0 --port 4173
```

---

## Les deux ensemble

```bash
# Terminal 1 — Backend
backend/.venv/Scripts/uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 --app-dir backend

# Terminal 2 — Frontend
npm --prefix frontend run dev -- --host 0.0.0.0
```
