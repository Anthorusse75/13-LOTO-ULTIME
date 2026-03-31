# 05 — Évolutions Algorithmiques

> Améliorations possibles sur scoring, optimisation, simulation, calibration, benchmark. Distingue indispensable, utile, avancé, premium.

---

## Références croisées

- [00_Index_Evolutions](./00_Index_Evolutions.md)
- [03_Audit_Existant_et_Ecarts](./03_Audit_Existant_et_Ecarts.md) — Bugs algo (BUG-02)
- [08_Evolution_Systeme_Reduit_Wheeling](./08_Evolution_Systeme_Reduit_Wheeling.md) — Algorithme de covering
- [09_Evolution_Mode_Budget_Intelligent](./09_Evolution_Mode_Budget_Intelligent.md) — Optimisation sous contrainte
- [10_Evolution_Comparateur_Strategies](./10_Evolution_Comparateur_Strategies.md) — Benchmark
- [16_Impacts_Backend](./16_Impacts_Backend.md) — Impacts code
- [22_Impacts_Performance_Scalabilite](./22_Impacts_Performance_Scalabilite.md) — Performance
- [25_Strategie_Tests_Evolutions](./25_Strategie_Tests_Evolutions.md) — Tests algo

---

## 1. Objectif du document

Cartographier **toutes les améliorations algorithmiques** possibles, les classer par niveau (indispensable → premium), et documenter leur impact sur l'architecture existante.

---

## 2. État actuel des moteurs

### 2.1 — Moteurs statistiques (7)

| Moteur       | Maturité  | Améliorations possibles                       |
| ------------ | --------- | --------------------------------------------- |
| Fréquence    | ✅ Mature  | Fenêtrage temporel configurable               |
| Écart (Gap)  | ✅ Mature  | Gap moyen / médian / max séparés              |
| Cooccurrence | ✅ Mature  | Triplets en plus des paires                   |
| Temporel     | ⚠️ Correct | Détection de changement de régime             |
| Distribution | ✅ Mature  | Tests de goodness-of-fit (Kolmogorov-Smirnov) |
| Bayésien     | ✅ Mature  | Prior configurable, sensibilité paramétrable  |
| Graphe       | ✅ Mature  | Communautés dynamiques (temporal network)     |

### 2.2 — Critères de scoring (6)

| Critère         | Maturité  | Améliorations possibles                    |
| --------------- | --------- | ------------------------------------------ |
| Fréquence       | ✅ Mature  | Pondération par fenêtre temporelle         |
| Balance         | ✅ Mature  | Granularité configurable (3 ou 5 tranches) |
| Gap             | ✅ Mature  | Sensibilité ajustable                      |
| Cooccurrence    | ✅ Mature  | Prise en compte des triplets               |
| Structure       | ⚠️ Correct | Critères plus fins (parité, décades)       |
| Pattern Penalty | ⚠️ Rigide  | Seuils codés en dur → configurable         |

### 2.3 — Optimiseurs (5)

| Algorithme    | Maturité                | Améliorations possibles          |
| ------------- | ----------------------- | -------------------------------- |
| Génétique     | ✅ Mature                | Adaptive mutation rate           |
| Recuit Simulé | ❌ Inaccessible (BUG-02) | Corriger method_selector d'abord |
| Tabou         | ✅ Mature                | Tabu tenure adaptatif            |
| Hill Climbing | ✅ Mature                | Multi-start, stochastic HC       |
| NSGA-II       | ✅ Mature                | Objectifs supplémentaires        |

### 2.4 — Simulateurs (2)

| Simulateur  | Maturité | Améliorations possibles                              |
| ----------- | -------- | ---------------------------------------------------- |
| Monte Carlo | ✅ Mature | Variance reduction (antithetic), importance sampling |
| Robustesse  | ✅ Mature | Cross-validation k-fold, confidence intervals        |

---

## 3. Améliorations classées par niveau

### 3.1 — Indispensable (Phase A/B)

| ID     | Amélioration                              | Raison                                  | Effort   |
| ------ | ----------------------------------------- | --------------------------------------- | -------- |
| ALG-01 | Corriger method_selector (BUG-02)         | SA inaccessible en prod                 | 0.5 jour |
| ALG-02 | Rendre Pattern Penalty configurable       | Seuils arbitraires en dur               | 1 jour   |
| ALG-03 | Normalisation scoring stable (edge cases) | Scores incohérents sur petits ensembles | 1 jour   |

### 3.2 — Utile (Phase C/D)

| ID     | Amélioration                                 | Raison                                               | Effort    |
| ------ | -------------------------------------------- | ---------------------------------------------------- | --------- |
| ALG-04 | Greedy covering engine (système réduit)      | Fondation du wheeling                                | 3–5 jours |
| ALG-05 | Optimisation sous contrainte budgétaire      | Fondation du mode budget                             | 2–3 jours |
| ALG-06 | Benchmark automatisé des 5 méthodes          | Valider quelle méthode est la meilleure par contexte | 2 jours   |
| ALG-07 | Multi-start hill climbing                    | Éviter les minima locaux                             | 1 jour    |
| ALG-08 | Fenêtrage temporel configurable pour scoring | Score basé sur N derniers tirages                    | 1–2 jours |
| ALG-09 | Scoring séparé des étoiles/chance            | Score 0–10 distinct pour les numéros complémentaires | 1 jour    |

### 3.3 — Avancé (Phase D)

| ID     | Amélioration                                 | Raison                                            | Effort  |
| ------ | -------------------------------------------- | ------------------------------------------------- | ------- |
| ALG-10 | Triplets dans cooccurrence                   | Enrichir au-delà des paires                       | 2 jours |
| ALG-11 | Profils de scoring hybrides / custom         | Utilisateur défini ses propres poids              | 2 jours |
| ALG-12 | Adaptive mutation rate (génétique)           | Convergence plus rapide                           | 1 jour  |
| ALG-13 | Variance reduction Monte Carlo               | Simulations plus précises avec moins d'itérations | 2 jours |
| ALG-14 | Détection de changement de régime (temporal) | Alerter sur un changement de distribution         | 3 jours |

### 3.4 — Premium / Recherche (Phase E)

| ID     | Amélioration                                    | Raison                                                 | Effort     |
| ------ | ----------------------------------------------- | ------------------------------------------------------ | ---------- |
| ALG-15 | ILP exact pour covering design                  | Solution optimale garantie (NP-hard, petits ensembles) | 5 jours    |
| ALG-16 | Genetic wheel (covering optimization)           | Évolution de systèmes réduits entiers                  | 5 jours    |
| ALG-17 | Temporal network analysis                       | Communautés de numéros évoluant dans le temps          | 5 jours    |
| ALG-18 | Calibration automatique des poids (backtesting) | Optimiser les poids de scoring sur l'historique        | 5–10 jours |

---

## 4. Détail des améliorations clés

### ALG-04 — Greedy Covering Engine

**Description** : Algorithme glouton pour le problème de Set Cover / Maximum Coverage appliqué aux systèmes réduits de loteries.

**Principe mathématique** :
- Entrée : ensemble N de numéros choisis, paramètre k (taille grille), paramètre t (garantie de couverture)
- Objectif : trouver le minimum de grilles de k numéros tels que toute sous-combinaison de t numéros parmi N apparaît dans au moins une grille
- Approche gloutonne : à chaque itération, ajouter la grille qui couvre le plus de sous-combinaisons non couvertes
- Complexité : O(C(n,k) × C(n,t)) par itération — borner n ≤ 20, k ≤ 5, t ≤ 3

**Garantie** : approximation ln(n)+1 du Set Cover optimal (théorème de Chvátal).

**Impact backend** : nouveau module `engines/wheeling/greedy_cover.py`

### ALG-05 — Optimisation sous contrainte budgétaire

**Description** : Étant donné un budget B et un prix par grille P, trouver l'allocation optimale parmi : grilles top, portefeuille, système réduit.

**Principe** :
- Budget → nombre max de grilles = B / P
- Itérer : pour chaque allocation (n_top, n_portfolio, n_wheeling), calculer score couverture + score qualité + diversité
- Retourner le Pareto front (couverture vs coût)

### ALG-06 — Benchmark automatisé

**Description** : Pour un jeu et un snapshot statistique donnés, générer N grilles avec chacun des 5 algorithmes, scorer, et comparer.

**Métriques de comparaison** :
- Score moyen
- Score variance
- Temps d'exécution
- Diversité (Hamming distance moyenne)
- Couverture combinatoire

---

## 5. Impacts techniques

| Amélioration              | Backend | Frontend | API | DB  | Perf |
| ------------------------- | ------- | -------- | --- | --- | ---- |
| ALG-01 (method_selector)  | ●●      | ○        | ○   | ○   | ○    |
| ALG-04 (greedy covering)  | ●●●     | ○        | ●●● | ●●  | ●●●  |
| ALG-05 (budget optimizer) | ●●●     | ○        | ●●  | ●   | ●●   |
| ALG-06 (benchmark)        | ●●      | ●●       | ●●  | ○   | ●●   |
| ALG-08 (fenêtrage)        | ●       | ●        | ●   | ○   | ○    |
| ALG-11 (custom profiles)  | ●       | ●●       | ●   | ○   | ○    |
| ALG-18 (calibration auto) | ●●●     | ○        | ●   | ●   | ●●●  |

---

## 6. Risques

| Risque                                                | Probabilité | Impact | Mitigation                                        |
| ----------------------------------------------------- | ----------- | ------ | ------------------------------------------------- |
| Explosion combinatoire (covering grands ensembles)    | Haute       | Fort   | Bornes strictes n ≤ 20, timeout 30s               |
| Résultats non déterministes (algo stochastiques)      | Certaine    | Moyen  | Seed fixe en test, documentation variance         |
| Sur-optimisation scoring sur historique (overfitting) | Moyenne     | Moyen  | Validation croisée, backtesting out-of-sample     |
| Complexité de maintenance (nhiều algorithmes)         | Moyenne     | Moyen  | Interface commune BaseEngine, tests systématiques |

---

## 7. Critères d'acceptation

| Critère                                    | Mesure                                           |
| ------------------------------------------ | ------------------------------------------------ |
| BUG-02 corrigé et testé                    | Test avec n_grids=100 → SA sélectionné           |
| Greedy covering produit un covering valide | Test : C(n,t) sous-combinaisons couvertes à 100% |
| Benchmark compare les 5 méthodes           | Endpoint retourne tableau comparatif             |
| Temps de calcul covering < 30s pour n=15   | Test de performance                              |
| Normalisation scoring stable               | Test avec 1 tirage, 10 tirages, 1000 tirages     |

---

## 8. Checklist locale

- [ ] ALG-01 : Corriger method_selector.py + tests
- [ ] ALG-02 : Rendre Pattern Penalty configurable via profil
- [ ] ALG-03 : Stabiliser normalisation scoring edge cases
- [ ] ALG-04 : Créer engines/wheeling/greedy_cover.py + tests
- [ ] ALG-05 : Créer engines/wheeling/budget_optimizer.py + tests
- [ ] ALG-06 : Créer endpoint POST /benchmark + tests
- [ ] ALG-07 : Ajouter multi-start à hill_climbing.py
- [ ] ALG-08 : Paramètre window_size dans scoring
- [ ] ALG-09 : Scoring séparé étoiles dans scorer.py
- [ ] ALG-10 : Triplets dans cooccurrence engine
- [ ] ALG-11 : Endpoint custom weights + frontend CustomWeightsEditor
- [ ] ALG-12 : Adaptive mutation dans genetic.py
- [ ] ALG-13 : Antithetic variates dans monte_carlo.py
- [ ] ALG-14 : Détection régime dans temporal.py
- [ ] ALG-15 : ILP covering via scipy.optimize.linprog
- [ ] ALG-16 : Genetic wheel engine
- [ ] ALG-17 : Temporal graph analysis
- [ ] ALG-18 : Auto-calibration backtesting pipeline

Réf. : [27_Checklist_Globale_Evolutions](./27_Checklist_Globale_Evolutions.md)
