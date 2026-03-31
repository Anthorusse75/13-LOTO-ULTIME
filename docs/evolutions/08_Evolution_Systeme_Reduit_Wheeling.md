# 08 — Évolution : Système Réduit / Wheeling / Covering Design

> Chantier de **différenciation forte** — Permettre à l'utilisateur de sélectionner des numéros et de générer un système réduit optimisé qui garantit une couverture combinatoire maximale avec un minimum de grilles.

---

## Références croisées

- [00_Index_Evolutions](./00_Index_Evolutions.md)
- [05_Evolutions_Algorithmiques](./05_Evolutions_Algorithmiques.md) — ALG-04 (Greedy Cover), ALG-15 (ILP), ALG-16 (Genetic Wheel)
- [06_Evolutions_Fonctionnelles](./06_Evolutions_Fonctionnelles.md) — FUNC-04 (tableaux de gains), FUNC-05 (prix grille)
- [09_Evolution_Mode_Budget_Intelligent](./09_Evolution_Mode_Budget_Intelligent.md) — Réutilise le wheeling
- [10_Evolution_Comparateur_Strategies](./10_Evolution_Comparateur_Strategies.md) — Compare avec wheeling
- [16_Impacts_Backend](./16_Impacts_Backend.md)
- [17_Impacts_Frontend](./17_Impacts_Frontend.md)
- [18_Impacts_API](./18_Impacts_API.md)
- [19_Impacts_Base_De_Donnees](./19_Impacts_Base_De_Donnees.md)
- [22_Impacts_Performance_Scalabilite](./22_Impacts_Performance_Scalabilite.md)

---

## 1. Objectif

Offrir un **outil interactif de construction de systèmes réduits** : l'utilisateur choisit ses numéros favoris, configure le niveau de couverture souhaité, et obtient un ensemble optimisé de grilles avec toutes les métriques associées (couverture, coût, scénarios de gains).

---

## 2. Contexte technique : qu'est-ce qu'un système réduit ?

### 2.1 — Terminologie

| Terme                 | Définition                                                                                                                     |
| --------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| **Système réduit**    | Ensemble de grilles construit pour couvrir toutes les sous-combinaisons d'un sous-ensemble de numéros choisis                  |
| **Wheeling system**   | Terme anglais pour système réduit                                                                                              |
| **Covering design**   | Formalisation mathématique : C(n, k, t) — couvrir toute t-combinaison d'un ensemble de n éléments avec des blocs de k éléments |
| **Full wheel**        | Toutes les C(n, k) combinaisons — coûteux mais exhaustif                                                                       |
| **Abbreviated wheel** | Sous-ensemble optimisé — moins de grilles, couverture partielle ou totale d'un sous-niveau t                                   |

### 2.2 — Formalisation mathématique

Soit :
- **N** : ensemble de numéros sélectionnés par l'utilisateur (|N| = n)
- **k** : nombre de numéros par grille (ex: 5 pour Loto FDJ)
- **t** : niveau de garantie (2 ≤ t ≤ k) — « si t numéros parmi mes N sont tirés, au moins une grille a ces t numéros »

Le **covering number** C(n, k, t) est le nombre minimal de grilles de k éléments parmi n tels que chaque t-combinaison apparaît dans au moins une grille.

**Exemples** :
- Loto FDJ, n=10, k=5, t=3 : ~10 grilles (au lieu de C(10,5) = 252)
- Loto FDJ, n=15, k=5, t=3 : ~50 grilles (au lieu de C(15,5) = 3003)
- Loto FDJ, n=15, k=5, t=4 : ~200 grilles

### 2.3 — Relation avec Set Cover

Le problème C(n, k, t) est un cas particulier du **Set Cover Problem** (NP-hard). L'algorithme glouton est une approximation en O(ln n + 1) du minimum.

---

## 3. Intérêt utilisateur

| Persona                | Bénéfice                                                                          |
| ---------------------- | --------------------------------------------------------------------------------- |
| Joueur régulier        | « Je choisis mes 12 numéros fétiches et le système me dit quoi jouer exactement » |
| Joueur analytique      | « Je vois exactement quelle couverture j'obtiens et combien ça coûte »            |
| Passionné combinatoire | « J'explore les paramètres (n, k, t) et je comprends les compromis »              |

---

## 4. Intérêt produit

- **Différenciation forte** : très peu de plateformes offrent un covering design interactif
- **Rétention** : l'utilisateur revient pour construire ses systèmes tirage après tirage
- **Monétisation potentielle** : feature premium naturelle

---

## 5. Workflow utilisateur

### Étape 1 — Sélection des numéros

L'utilisateur voit une **grille visuelle** correspondant au jeu sélectionné :
- Loto FDJ : grille 1–49 (7×7) + grille chance 1–10
- EuroMillions : grille 1–50 (5×10) + grille étoiles 1–12

Il clique sur les numéros souhaités. Les numéros sélectionnés sont mis en avant. Un compteur affiche « 12/49 numéros sélectionnés ».

**Bornes** : 6 ≤ n ≤ 20 (numéros principaux), 0 ≤ m ≤ 6 (étoiles/chance).

### Étape 2 — Configuration

| Paramètre      | Description                                         | Valeur par défaut |
| -------------- | --------------------------------------------------- | ----------------- |
| Garantie t     | Niveau de sous-combinaison garanti (2, 3, 4 ou k)   | 3                 |
| Étoiles/chance | Stratégie : toutes les combinaisons ou distribution | « distribuer »    |

**Présets** :
- « Économique » : t=2 (couverture minimale, peu de grilles)
- « Équilibré » : t=3 (bon compromis)
- « Maximal » : t=4 (couverture étendue, plus de grilles)

### Étape 3 — Preview (avant génération)

Afficher immédiatement (calcul rapide) :
- Nombre estimé de grilles
- Coût total estimé
- Nombre de sous-combinaisons à couvrir : C(n, t)
- Comparaison avec le full wheel : C(n, k) grilles

### Étape 4 — Génération

Appel API → retour :
- Liste des grilles générées (chaque grille = numéros principaux + étoiles/chance)
- **Métriques** :
  - Taux de couverture : 100 % si covering exact, sinon % de t-combinaisons couvertes
  - Coût total : nombre_grilles × prix_grille
  - Réduction : (1 - n_grilles / C(n,k)) × 100 %
  - Distribution des numéros : histogramme de fréquence dans le système

### Étape 5 — Résultats enrichis

- **Tableau des grilles** : numéros + étoiles, triable, exportable
- **Matrice de couverture** : visualisation heatmap (quels numéros apparaissent dans quelles grilles)
- **Scénarios de gains** : si X numéros + Y étoiles sont tirés, combien de grilles matchent quel rang
  - Scénario optimiste : meilleur cas raisonnable
  - Scénario moyen : espérance
  - Scénario pessimiste : pire cas
- **Bouton sauvegarder** → stocke le système dans l'historique utilisateur

---

## 6. Proposition d'implémentation

### 6.1 — Backend

#### Nouveau modèle : `WheelingSystem`

```python
class WheelingSystem(Base):
    __tablename__ = "wheeling_systems"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    game_id: Mapped[int] = mapped_column(ForeignKey("game_definitions.id"), index=True)
    selected_numbers: Mapped[list[int]] = mapped_column(JSON)
    selected_stars: Mapped[list[int] | None] = mapped_column(JSON, nullable=True)
    guarantee_level: Mapped[int]  # t
    grids: Mapped[list[dict]] = mapped_column(JSON)  # [{numbers: [...], stars: [...]}]
    grid_count: Mapped[int]
    total_cost: Mapped[float]
    coverage_rate: Mapped[float]
    reduction_rate: Mapped[float]
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
```

#### Nouveau modèle : `GamePrizeTier`

```python
class GamePrizeTier(Base):
    __tablename__ = "game_prize_tiers"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    game_id: Mapped[int] = mapped_column(ForeignKey("game_definitions.id"), index=True)
    rank: Mapped[int]
    name: Mapped[str]  # "5+chance", "5+2★"
    match_numbers: Mapped[int]  # nombre de numéros corrects requis
    match_stars: Mapped[int]  # nombre d'étoiles/chance correctes requises
    avg_prize: Mapped[float]  # gain moyen en euros
    probability: Mapped[float]  # probabilité théorique
```

#### Nouveau engine : `engines/wheeling/`

```
engines/wheeling/
├── __init__.py
├── greedy_cover.py     # Algorithme glouton de covering (V1)
├── coverage.py         # Calcul du taux de couverture
├── cost_estimator.py   # Estimation du coût
├── gain_analyzer.py    # Scénarios de gains par rang
└── engine.py           # Orchestrateur
```

**Algorithme Greedy Cover** (V1) :
```python
def greedy_cover(numbers: list[int], k: int, t: int) -> list[tuple[int, ...]]:
    """
    Algorithme glouton pour le covering design C(n, k, t).
    
    1. Énumérer toutes les t-combinaisons de `numbers` → univers U
    2. Pour chaque k-combinaison candidate :
       a. Calculer le nombre de t-combinaisons de U qu'elle couvre
       b. Sélectionner celle qui couvre le plus (glouton)
    3. Retirer les t-combinaisons couvertes de U
    4. Répéter jusqu'à U vide
    
    Complexité : O(C(n,k) × C(k,t)) par itération
    Garantie : approximation ln(C(n,t)) + 1 du minimum
    """
```

**Gestion des étoiles / chance** :
- Les étoiles sont un problème séparé (petit pool)
- Loto FDJ : chance 1/10 → distribuer cycliquement parmi les grilles
- EuroMillions : C(m, 2) étoiles parmi m sélectionnées → combiner avec grilles principales

#### Nouveau service : `services/wheeling.py`

```python
class WheelingService:
    async def preview(game_id, numbers, stars, guarantee) -> WheelingPreview
    async def generate(game_id, numbers, stars, guarantee) -> WheelingResult
    async def get_user_systems(user_id) -> list[WheelingSystem]
    async def get_system(system_id) -> WheelingSystem
    async def delete_system(system_id) -> None
```

#### Nouveaux endpoints

```
POST   /wheeling/preview     → WheelingPreviewResponse
POST   /wheeling/generate    → WheelingGenerateResponse
GET    /wheeling/history     → list[WheelingSystemResponse]
GET    /wheeling/{id}        → WheelingSystemResponse
DELETE /wheeling/{id}        → 204
GET    /games/{slug}/prize-tiers → list[PrizeTierResponse]
```

### 6.2 — Frontend

#### Nouveaux composants

| Composant            | Rôle                                               |
| -------------------- | -------------------------------------------------- |
| `NumberGrid`         | Grille interactive de sélection (1–49/50/69/70)    |
| `StarsGrid`          | Grille interactive étoiles/chance/PowerBall        |
| `SelectionSummary`   | Résumé de la sélection (count, auto-validation)    |
| `WheelingConfig`     | Panneau de configuration (t, présets, étoiles)     |
| `WheelingPreview`    | Affichage preview (coût estimé, grilles estimées)  |
| `WheelingResults`    | Résultats complets (grilles, métriques, scénarios) |
| `CoverageMatrix`     | Heatmap de couverture (numéros × grilles)          |
| `GainScenariosTable` | Tableau 3 scénarios × rangs de gains               |

#### Nouvelle page : `WheelingPage.tsx`

Layout en 4 sections :
1. **Sélection** : NumberGrid + StarsGrid + SelectionSummary
2. **Configuration** : WheelingConfig + WheelingPreview
3. **Résultats** : WheelingResults + CoverageMatrix
4. **Gains** : GainScenariosTable

#### Nouvelle route : `/wheeling`

Sidebar : icône `Layers` (lucide-react), groupe « GÉNÉRATION ».

---

## 7. Phasage

| Phase | Contenu                                                                  | Effort    |
| ----- | ------------------------------------------------------------------------ | --------- |
| C.1   | Backend : modèles, migration, greedy_cover, coverage, service, endpoints | 3–5 jours |
| C.2   | Frontend : NumberGrid, StarsGrid, page assemblage, intégration API       | 3–5 jours |
| C.3   | Enrichissement : GainScenarios, CoverageMatrix, preview, export          | 2–3 jours |
| D.1   | Algorithme avancé : ILP exact ou Genetic Wheel (V2)                      | 3–5 jours |

---

## 8. Risques

| Risque                                       | Probabilité | Impact   | Mitigation                                                  |
| -------------------------------------------- | ----------- | -------- | ----------------------------------------------------------- |
| Explosion combinatoire n > 20                | Haute       | Fort     | Borne stricte n ≤ 20, m ≤ 6, timeout 30s                    |
| UX confuse pour novices                      | Moyenne     | Fort     | Présets, PageIntro explicatif, mode simplifié               |
| Covering non optimal (glouton)               | Certaine    | Faible   | Acceptable en V1, ILP en V2                                 |
| Formulation trompeuse (« garantie de gain ») | Moyenne     | Critique | Vocabulaire : « couverture combinatoire », pas « garantie » |
| Résultats lents sur mobile                   | Moyenne     | Moyen    | Calcul côté serveur, pas côté client                        |

---

## 9. Critères d'acceptation

| Critère                                           | Test             |
| ------------------------------------------------- | ---------------- |
| n=10, k=5, t=3 → ≤ 15 grilles et couverture 100%  | Test unitaire    |
| n=15, k=5, t=3 → ≤ 60 grilles et couverture 100%  | Test unitaire    |
| Toute t-combinaison de N apparaît dans ≥ 1 grille | Test de validité |
| Coût = grid_count × grid_price                    | Test calcul      |
| Scénarios de gains cohérents avec prize_tiers     | Test calcul      |
| Temps < 5s pour n ≤ 15, < 30s pour n ≤ 20         | Test perf        |
| Preview retourne en < 500ms                       | Test perf        |
| Système sauvegardé et retrouvable dans historique | Test E2E         |

---

## 10. Tests à prévoir

- [ ] Unit : greedy_cover avec n=8, k=5, t=2 → vérifier couverture
- [ ] Unit : greedy_cover avec n=10, k=5, t=3 → vérifier couverture
- [ ] Unit : coverage.py — calcul C(n,t), taux de couverture
- [ ] Unit : cost_estimator — coût total, réduction
- [ ] Unit : gain_analyzer — scénarios 3 niveaux
- [ ] Unit : étoiles distribution cyclique
- [ ] Integration : POST /wheeling/preview → 200 + métriques
- [ ] Integration : POST /wheeling/generate → 200 + grilles
- [ ] Integration : GET /wheeling/history → liste
- [ ] Integration : DELETE /wheeling/{id} → 204
- [ ] Performance : n=20, k=5, t=3 → temps < 30s
- [ ] Validation : n > 20 → 422
- [ ] Validation : t > k → 422
- [ ] Frontend : clic numéros → mise à jour compteur
- [ ] Frontend : sélection + config → preview affiché
- [ ] Frontend : générer → résultats affichés

---

## 11. Checklist locale

- [ ] Créer modèle WheelingSystem + migration Alembic
- [ ] Créer modèle GamePrizeTier + migration + seed Loto/EuroMillions
- [ ] Créer engines/wheeling/greedy_cover.py
- [ ] Créer engines/wheeling/coverage.py
- [ ] Créer engines/wheeling/cost_estimator.py
- [ ] Créer engines/wheeling/gain_analyzer.py
- [ ] Créer engines/wheeling/engine.py (orchestrateur)
- [ ] Créer schemas/wheeling.py (request/response)
- [ ] Créer schemas/prize_tier.py
- [ ] Créer repositories/wheeling_repository.py
- [ ] Créer services/wheeling.py
- [ ] Créer api/v1/wheeling.py (5 endpoints)
- [ ] Créer api/v1/prize_tiers.py (1 endpoint)
- [ ] Enregistrer routers dans api/v1/__init__.py
- [ ] Écrire tests unitaires engines (8 tests min)
- [ ] Écrire tests intégration API (6 tests min)
- [ ] Écrire test performance n=20
- [ ] Créer types/wheeling.ts frontend
- [ ] Créer services/wheelingService.ts
- [ ] Créer hooks/useWheeling.ts
- [ ] Créer composant NumberGrid
- [ ] Créer composant StarsGrid
- [ ] Créer composant SelectionSummary
- [ ] Créer composant WheelingConfig
- [ ] Créer composant WheelingPreview
- [ ] Créer composant WheelingResults
- [ ] Créer composant CoverageMatrix
- [ ] Créer composant GainScenariosTable
- [ ] Créer WheelingPage.tsx
- [ ] Ajouter route /wheeling dans App.tsx
- [ ] Ajouter entrée Sidebar « Système réduit »
- [ ] PageIntro + tooltips sur WheelingPage
- [ ] Export PDF des grilles wheeling
- [ ] Disclaimer mention légale sur la page

Réf. : [27_Checklist_Globale_Evolutions](./27_Checklist_Globale_Evolutions.md)
