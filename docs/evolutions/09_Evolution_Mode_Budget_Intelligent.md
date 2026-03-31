# 09 — Évolution : Mode Budget Intelligent

> L'utilisateur part de son budget, et le système lui propose la meilleure allocation de grilles (top, portefeuille, système réduit) optimisée pour son niveau de couverture souhaité.

---

## Références croisées

- [00_Index_Evolutions](./00_Index_Evolutions.md)
- [05_Evolutions_Algorithmiques](./05_Evolutions_Algorithmiques.md) — ALG-05 (optimisation sous contrainte)
- [06_Evolutions_Fonctionnelles](./06_Evolutions_Fonctionnelles.md) — FUNC-04 (gains), FUNC-05 (prix)
- [08_Evolution_Systeme_Reduit_Wheeling](./08_Evolution_Systeme_Reduit_Wheeling.md) — Dépendance directe
- [10_Evolution_Comparateur_Strategies](./10_Evolution_Comparateur_Strategies.md) — Compare budget vs autres
- [16_Impacts_Backend](./16_Impacts_Backend.md) — [17_Impacts_Frontend](./17_Impacts_Frontend.md)
- [18_Impacts_API](./18_Impacts_API.md) — [19_Impacts_Base_De_Donnees](./19_Impacts_Base_De_Donnees.md)

---

## 1. Objectif

Permettre à l'utilisateur de saisir un **budget en euros** et d'obtenir une recommandation complète : combien de grilles, avec quelle stratégie, quel niveau de couverture, quel scénario de rendement théorique.

---

## 2. Description détaillée

### 2.1 — Entrées utilisateur

| Paramètre | Type | Exemple | Obligatoire |
|-----------|------|---------|-------------|
| Budget (€) | Float | 20.00 | Oui |
| Jeu | Slug | loto-fdj | Oui |
| Objectif | Enum | `couverture` / `qualite` / `equilibre` | Oui |
| Numéros présélectionnés | list[int] (optionnel) | [7, 14, 23, 31, 45] | Non |

### 2.2 — Calculs internes

1. **Nombre max de grilles** : `budget / grid_price` (arrondi inférieur)
2. **Stratégies candidates** :
   - **Top N** : prendre les N meilleures grilles du top 50 existant
   - **Portefeuille** : générer un portefeuille de N grilles optimisé (diversité + score)
   - **Système réduit** : si numéros présélectionnés, construire un wheeling avec n grilles max
   - **Mixte** : combiner top + wheeling
3. **Scoring de chaque stratégie** :
   - Score moyen des grilles
   - Diversité (Hamming moyen)
   - Couverture combinatoire (si wheeling)
   - Scénario de gain théorique (espérance conditionnelle pondérée)
4. **Recommandation** : Pareto front (qualité vs couverture vs coût)

### 2.3 — Sortie

```json
{
  "budget": 20.00,
  "grid_price": 2.20,
  "max_grids": 9,
  "recommendations": [
    {
      "strategy": "portfolio",
      "grids": [...],
      "grid_count": 9,
      "total_cost": 19.80,
      "avg_score": 7.2,
      "diversity_score": 0.85,
      "coverage_rate": null,
      "expected_gain_scenario": { "optimistic": 120, "mean": 18, "pessimistic": 0 },
      "explanation": "Portefeuille de 9 grilles optimisé pour la diversité et le score."
    },
    {
      "strategy": "wheeling",
      "grids": [...],
      "grid_count": 8,
      "total_cost": 17.60,
      "avg_score": 6.8,
      "diversity_score": 0.72,
      "coverage_rate": 0.95,
      "expected_gain_scenario": { "optimistic": 150, "mean": 22, "pessimistic": 0 },
      "explanation": "Système réduit couvrant 95 % des triplets de vos 12 numéros."
    }
  ]
}
```

---

## 3. Intérêt utilisateur

| Persona | Bénéfice |
|---------|----------|
| Joueur régulier | « Je mets 10 € et le système me dit exactement quoi jouer » |
| Joueur analytique | « Je compare les stratégies dans mon budget et je choisis en connaissance de cause » |

---

## 4. Intérêt produit

- **Product-market fit** : le budget est la première contrainte du joueur
- **Différenciation** : aucun concurrent ne propose un optimiseur budgétaire multi-stratégie
- **Engagement** : l'utilisateur revient chaque semaine avec son budget

---

## 5. Workflow utilisateur

1. **Saisir le budget** : input numérique (€), slider optionnel
2. **Choisir l'objectif** : 3 boutons radio (couverture / qualité / équilibre)
3. **Optionnel** : sélectionner des numéros fétiches (réutilise NumberGrid du wheeling)
4. **Lancer** : bouton « Optimiser mon budget »
5. **Résultats** : 2–3 recommandations sous forme de cartes comparatives
   - Chaque carte : stratégie, grilles, coût, score, couverture, scénario de gain
   - Mise en avant de la recommandation « meilleure » selon l'objectif
6. **Actions** : Sauvegarder, exporter, voir détails de chaque recommandation

---

## 6. Proposition d'implémentation

### 6.1 — Backend

#### Nouveau modèle : `BudgetPlan`

```python
class BudgetPlan(Base):
    __tablename__ = "budget_plans"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    game_id: Mapped[int] = mapped_column(ForeignKey("game_definitions.id"))
    budget: Mapped[float]
    objective: Mapped[str]  # 'coverage', 'quality', 'balanced'
    selected_numbers: Mapped[list[int] | None] = mapped_column(JSON, nullable=True)
    recommendations: Mapped[list[dict]] = mapped_column(JSON)  # liste de recommandations
    chosen_strategy: Mapped[str | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
```

#### Nouveau service : `services/budget.py`

```python
class BudgetService:
    async def optimize(game_id, budget, objective, numbers=None) -> BudgetOptimizationResult
    async def get_user_plans(user_id) -> list[BudgetPlan]
    async def get_plan(plan_id) -> BudgetPlan
    async def delete_plan(plan_id) -> None
```

**Logique `optimize()`** :
1. Calculer `max_grids = floor(budget / game.grid_price)`
2. Si `max_grids < 1` → erreur 422 (budget insuffisant)
3. Générer stratégie TOP : appeler `grid_service.get_top(game_id, limit=max_grids)`
4. Générer stratégie PORTFOLIO : appeler `portfolio_service.generate(game_id, max_grids)`
5. Si `numbers` fournis et `len(numbers) >= k+1` : générer stratégie WHEELING via `wheeling_service`
6. Pour chaque stratégie : calculer métriques (score, diversité, couverture, gain scénarios)
7. Trier selon `objective` et retourner les recommandations

#### Nouveaux endpoints

```
POST   /budget/optimize    → BudgetOptimizationResponse
GET    /budget/history      → list[BudgetPlanResponse]
GET    /budget/{id}         → BudgetPlanResponse
DELETE /budget/{id}         → 204
```

### 6.2 — Frontend

#### Nouveaux composants

| Composant | Rôle |
|-----------|------|
| `BudgetInput` | Saisie budget (€) + slider |
| `ObjectiveSelector` | 3 boutons radio illustrés |
| `BudgetRecommendationCard` | Carte comparative d'une stratégie |
| `BudgetResults` | Conteneur des 2–3 cartes + mise en avant |
| `GainScenarioBar` | Barre visuelle optimiste/moyen/pessimiste |

#### Nouvelle page : `BudgetPage.tsx`

#### Nouvelle route : `/budget`

Sidebar : icône `Wallet` (lucide-react), groupe « GÉNÉRATION ».

---

## 7. Phasage

| Phase | Contenu | Effort |
|-------|---------|--------|
| C.4 | Backend : modèle, service, endpoints (requiert wheeling terminé) | 2–3 jours |
| C.5 | Frontend : composants, page, intégration | 2–3 jours |
| C.6 | Enrichissement : scénarios de gains, recommandation intelligente | 1–2 jours |

---

## 8. Dépendances

| Dépendance | Raison | Obligatoire ? |
|------------|--------|---------------|
| FUNC-05 (grid_price) | Calcul max_grids | Oui |
| 08 Wheeling (greedy_cover) | Stratégie wheeling | Non (optionnel dans budget) |
| FUNC-04 (prize_tiers) | Scénarios de gains | Non (estimations sans) |
| Top 50 existant | Stratégie top | Oui (déjà en prod) |
| Portfolio existant | Stratégie portfolio | Oui (déjà en prod) |

---

## 9. Risques

| Risque | Probabilité | Impact | Mitigation |
|--------|-------------|--------|------------|
| Temps de calcul long (3 stratégies à générer) | Moyenne | Moyen | Paralléliser les 3 stratégies, timeout 30s |
| Scénarios de gains trompeurs | Haute | Critique | Vocabulaire strict + disclaimer + « conditionnel » |
| Budget insuffisant (< 1 grille) | Basse | Mineur | Validation 422 + message UX |
| Stratégie wheeling non disponible (pas de numéros) | Fréquente | Mineur | Afficher 2 stratégies au lieu de 3 |

---

## 10. Critères d'acceptation

| Critère | Test |
|---------|------|
| Budget 20€, Loto → 9 grilles max proposées | Test unitaire |
| 2–3 stratégies comparées avec métriques | Test intégration |
| Scénarios de gains cohérents | Test calcul |
| Sauvegarde / historique fonctionnel | Test E2E |
| Budget < prix grille → erreur claire | Test validation |
| Temps de réponse < 15s | Test perf |

---

## 11. Checklist locale

- [ ] Créer modèle BudgetPlan + migration Alembic
- [ ] Ajouter grid_price dans game configs YAML
- [ ] Créer schemas/budget.py
- [ ] Créer repositories/budget_repository.py
- [ ] Créer services/budget.py avec logique optimize()
- [ ] Créer api/v1/budget.py (4 endpoints)
- [ ] Tests unitaires service budget (5 tests min)
- [ ] Tests intégration API budget (4 tests min)
- [ ] Créer types/budget.ts frontend
- [ ] Créer services/budgetService.ts
- [ ] Créer hooks/useBudget.ts
- [ ] Créer composant BudgetInput
- [ ] Créer composant ObjectiveSelector
- [ ] Créer composant BudgetRecommendationCard
- [ ] Créer composant BudgetResults
- [ ] Créer BudgetPage.tsx
- [ ] Ajouter route /budget + sidebar
- [ ] PageIntro + tooltips
- [ ] Disclaimer mention légale

Réf. : [27_Checklist_Globale_Evolutions](./27_Checklist_Globale_Evolutions.md)
