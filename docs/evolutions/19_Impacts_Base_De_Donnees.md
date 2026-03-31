# 19 — Impacts Base de Données

> Analyse complète des impacts de toutes les évolutions sur le schéma de base de données : nouvelles tables, colonnes, migrations, indexation, seed data.

---

## Références croisées

- [00_Index_Evolutions](./00_Index_Evolutions.md)
- [05_Modele_Donnees](../05_Modele_Donnees.md) — Modèle actuel
- [16_Impacts_Backend](./16_Impacts_Backend.md) — Modèles SQLAlchemy
- [22_Impacts_Performance_Scalabilite](./22_Impacts_Performance_Scalabilite.md) — Indexation, volume

---

## 1. Schéma actuel (7 tables)

```
users
├── id (PK)
├── username (UNIQUE)
├── email (UNIQUE)
├── hashed_password
├── role (ADMIN | UTILISATEUR | CONSULTATION)
├── is_active
├── created_at
└── updated_at

game_definitions
├── id (PK)
├── name (UNIQUE)
├── slug (UNIQUE)
├── main_numbers_count
├── max_main_number
├── star_numbers_count
├── max_star_number
├── grid_price
├── draw_schedule
├── is_active
└── created_at

draws
├── id (PK)
├── game_id (FK → game_definitions)
├── draw_date
├── main_numbers (JSON)
├── star_numbers (JSON)
├── jackpot
├── source_url
└── created_at

scored_grids
├── id (PK)
├── game_id (FK → game_definitions)
├── main_numbers (JSON)
├── star_numbers (JSON)
├── score
├── scoring_details (JSON)
├── is_favorite
├── is_played
├── played_at
├── generation_method
├── optimization_method
└── created_at

statistics_snapshots
├── id (PK)
├── game_id (FK → game_definitions)
├── frequencies (JSON)
├── gaps (JSON)
├── cooccurrence_matrix (JSON)
├── star_frequencies (JSON)
├── star_gaps (JSON)
├── computed_at
└── created_at

portfolios
├── id (PK)
├── game_id (FK → game_definitions)
├── grids (JSON)
├── expected_score
├── diversity_score
├── total_cost
├── optimization_method
└── created_at

job_executions
├── id (PK)
├── job_name
├── status (PENDING | RUNNING | SUCCESS | FAILED)
├── started_at
├── completed_at
├── duration_seconds
├── result_summary (JSON)
└── error_message
```

---

## 2. Nouvelles tables

### 2.1 — game_prize_tiers (doc 08)

```sql
CREATE TABLE game_prize_tiers (
    id SERIAL PRIMARY KEY,
    game_id INTEGER NOT NULL REFERENCES game_definitions(id),
    rank INTEGER NOT NULL,              -- 1 = jackpot, 2, 3...
    name VARCHAR(100) NOT NULL,         -- "5 + Chance", "5 + 0", etc.
    match_numbers INTEGER NOT NULL,     -- Nombre de numéros matchés
    match_stars INTEGER NOT NULL DEFAULT 0, -- Nombre d'étoiles/chance matchées
    avg_prize NUMERIC(12,2) NOT NULL,   -- Gain moyen en euros
    probability NUMERIC(20,15) NOT NULL, -- Probabilité exacte
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(game_id, rank)
);
```

**Seed data** : 9 rangs Loto FDJ + 13 rangs EuroMillions + rangs PowerBall/Mega/Keno.

### 2.2 — wheeling_systems (doc 08)

```sql
CREATE TABLE wheeling_systems (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),  -- nullable (anonyme)
    game_id INTEGER NOT NULL REFERENCES game_definitions(id),
    selected_numbers JSON NOT NULL,       -- [1, 7, 12, 23, ...]
    selected_stars JSON,                   -- [3, 8] ou null
    guarantee_level INTEGER NOT NULL,     -- t (2, 3, 4...)
    grids JSON NOT NULL,                   -- [[1,2,3,4,5], ...]
    grid_count INTEGER NOT NULL,
    total_cost NUMERIC(8,2) NOT NULL,
    coverage_rate NUMERIC(5,4) NOT NULL,  -- 0.0000–1.0000
    reduction_rate NUMERIC(5,4) NOT NULL, -- vs full wheel
    gain_scenarios JSON,                   -- Scénarios pré-calculés
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

### 2.3 — budget_plans (doc 09)

```sql
CREATE TABLE budget_plans (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    game_id INTEGER NOT NULL REFERENCES game_definitions(id),
    budget NUMERIC(8,2) NOT NULL,
    objective VARCHAR(50) NOT NULL,       -- 'coverage', 'diversity', 'scoring'
    selected_numbers JSON,
    recommendations JSON NOT NULL,         -- [{strategy, grids, cost, score}×3]
    chosen_strategy VARCHAR(50),           -- Stratégie choisie par l'utilisateur
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

### 2.4 — user_saved_results (doc 11)

```sql
CREATE TABLE user_saved_results (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    type VARCHAR(50) NOT NULL,             -- 'grid', 'portfolio', 'wheeling', 'budget_plan', 'comparison', 'simulation'
    name VARCHAR(200),
    parameters JSON NOT NULL,              -- Paramètres de la requête originale
    result_data JSON NOT NULL,             -- Résultat complet
    is_favorite BOOLEAN NOT NULL DEFAULT FALSE,
    tags JSON DEFAULT '[]',                -- ["tag1", "tag2"]
    game_id INTEGER REFERENCES game_definitions(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ
);
```

### 2.5 — grid_draw_results (doc 15)

```sql
CREATE TABLE grid_draw_results (
    id SERIAL PRIMARY KEY,
    scored_grid_id INTEGER NOT NULL REFERENCES scored_grids(id) ON DELETE CASCADE,
    draw_id INTEGER NOT NULL REFERENCES draws(id),
    matched_numbers JSON NOT NULL,         -- [7, 23, 41]
    matched_stars JSON,                    -- [3] ou null
    match_count INTEGER NOT NULL,
    star_match_count INTEGER NOT NULL DEFAULT 0,
    prize_rank INTEGER,                    -- Rang de gain ou null (pas gagné)
    estimated_prize NUMERIC(12,2) NOT NULL DEFAULT 0.00,
    checked_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(scored_grid_id, draw_id)
);
```

### 2.6 — user_notifications (doc 15)

```sql
CREATE TABLE user_notifications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL,             -- 'new_draw', 'grid_result', 'suggestion', 'stats_updated'
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    data JSON,                             -- Données contextuelles
    is_read BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

---

## 3. Colonnes ajoutées sur tables existantes

### scored_grids

```sql
ALTER TABLE scored_grids ADD COLUMN user_id INTEGER REFERENCES users(id);
-- Nullable : les grilles existantes restent sans user
-- Index pour filtrage par utilisateur
CREATE INDEX idx_scored_grids_user_id ON scored_grids(user_id) WHERE user_id IS NOT NULL;
```

### portfolios

```sql
ALTER TABLE portfolios ADD COLUMN user_id INTEGER REFERENCES users(id);
CREATE INDEX idx_portfolios_user_id ON portfolios(user_id) WHERE user_id IS NOT NULL;
```

### statistics_snapshots

```sql
ALTER TABLE statistics_snapshots ADD COLUMN hot_cold_summary JSON;
-- Top 5 chauds, top 5 froids, pré-calculé par le pipeline
```

---

## 4. Indexation

### Index sur nouvelles tables

```sql
-- game_prize_tiers
CREATE INDEX idx_prize_tiers_game_id ON game_prize_tiers(game_id);

-- wheeling_systems
CREATE INDEX idx_wheeling_user_id ON wheeling_systems(user_id) WHERE user_id IS NOT NULL;
CREATE INDEX idx_wheeling_game_id ON wheeling_systems(game_id);
CREATE INDEX idx_wheeling_created_at ON wheeling_systems(created_at DESC);

-- budget_plans
CREATE INDEX idx_budget_user_id ON budget_plans(user_id) WHERE user_id IS NOT NULL;
CREATE INDEX idx_budget_game_id ON budget_plans(game_id);

-- user_saved_results
CREATE INDEX idx_saved_results_user_id ON user_saved_results(user_id);
CREATE INDEX idx_saved_results_type ON user_saved_results(type);
CREATE INDEX idx_saved_results_favorite ON user_saved_results(user_id, is_favorite) WHERE is_favorite = TRUE;
CREATE INDEX idx_saved_results_game_id ON user_saved_results(game_id) WHERE game_id IS NOT NULL;
CREATE INDEX idx_saved_results_created_at ON user_saved_results(created_at DESC);

-- grid_draw_results
CREATE INDEX idx_grid_results_grid_id ON grid_draw_results(scored_grid_id);
CREATE INDEX idx_grid_results_draw_id ON grid_draw_results(draw_id);

-- user_notifications
CREATE INDEX idx_notifications_user_id ON user_notifications(user_id);
CREATE INDEX idx_notifications_unread ON user_notifications(user_id, is_read) WHERE is_read = FALSE;
CREATE INDEX idx_notifications_created_at ON user_notifications(created_at DESC);
```

### Index sur tables existantes

```sql
-- draws : accélère filtrage par game + date
CREATE INDEX IF NOT EXISTS idx_draws_game_date ON draws(game_id, draw_date DESC);

-- scored_grids : accélère tri par score
CREATE INDEX IF NOT EXISTS idx_grids_game_score ON scored_grids(game_id, score DESC);

-- scored_grids : grilles jouées non vérifiées
CREATE INDEX IF NOT EXISTS idx_grids_played ON scored_grids(is_played) WHERE is_played = TRUE;
```

---

## 5. Migrations Alembic

### Ordre des migrations

| Migration | Contenu | Phase | Dépendance |
|-----------|---------|-------|------------|
| `001_add_game_prize_tiers` | Table game_prize_tiers + seed data | B | — |
| `002_add_user_id_columns` | user_id sur scored_grids, portfolios | B | — |
| `003_add_wheeling_systems` | Table wheeling_systems | C | 001 |
| `004_add_budget_plans` | Table budget_plans | C | — |
| `005_add_user_saved_results` | Table user_saved_results | B | — |
| `006_add_grid_draw_results` | Table grid_draw_results | B | — |
| `007_add_user_notifications` | Table user_notifications | D | — |
| `008_add_hot_cold_summary` | Colonne sur statistics_snapshots | B | — |
| `009_add_indexes` | Tous les index secondaires | B | 001–008 |

### Seed data game_prize_tiers

**Loto FDJ** (9 rangs) :

| Rang | Nom | Numéros | Chance | Gain moyen |
|------|-----|---------|--------|------------|
| 1 | 5 + Chance | 5 | 1 | 2 000 000 € |
| 2 | 5 + 0 | 5 | 0 | 100 000 € |
| 3 | 4 + Chance | 4 | 1 | 1 000 € |
| 4 | 4 + 0 | 4 | 0 | 500 € |
| 5 | 3 + Chance | 3 | 1 | 50 € |
| 6 | 3 + 0 | 3 | 0 | 20 € |
| 7 | 2 + Chance | 2 | 1 | 10 € |
| 8 | 2 + 0 | 2 | 0 | 5 € |
| 9 | 1 + Chance | 1 | 1 | 2.20 € |

**EuroMillions** (13 rangs) :

| Rang | Nom | Numéros | Étoiles | Gain moyen |
|------|-----|---------|---------|------------|
| 1 | 5 + 2 | 5 | 2 | 50 000 000 € |
| 2 | 5 + 1 | 5 | 1 | 300 000 € |
| 3 | 5 + 0 | 5 | 0 | 30 000 € |
| 4 | 4 + 2 | 4 | 2 | 3 000 € |
| 5 | 4 + 1 | 4 | 1 | 200 € |
| 6 | 3 + 2 | 3 | 2 | 100 € |
| 7 | 4 + 0 | 4 | 0 | 50 € |
| 8 | 2 + 2 | 2 | 2 | 20 € |
| 9 | 3 + 1 | 3 | 1 | 15 € |
| 10 | 3 + 0 | 3 | 0 | 13 € |
| 11 | 1 + 2 | 1 | 2 | 10 € |
| 12 | 2 + 1 | 2 | 1 | 8 € |
| 13 | 2 + 0 | 2 | 0 | 4 € |

---

## 6. Volume et croissance estimés

| Table | Volume initial | Croissance |
|-------|---------------|------------|
| game_prize_tiers | ~50 lignes (5 jeux × ~10 rangs) | Quasi-statique |
| wheeling_systems | 0 | ~10/jour (si multi-users) |
| budget_plans | 0 | ~10/jour |
| user_saved_results | 0 | ~50/jour |
| grid_draw_results | 0 | ~100/tirage (grilles jouées × tirages) |
| user_notifications | 0 | ~20/jour |

### Purge automatique

| Table | Politique | Job |
|-------|-----------|-----|
| user_notifications | Supprimer > 30 jours si lues | cleanup_notifications |
| grid_draw_results | Conserver 1 an | cleanup_old_results |
| wheeling_systems (anonyme) | Supprimer > 7 jours si user_id IS NULL | cleanup_anonymous |

---

## 7. Contraintes et intégrité

### Foreign keys

Toutes les FK ont `ON DELETE` approprié :
- `user_notifications.user_id` → `CASCADE` (supprimer avec l'user)
- `grid_draw_results.scored_grid_id` → `CASCADE`
- `wheeling_systems.user_id` → `SET NULL` (conserver le système)
- `budget_plans.user_id` → `SET NULL`
- `user_saved_results.user_id` → `CASCADE`

### Contraintes CHECK

```sql
-- wheeling_systems
ALTER TABLE wheeling_systems ADD CONSTRAINT chk_guarantee CHECK (guarantee_level >= 2);
ALTER TABLE wheeling_systems ADD CONSTRAINT chk_grid_count CHECK (grid_count >= 1);
ALTER TABLE wheeling_systems ADD CONSTRAINT chk_coverage CHECK (coverage_rate >= 0 AND coverage_rate <= 1);

-- budget_plans
ALTER TABLE budget_plans ADD CONSTRAINT chk_budget_positive CHECK (budget > 0);

-- game_prize_tiers
ALTER TABLE game_prize_tiers ADD CONSTRAINT chk_rank_positive CHECK (rank >= 1);
ALTER TABLE game_prize_tiers ADD CONSTRAINT chk_probability CHECK (probability > 0 AND probability < 1);
```

---

## 8. Risques

| Risque | Impact | Mitigation |
|--------|--------|------------|
| Migration en production casse le service | Critique | Toutes migrations non-breaking (ADD COLUMN nullable, CREATE TABLE) |
| JSON columns sans schéma → données corrompues | Moyen | Validation Pydantic côté application |
| Volume grid_draw_results si beaucoup de grilles jouées | Faible | Purge auto + index |
| Seed data prize_tiers incorrecte | Moyen | Vérifier sur sources FDJ/EuroMillions officielles |

---

## 9. Checklist locale

- [ ] Migration 001 : Créer table game_prize_tiers + seed Loto + EuroMillions
- [ ] Migration 002 : Ajouter user_id sur scored_grids et portfolios
- [ ] Migration 003 : Créer table wheeling_systems
- [ ] Migration 004 : Créer table budget_plans
- [ ] Migration 005 : Créer table user_saved_results
- [ ] Migration 006 : Créer table grid_draw_results
- [ ] Migration 007 : Créer table user_notifications
- [ ] Migration 008 : Ajouter hot_cold_summary sur statistics_snapshots
- [ ] Migration 009 : Créer tous les index secondaires
- [ ] Seed data : rangs de gain PowerBall, Mega Millions, Keno
- [ ] Vérifier ON DELETE sur toutes les FK
- [ ] Ajouter contraintes CHECK
- [ ] Configurer jobs de purge automatique
- [ ] Tester rollback de chaque migration

Réf. : [27_Checklist_Globale_Evolutions](./27_Checklist_Globale_Evolutions.md)
