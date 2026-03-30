# Contribuer à LOTO ULTIME

Merci de contribuer au projet ! Ce guide explique les conventions et le workflow à suivre.

---

## Prérequis

- **Python 3.11+** avec un environnement virtuel
- **Node.js 22+** et npm
- **Git** configuré

## Installation locale

```bash
# Backend
cd backend
python -m venv .venv
source .venv/bin/activate     # Linux/Mac
# .venv\Scripts\activate      # Windows
pip install -e ".[dev]"
alembic upgrade head

# Frontend
cd frontend
npm install
```

---

## Workflow Git

### Branches

| Branche        | Usage                          |
| -------------- | ------------------------------ |
| `main`         | Production — toujours stable   |
| `feat/<nom>`   | Nouvelle fonctionnalité        |
| `fix/<nom>`    | Correction de bug              |
| `refactor/<nom>` | Refactoring sans changement fonctionnel |

### Commits

Format [Conventional Commits](https://www.conventionalcommits.org/) :

```
<type>(<scope>): <description>

[body optionnel]
```

**Types** : `feat`, `fix`, `refactor`, `test`, `docs`, `chore`, `perf`, `ci`  
**Scopes** : `api`, `ui`, `db`, `auth`, `stats`, `scoring`, `optim`, `sim`, `scheduler`, `docker`

Exemples :
```
feat(api): add grid comparison endpoint
fix(ui): fix mobile sidebar overflow
test(scoring): add boundary tests for balance criterion
```

---

## Tests

### Backend

```bash
cd backend

# Tous les tests
pytest

# Avec couverture
pytest --cov=app --cov-report=html

# Un fichier
pytest tests/unit/test_auth.py -v

# Un test spécifique
pytest tests/unit/test_auth.py::test_login_success -v
```

**Couverture minimale** : 80% global (actuellement ~85%)

### Frontend

```bash
cd frontend

# Tests unitaires (Vitest)
npm test

# Mode watch
npx vitest --watch
```

---

## Style de code

### Backend (Python)

- **Linter** : `ruff check app/`
- **Format** : `ruff format app/`
- **Type hints** obligatoires sur les signatures publiques
- **Docstrings** sur les classes et fonctions publiques

### Frontend (TypeScript)

- **Linter** : `npm run lint`
- **Format** : Prettier via config
- **Strict mode** TypeScript activé

---

## Architecture

Respecter la séparation en couches :

```
API (Routers) → Services → Engines / Repositories → Models
```

- **Engines** : calculs purs, aucune dépendance I/O
- **Services** : orchestration, injection des repositories
- **Repositories** : accès données via SQLAlchemy

Ne pas appeler un repository directement depuis un router — toujours passer par un service.

---

## Ajouter un jeu de loterie

1. Créer `backend/configs/games/<slug>.yaml` (voir `loto_fdj.yaml` comme modèle)
2. Le jeu sera automatiquement chargé au démarrage de l'application
3. Tous les moteurs (stats, scoring, optimisation, simulation) sont game-agnostic

---

## Résolution de problèmes courants

| Problème | Solution |
| -------- | -------- |
| `ModuleNotFoundError` | Vérifier que le venv est activé et `pip install -e ".[dev]"` |
| Tests DB échouent | Vérifier que `alembic upgrade head` a été exécuté |
| Frontend erreurs CORS | Vérifier `CORS_ORIGINS` dans `.env` |
| Docker build échoue | Vérifier les `.dockerignore` et le contenu des `Dockerfile` |
