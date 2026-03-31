# 10 — Évolution : Comparateur de Stratégies

> Tableau de bord permettant de comparer visuellement et quantitativement les différentes approches (top 10, portefeuille, système réduit, budget, profils de scoring, méthodes d'optimisation).

---

## Références croisées

- [00_Index_Evolutions](./00_Index_Evolutions.md)
- [05_Evolutions_Algorithmiques](./05_Evolutions_Algorithmiques.md) — ALG-06 (benchmark)
- [08_Evolution_Systeme_Reduit_Wheeling](./08_Evolution_Systeme_Reduit_Wheeling.md) — Stratégie wheeling
- [09_Evolution_Mode_Budget_Intelligent](./09_Evolution_Mode_Budget_Intelligent.md) — Stratégie budget
- [11_Evolution_Historique_Favoris](./11_Evolution_Historique_Favoris.md) — Stratégies sauvegardées
- [12_Evolution_Explicabilite](./12_Evolution_Explicabilite.md) — Interprétation des résultats
- [17_Impacts_Frontend](./17_Impacts_Frontend.md) — [18_Impacts_API](./18_Impacts_API.md)

---

## 1. Objectif

Offrir un **tableau de bord comparatif** permettant de mettre côte à côte plusieurs stratégies et d'en visualiser les forces/faiblesses sur des axes mesurables.

---

## 2. Description détaillée

### 2.1 — Stratégies comparables

| Stratégie          | Source       | Description                                                                     |
| ------------------ | ------------ | ------------------------------------------------------------------------------- |
| Top N              | Existant     | Les N meilleures grilles du scoring nightly                                     |
| Portefeuille       | Existant     | Portefeuille optimisé (Greedy + Hamming)                                        |
| Aléatoire          | Existant     | N grilles aléatoires (baseline)                                                 |
| Système réduit     | Nouveau (08) | Wheeling à partir de numéros sélectionnés                                       |
| Budget intelligent | Nouveau (09) | Recommandation optimisée sous budget                                            |
| Profil X           | Existant     | Grilles avec profil scoring spécifique (frequence, gaps, cooccurrence, balance) |
| Méthode Y          | Existant     | Grilles via algorithme spécifique (genetic, SA, tabu, HC, NSGA-II)              |

### 2.2 — Axes de comparaison

| Axe                   | Description                                           | Unité  |
| --------------------- | ----------------------------------------------------- | ------ |
| **Score moyen**       | Qualité moyenne des grilles                           | 0–10   |
| **Score variance**    | Homogénéité du lot                                    | σ²     |
| **Diversité**         | Distance Hamming moyenne entre grilles                | 0–1    |
| **Couverture**        | % de t-combinaisons couvertes (si applicable)         | 0–100% |
| **Coût**              | Prix total en euros                                   | €      |
| **Nombre de grilles** | Quantité                                              | entier |
| **Robustesse**        | CV du score en bootstrap                              | 0–100% |
| **Gain espéré**       | Espérance conditionnelle pondérée par les prize tiers | €      |

### 2.3 — Visualisations

1. **Tableau comparatif** : stratégies en colonnes, axes en lignes, coloration conditionnelle
2. **Radar chart** : profil multi-axes de chaque stratégie (overlay)
3. **Bar chart** : score moyen côte à côte
4. **Scatter plot** : coût vs couverture, avec chaque stratégie comme point
5. **Résumé textuel** : « La stratégie Portefeuille offre le meilleur rapport score/diversité. Le système réduit maximise la couverture mais coûte 35 % de plus. »

---

## 3. Intérêt utilisateur

| Persona                | Bénéfice                                                                  |
| ---------------------- | ------------------------------------------------------------------------- |
| Joueur régulier        | « Quelle est la meilleure approche pour moi ? » — réponse visuelle claire |
| Joueur analytique      | « Je vois les trade-offs et je décide en connaissance de cause »          |
| Passionné combinatoire | « Je benchmark toutes les méthodes et optimise mon choix »                |

---

## 4. Intérêt produit

- **Engagement** : incite l'utilisateur à explorer plusieurs stratégies
- **Pédagogie** : illustre que chaque méthode a des forces et faiblesses
- **Complétion** : transforme le produit en véritable outil d'aide à la décision

---

## 5. Workflow utilisateur

1. **Sélection** : cocher 2 à 5 stratégies à comparer
2. **Configuration** : nombre de grilles commun (ou budget commun)
3. **Lancer** : bouton « Comparer »
4. **Résultats** :
   - Tableau comparatif avec meilleur score en surbrillance
   - Radar chart overlay
   - Scatter coût/couverture
   - Résumé textuel explicatif
5. **Actions** : sauvegarder la comparaison, exporter en PDF

---

## 6. Proposition d'implémentation

### 6.1 — Backend

#### Nouveau endpoint

```
POST /compare/strategies → ComparisonResponse
```

**Payload** :
```json
{
  "game_id": 1,
  "strategies": [
    {"type": "top", "count": 10},
    {"type": "portfolio", "count": 10},
    {"type": "random", "count": 10},
    {"type": "wheeling", "numbers": [3,7,14,21,28,35,42], "guarantee": 3}
  ],
  "include_gain_scenarios": true
}
```

**Réponse** : pour chaque stratégie, toutes les métriques (score, diversité, couverture, coût, robustesse, gain).

#### Nouveau service : `services/comparison.py`

```python
class ComparisonService:
    async def compare(game_id, strategies, include_gains) -> ComparisonResult
```

**Logique** :
1. Pour chaque stratégie demandée, appeler le service correspondant (grid, portfolio, wheeling, simulation)
2. Calculer les métriques unifiées
3. Assembler le résultat comparatif

**Pas de table DB dédiée** — la comparaison est un calcul à la volée. Si l'utilisateur veut sauvegarder, on utilise le mécanisme de persistance générique (FUNC-01).

### 6.2 — Frontend

#### Nouveaux composants

| Composant           | Rôle                                                      |
| ------------------- | --------------------------------------------------------- |
| `StrategySelector`  | Sélection des stratégies à comparer (checkboxes + config) |
| `ComparisonTable`   | Tableau comparatif avec coloration                        |
| `ComparisonRadar`   | Radar chart Recharts                                      |
| `ComparisonScatter` | Scatter plot coût/couverture                              |
| `ComparisonSummary` | Résumé textuel généré                                     |

#### Nouvelle page : `ComparatorPage.tsx`

#### Nouvelle route : `/comparator`

Sidebar : icône `BarChart3` (lucide-react), groupe « ÉVALUATION ».

---

## 7. Phasage

| Phase | Contenu                                         | Effort    |
| ----- | ----------------------------------------------- | --------- |
| C.7   | Backend : service comparison, endpoint, schémas | 2–3 jours |
| C.8   | Frontend : composants, page, intégration        | 3–4 jours |
| C.9   | Polish : résumé textuel, export PDF             | 1–2 jours |

---

## 8. Dépendances

| Dépendance                            | Raison              | Obligatoire ?   |
| ------------------------------------- | ------------------- | --------------- |
| Top 50 existant                       | Stratégie top       | Oui             |
| Portfolio existant                    | Stratégie portfolio | Oui             |
| Simulation existante (compare random) | Stratégie aléatoire | Oui             |
| 08 Wheeling                           | Stratégie wheeling  | Non (optionnel) |
| 09 Budget                             | Stratégie budget    | Non (optionnel) |
| FUNC-04 (prize_tiers)                 | Scénarios de gain   | Non             |

---

## 9. Risques

| Risque                                          | Probabilité | Impact | Mitigation                                                |
| ----------------------------------------------- | ----------- | ------ | --------------------------------------------------------- |
| Temps de calcul (5 stratégies en parallèle)     | Moyenne     | Moyen  | asyncio.gather pour paralléliser, timeout 60s             |
| Comparaison trompeuse (pas les mêmes n_grilles) | Moyenne     | Fort   | Forcer count commun ou afficher la comparaison par grille |
| Radar chart illisible avec > 4 stratégies       | Faible      | Mineur | Limiter à 5 stratégies max                                |
| Résumé textuel incorrect                        | Faible      | Moyen  | Templates structurés, pas de GPT                          |

---

## 10. Critères d'acceptation

| Critère                                               | Test             |
| ----------------------------------------------------- | ---------------- |
| Comparer 3 stratégies retourne métriques pour chacune | Test intégration |
| Métriques cohérentes (score, diversité, coût)         | Test calcul      |
| Radar chart rend correctement                         | Test visuel      |
| Temps < 30s pour 4 stratégies × 10 grilles            | Test perf        |
| Résumé textuel identifie la meilleure stratégie       | Test             |

---

## 11. Checklist locale

- [ ] Créer schemas/comparison.py
- [ ] Créer services/comparison.py
- [ ] Créer api/v1/comparison.py (1 endpoint)
- [ ] Tests unitaires service comparison
- [ ] Tests intégration API comparison
- [ ] Créer types/comparison.ts frontend
- [ ] Créer services/comparisonService.ts
- [ ] Créer hooks/useComparison.ts
- [ ] Créer composant StrategySelector
- [ ] Créer composant ComparisonTable
- [ ] Créer composant ComparisonRadar (Recharts)
- [ ] Créer composant ComparisonScatter
- [ ] Créer composant ComparisonSummary
- [ ] Créer ComparatorPage.tsx
- [ ] Ajouter route /comparator + sidebar
- [ ] PageIntro + tooltips
- [ ] Export PDF comparaison

Réf. : [27_Checklist_Globale_Evolutions](./27_Checklist_Globale_Evolutions.md)
