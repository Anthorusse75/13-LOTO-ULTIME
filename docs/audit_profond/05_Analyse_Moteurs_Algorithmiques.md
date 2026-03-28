# 5. Analyse Détaillée du Moteur Algorithmique

Cette section est le cœur de l'audit. Le moteur algorithmique est ce qui distingue LOTO ULTIME d'un simple affichage de statistiques brutes. Sa qualité détermine directement la crédibilité et la valeur perçue du produit.

Le moteur se décompose en **quatre étages** :
1. **Moteurs statistiques** (7) — Analysent l'historique des tirages
2. **Moteurs de scoring** (6) — Évaluent la qualité d'une grille
3. **Moteurs d'optimisation** (5) — Génèrent des grilles optimisées
4. **Moteurs de simulation** (2) — Testent la robustesse des grilles

---

## 5.1 Moteurs Statistiques

### Vue d'ensemble

| Moteur | Sophistication | Verdict | Problème principal |
|--------|---------------|---------|-------------------|
| FrequencyEngine | BASIQUE | ⚠️ Suffisant mais limité | Pas de pondération temporelle |
| GapEngine | MODÉRÉ | ⚠️ Correct | expected_gap hardcodé |
| CooccurrenceEngine | MODÉRÉ | ⚠️ Correct | Pas de test de significativité |
| DistributionEngine | MODÉRÉ-ÉLEVÉ | ⚠️ Bon sauf bug | decade_size=10 casse pour pools non divisibles par 10 |
| BayesianEngine | ÉLEVÉ | ✅ Bon | Pas de posterior predictive |
| GraphEngine | ÉLEVÉ | ⚠️ Bon sauf erreur silencieuse | Eigenvector failure silencieux |
| TemporalEngine | MODÉRÉ-ÉLEVÉ | ⚠️ Fragile | Régression linéaire sur 4 points |

### Analyse détaillée par moteur

#### FrequencyEngine — BASIQUE

**Ce qu'il fait** : Compte le nombre d'apparitions de chaque numéro dans l'historique des tirages. Produit un histogramme simple.

**Ce qu'il ne fait pas** :
- **Pas de pondération temporelle** : Un tirage de 2008 compte autant qu'un tirage de la semaine dernière. Or, l'intérêt principal des fréquences est de détecter des tendances récentes. Un numéro qui était fréquent il y a 10 ans mais absent depuis 2 ans n'est pas « fréquent » dans un sens utile.
- **Pas d'intervalles de confiance** : On obtient « le numéro 7 est apparu 142 fois » mais pas « avec un IC à 95%, sa fréquence attendue est entre 2.1% et 3.2% ». L'intervalle de confiance est ce qui distingue une observation significative d'un artefact statistique.
- **Pas de comparaison avec l'attendu théorique** : Si chaque numéro avait une probabilité égale, il devrait apparaître environ N_tirages × N_numéros_tirés / N_pool fois. L'écart entre le réel et l'attendu est plus informatif que la fréquence brute.

**Pourquoi c'est insuffisant** : Un histogramme de fréquences est la première chose qu'un étudiant de statistique produirait. Pour un produit qui affiche un onglet « Statistiques » avec 7 sous-onglets, le niveau attendu est significativement plus élevé.

**Améliorations recommandées** :
- 🔧 Ajouter une fenêtre glissante pondérée (exponential decay : poids = e^(-λ × âge_semaines))
- 📈 Calculer l'écart Z entre la fréquence observée et la fréquence attendue (Z = (obs - exp) / √(exp × (1-p)))
- 📈 Ajouter un IC binomial pour chaque numéro
- 🎯 Distinguer « fréquence globale » et « fréquence récente (50 derniers tirages) »

**Classement** : 📈 Amélioration indispensable (le moteur de fréquences est la base de tout le scoring)

---

#### GapEngine — MODÉRÉ

**Ce qu'il fait** : Pour chaque numéro, calcule le nombre de tirages depuis sa dernière apparition (gap courant), le gap moyen historique, le gap maximum, et le gap "attendu".

**Point fort** : Identifie les numéros « en retard » (gap courant >> gap attendu), ce qui est un des arguments les plus parlants pour un utilisateur.

**Problèmes** :
- Le `expected_gap` est calculé comme `N_pool / N_numbers_drawn` — cette approximation est correcte pour un tirage sans remise, mais elle est **hardcodée** sans mention de la formule utilisée ni de ses limites.
- Aucun **test de significativité** : un gap de 20 pour un numéro dont le gap attendu est 10 est-il significatif ? Avec 49 numéros, on s'attend statistiquement à ce que certains numéros aient des gaps élevés par pure chance. Le test exact serait une distribution géométrique : P(gap ≥ k) = (1 - p)^k.
- Le seuil `gap > 2 × expected_gap` utilisé dans le frontend pour l'alerte est **arbitraire** et non justifié.

**Améliorations recommandées** :
- 📈 Calculer la p-value du gap courant selon la distribution géométrique
- 📈 Classifier les gaps en « normal », « modéré », « remarquable », « extrême » avec des seuils basés sur les quantiles
- 📈 Ajouter la tendance du gap (augmente-t-il régulièrement ?)

**Classement** : 📈 Amélioration très utile

---

#### CooccurrenceEngine — MODÉRÉ

**Ce qu'il fait** : Construit une matrice de co-occurrences (combien de fois deux numéros sont apparus ensemble) et calcule un score d'affinité pondéré.

**Problèmes** :
- La matrice est **binaire** (pair apparue ou non par tirage), ce qui perd l'information sur les occurrences multiples dans des contextes temporels différents.
- L'affinité est calculée par une formule pondérée mais **pas de test de Fisher** pour déterminer si l'association est statistiquement significative. Deux numéros qui apparaissent ensemble 50 fois sur 1000 tirages, est-ce plus que le hasard ? Cela dépend de leurs fréquences individuelles. Le test exact de Fisher ou le Chi-² d'indépendance répondraient rigoureusement.
- **Pas de pondération temporelle** : les co-occurrences de 2008 pèsent autant que celles de 2025.

**Améliorations recommandées** :
- 📈 Ajouter un test de Fisher ou Chi-² par paire pour filtrer les associations non significatives
- 📈 Introduire une fenêtre temporelle (co-occurrences récentes vs historiques)
- 🎯 Calculer le lift : ratio entre la co-occurrence observée et la co-occurrence attendue sous indépendance

**Classement** : 📈 Amélioration utile

---

#### DistributionEngine — MODÉRÉ-ÉLEVÉ

**Ce qu'il fait** : Calcule l'entropie de Shannon, le test Chi-² d'uniformité, et un score de répartition par décade.

**Point fort** : L'entropie de Shannon est une métrique pertinente pour évaluer la diversité d'une combinaison. Le Chi-² permet de tester formellement si la distribution est uniforme.

**Bug** :
```python
decade_size = 10  # HARDCODÉ
```
La répartition par « décade » divise le pool en tranches de 10. Pour le Loto (1-49), cela donne 5 tranches : [1-10], [11-20], [21-30], [31-40], [41-49]. La dernière tranche n'a que 9 numéros, ce qui **biaise** le calcul d'uniformité. Pour l'EuroMillions (1-50), ça tombe juste. Pour d'autres loteries éventuelles (Keno 1-70), le biais est amplifié.

**Correction** : Calculer la taille de décade dynamiquement : `decade_size = max_number // 5` ou utiliser des quantiles au lieu de tranches fixes.

**Classement** : 🔧 Correction (bug sur le decade_size)

---

#### BayesianEngine — ÉLEVÉ

**Ce qu'il fait** : Applique un modèle Beta-Binomial conjugué pour calculer la probabilité postérieure de chaque numéro. Utilise le prior de Jeffreys (α₀ = 0.5, β₀ = 0.5), qui est le prior non-informatif standard pour les proportions.

**Point fort** : C'est l'implémentation la plus rigoureuse statistiquement du projet. Le choix du prior de Jeffreys, le calcul de l'IC crédible à 95%, et l'estimation MAP sont tous corrects et bien fondés.

**Limites actuelles** :
- Pas de **posterior predictive** : la probabilité que le prochain tirage contienne le numéro X, en marginalisant sur l'incertitude des paramètres
- Pas de **modèle hiérarchique** : les numéros sont traités indépendamment, sans partage d'information entre eux
- L'IC à 95% est calculé mais jamais utilisé pour prendre des décisions (par exemple : « ce numéro est significativement sur-/sous-représenté si l'IC exclut 1/49 »)

**Améliorations recommandées** :
- 📈 Utiliser l'IC pour classifier automatiquement les numéros (sur-représenté / normal / sous-représenté)
- 🎯 Calculer la posterior predictive pour alimenter le scoring
- 🎯 Explorer un modèle Dirichlet-Multinomial pour traiter tous les numéros conjointement

**Classement** : 📈 Amélioration avancée (le moteur est déjà le meilleur du lot)

---

#### GraphEngine — ÉLEVÉ

**Ce qu'il fait** : Construit un graphe de co-occurrences avec NetworkX, calcule les centralités (degree, betweenness, eigenvector), détecte les communautés avec l'algorithme de Louvain.

**Point fort** : L'approche par graphe est originale et potentiellement puissante. Les communautés de Louvain peuvent révéler des « clusters » de numéros qui apparaissent ensemble de manière récurrente.

**Problème** : Le calcul de la centralité eigenvector peut échouer à converger (NetworkX lève `PowerIterationFailedConvergence`). Cette exception est attrapée silencieusement :

```python
try:
    eigenvector = nx.eigenvector_centrality(G, max_iter=500)
except nx.PowerIterationFailedConvergence:
    eigenvector = {n: 0.0 for n in G.nodes()}  # ← Valeurs à zéro en cas d'échec
```

L'utilisateur ne sait jamais que les valeurs affichées sont des zéros par défaut, pas des résultats réels.

**Améliorations recommandées** :
- 🔧 Logger l'échec et le signaler dans le snapshot (champ `warnings`)
- 📈 Utiliser `eigenvector_centrality_numpy` comme fallback (plus robuste)
- 📈 Ajouter la visualisation interactive du graphe avec zoom et clustering visuel

**Classement** : 🔧 Correction (erreur silencieuse)

---

#### TemporalEngine — MODÉRÉ-ÉLEVÉ

**Ce qu'il fait** : Calcule les fréquences sur plusieurs fenêtres temporelles [20, 50, 100, 200 tirages], puis effectue une régression linéaire pour détecter les « tendances » (momentum).

**Problème fondamental** : La régression linéaire est calculée sur **4 points** (un par fenêtre). En statistique, une régression sur 4 points n'a pratiquement aucune valeur :
- Le R² sera mécaniquement élevé (peu de degrés de liberté)
- La pente est extrêmement sensible au moindre bruit
- Les seuils de classification (momentum > 0.02 = hausse, < -0.02 = baisse) sont **arbitraires** et ne correspondent à aucun test statistique

Un numéro peut être classé en « forte hausse » simplement parce qu'il est apparu une fois de plus dans la fenêtre de 20 tirages par rapport à celle de 50.

**Améliorations recommandées** :
- 🔧 Utiliser au minimum 10 points (fenêtres de 10, 20, 30, ..., 100 tirages) pour que la régression ait du sens
- 📈 Remplacer ou compléter par un test de Mann-Kendall (test de tendance monotone non-paramétrique)
- 📈 Ajouter des bandes de confiance autour de la pente
- 📈 Les seuils ±0.02 devraient être remplacés par un test de significativité (p-value < 0.05)

**Classement** : 🔧 Correction (régression sur 4 points est méthodologiquement invalide)

---

## 5.2 Moteurs de Scoring

Le scoring est l'étape qui convertit les observations statistiques en un **score unique par grille** (0 à 10). C'est le composant le plus critique pour l'expérience utilisateur, car c'est ce score qui guide les recommandations.

### Vue d'ensemble

| Critère | Sophistication | Problème principal |
|---------|---------------|-------------------|
| FrequencyCriterion | BASIQUE | Normalisation min-max instable |
| GapCriterion | MODÉRÉ | Paramètre sigmoid arbitraire (sensitivity=3.0) |
| CooccurrenceCriterion | MODÉRÉ | Paires manquantes scorées 0.5 (injustifié) |
| BalanceCriterion | BASIQUE | « Magic number » facteur 2 |
| StructureCriterion | MODÉRÉ-ÉLEVÉ | Pondérations hardcodées [0.30, 0.30, 0.20, 0.20] |
| PatternPenalty | ÉLEVÉ mais dangereux | Pénalités qui s'empilent sans limite |

### Analyse approfondie

#### 🔴 FrequencyCriterion — Normalisation instable

Le score de fréquence utilise une normalisation min-max globale :

```python
norm = (freq - min_freq) / (max_freq - min_freq)
```

**Pourquoi c'est un problème** : Si un seul numéro a une fréquence anormalement élevée (ou basse), toute l'échelle de normalisation est déformée. Tous les autres numéros se retrouvent écrasés dans une plage étroite. C'est un phénomène classique en machine learning : la normalisation min-max est **non robuste aux outliers**.

**Conséquence concrète** : Le score de fréquence d'une grille peut varier fortement d'un recalcul à l'autre si un seul numéro change de position dans le classement.

**Solution** : Utiliser une normalisation par z-score (robust z-score avec médiane et MAD) ou par percentile-rank. Le z-score est défini comme :

$$z = \frac{x - \text{médiane}}{\text{MAD} \times 1.4826}$$

où MAD est la déviation absolue médiane. Cette normalisation est insensible aux outliers.

**Classement** : 🔧 Correction indispensable

#### 🔴 PatternPenalty — Accumulation non bornée

Le `PatternPenalty` vérifie 7 patterns indésirables (trop de numéros consécutifs, trop de numéros dans la même décade, trop de pairs/impairs, etc.) et additionne les pénalités :

```python
total_penalty = sum(penalties)  # Peut dépasser 1.0
clamped = min(total_penalty, 1.0)  # Clampé à 1.0
score = max(0, 1 - clamped)  # Score final entre 0 et 1
```

**Problème** : 7 pénalités qui s'empilent signifient qu'une grille cumulative (par exemple : 5 numéros consécutifs qui sont aussi dans la même décade et tous impairs) reçoit une pénalité cumulée de 1.0+, donc un score final de 0.0. Cette grille est totalement éliminée du scoring, même si elle a par ailleurs un excellent score de fréquence.

**Pourquoi c'est dangereux** : Le pattern penalty agit comme un **veto absolu**. Or, les patterns ne sont pas tous égaux en gravité. 5 numéros consécutifs (1-2-3-4-5) est effectivement suspect. Mais 3 numéros dans la même décade avec 2 numéros impairs est parfaitement banal.

**Solution** :
- Pondérer chaque pattern par sa gravité réelle
- Utiliser un produit de facteurs plutôt qu'une somme : `score = ∏(1 - penalty_i × weight_i)`
- Borner chaque pénalité individuelle à 0.3 maximum

**Classement** : 🔧 Correction importante

#### ⚠️ CooccurrenceCriterion — Valeur par défaut injustifiée

Les paires de numéros absentes de la matrice de co-occurrence reçoivent un score de 0.5 (milieu de l'échelle). Ce choix est arbitraire : une paire jamais vue dans l'historique pourrait être scorée à 0.0 (pessimiste) ou à la moyenne des paires connues.

**Classement** : 📈 Amélioration utile

#### ⚠️ Magic numbers partout

| Critère | Constante | Valeur | Justification |
|---------|-----------|--------|---------------|
| GapCriterion | sensitivity | 3.0 | Aucune |
| BalanceCriterion | facteur d'échelle | 2 | Aucune |
| StructureCriterion | pondérations | [0.30, 0.30, 0.20, 0.20] | Aucune |
| TemporalEngine | seuils momentum | ±0.02 | Aucune |
| PatternPenalty | 7 seuils | variables | Partiellement justifiés |

Chaque constante devrait être soit paramétrable via la configuration, soit accompagnée d'un commentaire expliquant le raisonnement.

**Classement** : 📈 Amélioration (documentation + configurabilité)

---

## 5.3 Moteurs d'Optimisation

### Vue d'ensemble

| Algorithme | Sophistication | Problème principal |
|-----------|---------------|-------------------|
| HillClimbing | BASIQUE | 100 restarts × 50 stagnation, échanges 1-élément seulement |
| GeneticAlgorithm | MODÉRÉ-ÉLEVÉ | Bon paramétrage (pop=200, gen=500) |
| SimulatedAnnealing | ÉLEVÉ | **JAMAIS EXÉCUTÉ** (bug select_method) + 50K itérations coûteux |
| TabuSearch | MODÉRÉ-ÉLEVÉ | Pas de critère d'aspiration |
| NSGA-II (MultiObjective) | ÉLEVÉ | 3 objectifs pertinents (score, diversité, couverture) |

### 🔴 Bug critique : select_method()

La fonction `select_method()` est censée choisir intelligemment entre les algorithmes selon le contexte (nombre de numéros, taille du pool, contraintes). En pratique, elle **retourne toujours `"genetic"`**.

**Impact** : Le recuit simulé (SimulatedAnnealing), qui est probablement l'algorithme le plus adapté pour l'optimisation combinatoire de grilles de loto, n'est **jamais utilisé**. L'investissement de développement dans cet algorithme (50 000 itérations, cooling rate adaptatif 0.9995) est totalement gaspillé.

**Correction recommandée** :
```python
def select_method(numbers_pool, numbers_drawn, constraints=None):
    if numbers_pool <= 30:
        return "hill_climbing"  # Petits pools : HC suffit
    elif numbers_drawn >= 7:
        return "simulated_annealing"  # Grands tirages : SA plus robuste
    elif constraints and constraints.get("multi_objective"):
        return "nsga2"  # Multi-objectif demandé
    else:
        return "genetic"  # Défaut pour la plupart des cas
```

**Classement** : 🔧 Correction critique

### ⚠️ SimulatedAnnealing — Performance

Même une fois le bug corrigé, le SA est configuré avec **50 000 itérations** et un cooling rate de 0.9995. Pour une seule grille, cela prend ~1-2 secondes. Pour 10 grilles (top grids), c'est 10-20 secondes. Pour un portefeuille avec 4 stratégies × 7 grilles, c'est potentiellement 1-2 minutes.

**Recommandation** : Réduire à 10 000 itérations avec un cooling rate de 0.999 (converge plus vite, résultats quasi-identiques pour ce type de problème), ou implémenter un early stopping si le score n'améliore plus sur 500 itérations.

**Classement** : 📈 Amélioration

### PortfolioOptimizer — Cas d'utilisation mal compris ?

L'optimiseur de portefeuille utilise une approche **greedy de valeur marginale** : il ajoute les grilles une par une en maximisant le gain marginal en diversité/couverture. C'est une bonne première approximation.

**Ce qui manque** :
- **Backtesting** : Combien un portefeuille optimisé aurait-il gagné sur les 100 derniers tirages ? C'est la métrique que l'utilisateur veut réellement.
- **Comparaison formelle** : Est-ce que le portefeuille optimisé fait significativement mieux que des grilles tirées aléatoirement ? Le `compare-random` existe dans la simulation, mais il devrait être systématiquement inclus dans le résultat du portefeuille.
- **Diversification par corrélation** : La distance de Hamming mesure la distance combinatoire, mais pas la complémentarité statistique. Deux grilles peuvent être distantes en Hamming mais couvrir les mêmes patterns fréquentiels.

**Classement** : 📈 Amélioration très utile (backtesting) / 🎯 Repositionnement (corrélation statistique)

---

## 5.4 Moteurs de Simulation

### MonteCarloSimulator

**Ce qu'il fait** : Génère 10 000 tirages aléatoires et compare chaque tirage avec la grille fournie pour calculer les correspondances (3/5, 4/5, 5/5).

**Forces** :
- Approche correcte et standard
- Résultat reproductible via seed

**Faiblesses** :
- **Pas d'intervalles de confiance** : Le résultat est un point estimate. Avec 10K simulations, l'IC est calculable et informatif.
- **Pas d'importance sampling** : Certaines combinaisons rares (5/5) nécessitent des millions de simulations pour être observées. L'importance sampling permettrait d'estimer ces probabilités avec moins de simulations.
- **Pas de comparaison avec la théorie** : Les probabilités théoriques de gain sont connues exactement (combinatoire). Comparer le résultat Monte Carlo avec la valeur théorique validera la simulation.

**Classement** : 📈 Amélioration utile (IC + comparaison théorique)

### RobustnessAnalyzer

**Ce qu'il fait** : Bootstrap avec 100 rééchantillonnages pour tester la stabilité du score, plus comparaison avec 1 000 grilles aléatoires.

**Point fort** : C'est un des composants les mieux conçus. Le z-score comparatif (score de la grille vs distribution des grilles aléatoires) donne une mesure objective de la qualité relative.

**Limite** : 100 rééchantillonnages bootstrap est le minimum. Pour un IC fiable, 1 000 rééchantillonnages seraient préférables (mais plus lents).

**Classement** : 📈 Amélioration modérée (augmenter le nombre de rééchantillonnages)

---

## 5.5 Synthèse et priorisation algorithmique

### Améliorations indispensables (à faire immédiatement)

1. 🔧 Corriger `select_method()` pour utiliser réellement le SA et les autres algorithmes
2. 🔧 Remplacer la normalisation min-max dans FrequencyCriterion par un z-score robuste
3. 🔧 Corriger le `decade_size` hardcodé dans DistributionEngine
4. 🔧 Borner les pénalités individuelles dans PatternPenalty
5. 🔧 Augmenter le nombre de points dans la régression temporelle (minimum 10 fenêtres)
6. 🔧 Logger les échecs de convergence eigenvector au lieu de les masquer

### Améliorations très utiles (court terme)

7. 📈 Ajouter une pondération temporelle exponentielle dans FrequencyEngine
8. 📈 Ajouter un test de Fisher/Chi-² dans CooccurrenceEngine
9. 📈 Calculer la p-value des gaps dans GapEngine
10. 📈 Ajouter des intervalles de confiance dans MonteCarloSimulator
11. 📈 Configurer les magic numbers via Settings ou via les profils de scoring
12. 📈 Implémenter un early stopping dans SimulatedAnnealing

### Améliorations avancées (moyen terme)

13. 📈 Posterior predictive dans BayesianEngine
14. 📈 Backtesting automatique des portefeuilles sur l'historique
15. 📈 Modèle Dirichlet-Multinomial pour le bayésien conjoint
16. 📈 Importance sampling dans Monte Carlo
17. 📈 Test de Mann-Kendall dans TemporalEngine

### Améliorations premium / recherche (long terme)

18. 🎯 Machine learning supervisé sur les patterns gagnants historiques
19. 🎯 Analyse de séries temporelles (ARIMA/Prophet) sur les fréquences
20. 🎯 Optimisation multi-objectif avec Pareto front interactif
21. 🎯 Corrélation statistique entre grilles pour la diversification de portefeuille
22. 🎯 Explainability : « pourquoi cette grille est recommandée » en langage naturel
