# 09 — Moteur d'Optimisation

> **Projet** : LOTO ULTIME  
> **Version** : 1.0  
> **Date** : 2026-03-27  
> **Références croisées** : [08_Moteur_Scoring](08_Moteur_Scoring.md) · [07_Moteur_Statistique](07_Moteur_Statistique.md) · [10_Moteur_Simulation](10_Moteur_Simulation.md)

---

## 1. Rôle du Moteur d'Optimisation

Le moteur d'optimisation explore l'espace combinatoire des grilles possibles pour trouver celles qui maximisent le score multicritère. Il utilise des **méta-heuristiques** car l'espace est trop grand pour une recherche exhaustive.

**Objectif** : Trouver les $n$ meilleures grilles selon la fonction de scoring.

**Espace de recherche** :
- Loto FDJ : $\binom{49}{5} = 1\,906\,884$ combinaisons
- EuroMillions : $\binom{50}{5} = 2\,118\,760$ combinaisons de numéros

---

## 2. Méta-heuristiques Implémentées

### 2.1 Recuit Simulé (`simulated_annealing.py`)

#### Principe

Partant d'une solution aléatoire, explorer le voisinage en acceptant parfois des solutions moins bonnes (pour éviter les optima locaux), avec une probabilité décroissante au fil du temps (température).

#### Algorithme

```
T ← T_initial
G ← grille_aléatoire()
meilleur ← G

POUR i = 1 À max_iterations :
    G' ← voisin(G)
    ΔE ← Score(G') - Score(G)
    
    SI ΔE > 0 :
        G ← G'
    SINON :
        SI random() < exp(ΔE / T) :
            G ← G'
    
    SI Score(G) > Score(meilleur) :
        meilleur ← G
    
    T ← T × cooling_rate

RETOURNER meilleur
```

#### Paramètres

| Paramètre | Défaut | Description |
|---|---|---|
| `T_initial` | 1.0 | Température initiale |
| `T_min` | 0.001 | Température minimale |
| `cooling_rate` | 0.9995 | Facteur de refroidissement |
| `max_iterations` | 50000 | Nombre d'itérations max |

#### Fonction de voisinage

Un voisin est obtenu en remplaçant un numéro aléatoire par un autre numéro valide non présent dans la grille.

```python
class SimulatedAnnealing:
    def __init__(
        self,
        scorer: GridScorer,
        statistics: StatisticsSnapshot,
        game: GameConfig,
        t_initial: float = 1.0,
        t_min: float = 0.001,
        cooling_rate: float = 0.9995,
        max_iterations: int = 50000,
        seed: int | None = None,
    ):
        self.scorer = scorer
        self.statistics = statistics
        self.game = game
        self.t_initial = t_initial
        self.t_min = t_min
        self.cooling_rate = cooling_rate
        self.max_iterations = max_iterations
        self.rng = np.random.default_rng(seed)
    
    def _random_grid(self) -> list[int]:
        return sorted(self.rng.choice(
            range(self.game.min_number, self.game.max_number + 1),
            size=self.game.numbers_drawn,
            replace=False,
        ).tolist())
    
    def _neighbor(self, grid: list[int]) -> list[int]:
        new_grid = grid.copy()
        idx = self.rng.integers(0, len(new_grid))
        available = [
            n for n in range(self.game.min_number, self.game.max_number + 1)
            if n not in new_grid
        ]
        new_grid[idx] = self.rng.choice(available)
        return sorted(new_grid)
    
    def optimize(self, n_grids: int = 10) -> list[ScoredResult]:
        best_results = []
        
        for _ in range(n_grids):
            grid = self._random_grid()
            current_score = self.scorer.score(grid, self.statistics, self.game)
            best = current_score
            T = self.t_initial
            
            for _ in range(self.max_iterations):
                if T < self.t_min:
                    break
                
                neighbor = self._neighbor(grid)
                neighbor_score = self.scorer.score(neighbor, self.statistics, self.game)
                
                delta = neighbor_score.total_score - current_score.total_score
                
                if delta > 0 or self.rng.random() < np.exp(delta / T):
                    grid = neighbor
                    current_score = neighbor_score
                
                if current_score.total_score > best.total_score:
                    best = current_score
                
                T *= self.cooling_rate
            
            best_results.append(best)
        
        best_results.sort(key=lambda r: -r.total_score)
        return best_results
```

---

### 2.2 Algorithme Génétique (`genetic_algorithm.py`)

#### Principe

Population de grilles qui évolue par sélection, croisement et mutation.

#### Algorithme

```
population ← initialiser_population(pop_size)
évaluer(population)

POUR gen = 1 À max_generations :
    parents ← sélection_tournoi(population)
    enfants ← []
    
    POUR chaque paire de parents :
        enfant ← croisement(parent1, parent2)
        enfant ← mutation(enfant, taux_mutation)
        enfants.ajouter(enfant)
    
    population ← élitisme(population, enfants)
    évaluer(population)

RETOURNER top_n(population)
```

#### Opérateurs génétiques

**Croisement** : Combiner les numéros de deux parents.

```python
def crossover(self, parent1: list[int], parent2: list[int]) -> list[int]:
    """Crossover uniforme avec résolution de conflits."""
    combined = list(set(parent1) | set(parent2))
    # Sélection probabiliste pondérée par le score individuel des numéros
    child = sorted(self.rng.choice(combined, size=self.game.numbers_drawn, replace=False).tolist())
    return child
```

**Mutation** : Remplacer un numéro aléatoirement.

```python
def mutate(self, grid: list[int], rate: float = 0.1) -> list[int]:
    """Mutation : remplacement d'un numéro avec probabilité `rate`."""
    new_grid = grid.copy()
    for i in range(len(new_grid)):
        if self.rng.random() < rate:
            available = [
                n for n in range(self.game.min_number, self.game.max_number + 1)
                if n not in new_grid
            ]
            new_grid[i] = self.rng.choice(available)
    return sorted(new_grid)
```

**Sélection tournoi** :

```python
def tournament_selection(self, population: list, tournament_size: int = 3) -> list:
    selected = []
    for _ in range(len(population)):
        tournament = self.rng.choice(population, size=tournament_size, replace=False)
        winner = max(tournament, key=lambda x: x.total_score)
        selected.append(winner)
    return selected
```

#### Paramètres

| Paramètre | Défaut | Description |
|---|---|---|
| `population_size` | 200 | Taille de la population |
| `max_generations` | 500 | Nombre de générations |
| `mutation_rate` | 0.1 | Probabilité de mutation par gène |
| `crossover_rate` | 0.8 | Probabilité de croisement |
| `elite_size` | 10 | Nombre d'individus conservés |
| `tournament_size` | 3 | Taille du tournoi de sélection |

---

### 2.3 Recherche Tabou (`tabu_search.py`)

#### Principe

Exploration du voisinage en interdisant le retour aux solutions récemment visitées (liste tabou).

#### Algorithme

```
G ← grille_initiale()
meilleur ← G
tabou_list ← []

POUR i = 1 À max_iterations :
    voisins ← générer_voisins(G, n_voisins)
    voisins ← filtrer_non_tabou(voisins, tabou_list)
    
    G' ← meilleur_voisin(voisins)
    
    tabou_list.ajouter(G')
    SI |tabou_list| > taille_tabou :
        tabou_list.retirer_plus_ancien()
    
    SI Score(G') > Score(meilleur) :
        meilleur ← G'
    
    G ← G'

RETOURNER meilleur
```

#### Paramètres

| Paramètre | Défaut | Description |
|---|---|---|
| `max_iterations` | 10000 | Itérations max |
| `tabu_size` | 100 | Taille de la liste tabou |
| `n_neighbors` | 20 | Voisins générés par itération |

---

### 2.4 Hill Climbing (`hill_climbing.py`)

#### Principe

Recherche locale simple : à chaque étape, se déplacer vers le meilleur voisin. Version avec redémarrage aléatoire pour échapper aux optima locaux.

#### Algorithme

```
meilleur_global ← null

POUR restart = 1 À n_restarts :
    G ← grille_aléatoire()
    amélioré ← vrai
    
    TANT QUE amélioré :
        amélioré ← faux
        POUR chaque voisin G' de G :
            SI Score(G') > Score(G) :
                G ← G'
                amélioré ← vrai
    
    SI Score(G) > Score(meilleur_global) :
        meilleur_global ← G

RETOURNER meilleur_global
```

#### Paramètres

| Paramètre | Défaut | Description |
|---|---|---|
| `n_restarts` | 100 | Nombre de redémarrages |
| `max_no_improve` | 50 | Arrêt si pas d'amélioration |

---

### 2.5 Optimisation Multi-Objectifs (`multi_objective.py`)

#### Principe

Optimiser simultanément plusieurs objectifs potentiellement conflictuels via le concept de **front de Pareto**.

#### Objectifs

1. **Maximiser le score total**
2. **Maximiser la diversité** (distance avec les grilles déjà sélectionnées)
3. **Maximiser la couverture** (nombre de numéros distincts couverts)

#### Dominance de Pareto

Une grille $G_1$ **domine** $G_2$ si $G_1$ est au moins aussi bonne sur tous les objectifs et strictement meilleure sur au moins un.

#### Front de Pareto

Ensemble des grilles non dominées.

#### Algorithme NSGA-II simplifié

```python
class MultiObjectiveOptimizer:
    def optimize(self, n_grids: int) -> list[ScoredResult]:
        population = self._init_population(n_grids * 10)
        
        for gen in range(self.max_generations):
            offspring = self._create_offspring(population)
            combined = population + offspring
            
            # Tri par fronts de Pareto
            fronts = self._non_dominated_sort(combined)
            
            # Sélection par crowding distance
            new_population = []
            for front in fronts:
                if len(new_population) + len(front) <= len(population):
                    new_population.extend(front)
                else:
                    remaining = len(population) - len(new_population)
                    crowding = self._crowding_distance(front)
                    sorted_front = sorted(
                        zip(front, crowding),
                        key=lambda x: -x[1],
                    )
                    new_population.extend([f for f, _ in sorted_front[:remaining]])
                    break
            
            population = new_population
        
        return self._extract_top(population, n_grids)
```

---

## 3. Théorie des Codes Correcteurs

### 3.1 Application

Les concepts des codes correcteurs sont utilisés pour **maximiser la distance entre grilles** dans un portefeuille, réduisant la corrélation et améliorant la couverture.

### 3.2 Distance de Hamming entre grilles

Deux grilles sont représentées comme vecteurs binaires de taille $n$ :

$$\text{grid\_vector}(G) \in \{0, 1\}^n$$

où $\text{grid\_vector}(G)_i = 1$ si $i \in G$.

$$d_H(G_1, G_2) = \sum_{i=1}^{n} |G_1[i] - G_2[i]|$$

### 3.3 Distance d'intersection

$$d_{inter}(G_1, G_2) = k - |G_1 \cap G_2|$$

### 3.4 Distance minimum d'un portefeuille

$$d_{min}(P) = \min_{G_i, G_j \in P, i \neq j} d_H(G_i, G_j)$$

**Objectif** : Maximiser $d_{min}(P)$.

---

## 4. Optimisation de Portefeuille (`portfolio_optimizer.py`)

### 4.1 Objectifs

| Objectif | Métrique | Cible |
|---|---|---|
| Diversité | Min Hamming distance | Maximiser |
| Couverture | Numéros distincts couverts / n | Maximiser |
| Qualité | Score moyen des grilles | Maximiser |
| Anti-corrélation | Corrélation maximale entre grilles | Minimiser |

### 4.2 Fonction objectif composite

$$F(P) = \lambda_1 \cdot \bar{S}(P) + \lambda_2 \cdot \text{Div}(P) + \lambda_3 \cdot \text{Cov}(P) - \lambda_4 \cdot \text{Corr}(P)$$

### 4.3 Stratégies prédéfinies

| Stratégie | $\lambda_1$ | $\lambda_2$ | $\lambda_3$ | $\lambda_4$ | Description |
|---|---|---|---|---|---|
| `balanced` | 0.30 | 0.25 | 0.25 | 0.20 | Équilibre entre tous les objectifs |
| `max_diversity` | 0.15 | 0.45 | 0.25 | 0.15 | Maximise la distance entre grilles |
| `max_coverage` | 0.15 | 0.15 | 0.55 | 0.15 | Couvre un maximum de numéros |
| `min_correlation` | 0.20 | 0.20 | 0.20 | 0.40 | Minimise les doublons entre grilles |

### 4.4 Algorithme glouton amélioré

```python
class PortfolioOptimizer:
    def optimize(self, candidate_grids: list[ScoredResult], target_size: int, strategy: str) -> Portfolio:
        weights = self.STRATEGY_WEIGHTS[strategy]
        
        # Commencer avec la meilleure grille
        portfolio = [candidate_grids[0]]
        remaining = candidate_grids[1:]
        
        while len(portfolio) < target_size and remaining:
            best_candidate = None
            best_marginal_value = -float("inf")
            
            for candidate in remaining:
                # Calculer la valeur marginale d'ajout
                marginal = self._marginal_value(portfolio, candidate, weights)
                
                if marginal > best_marginal_value:
                    best_marginal_value = marginal
                    best_candidate = candidate
            
            portfolio.append(best_candidate)
            remaining.remove(best_candidate)
        
        return self._build_portfolio(portfolio, strategy)
    
    def _marginal_value(self, portfolio, candidate, weights):
        """Valeur marginale d'ajouter candidate au portfolio."""
        score_component = weights[0] * candidate.total_score
        
        # Diversité : distance min avec les grilles existantes
        min_distance = min(
            self._hamming_distance(candidate.numbers, g.numbers)
            for g in portfolio
        )
        diversity_component = weights[1] * (min_distance / (2 * self.game.numbers_drawn))
        
        # Couverture : nouveaux numéros apportés
        existing_numbers = set()
        for g in portfolio:
            existing_numbers.update(g.numbers)
        new_numbers = len(set(candidate.numbers) - existing_numbers)
        coverage_component = weights[2] * (new_numbers / self.game.numbers_drawn)
        
        # Anti-corrélation
        max_overlap = max(
            len(set(candidate.numbers) & set(g.numbers))
            for g in portfolio
        )
        correlation_component = weights[3] * (max_overlap / self.game.numbers_drawn)
        
        return score_component + diversity_component + coverage_component - correlation_component
```

---

## 5. Sélection Automatique de Méthode

Le mode `auto` sélectionne la méthode optimale selon le contexte :

```python
def select_method(game: GameConfig, n_grids: int, time_budget: float) -> str:
    space_size = comb(game.numbers_pool, game.numbers_drawn, exact=True)
    
    if space_size < 100_000 and time_budget > 10:
        return "exhaustive"  # Recherche exhaustive faisable
    elif n_grids <= 5 and time_budget > 5:
        return "simulated_annealing"  # Meilleure convergence pour peu de grilles
    elif n_grids >= 20:
        return "genetic_algorithm"  # Meilleur pour populations
    else:
        return "genetic_algorithm"  # Défaut
```

---

## 6. Références

| Document | Contenu |
|---|---|
| [07_Moteur_Statistique](07_Moteur_Statistique.md) | Données d'entrée |
| [08_Moteur_Scoring](08_Moteur_Scoring.md) | Fonction objectif |
| [10_Moteur_Simulation](10_Moteur_Simulation.md) | Validation des résultats |
| [14_Performance](14_Performance_et_Scalabilite.md) | Performance des algorithmes |

---

*Fin du document 09_Moteur_Optimisation.md*
