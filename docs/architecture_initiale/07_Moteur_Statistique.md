# 07 — Moteur Statistique

> **Projet** : LOTO ULTIME  
> **Version** : 1.0  
> **Date** : 2026-03-27  
> **Références croisées** : [03_Backend](03_Architecture_Backend.md) · [05_Modele](05_Modele_Donnees.md) · [08_Scoring](08_Moteur_Scoring.md) · [09_Optimisation](09_Moteur_Optimisation.md)

---

## 1. Rôle du Moteur Statistique

Le moteur statistique est le **cœur analytique** du système. Il transforme l'historique des tirages en indicateurs exploitables par le moteur de scoring et d'optimisation.

**Entrée** : Matrice de tirages $D \in \mathbb{N}^{N \times k}$ (N tirages de k numéros)

**Sortie** : `StatisticsSnapshot` contenant toutes les métriques

---

## 2. Modélisation Mathématique

### 2.1 Espace combinatoire

Pour un jeu tirant $k$ numéros parmi $n$ :

$$|\Omega| = \binom{n}{k} = \frac{n!}{k!(n-k)!}$$

| Jeu | Formule | Taille espace |
|---|---|---|
| Loto FDJ | $\binom{49}{5} \times \binom{10}{1}$ | 19 068 840 |
| EuroMillions | $\binom{50}{5} \times \binom{12}{2}$ | 139 838 160 |

### 2.2 Probabilité théorique d'un numéro

Pour un tirage uniforme, la probabilité qu'un numéro $i$ apparaisse :

$$P(i) = \frac{k}{n}$$

| Jeu | Probabilité théorique |
|---|---|
| Loto FDJ (numéros) | $5/49 \approx 0.1020$ |
| Loto FDJ (chance) | $1/10 = 0.1000$ |
| EuroMillions (numéros) | $5/50 = 0.1000$ |
| EuroMillions (étoiles) | $2/12 \approx 0.1667$ |

---

## 3. Modules Statistiques

### 3.1 Fréquences (`frequency.py`)

#### Fréquence absolue

Pour chaque numéro $i \in [1, n]$ :

$$f_i = \sum_{t=1}^{N} \mathbb{1}_{i \in D_t}$$

où $D_t$ est l'ensemble des numéros du tirage $t$.

#### Fréquence relative

$$\hat{p}_i = \frac{f_i}{N}$$

#### Ratio de fréquence

$$R_i = \frac{\hat{p}_i}{P_{théo}} = \frac{f_i \cdot n}{N \cdot k}$$

- $R_i > 1$ : numéro **surreprésenté** (chaud)
- $R_i < 1$ : numéro **sous-représenté** (froid)
- $R_i \approx 1$ : conforme à l'attente

#### Implémentation

```python
class FrequencyEngine(BaseStatisticsEngine):
    def compute(self, draws: np.ndarray, game: GameConfig) -> dict:
        """
        Args:
            draws: Matrice (N, k) des numéros tirés
            game: Configuration du jeu
        Returns:
            Dict {numéro: {count, relative, ratio, last_seen}}
        """
        n_draws = draws.shape[0]
        theoretical_p = game.numbers_drawn / game.numbers_pool
        
        frequencies = {}
        for num in range(game.min_number, game.max_number + 1):
            mask = np.any(draws == num, axis=1)
            count = int(mask.sum())
            relative = count / n_draws if n_draws > 0 else 0
            
            # Dernier tirage contenant ce numéro
            appearances = np.where(mask)[0]
            last_seen = (n_draws - 1 - appearances[-1]) if len(appearances) > 0 else n_draws
            
            frequencies[num] = {
                "count": count,
                "relative": round(relative, 6),
                "ratio": round(relative / theoretical_p, 4) if theoretical_p > 0 else 0,
                "last_seen": int(last_seen),
            }
        
        return frequencies
    
    def get_name(self) -> str:
        return "frequency"
```

---

### 3.2 Retards / Gaps (`gaps.py`)

#### Définition

Le **gap** (retard) d'un numéro $i$ au tirage $t$ est le nombre de tirages depuis sa dernière apparition :

$$G_i(t) = t - \max\{s < t : i \in D_s\}$$

#### Métriques de gap

Pour chaque numéro $i$ :

| Métrique | Formule | Signification |
|---|---|---|
| Gap courant | $G_i(N)$ | Retard actuel |
| Gap maximum | $\max_t G_i(t)$ | Plus long retard historique |
| Gap moyen | $\bar{G}_i = \frac{1}{f_i} \sum G_i$ | Retard moyen entre apparitions |
| Gap minimum | $\min_t G_i(t)$ | Plus court retard |
| Gap médian | $\text{median}(G_i)$ | Retard médian |

#### Gap attendu théorique

$$E[G_i] = \frac{n}{k} = \frac{1}{P(i)}$$

| Jeu | Gap attendu |
|---|---|
| Loto FDJ | $49/5 = 9.8$ tirages |
| EuroMillions | $50/5 = 10$ tirages |

#### Implémentation

```python
class GapEngine(BaseStatisticsEngine):
    def compute(self, draws: np.ndarray, game: GameConfig) -> dict:
        n_draws = draws.shape[0]
        gaps = {}
        
        for num in range(game.min_number, game.max_number + 1):
            mask = np.any(draws == num, axis=1)
            positions = np.where(mask)[0]
            
            if len(positions) == 0:
                gaps[num] = {
                    "current_gap": n_draws,
                    "max_gap": n_draws,
                    "avg_gap": float(n_draws),
                    "min_gap": n_draws,
                    "median_gap": float(n_draws),
                    "expected_gap": game.numbers_pool / game.numbers_drawn,
                }
                continue
            
            # Calcul des intervalles entre apparitions
            intervals = np.diff(positions)
            current_gap = n_draws - 1 - positions[-1]
            
            # Inclure le gap initial (avant première apparition)
            all_gaps = np.concatenate([[positions[0]], intervals, [current_gap]])
            
            gaps[num] = {
                "current_gap": int(current_gap),
                "max_gap": int(all_gaps.max()),
                "avg_gap": round(float(all_gaps.mean()), 2),
                "min_gap": int(all_gaps.min()),
                "median_gap": round(float(np.median(all_gaps)), 2),
                "expected_gap": round(game.numbers_pool / game.numbers_drawn, 2),
            }
        
        return gaps
    
    def get_name(self) -> str:
        return "gaps"
```

---

### 3.3 Cooccurrences (`cooccurrence.py`)

#### Matrice de cooccurrence (paires)

$$M_{ij} = \sum_{t=1}^{N} \mathbb{1}_{i \in D_t \wedge j \in D_t}$$

#### Cooccurrence attendue (hypothèse indépendance)

$$E[M_{ij}] = N \cdot \frac{\binom{n-2}{k-2}}{\binom{n}{k}} = N \cdot \frac{k(k-1)}{n(n-1)}$$

#### Indice d'affinité

$$A_{ij} = \frac{M_{ij}}{E[M_{ij}]}$$

- $A_{ij} > 1$ : paire surreprésentée (affinité positive)
- $A_{ij} < 1$ : paire sous-représentée (affinité négative)

#### Analyse des triplets

$$T_{ijk} = \sum_{t=1}^{N} \mathbb{1}_{i \in D_t \wedge j \in D_t \wedge k \in D_t}$$

$$E[T_{ijk}] = N \cdot \frac{\binom{n-3}{k-3}}{\binom{n}{k}} = N \cdot \frac{k(k-1)(k-2)}{n(n-1)(n-2)}$$

#### Implémentation

```python
class CooccurrenceEngine(BaseStatisticsEngine):
    def compute(self, draws: np.ndarray, game: GameConfig) -> dict:
        n_draws = draws.shape[0]
        n = game.numbers_pool
        k = game.numbers_drawn
        
        # Matrice binaire (N tirages × n numéros)
        binary_matrix = np.zeros((n_draws, n), dtype=np.int8)
        for t in range(n_draws):
            for num in draws[t]:
                binary_matrix[t, num - game.min_number] = 1
        
        # Matrice de cooccurrence = M^T × M
        cooc_matrix = binary_matrix.T @ binary_matrix
        
        # Cooccurrence attendue
        expected_pair = n_draws * k * (k - 1) / (n * (n - 1))
        
        # Extraction des paires significatives
        pairs = {}
        for i in range(n):
            for j in range(i + 1, n):
                num_i = i + game.min_number
                num_j = j + game.min_number
                count = int(cooc_matrix[i, j])
                affinity = round(count / expected_pair, 4) if expected_pair > 0 else 0
                pairs[f"{num_i}-{num_j}"] = {
                    "count": count,
                    "expected": round(expected_pair, 2),
                    "affinity": affinity,
                }
        
        return {
            "pairs": pairs,
            "expected_pair_count": round(expected_pair, 2),
            "matrix_shape": [n, n],
        }
    
    def get_name(self) -> str:
        return "cooccurrence"
```

---

### 3.4 Analyse Temporelle (`temporal.py`)

#### Fenêtres glissantes

Analyse des fréquences sur des fenêtres temporelles de taille $W$ :

- Derniers 20 tirages
- Derniers 50 tirages
- Derniers 100 tirages
- Derniers 200 tirages

#### Tendance

Pour chaque numéro, comparer la fréquence récente à la fréquence globale :

$$\Delta_i(W) = \hat{p}_i^{(W)} - \hat{p}_i^{(global)}$$

- $\Delta_i > 0$ : tendance haussière (le numéro sort plus souvent récemment)
- $\Delta_i < 0$ : tendance baissière

#### Momentum

Régression linéaire sur les fréquences glissantes pour détecter la direction :

$$\text{momentum}_i = \text{slope}(\hat{p}_i^{(W_1)}, \hat{p}_i^{(W_2)}, \hat{p}_i^{(W_3)}, \hat{p}_i^{(W_4)})$$

#### Implémentation

```python
class TemporalEngine(BaseStatisticsEngine):
    WINDOWS = [20, 50, 100, 200]
    
    def compute(self, draws: np.ndarray, game: GameConfig) -> dict:
        n_draws = draws.shape[0]
        theoretical_p = game.numbers_drawn / game.numbers_pool
        
        windows_data = []
        for w in self.WINDOWS:
            if n_draws < w:
                continue
            
            recent_draws = draws[-w:]
            hot = []
            cold = []
            
            for num in range(game.min_number, game.max_number + 1):
                mask = np.any(recent_draws == num, axis=1)
                freq = mask.sum() / w
                delta = freq - theoretical_p
                
                if delta > 0.02:  # Seuil configurable
                    hot.append({"number": num, "freq": round(freq, 4), "delta": round(delta, 4)})
                elif delta < -0.02:
                    cold.append({"number": num, "freq": round(freq, 4), "delta": round(delta, 4)})
            
            hot.sort(key=lambda x: -x["delta"])
            cold.sort(key=lambda x: x["delta"])
            
            windows_data.append({
                "window_size": w,
                "hot_numbers": hot[:10],
                "cold_numbers": cold[:10],
            })
        
        return {"windows": windows_data}
    
    def get_name(self) -> str:
        return "temporal"
```

---

### 3.5 Distributions (`distribution.py`)

#### Entropie de Shannon

$$H = -\sum_{i=1}^{n} \hat{p}_i \log_2 \hat{p}_i$$

Entropie maximale (distribution uniforme) :

$$H_{max} = \log_2(n)$$

Score d'uniformité :

$$U = \frac{H}{H_{max}}$$

#### Test du Chi-2

$$\chi^2 = \sum_{i=1}^{n} \frac{(f_i - E[f_i])^2}{E[f_i]}$$

avec $E[f_i] = N \cdot k / n$.

La p-value du test indique si les fréquences observées diffèrent significativement de l'uniforme.

#### Analyse par décades / tranches

Répartition des numéros par tranches (1-10, 11-20, ...) dans chaque tirage.

#### Ratio pair/impair

Pour chaque tirage, compter le nombre de numéros pairs et impairs. Évaluer la distribution.

#### Somme des numéros

Distribution de $S_t = \sum_{i \in D_t} i$ sur tous les tirages.

#### Implémentation

```python
class DistributionEngine(BaseStatisticsEngine):
    def compute(self, draws: np.ndarray, game: GameConfig) -> dict:
        from scipy import stats as sp_stats
        
        n = game.numbers_pool
        k = game.numbers_drawn
        n_draws = draws.shape[0]
        
        # Fréquences
        counts = np.zeros(n, dtype=int)
        for num in range(game.min_number, game.max_number + 1):
            idx = num - game.min_number
            counts[idx] = np.any(draws == num, axis=1).sum()
        
        # Entropie
        probs = counts / counts.sum()
        probs = probs[probs > 0]
        entropy = float(-np.sum(probs * np.log2(probs)))
        max_entropy = np.log2(n)
        uniformity = entropy / max_entropy if max_entropy > 0 else 0
        
        # Chi-2
        expected = np.full(n, n_draws * k / n)
        chi2_stat, chi2_pvalue = sp_stats.chisquare(counts, f_exp=expected)
        
        # Sommes
        sums = draws.sum(axis=1)
        
        # Ratio pair/impair
        even_counts = np.sum(draws % 2 == 0, axis=1)
        
        return {
            "entropy": round(entropy, 4),
            "max_entropy": round(max_entropy, 4),
            "uniformity_score": round(uniformity, 4),
            "chi2_statistic": round(float(chi2_stat), 4),
            "chi2_pvalue": round(float(chi2_pvalue), 6),
            "is_uniform": chi2_pvalue > 0.05,
            "sum_stats": {
                "mean": round(float(sums.mean()), 2),
                "std": round(float(sums.std()), 2),
                "min": int(sums.min()),
                "max": int(sums.max()),
                "median": float(np.median(sums)),
            },
            "even_odd_distribution": {
                "mean_even": round(float(even_counts.mean()), 2),
                "mean_odd": round(float(k - even_counts.mean()), 2),
            },
        }
    
    def get_name(self) -> str:
        return "distribution"
```

---

### 3.6 Approche Bayésienne (`bayesian.py`)

#### Modèle Beta-Binomial

Pour chaque numéro $i$, on modélise sa probabilité d'apparition par une distribution Beta :

$$p_i \sim \text{Beta}(\alpha_i, \beta_i)$$

#### Prior non informatif (Jeffreys)

$$\alpha_0 = 0.5, \quad \beta_0 = 0.5$$

#### Mise à jour

Après $N$ tirages avec $f_i$ apparitions :

$$\alpha_i = \alpha_0 + f_i$$
$$\beta_i = \beta_0 + (N - f_i)$$

#### Estimation ponctuelle (moyenne a posteriori)

$$\hat{p}_i^{Bayes} = \frac{\alpha_i}{\alpha_i + \beta_i}$$

#### Intervalle de crédibilité (95%)

$$IC_{95\%}(p_i) = \left[\text{Beta}_{0.025}(\alpha_i, \beta_i), \text{Beta}_{0.975}(\alpha_i, \beta_i)\right]$$

#### Implémentation

```python
class BayesianEngine(BaseStatisticsEngine):
    ALPHA_PRIOR = 0.5  # Jeffreys prior
    BETA_PRIOR = 0.5
    
    def compute(self, draws: np.ndarray, game: GameConfig) -> dict:
        from scipy.stats import beta as beta_dist
        
        n_draws = draws.shape[0]
        results = {}
        
        for num in range(game.min_number, game.max_number + 1):
            count = int(np.any(draws == num, axis=1).sum())
            
            alpha = self.ALPHA_PRIOR + count
            beta = self.BETA_PRIOR + (n_draws - count)
            
            posterior_mean = alpha / (alpha + beta)
            ci_low, ci_high = beta_dist.ppf([0.025, 0.975], alpha, beta)
            
            results[num] = {
                "alpha": round(alpha, 2),
                "beta": round(beta, 2),
                "posterior_mean": round(posterior_mean, 6),
                "ci_95_low": round(float(ci_low), 6),
                "ci_95_high": round(float(ci_high), 6),
                "ci_width": round(float(ci_high - ci_low), 6),
            }
        
        return results
    
    def get_name(self) -> str:
        return "bayesian"
```

---

### 3.7 Analyse de Graphe

→ Détails dans la section dédiée ci-dessous et dans [09_Moteur_Optimisation](09_Moteur_Optimisation.md)

#### Graphe de cooccurrence (`cooccurrence_graph.py`)

Construction d'un graphe pondéré $G = (V, E)$ :
- **Sommets** $V$ : numéros $\{1, ..., n\}$
- **Arêtes** $E$ : $(i, j)$ avec poids $w_{ij} = M_{ij}$ (cooccurrence)

#### Centralité (`centrality.py`)

| Métrique | Formule | Interprétation |
|---|---|---|
| Degré | $C_D(i) = \frac{\deg(i)}{n-1}$ | Nombre de connexions |
| Intermédiarité | $C_B(i) = \sum \frac{\sigma_{st}(i)}{\sigma_{st}}$ | Rôle de pont |
| Vecteur propre | $C_E(i)$ | Importance des voisins |
| PageRank | $PR(i)$ | Importance récursive |

#### Détection de communautés (`community.py`)

Algorithme de Louvain pour détecter des groupes de numéros qui co-apparaissent souvent :

```python
import networkx as nx
from networkx.algorithms.community import louvain_communities

def detect_communities(cooc_matrix: np.ndarray, game: GameConfig) -> dict:
    G = nx.Graph()
    n = game.numbers_pool
    
    for i in range(n):
        for j in range(i + 1, n):
            weight = cooc_matrix[i, j]
            if weight > 0:
                G.add_edge(
                    i + game.min_number,
                    j + game.min_number,
                    weight=weight,
                )
    
    communities = louvain_communities(G, weight="weight", seed=42)
    
    centrality = {
        "degree": nx.degree_centrality(G),
        "betweenness": nx.betweenness_centrality(G, weight="weight"),
        "eigenvector": nx.eigenvector_centrality(G, weight="weight", max_iter=1000),
    }
    
    return {
        "communities": [sorted(list(c)) for c in communities],
        "centrality": centrality,
        "density": nx.density(G),
        "clustering_coefficient": nx.average_clustering(G, weight="weight"),
    }
```

---

## 4. Pipeline de Calcul Complet

```
Historique tirages (DB)
        │
        ▼
┌───────────────────────────────┐
│     Extraction matrice NumPy  │
│     draws: np.ndarray (N, k)  │
└───────────┬───────────────────┘
            │
    ┌───────┼───────┬───────────┬──────────┬──────────┐
    ▼       ▼       ▼           ▼          ▼          ▼
 Freq.   Gaps   Cooccur.   Temporal   Distrib.   Bayesian
    │       │       │           │          │          │
    └───────┼───────┘           │          │          │
            │                   │          │          │
            ▼                   │          │          │
      Graphe cooccurrence      │          │          │
            │                   │          │          │
            ▼                   ▼          ▼          ▼
    ┌───────────────────────────────────────────────────┐
    │             StatisticsSnapshot                     │
    │        (assemblage de tous les résultats)          │
    └───────────────────────┬───────────────────────────┘
                            │
                            ▼
                    Persistance DB
```

---

## 5. Références

| Document | Contenu |
|---|---|
| [05_Modele_Donnees](05_Modele_Donnees.md) | Structure StatisticsSnapshot |
| [08_Moteur_Scoring](08_Moteur_Scoring.md) | Utilisation des statistiques pour le scoring |
| [09_Moteur_Optimisation](09_Moteur_Optimisation.md) | Graphes dans l'optimisation |
| [10_Moteur_Simulation](10_Moteur_Simulation.md) | Validation statistique |
| [16_Strategie_Tests](16_Strategie_Tests.md) | Tests unitaires des engines |

---

*Fin du document 07_Moteur_Statistique.md*
