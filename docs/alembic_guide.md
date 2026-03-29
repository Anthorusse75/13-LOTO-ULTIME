# Guide de migration Alembic

## Vue d'ensemble

Loto Ultime utilise [Alembic](https://alembic.sqlalchemy.org/) pour gérer les migrations de base de données SQLite, couplé à SQLAlchemy 2.0 (mode asynchrone avec `aiosqlite`).

---

## Structure des fichiers

```
backend/
├── alembic.ini                    # Configuration Alembic (URL de DB, emplacement des révisions)
├── alembic/
│   ├── env.py                     # Environnement Alembic (connexion synchrone pour migrations)
│   └── versions/
│       ├── 17f0eca1a355_initial_schema.py
│       ├── 6773450d8c55_add_statistics_snapshot.py
│       ├── a3b4c5d6e7f8_add_favorite_to_scored_grids.py
│       └── b1c2d3e4f5a6_add_is_played_to_scored_grids.py
└── app/
    └── models/                    # Modèles SQLAlchemy (source de vérité)
```

---

## Commandes essentielles

### Afficher l'état actuel

```bash
cd backend
alembic current       # Révision active dans la DB
alembic history       # Toutes les révisions (ordre chronologique)
alembic heads         # Révision(s) en tête de chaîne
```

### Appliquer les migrations en attente

```bash
# Mettre à jour vers la dernière révision
alembic upgrade head

# Mettre à jour vers une révision spécifique
alembic upgrade b1c2d3e4f5a6

# Avancer d'un cran
alembic upgrade +1
```

### Revenir en arrière

```bash
# Revenir à la révision précédente
alembic downgrade -1

# Revenir à une révision spécifique
alembic downgrade a3b4c5d6e7f8

# Supprimer toutes les migrations (⚠️ perte de données !)
alembic downgrade base
```

---

## Créer une nouvelle migration

### 1. Modifier le modèle SQLAlchemy

Exemple : ajouter un champ `notes` au modèle `ScoredGrid` dans `backend/app/models/grid.py` :

```python
notes: Mapped[str | None] = mapped_column(String, nullable=True)
```

### 2. Générer la migration automatiquement

Alembic compare le modèle avec l'état actuel de la DB et génère le diff :

```bash
cd backend
alembic revision --autogenerate -m "add_notes_to_scored_grids"
```

Un fichier est créé dans `alembic/versions/` avec un hash unique.

### 3. Vérifier le fichier généré

**Ne jamais appliquer une migration sans l'avoir relue.** L'autogénération peut manquer des cas complexes (renommage de colonnes, contraintes complexes, etc.).

```python
# alembic/versions/xxxx_add_notes_to_scored_grids.py
def upgrade() -> None:
    op.add_column("scored_grids", sa.Column("notes", sa.String(), nullable=True))

def downgrade() -> None:
    op.drop_column("scored_grids", "notes")
```

### 4. Appliquer la migration

```bash
alembic upgrade head
```

### 5. Vérifier

```bash
alembic current   # Doit afficher la nouvelle révision avec "(head)"
```

---

## Bonnes pratiques

| Règle | Raison |
|-------|--------|
| **Toujours relire** le fichier généré avant `upgrade head` | L'autogénération peut générer des DROP TABLE par erreur |
| **Ne jamais modifier** une migration déjà appliquée en production | Cela casse la chaîne de révisions |
| **Inclure un `downgrade()`** fonctionnel | Permet de revenir en arrière proprement |
| **Nommer clairement** la révision | Ex: `add_played_at_to_scored_grids` (pas `fix`) |
| **Valider le schema** après migration | Via `alembic current` et test unitaire |
| **Committer** la migration avec le code | Toujours dans le même commit que la modification du modèle |

---

## Workflow CI/CD recommandé

```bash
# Au démarrage de l'application (startup hook)
alembic upgrade head

# En CI, avant les tests
alembic upgrade head
pytest  # les tests utilisent la DB migrée
```

Le fichier `backend/app/database.py` ne crée plus les tables via `create_all()` — les migrations Alembic sont la seule source de vérité.

---

## Résolution des problèmes courants

### `alembic.util.exc.CommandError: Can't locate revision identified by 'xxxx'`

La base de données référence une révision qui n'existe plus dans `alembic/versions/`. Solution :

```bash
# Vérifier les révisions disponibles
alembic history

# Marquer manuellement la DB à une révision connue
alembic stamp <revision_id>
```

### `Target database is not up to date`

Des migrations en attente existent. Lancer `alembic upgrade head`.

### Conflit de `down_revision` (deux migrations avec le même parent)

Si plusieurs branches existent :

```bash
alembic merge heads -m "merge_branches"
alembic upgrade head
```

---

## Révisions actuelles

| Révision | Description | Date |
|----------|-------------|------|
| `17f0eca1a355` | Schéma initial (users, games, draws, scored_grids, statistics_snapshots) | initial |
| `6773450d8c55` | Ajout de la table `statistics_snapshots` complète | v1.1 |
| `a3b4c5d6e7f8` | Ajout de `is_favorite` + `star_score` sur `scored_grids` | v1.2 |
| `b1c2d3e4f5a6` | Ajout de `is_played` + `played_at` sur `scored_grids` | v1.3 |
