# 08 — Moteur de Scoring

> **Projet** : LOTO ULTIME  
> **Version** : 1.0  
> **Date** : 2026-03-27  
> **Références croisées** : [07_Moteur_Statistique](07_Moteur_Statistique.md) · [09_Moteur_Optimisation](09_Moteur_Optimisation.md) · [05_Modele](05_Modele_Donnees.md)

---

## 1. Rôle du Moteur de Scoring

Le moteur de scoring évalue la **qualité heuristique** d'une grille en combinant plusieurs critères statistiques en un score unique normalisé.

**Entrée** : Une grille (combinaison de numéros) + StatisticsSnapshot  
**Sortie** : Un score total $\in [0, 1]$ + détail par critère

---

## 2. Formule Globale

$$\text{Score}(G) = \sum_{c=1}^{C} w_c \cdot S_c(G) - w_{penalty} \cdot P(G)$$

Avec :
- $G$ : la grille évaluée
- $S_c(G)$ : score du critère $c$ pour la grille $G$ (normalisé $\in [0, 1]$)
- $w_c$ : poids du critère $c$ ($w_c > 0$, $\sum w_c = 1$)
- $P(G)$ : pénalité de motif ($\in [0, 1]$)

### Critères

| # | Critère | Identifiant | Poids par défaut | Description |
|---|---|---|---|---|
| 1 | Fréquence | `frequency` | 0.20 | Favorise les numéros fréquemment tirés |
| 2 | Retard | `gap` | 0.20 | Favorise les numéros avec un retard significatif |
| 3 | Cooccurrence | `cooccurrence` | 0.15 | Favorise les paires/triplets ayant une forte affinité |
| 4 | Structure | `structure` | 0.15 | Évalue la répartition structurelle (pair/impair, décades) |
| 5 | Équilibre | `balance` | 0.20 | Évalue la distribution spatiale sur l'ensemble des numéros |
| 6 | Pénalité motif | `pattern_penalty` | 0.10 | Pénalise les motifs trop réguliers (suites, multiples) |

---

## 3. Détail des Critères

### 3.1 Score Fréquence (`frequency_score.py`)

Évalue si les numéros de la grille sont des numéros fréquemment tirés.

$$S_{freq}(G) = \frac{1}{k} \sum_{i \in G} \text{norm}(R_i)$$

avec $R_i$ le ratio de fréquence et $\text{norm}$ une normalisation min-max sur tous les numéros.

```python
class FrequencyScoreCriterion:
    def compute(self, grid: list[int], frequencies: dict, game: GameConfig) -> float:
        """Score basé sur les fréquences relatives des numéros."""
        ratios = []
        all_ratios = [frequencies[n]["ratio"] for n in range(game.min_number, game.max_number + 1)]
        min_r, max_r = min(all_ratios), max(all_ratios)
        range_r = max_r - min_r if max_r > min_r else 1
        
        for num in grid:
            ratio = frequencies[num]["ratio"]
            normalized = (ratio - min_r) / range_r
            ratios.append(normalized)
        
        return sum(ratios) / len(ratios)
```

---

### 3.2 Score Retard (`gap_score.py`)

Favorise les numéros dont le retard courant est significatif par rapport à leur retard moyen.

$$S_{gap}(G) = \frac{1}{k} \sum_{i \in G} \text{sigmoid}\left(\frac{G_i^{current} - \bar{G}_i}{\bar{G}_i}\right)$$

La sigmoïde compresse le ratio dans $[0, 1]$ :

$$\text{sigmoid}(x) = \frac{1}{1 + e^{-\alpha x}}$$

avec $\alpha$ un paramètre de sensibilité (défaut : 3).

```python
class GapScoreCriterion:
    def __init__(self, sensitivity: float = 3.0):
        self.sensitivity = sensitivity
    
    def compute(self, grid: list[int], gaps: dict, game: GameConfig) -> float:
        scores = []
        for num in grid:
            gap_data = gaps[num]
            current = gap_data["current_gap"]
            avg = gap_data["avg_gap"]
            
            if avg > 0:
                ratio = (current - avg) / avg
                score = 1 / (1 + np.exp(-self.sensitivity * ratio))
            else:
                score = 0.5
            
            scores.append(score)
        
        return sum(scores) / len(scores)
```

**Interprétation** :
- Si le retard courant est très supérieur à la moyenne → score élevé (numéro "dû")
- Si le retard courant est inférieur à la moyenne → score faible

**Note scientifique** : Le concept de numéro "dû" est un biais cognitif (gambler's fallacy). Le score l'utilise comme heuristique, pas comme prédiction.

---

### 3.3 Score Cooccurrence (`cooccurrence_score.py`)

Évalue si les paires de numéros dans la grille ont une forte affinité historique.

$$S_{cooc}(G) = \frac{1}{\binom{k}{2}} \sum_{\{i,j\} \subset G} \text{norm}(A_{ij})$$

```python
class CooccurrenceScoreCriterion:
    def compute(self, grid: list[int], cooccurrences: dict, game: GameConfig) -> float:
        pairs = cooccurrences.get("pairs", {})
        
        # Collecter toutes les affinités pour normalisation
        all_affinities = [v["affinity"] for v in pairs.values()]
        if not all_affinities:
            return 0.5
        
        min_a, max_a = min(all_affinities), max(all_affinities)
        range_a = max_a - min_a if max_a > min_a else 1
        
        pair_scores = []
        sorted_grid = sorted(grid)
        for i in range(len(sorted_grid)):
            for j in range(i + 1, len(sorted_grid)):
                key = f"{sorted_grid[i]}-{sorted_grid[j]}"
                if key in pairs:
                    affinity = pairs[key]["affinity"]
                    normalized = (affinity - min_a) / range_a
                    pair_scores.append(normalized)
                else:
                    pair_scores.append(0.5)  # Neutre si pas de données
        
        return sum(pair_scores) / len(pair_scores) if pair_scores else 0.5
```

---

### 3.4 Score Structure (`structure_score.py`)

Évalue la qualité structurelle de la grille.

#### Sous-critères

| Sous-critère | Cible optimale | Poids interne |
|---|---|---|
| Ratio pair/impair | Proche de $k/2$ | 0.30 |
| Répartition par décade | Uniforme | 0.30 |
| Ratio bas/haut | Proche de $k/2$ | 0.20 |
| Écarts entre numéros consécutifs | Variés (pas de clusters) | 0.20 |

```python
class StructureScoreCriterion:
    def compute(self, grid: list[int], game: GameConfig) -> float:
        sorted_grid = sorted(grid)
        k = len(grid)
        midpoint = (game.min_number + game.max_number) / 2
        
        # Ratio pair/impair
        even_count = sum(1 for n in grid if n % 2 == 0)
        ideal_even = k / 2
        even_odd_score = 1 - abs(even_count - ideal_even) / (k / 2)
        
        # Répartition par décade
        decade_size = 10
        n_decades = (game.max_number - game.min_number) // decade_size + 1
        decade_counts = [0] * n_decades
        for n in grid:
            decade_idx = (n - game.min_number) // decade_size
            decade_counts[decade_idx] += 1
        ideal_per_decade = k / n_decades
        decade_deviation = sum(abs(c - ideal_per_decade) for c in decade_counts)
        max_deviation = k  # Pire cas : tous dans une décade
        decade_score = 1 - decade_deviation / max_deviation
        
        # Ratio bas/haut
        low_count = sum(1 for n in grid if n <= midpoint)
        low_high_score = 1 - abs(low_count - k / 2) / (k / 2)
        
        # Écarts consécutifs
        gaps = [sorted_grid[i+1] - sorted_grid[i] for i in range(k - 1)]
        gap_std = np.std(gaps) if len(gaps) > 1 else 0
        max_possible_std = (game.max_number - game.min_number) / 2
        gap_score = 1 - min(gap_std / max_possible_std, 1)
        
        return (
            0.30 * even_odd_score
            + 0.30 * decade_score
            + 0.20 * low_high_score
            + 0.20 * gap_score
        )
```

---

### 3.5 Score Équilibre (`balance_score.py`)

Évalue la distribution spatiale de la grille sur l'ensemble des numéros possibles.

$$S_{bal}(G) = 1 - \frac{D_{KL}(\text{grille} \| \text{uniforme})}{D_{KL}^{max}}$$

Approche simplifiée : mesurer l'écart entre les positions cumulées et une répartition idéale.

```python
class BalanceScoreCriterion:
    def compute(self, grid: list[int], game: GameConfig) -> float:
        sorted_grid = sorted(grid)
        k = len(grid)
        n = game.max_number - game.min_number + 1
        
        # Positions idéales (répartition uniforme)
        ideal_positions = [
            game.min_number + (i + 1) * n / (k + 1)
            for i in range(k)
        ]
        
        # Écart moyen normalisé
        deviations = [
            abs(sorted_grid[i] - ideal_positions[i]) / n
            for i in range(k)
        ]
        
        avg_deviation = sum(deviations) / k
        score = 1 - min(avg_deviation * 2, 1)  # Facteur 2 pour sensibilité
        
        return max(0, min(1, score))
```

---

### 3.6 Pénalité Motif (`pattern_penalty.py`)

Détecte et pénalise les motifs trop réguliers qui sont peu probables (suites arithmétiques, multiples, etc.)

| Motif | Pénalité |
|---|---|
| Suite arithmétique complète (1,2,3,4,5) | 1.0 |
| Suite arithmétique partielle (≥ 3 consécutifs) | 0.5 |
| Tous multiples d'un même nombre | 0.8 |
| Tous dans la même décade | 0.6 |
| Tous pairs ou tous impairs | 0.4 |
| Numéros trop proches (span < 15) | 0.3 |

```python
class PatternPenaltyCriterion:
    def compute(self, grid: list[int], game: GameConfig) -> float:
        sorted_grid = sorted(grid)
        k = len(grid)
        penalties = []
        
        # Suite arithmétique
        diffs = [sorted_grid[i+1] - sorted_grid[i] for i in range(k-1)]
        if len(set(diffs)) == 1:  # Suite arithmétique parfaite
            penalties.append(1.0)
        
        # Consécutifs
        consecutive_count = sum(1 for d in diffs if d == 1)
        if consecutive_count >= 3:
            penalties.append(0.5)
        elif consecutive_count >= 2:
            penalties.append(0.2)
        
        # Multiples
        for m in range(2, 10):
            if all(n % m == 0 for n in grid):
                penalties.append(0.8)
                break
        
        # Même décade
        decades = set((n - 1) // 10 for n in grid)
        if len(decades) == 1:
            penalties.append(0.6)
        
        # Tous pairs ou tous impairs
        parities = set(n % 2 for n in grid)
        if len(parities) == 1:
            penalties.append(0.4)
        
        # Span trop faible
        span = sorted_grid[-1] - sorted_grid[0]
        if span < 15:
            penalties.append(0.3 * (1 - span / 15))
        
        return min(sum(penalties), 1.0)  # Plafonné à 1.0
```

---

## 4. Orchestrateur de Scoring (`scorer.py`)

```python
class GridScorer:
    def __init__(
        self,
        frequency_criterion: FrequencyScoreCriterion,
        gap_criterion: GapScoreCriterion,
        cooccurrence_criterion: CooccurrenceScoreCriterion,
        structure_criterion: StructureScoreCriterion,
        balance_criterion: BalanceScoreCriterion,
        pattern_criterion: PatternPenaltyCriterion,
        weights: dict[str, float] | None = None,
    ):
        self.criteria = {
            "frequency": frequency_criterion,
            "gap": gap_criterion,
            "cooccurrence": cooccurrence_criterion,
            "structure": structure_criterion,
            "balance": balance_criterion,
        }
        self.pattern_criterion = pattern_criterion
        self.weights = weights or self.default_weights()
    
    @staticmethod
    def default_weights() -> dict[str, float]:
        return {
            "frequency": 0.20,
            "gap": 0.20,
            "cooccurrence": 0.15,
            "structure": 0.15,
            "balance": 0.20,
            "pattern_penalty": 0.10,
        }
    
    def score(
        self,
        grid: list[int],
        statistics: StatisticsSnapshot,
        game: GameConfig,
    ) -> ScoredResult:
        breakdown = {}
        
        breakdown["frequency"] = self.criteria["frequency"].compute(
            grid, statistics.frequencies, game
        )
        breakdown["gap"] = self.criteria["gap"].compute(
            grid, statistics.gaps, game
        )
        breakdown["cooccurrence"] = self.criteria["cooccurrence"].compute(
            grid, statistics.cooccurrences, game
        )
        breakdown["structure"] = self.criteria["structure"].compute(grid, game)
        breakdown["balance"] = self.criteria["balance"].compute(grid, game)
        breakdown["pattern_penalty"] = self.pattern_criterion.compute(grid, game)
        
        # Score total pondéré
        total = sum(
            self.weights[name] * breakdown[name]
            for name in self.criteria
        ) - self.weights["pattern_penalty"] * breakdown["pattern_penalty"]
        
        # Normalisation [0, 1]
        total = max(0.0, min(1.0, total))
        
        return ScoredResult(
            numbers=grid,
            total_score=round(total, 6),
            score_breakdown={k: round(v, 6) for k, v in breakdown.items()},
        )
```

---

## 5. Gestion des Poids

### 5.1 Poids par défaut

Les poids sont calibrés empiriquement pour favoriser un équilibre entre :
- L'exploitation (fréquences, retards) — suit les tendances historiques
- L'exploration (structure, équilibre) — favorise les grilles bien formées
- La prudence (pénalité motif) — évite les pièges cognitifs

### 5.2 Poids personnalisables

L'utilisateur peut ajuster les poids via l'API ou le frontend :

```json
{
  "frequency": 1.0,
  "gap": 0.5,
  "cooccurrence": 0.8,
  "structure": 0.6,
  "balance": 0.7,
  "pattern_penalty": 0.3
}
```

Les poids sont normalisés automatiquement :

$$w_c^{norm} = \frac{w_c}{\sum_{i} w_i}$$

### 5.3 Profils prédéfinis

| Profil | Freq | Gap | Cooc | Struct | Bal | Penalty | Philosophie |
|---|---|---|---|---|---|---|---|
| **Équilibré** | 0.20 | 0.20 | 0.15 | 0.15 | 0.20 | 0.10 | Compromis entre tous |
| **Tendance** | 0.35 | 0.10 | 0.25 | 0.10 | 0.15 | 0.05 | Suit les numéros chauds |
| **Contrarian** | 0.10 | 0.35 | 0.10 | 0.15 | 0.20 | 0.10 | Favorise les numéros froids |
| **Structurel** | 0.10 | 0.10 | 0.10 | 0.30 | 0.30 | 0.10 | Grilles bien formées |

---

## 6. Scoring des Étoiles / Numéros Chance

Le scoring des étoiles/chance est **séparé** du scoring principal.

Pour les étoiles, seuls les critères applicables sont utilisés :
- Fréquence étoiles
- Gap étoiles
- Cooccurrence étoiles (si ≥ 2)

Le score final combine :

$$\text{Score}_{total} = 0.85 \times \text{Score}_{numeros} + 0.15 \times \text{Score}_{etoiles}$$

---

## 7. Références

| Document | Contenu |
|---|---|
| [07_Moteur_Statistique](07_Moteur_Statistique.md) | Données d'entrée du scoring |
| [09_Moteur_Optimisation](09_Moteur_Optimisation.md) | Utilisation du score comme fonction objectif |
| [10_Moteur_Simulation](10_Moteur_Simulation.md) | Validation du scoring |
| [06_API_Design](06_API_Design.md) | Endpoint de scoring |

---

*Fin du document 08_Moteur_Scoring.md*
