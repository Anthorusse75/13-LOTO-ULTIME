# 10 — Moteur de Simulation

> **Projet** : LOTO ULTIME  
> **Version** : 1.0  
> **Date** : 2026-03-27  
> **Références croisées** : [07_Moteur_Statistique](07_Moteur_Statistique.md) · [08_Moteur_Scoring](08_Moteur_Scoring.md) · [09_Moteur_Optimisation](09_Moteur_Optimisation.md)

---

## 1. Rôle du Moteur de Simulation

Le moteur de simulation utilise des **simulations Monte Carlo** pour tester et valider les grilles et portefeuilles produits par les moteurs de scoring et d'optimisation.

**Objectifs** :
- Estimer la distribution du nombre de numéros corrects
- Évaluer la **robustesse** d'une grille (stabilité du score face à la variance)
- Comparer les performances de différentes stratégies
- Valider que les portefeuilles offrent une couverture effective

**Rappel scientifique** : Les simulations reproduisent l'aléa uniforme des tirages. Elles ne prédisent pas les résultats. Elles mesurent comment une stratégie se comporte *en moyenne* face à l'aléa pur.

---

## 2. Simulation Monte Carlo (`monte_carlo.py`)

### 2.1 Principe

Simuler $M$ tirages aléatoires uniformes et mesurer la performance d'une grille (ou portefeuille) sur ces tirages simulés.

### 2.2 Algorithme

```
ENTRÉE : grille G, configuration jeu, M simulations, seed
SORTIE : distribution des correspondances, métriques

compteurs ← {0: 0, 1: 0, ..., k: 0}
star_compteurs ← {0: 0, ..., s: 0}

POUR i = 1 À M :
    tirage ← tirage_aléatoire_uniforme(n, k)
    correspondances ← |G ∩ tirage|
    compteurs[correspondances] += 1
    
    SI étoiles :
        tirage_stars ← tirage_aléatoire_uniforme(n_stars, s)
        star_match ← |G_stars ∩ tirage_stars|
        star_compteurs[star_match] += 1

RETOURNER compteurs, star_compteurs, métriques
```

### 2.3 Implémentation

```python
class MonteCarloSimulator:
    def __init__(self, game: GameConfig, seed: int | None = None):
        self.game = game
        self.rng = np.random.default_rng(seed)
    
    def simulate_grid(
        self,
        grid: list[int],
        stars: list[int] | None,
        n_simulations: int = 10000,
    ) -> SimulationResult:
        k = self.game.numbers_drawn
        n = self.game.max_number - self.game.min_number + 1
        grid_set = set(grid)
        
        match_counts = np.zeros(k + 1, dtype=int)
        
        for _ in range(n_simulations):
            draw = set(self.rng.choice(
                range(self.game.min_number, self.game.max_number + 1),
                size=k,
                replace=False,
            ))
            matches = len(grid_set & draw)
            match_counts[matches] += 1
        
        # Étoiles
        star_match_counts = None
        if self.game.stars_pool and stars:
            s = self.game.stars_drawn
            star_match_counts = np.zeros(s + 1, dtype=int)
            star_set = set(stars)
            
            for _ in range(n_simulations):
                draw_stars = set(self.rng.choice(
                    range(1, self.game.stars_pool + 1),
                    size=s,
                    replace=False,
                ))
                star_matches = len(star_set & draw_stars)
                star_match_counts[star_matches] += 1
        
        return SimulationResult(
            grid=grid,
            stars=stars,
            n_simulations=n_simulations,
            match_distribution={
                i: int(match_counts[i]) for i in range(k + 1)
            },
            star_match_distribution={
                i: int(star_match_counts[i]) for i in range(s + 1)
            } if star_match_counts is not None else None,
            avg_matches=float(np.average(range(k + 1), weights=match_counts)),
            expected_matches=k * k / n,  # Attendu théorique
        )
```

### 2.4 Probabilités théoriques de correspondance

Pour $k$ numéros tirés parmi $n$, la probabilité d'avoir exactement $m$ correspondances :

$$P(X = m) = \frac{\binom{k}{m} \binom{n-k}{k-m}}{\binom{n}{k}}$$

C'est une distribution **hypergéométrique**.

| Matches | Loto FDJ ($k=5, n=49$) | EuroMillions ($k=5, n=50$) |
|---|---|---|
| 0 | 0.5086 | 0.5138 |
| 1 | 0.3690 | 0.3698 |
| 2 | 0.1027 | 0.1019 |
| 3 | 0.0183 | 0.0132 |
| 4 | 0.0010 | 0.0011 |
| 5 | 0.0000524 | 0.0000472 |

La simulation Monte Carlo doit **converger** vers ces valeurs théoriques (validation du simulateur).

---

## 3. Tests de Robustesse (`robustness.py`)

### 3.1 Stabilité du Score

Mesurer si le score d'une grille est stable à travers différents sous-échantillons de l'historique.

#### Méthode : Bootstrap

```
POUR b = 1 À B :
    historique_b ← échantillon_bootstrap(historique)
    stats_b ← calculer_statistiques(historique_b)
    score_b ← scorer(grille, stats_b)
    scores.ajouter(score_b)

stabilité ← 1 - coefficient_de_variation(scores)
```

```python
class RobustnessAnalyzer:
    def analyze_stability(
        self,
        grid: list[int],
        draws: np.ndarray,
        game: GameConfig,
        scorer: GridScorer,
        n_bootstrap: int = 100,
    ) -> StabilityResult:
        scores = []
        
        for _ in range(n_bootstrap):
            # Échantillon bootstrap
            indices = self.rng.choice(len(draws), size=len(draws), replace=True)
            bootstrap_draws = draws[indices]
            
            # Recalculer statistiques sur l'échantillon
            stats = self._compute_stats(bootstrap_draws, game)
            
            # Scorer la grille
            result = scorer.score(grid, stats, game)
            scores.append(result.total_score)
        
        scores = np.array(scores)
        
        return StabilityResult(
            mean_score=float(scores.mean()),
            std_score=float(scores.std()),
            cv=float(scores.std() / scores.mean()) if scores.mean() > 0 else float("inf"),
            stability=float(1 - min(scores.std() / scores.mean(), 1)) if scores.mean() > 0 else 0,
            ci_95=(float(np.percentile(scores, 2.5)), float(np.percentile(scores, 97.5))),
            min_score=float(scores.min()),
            max_score=float(scores.max()),
        )
```

### 3.2 Robustesse temporelle

Découper l'historique en fenêtres chronologiques et mesurer si le score est consistant :

```
historique = [fenêtre_1, fenêtre_2, ..., fenêtre_W]

POUR chaque fenêtre w :
    stats_w ← calculer_statistiques(fenêtre_w)
    score_w ← scorer(grille, stats_w)

consistance ← 1 - std(scores) / mean(scores)
```

### 3.3 Comparaison avec l'aléatoire

Comparer la performance d'une grille optimisée avec des grilles aléatoires :

```python
def compare_with_random(
    self,
    grid: ScoredResult,
    game: GameConfig,
    scorer: GridScorer,
    statistics: StatisticsSnapshot,
    n_random: int = 10000,
) -> ComparisonResult:
    random_scores = []
    
    for _ in range(n_random):
        random_grid = sorted(self.rng.choice(
            range(game.min_number, game.max_number + 1),
            size=game.numbers_drawn,
            replace=False,
        ).tolist())
        result = scorer.score(random_grid, statistics, game)
        random_scores.append(result.total_score)
    
    random_scores = np.array(random_scores)
    
    percentile = float((random_scores < grid.total_score).mean() * 100)
    
    return ComparisonResult(
        grid_score=grid.total_score,
        random_mean=float(random_scores.mean()),
        random_std=float(random_scores.std()),
        percentile=percentile,
        z_score=float((grid.total_score - random_scores.mean()) / random_scores.std())
        if random_scores.std() > 0 else 0,
    )
```

---

## 4. Simulation de Portefeuille

### 4.1 Couverture effective

Simuler $M$ tirages et mesurer combien de grilles du portefeuille ont au moins $m$ correspondances :

```python
def simulate_portfolio(
    self,
    portfolio: list[list[int]],
    n_simulations: int = 10000,
    min_matches: int = 2,
) -> PortfolioSimulationResult:
    hits = 0  # Nombre de simulations avec au moins un "hit"
    
    for _ in range(n_simulations):
        draw = set(self.rng.choice(
            range(self.game.min_number, self.game.max_number + 1),
            size=self.game.numbers_drawn,
            replace=False,
        ))
        
        for grid in portfolio:
            if len(set(grid) & draw) >= min_matches:
                hits += 1
                break
    
    return PortfolioSimulationResult(
        n_simulations=n_simulations,
        hit_rate=hits / n_simulations,
        min_matches_threshold=min_matches,
    )
```

### 4.2 Distribution des gains simulés

Pour chaque simulation, calculer le nombre de correspondances de **chaque grille** du portefeuille.

---

## 5. Validation du Simulateur

### 5.1 Tests de convergence

Vérifier que les fréquences simulées convergent vers les probabilités théoriques (loi hypergéométrique) :

$$|\hat{P}(X=m) - P(X=m)| < \epsilon$$

pour $M$ suffisamment grand.

### 5.2 Tests de reproductibilité

Avec le même `seed`, les résultats doivent être identiques.

### 5.3 Test du Chi-2

$$\chi^2 = \sum_{m=0}^{k} \frac{(O_m - E_m)^2}{E_m}$$

avec $O_m$ les occurrences observées et $E_m = M \cdot P(X=m)$.

---

## 6. Structures de Résultat

```python
@dataclass
class SimulationResult:
    grid: list[int]
    stars: list[int] | None
    n_simulations: int
    match_distribution: dict[int, int]
    star_match_distribution: dict[int, int] | None
    avg_matches: float
    expected_matches: float

@dataclass
class StabilityResult:
    mean_score: float
    std_score: float
    cv: float               # Coefficient de variation
    stability: float         # 1 - CV (∈ [0, 1])
    ci_95: tuple[float, float]
    min_score: float
    max_score: float

@dataclass
class ComparisonResult:
    grid_score: float
    random_mean: float
    random_std: float
    percentile: float        # Position dans la distribution aléatoire
    z_score: float           # Écart normalisé
```

---

## 7. Références

| Document | Contenu |
|---|---|
| [07_Moteur_Statistique](07_Moteur_Statistique.md) | Données statistiques |
| [08_Moteur_Scoring](08_Moteur_Scoring.md) | Fonction de scoring |
| [09_Moteur_Optimisation](09_Moteur_Optimisation.md) | Grilles à valider |
| [14_Performance](14_Performance_et_Scalabilite.md) | Performance des simulations |
| [16_Strategie_Tests](16_Strategie_Tests.md) | Tests de convergence |

---

*Fin du document 10_Moteur_Simulation.md*
