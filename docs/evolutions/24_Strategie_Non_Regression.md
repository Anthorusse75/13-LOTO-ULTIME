# 24 — Stratégie de Non-Régression

> Plan complet pour garantir que chaque évolution ne casse rien de l'existant : tests avant/après, snapshots, métriques de référence.

---

## Références croisées

- [00_Index_Evolutions](./00_Index_Evolutions.md)
- [16_Strategie_Tests](../16_Strategie_Tests.md) — Tests existants
- [03_Audit_Existant_et_Ecarts](./03_Audit_Existant_et_Ecarts.md) — Bugs à corriger
- [25_Strategie_Tests_Evolutions](./25_Strategie_Tests_Evolutions.md) — Tests des nouvelles features

---

## 1. État actuel des tests

### Métriques

| Métrique | Valeur |
|----------|--------|
| Tests total | 337 |
| Couverture | ~75% |
| Durée totale | ~45s |
| Framework | pytest + pytest-asyncio |
| DB de test | aiosqlite (in-memory) |
| CI | GitHub Actions |

### Répartition

| Catégorie | Nombre | Note |
|-----------|--------|------|
| Unit tests engines/ | ~180 | Bien couverts |
| Unit tests services/ | ~60 | Correct |
| Tests API (routers/) | ~70 | FastAPI TestClient |
| Tests scrapers | ~15 | Mocks HTTP |
| Tests scheduler | ~12 | Basiques |

---

## 2. Définition de la non-régression

### Qu'est-ce qui ne doit PAS changer ?

| Invariant | Mesure |
|-----------|--------|
| Le scoring d'une grille donnée est identique avant/après | Snapshot test |
| Les statistiques pour un jeu de données fixe sont identiques | Snapshot test |
| Le portfolio optimisé est reproductible (seed fixe) | Snapshot test |
| Les endpoints existants retournent les mêmes structures | Contract test |
| Les temps de réponse ne dégradent pas de > 20% | Benchmark test |
| Les 337 tests existants passent | CI gate |

---

## 3. Tests snapshot (valeur de référence)

### Principe

Avant chaque phase de développement, capturer les sorties de référence et les comparer après la modification.

### Snapshots à créer

#### SNAP-01 : Scoring de grilles de référence

```python
# test_snapshots/test_scoring_snapshot.py

REFERENCE_GRIDS = [
    {"numbers": [1, 7, 12, 23, 45], "stars": [3, 8], "game": "loto_fdj"},
    {"numbers": [5, 15, 25, 35, 45], "stars": [1, 10], "game": "euromillions"},
    {"numbers": [2, 14, 28, 36, 49], "stars": [5], "game": "loto_fdj"},
]

async def test_scoring_stability():
    for ref in REFERENCE_GRIDS:
        score = await score_grid(ref["numbers"], ref["stars"], ref["game"])
        # Comparer avec snapshot stocké
        assert abs(score.total - EXPECTED_SCORES[ref]) < 0.001
        for criterion, value in score.details.items():
            assert abs(value - EXPECTED_DETAILS[ref][criterion]) < 0.001
```

#### SNAP-02 : Statistiques pour dataset fixe

```python
# Fixture : 100 tirages fixés (fichier JSON)
# Calculer fréquences, gaps, cooccurrences
# Comparer avec snapshot

async def test_statistics_stability():
    draws = load_fixture("reference_draws_100.json")
    stats = await compute_statistics(draws, game_id=1)
    assert stats.frequencies == EXPECTED_FREQUENCIES
    assert stats.gaps == EXPECTED_GAPS
```

#### SNAP-03 : Portfolio avec seed fixe

```python
async def test_portfolio_stability():
    result = await optimize_portfolio(game_id=1, method="genetic", seed=42)
    assert len(result.grids) == EXPECTED_GRID_COUNT
    assert abs(result.expected_score - EXPECTED_SCORE) < 0.01
```

#### SNAP-04 : Simulation Monte Carlo avec seed fixe

```python
async def test_simulation_stability():
    result = await run_monte_carlo(grid=[1,7,12,23,45], iterations=1000, seed=42)
    assert abs(result.mean_score - EXPECTED_MEAN) < 0.01
    assert abs(result.std_score - EXPECTED_STD) < 0.01
```

---

## 4. Tests de contrat API

### Principe

Vérifier que la structure des réponses API ne change pas (champs, types, nullable).

```python
# test_contracts/test_api_contracts.py

async def test_grids_generate_contract(client):
    response = await client.post("/api/v1/grids/generate", json={
        "game_id": 1, "count": 5
    })
    assert response.status_code == 200
    data = response.json()
    
    # Champs obligatoires existants — ne doivent pas disparaître
    for grid in data["grids"]:
        assert "main_numbers" in grid
        assert "star_numbers" in grid
        assert "score" in grid
        assert "scoring_details" in grid
        assert isinstance(grid["main_numbers"], list)
        assert isinstance(grid["score"], (int, float))

async def test_statistics_contract(client):
    response = await client.get("/api/v1/statistics/frequencies?game_id=1")
    assert response.status_code == 200
    data = response.json()
    assert "frequencies" in data
    assert isinstance(data["frequencies"], dict)
```

### Endpoints à couvrir

| Endpoint | Champs critiques |
|----------|-----------------|
| GET /draws | draw_date, main_numbers, star_numbers |
| GET /statistics/* | frequencies, gaps, cooccurrence_matrix |
| POST /grids/generate | grids[].main_numbers, .score, .scoring_details |
| POST /simulations/monte-carlo | results, mean_score, std_score |
| POST /portfolios/optimize | grids, expected_score, diversity_score |

---

## 5. Tests de performance de référence

### Benchmarks à capturer

```python
# test_benchmarks/test_performance.py
import time

async def test_grid_generation_perf():
    start = time.perf_counter()
    await generate_grids(game_id=1, count=10)
    duration = time.perf_counter() - start
    assert duration < 2.0  # Max 2 secondes

async def test_statistics_perf():
    start = time.perf_counter()
    await compute_statistics(game_id=1)
    duration = time.perf_counter() - start
    assert duration < 1.0  # Max 1 seconde

async def test_portfolio_perf():
    start = time.perf_counter()
    await optimize_portfolio(game_id=1)
    duration = time.perf_counter() - start
    assert duration < 10.0  # Max 10 secondes
```

### Métriques de référence à capter

| Opération | Référence actuelle | Seuil max |
|-----------|-------------------|-----------|
| Generate 10 grids | ~500ms | 2s |
| Compute statistics | ~80ms | 1s |
| Optimize portfolio | ~3s | 10s |
| Monte Carlo 1000 iter | ~2s | 8s |
| GET /draws | ~50ms | 200ms |

---

## 6. Processus de non-régression par phase

### Avant chaque phase

1. **Capturer snapshots** : Exécuter `pytest test_snapshots/` et commit les fichiers de référence
2. **Capturer benchmarks** : Exécuter `pytest test_benchmarks/` et noter les durées
3. **Lancer suite complète** : `pytest` → 337 tests doivent passer

### Pendant le développement

4. **Développer la feature** en création (nouveaux fichiers)
5. **Lancer les tests existants** fréquemment
6. **Si un test existant casse** : STOP. Corriger avant de continuer.

### Après la phase

7. **Re-exécuter snapshots** : Comparer avec valeurs de référence
8. **Re-exécuter benchmarks** : Vérifier pas de dégradation > 20%
9. **Re-exécuter suite complète** : 337 + nouveaux tests doivent passer
10. **Mise à jour des snapshots** si changement intentionnel (documenter pourquoi)

---

## 7. Non-régression pour BUG-01 (multi-lottery)

### Risque spécifique

La correction de BUG-01 (propager game_id) touche de nombreux fichiers. Risque de régression sur le scoring Loto FDJ (game_id=1), qui est le jeu par défaut aujourd'hui.

### Plan de test spécifique

```
1. Avant fix : capturer les scores de 100 grilles Loto FDJ
2. Appliquer le fix BUG-01
3. Après fix : recalculer les mêmes 100 grilles avec game_id=1
4. Compare : les scores doivent être identiques (delta < 0.001)
5. Test additionnel : calculer pour game_id=2 (EuroMillions)
6. Vérifier que EuroMillions produit des scores différents (adaptés au jeu)
```

---

## 8. Non-régression pour BUG-02 (method_selector)

### Plan de test

```
1. Avant fix : noter que method_selector retourne toujours "genetic"
2. Appliquer le fix
3. Après fix : tester avec différents paramètres → méthodes variées
4. Vérifier que la méthode "genetic" est toujours disponible et fonctionne
5. Vérifier que les autres méthodes (simulated_annealing, tabu, etc.) fonctionnent
```

---

## 9. CI Gate

### Pipeline CI existant

```yaml
# .github/workflows/ci.yml
jobs:
  test:
    steps:
      - run: pytest --tb=short -q
      # 337 tests doivent passer
```

### Ajout recommandé

```yaml
  test:
    steps:
      - run: pytest --tb=short -q
      - run: pytest test_snapshots/ -v
      - run: pytest test_contracts/ -v
      # Benchmarks : en option (pas bloquant sur CI, trop dépendant du hardware)
```

---

## 10. Checklist locale

- [ ] Créer dossier test_snapshots/ avec SNAP-01 à SNAP-04
- [ ] Générer fichiers de référence (expected_scores, expected_frequencies)
- [ ] Créer fixture reference_draws_100.json (100 tirages fixés)
- [ ] Créer dossier test_contracts/ avec contrats API
- [ ] Créer dossier test_benchmarks/ avec benchmarks de performance
- [ ] Capturer métriques de référence actuelles
- [ ] Ajouter test_snapshots et test_contracts dans CI
- [ ] Plan de test spécifique BUG-01 avant/après
- [ ] Plan de test spécifique BUG-02 avant/après
- [ ] Documenter le process de non-régression dans README
- [ ] S'assurer que les 337 tests existants passent avant toute modification

Réf. : [27_Checklist_Globale_Evolutions](./27_Checklist_Globale_Evolutions.md)
