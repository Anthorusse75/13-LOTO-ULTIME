# 25 — Stratégie de Tests des Évolutions

> Plan de tests complet pour chaque nouvelle fonctionnalité : tests unitaires, intégration, API, et E2E.

---

## Références croisées

- [00_Index_Evolutions](./00_Index_Evolutions.md)
- [16_Strategie_Tests](../16_Strategie_Tests.md) — Stratégie tests existante
- [24_Strategie_Non_Regression](./24_Strategie_Non_Regression.md) — Non-régression
- [16_Impacts_Backend](./16_Impacts_Backend.md) — Modules à tester

---

## 1. Objectif

Chaque nouvelle fonctionnalité doit avoir une couverture de tests ≥ 80% avant mise en production. Les tests sont organisés en 4 niveaux :

| Niveau | Type | Outils | Durée cible |
|--------|------|--------|-------------|
| L1 | Unitaire | pytest | < 10s |
| L2 | Intégration | pytest + aiosqlite | < 30s |
| L3 | API | pytest + TestClient | < 20s |
| L4 | E2E (optionnel) | Playwright | < 2min |

---

## 2. Tests par évolution

### 2.1 — Wheeling (doc 08) — ~16 tests

#### Tests unitaires (L1)

| Test | Vérifie |
|------|---------|
| `test_greedy_cover_basic` | 6 numéros, k=5, t=2 → résultat correct |
| `test_greedy_cover_10_numbers` | 10 numéros, k=5, t=3 → couverture 100% |
| `test_greedy_cover_deterministic` | Même entrée → même sortie |
| `test_coverage_matrix_calculation` | Matrice t-subsets correcte |
| `test_coverage_matrix_100_percent` | Full wheel → couverture 100% |
| `test_cost_estimator` | grid_count × grid_price = total_cost |
| `test_gain_analyzer_basic` | Scénarios de gain pour t=3 |
| `test_gain_analyzer_with_stars` | Scénarios EuroMillions (étoiles) |

#### Tests intégration (L2)

| Test | Vérifie |
|------|---------|
| `test_wheeling_service_preview` | Service retourne preview correct |
| `test_wheeling_service_generate_and_save` | Service génère et persiste en DB |
| `test_wheeling_service_history` | Historique filtré par user_id |
| `test_wheeling_service_delete` | Suppression + vérification |

#### Tests API (L3)

| Test | Vérifie |
|------|---------|
| `test_wheeling_preview_endpoint` | POST /wheeling/preview → 200 |
| `test_wheeling_generate_endpoint` | POST /wheeling/generate → 200 |
| `test_wheeling_validation_too_many` | n > 20 → 422 |
| `test_wheeling_history_requires_auth` | GET /wheeling/history sans auth → 401 |

### 2.2 — Budget (doc 09) — ~10 tests

#### Tests unitaires (L1)

| Test | Vérifie |
|------|---------|
| `test_budget_optimizer_3_strategies` | Retourne exactement 3 recommandations |
| `test_budget_max_grids_calculation` | budget / grid_price = max_grids |
| `test_budget_pareto_front` | Frontière Pareto correcte |

#### Tests intégration (L2)

| Test | Vérifie |
|------|---------|
| `test_budget_service_optimize` | Service complet avec DB |
| `test_budget_service_save_plan` | Sauvegarde et récupération plan |

#### Tests API (L3)

| Test | Vérifie |
|------|---------|
| `test_budget_optimize_endpoint` | POST /budget/optimize → 200 |
| `test_budget_validation_below_price` | budget < grid_price → 400 |
| `test_budget_plans_requires_auth` | GET /budget/plans sans auth → 401 |
| `test_budget_plan_delete_ownership` | DELETE plan d'un autre user → 403 |
| `test_budget_plan_detail` | GET /budget/plans/{id} → 200 |

### 2.3 — Comparateur (doc 10) — ~8 tests

#### Tests unitaires (L1)

| Test | Vérifie |
|------|---------|
| `test_comparison_2_strategies` | Compare top_n vs random → résultats |
| `test_comparison_all_axes` | 8 axes retournées |
| `test_comparison_radar_data` | Format compatible chart |

#### Tests intégration (L2)

| Test | Vérifie |
|------|---------|
| `test_comparison_service_stateless` | Pas de sauvegarde en DB |

#### Tests API (L3)

| Test | Vérifie |
|------|---------|
| `test_comparison_endpoint` | POST /comparison/compare → 200 |
| `test_comparison_validation_min_2` | < 2 stratégies → 422 |
| `test_comparison_validation_max_5` | > 5 stratégies → 422 |
| `test_comparison_invalid_strategy_type` | Type inconnu → 422 |

### 2.4 — Historique & Favoris (doc 11) — ~12 tests

#### Tests intégration (L2)

| Test | Vérifie |
|------|---------|
| `test_save_grid_result` | Sauvegarde type=grid |
| `test_save_portfolio_result` | Sauvegarde type=portfolio |
| `test_list_with_filters` | Filtre par type, favori, date |
| `test_duplicate_result` | Copie avec nouveau ID |
| `test_toggle_favorite` | is_favorite bascule |
| `test_update_tags` | Tags mis à jour |

#### Tests API (L3)

| Test | Vérifie |
|------|---------|
| `test_save_requires_auth` | POST /history/save sans auth → 401 |
| `test_list_only_own_results` | User A ne voit pas résultats User B |
| `test_delete_own_result` | DELETE → 200, GET → 404 |
| `test_delete_other_user_result` | DELETE autre user → 403 |
| `test_pagination_history` | limit/offset fonctionnel |
| `test_export_result` | POST /history/{id}/export → 200 |

### 2.5 — Explicabilité (doc 12) — ~10 tests

#### Tests unitaires (L1)

| Test | Vérifie |
|------|---------|
| `test_grid_explainer_l1` | Résumé 1 phrase |
| `test_grid_explainer_l2` | Interprétation 1 paragraphe |
| `test_grid_explainer_l3` | Détails techniques |
| `test_portfolio_explainer` | Explication portfolio |
| `test_wheeling_explainer` | Explication système réduit |
| `test_simulation_explainer` | Explication simulation |
| `test_comparison_explainer` | Explication comparaison |
| `test_template_rendering` | Templates français (pas de placeholder non résolu) |

#### Tests intégration (L2)

| Test | Vérifie |
|------|---------|
| `test_explanation_in_grid_response` | Champ explanation rempli |
| `test_explanation_in_portfolio_response` | Champ explanation rempli |

### 2.6 — Automatisation (doc 15) — ~10 tests

#### Tests unitaires (L1)

| Test | Vérifie |
|------|---------|
| `test_check_played_grid_match` | Grid vs draw → matched_numbers correct |
| `test_check_played_grid_no_match` | 0 numéros matchés → prize_rank = None |
| `test_determine_prize_rank` | 3 numéros + 1 chance → rang 5 Loto |
| `test_daily_suggestion_excludes_played` | Suggestion ≠ grilles récentes |

#### Tests intégration (L2)

| Test | Vérifie |
|------|---------|
| `test_check_played_grids_job` | Job crée GridDrawResult en DB |
| `test_notification_creation` | Job crée notification |
| `test_notification_mark_read` | PATCH → is_read = true |
| `test_notification_unread_count` | Count correct |

#### Tests API (L3)

| Test | Vérifie |
|------|---------|
| `test_notifications_requires_auth` | GET /notifications sans auth → 401 |
| `test_daily_suggestion_public` | GET /suggestions/daily → 200 |

### 2.7 — Dettes techniques — ~8 tests

| Test | Vérifie | DT |
|------|---------|-----|
| `test_rate_limiting_blocks` | 11ème requête en 1 min → 429 | DT-04 |
| `test_rate_limiting_resets` | Après 60s → OK | DT-04 |
| `test_token_blacklist_persistent` | Token blacklisté survit au redémarrage | DT-02 |
| `test_cleanup_expired_tokens` | Tokens expirés supprimés | DT-02 |
| `test_pagination_draws` | limit=10, offset=20 → correct | DT-05 |
| `test_pagination_grids` | limit=50 → max 50 résultats | DT-05 |
| `test_cache_hit` | 2ème appel stats → cache hit | DT-03 |
| `test_cache_invalidation` | Après compute_statistics → cache vidé | DT-03 |

---

## 3. Estimation totale

| Catégorie | Tests |
|-----------|-------|
| Wheeling | 16 |
| Budget | 10 |
| Comparateur | 8 |
| Historique | 12 |
| Explicabilité | 10 |
| Automatisation | 10 |
| Dettes techniques | 8 |
| **Total nouveaux tests** | **74** |
| Tests existants | 337 |
| **Total final** | **~411** |

---

## 4. Organisation des fichiers de test

```
backend/tests/
├── test_snapshots/             # SNAP-01 à SNAP-04 (non-régression)
├── test_contracts/             # Contrats API
├── test_benchmarks/            # Benchmarks performance
├── unit/
│   ├── test_wheeling_engine.py
│   ├── test_budget_optimizer.py
│   ├── test_comparison_service.py
│   ├── test_explainability.py
│   └── test_played_grid_check.py
├── integration/
│   ├── test_wheeling_service.py
│   ├── test_budget_service.py
│   ├── test_history_service.py
│   ├── test_notification_service.py
│   └── test_cache.py
├── api/
│   ├── test_wheeling_api.py
│   ├── test_budget_api.py
│   ├── test_comparison_api.py
│   ├── test_history_api.py
│   ├── test_notification_api.py
│   └── test_rate_limiting.py
└── fixtures/
    ├── reference_draws_100.json
    └── reference_scores.json
```

---

## 5. Fixtures partagées

### Fixture utilisateur

```python
@pytest.fixture
async def user_a(db):
    user = User(username="user_a", email="a@test.com", ...)
    db.add(user)
    await db.commit()
    return user

@pytest.fixture
async def user_b(db):
    user = User(username="user_b", email="b@test.com", ...)
    db.add(user)
    await db.commit()
    return user
```

### Fixture jeu

```python
@pytest.fixture
async def loto_fdj(db):
    game = GameDefinition(
        name="Loto FDJ", slug="loto-fdj",
        main_numbers_count=5, max_main_number=49,
        star_numbers_count=1, max_star_number=10,
        grid_price=2.20, is_active=True,
    )
    db.add(game)
    await db.commit()
    return game
```

### Fixture prize tiers

```python
@pytest.fixture
async def loto_prize_tiers(db, loto_fdj):
    tiers = [
        GamePrizeTier(game_id=loto_fdj.id, rank=1, name="5+Chance", match_numbers=5, match_stars=1, avg_prize=2000000, probability=0.0000000526),
        # ... 8 autres rangs
    ]
    db.add_all(tiers)
    await db.commit()
    return tiers
```

---

## 6. CI intégration

```yaml
# Extension du workflow CI
jobs:
  test:
    steps:
      - name: Run all tests
        run: pytest --tb=short -q --cov=app --cov-report=term-missing
      
      - name: Check coverage >= 80%
        run: |
          coverage=$(pytest --cov=app --cov-report=term | grep TOTAL | awk '{print $4}' | tr -d '%')
          if [ "$coverage" -lt 80 ]; then
            echo "Coverage $coverage% < 80%"
            exit 1
          fi
```

---

## 7. Checklist locale

- [ ] Créer 16 tests wheeling (unit/integration/API)
- [ ] Créer 10 tests budget (unit/integration/API)
- [ ] Créer 8 tests comparateur (unit/integration/API)
- [ ] Créer 12 tests historique (integration/API)
- [ ] Créer 10 tests explicabilité (unit/integration)
- [ ] Créer 10 tests automatisation (unit/integration/API)
- [ ] Créer 8 tests dettes techniques (rate limiting/cache/pagination/blacklist)
- [ ] Créer fixtures partagées (users, games, prize_tiers)
- [ ] Créer fixture reference_draws_100.json
- [ ] Organiser fichiers de test selon la structure proposée
- [ ] Ajouter couverture ≥ 80% dans CI gate
- [ ] Vérifier que les 411 tests passent et durent < 2 min

Réf. : [27_Checklist_Globale_Evolutions](./27_Checklist_Globale_Evolutions.md)
