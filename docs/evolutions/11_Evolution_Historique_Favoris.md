# 11 — Évolution : Historique / Favoris / Rejouer une Stratégie

> Couche de persistance utilisateur complète : sauvegarder, retrouver, dupliquer et relancer tout type de résultat.

---

## Références croisées

- [00_Index_Evolutions](./00_Index_Evolutions.md)
- [06_Evolutions_Fonctionnelles](./06_Evolutions_Fonctionnelles.md) — FUNC-01 (persistance), FUNC-02 (export)
- [08_Evolution_Systeme_Reduit_Wheeling](./08_Evolution_Systeme_Reduit_Wheeling.md) — Sauvegarder wheeling
- [09_Evolution_Mode_Budget_Intelligent](./09_Evolution_Mode_Budget_Intelligent.md) — Sauvegarder plans
- [10_Evolution_Comparateur_Strategies](./10_Evolution_Comparateur_Strategies.md) — Sauvegarder comparaisons
- [19_Impacts_Base_De_Donnees](./19_Impacts_Base_De_Donnees.md) — Nouvelles tables
- [21_Impacts_Securite_Roles](./21_Impacts_Securite_Roles.md) — Données utilisateur

---

## 1. Objectif

Transformer la page Historique et Favoris actuels (basiques) en une **vraie couche de persistance utilisateur** permettant de sauvegarder, retrouver, dupliquer et relancer tout type de résultat produit par la plateforme.

---

## 2. État actuel

| Fonctionnalité | Statut | Limites |
|----------------|--------|---------|
| Grilles favorites | ✅ `is_favorite` sur `ScoredGrid` | Limité aux grilles scorées |
| Grilles jouées | ✅ `is_played` + `played_at` sur `ScoredGrid` | Limité aux grilles scorées |
| Historique grilles | ⚠️ Page HistoryPage | Affiche les grilles jouées mais pas d'autres types |
| Portefeuilles | ⚠️ Table `portfolios` | Pas de lien utilisateur, pas de duplication |
| Wheeling | ❌ N'existe pas | — |
| Budget plans | ❌ N'existe pas | — |
| Comparaisons | ❌ N'existe pas | — |
| Simulations | ❌ Non sauvegardées | Résultats perdus à chaque session |

---

## 3. Description détaillée

### 3.1 — Types de résultats sauvegardables

| Type | Contenu | Source |
|------|---------|--------|
| `grid` | Grille scorée (numéros, étoiles, score, breakdown) | GridsPage |
| `portfolio` | Portefeuille (grilles, métriques, stratégie) | PortfolioPage |
| `wheeling` | Système réduit (sélection, config, grilles, couverture) | WheelingPage |
| `budget_plan` | Plan budgétaire (budget, recommandations) | BudgetPage |
| `comparison` | Comparaison (stratégies, métriques, résultats) | ComparatorPage |
| `simulation` | Résultat Monte Carlo (distribution, stats) | SimulationPage |

### 3.2 — Actions utilisateur

| Action | Description |
|--------|-------------|
| **Sauvegarder** | Stocker le résultat avec un nom optionnel |
| **Lister** | Voir tous ses résultats sauvegardés, filtrables par type |
| **Détail** | Ouvrir un résultat sauvegardé en lecture |
| **Dupliquer** | Copier un résultat sauvegardé comme point de départ pour une nouvelle génération |
| **Relancer** | Réexécuter la même stratégie avec les mêmes paramètres (sur données à jour) |
| **Supprimer** | Effacer un résultat |
| **Exporter** | PDF / CSV / JSON |

### 3.3 — Approche de modélisation

**Option A — Modèle générique** (recommandé pour la simplicité) :

```python
class UserSavedResult(Base):
    __tablename__ = "user_saved_results"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    game_id: Mapped[int] = mapped_column(ForeignKey("game_definitions.id"))
    result_type: Mapped[str] = mapped_column(index=True)  # grid, portfolio, wheeling, budget, comparison, simulation
    name: Mapped[str | None]  # nom libre
    parameters: Mapped[dict] = mapped_column(JSON)  # paramètres de la génération
    result_data: Mapped[dict] = mapped_column(JSON)  # résultat complet
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    is_favorite: Mapped[bool] = mapped_column(default=False, index=True)
    tags: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
```

**Avantages** : un seul modèle, un seul set d'endpoints, extensible.  
**Inconvénients** : pas de typage fort en DB (tout est JSON).

**Option B — Modèles spécifiques** : `WheelingSystem`, `BudgetPlan` déjà prévus dans leurs chantiers respectifs + table générique pour les autres.

**Recommandation** : Option B — les chantiers 08 et 09 ont déjà défini des modèles spécifiques (WheelingSystem, BudgetPlan). Ajouter `UserSavedResult` pour les types restants (simulation, comparison).

---

## 4. Proposition d'implémentation

### 4.1 — Backend

#### Modèle `UserSavedResult` (pour simulations et comparaisons)

Voir section 3.3.

#### Extension des modèles existants

- `ScoredGrid` : ajouter `user_id` (nullable, FK) — pour lier les grilles à un utilisateur
- `Portfolio` : ajouter `user_id` (nullable, FK) — idem
- `WheelingSystem` : déjà `user_id` (doc 08)
- `BudgetPlan` : déjà `user_id` (doc 09)

#### Endpoints

```
GET    /history                     → list paginée de tous les résultats
GET    /history?type=wheeling       → filtrer par type
GET    /history/{id}                → détail d'un résultat
POST   /history                     → sauvegarder un résultat
DELETE /history/{id}                → supprimer
PATCH  /history/{id}/favorite       → toggle favori
POST   /history/{id}/duplicate      → dupliquer
POST   /history/{id}/replay         → relancer avec même paramètres
```

#### Service : `services/history.py`

```python
class HistoryService:
    async def list_results(user_id, type_filter, page, per_page) -> PaginatedResults
    async def get_result(result_id, user_id) -> SavedResult
    async def save_result(user_id, result_type, params, data) -> SavedResult
    async def delete_result(result_id, user_id) -> None
    async def duplicate(result_id, user_id) -> SavedResult
    async def replay(result_id, user_id) -> ReplayResult
```

### 4.2 — Frontend

#### Page `HistoryPage.tsx` enrichie

**Sections** :
1. **Filtres** : par type (grilles, portefeuilles, wheeling, budget, simulations, comparaisons), par date, par favori
2. **Liste** : cartes résumées avec type, nom, date, score principal, actions
3. **Tri** : par date, par score, par type
4. **Pagination** : 20 résultats par page

#### Enrichissements FavoritesPage

- Filtrer par type (pas seulement grilles)
- Actions : dupliquer, relancer, exporter

#### Nouveaux composants

| Composant | Rôle |
|-----------|------|
| `SavedResultCard` | Carte résumée d'un résultat (type, date, métriques clés) |
| `HistoryFilters` | Filtres par type, date, favori |
| `SaveButton` | Bouton « Sauvegarder » avec nom optionnel |
| `ReplayButton` | Bouton « Relancer cette stratégie » |

---

## 5. Phasage

| Phase | Contenu | Effort |
|-------|---------|--------|
| B.1 | Backend : modèle UserSavedResult, migration, service, endpoints | 2–3 jours |
| B.2 | Frontend : HistoryPage enrichie, composants, intégration | 2–3 jours |
| B.3 | Extension : ajouter user_id sur ScoredGrid et Portfolio + migration | 1 jour |
| C.x | Intégration avec chaque nouveau chantier (wheeling, budget, comparateur) | inclus dans chaque chantier |

---

## 6. Risques

| Risque | Probabilité | Impact | Mitigation |
|--------|-------------|--------|------------|
| Volume de données JSON croissant | Moyenne | Moyen | Politique de rétention (ex: 100 résultats max par user) |
| Replay avec données obsolètes (stats changées) | Certaine | Mineur | Indiquer « résultat recalculé avec les données du jour » |
| Migration user_id sur tables existantes | Faible | Moyen | Colonne nullable, pas de breaking change |
| Conflit entre is_favorite sur ScoredGrid et UserSavedResult | Faible | Mineur | Migrer progressivement, cohabitation initiale |

---

## 7. Critères d'acceptation

| Critère | Test |
|---------|------|
| Sauvegarder un résultat → retrouvé dans /history | Test E2E |
| Filtrer par type retourne les bons résultats | Test intégration |
| Dupliquer crée un nouveau résultat identique | Test |
| Relancer retourne un nouveau résultat (potentiellement différent) | Test |
| Pagination fonctionne (page 1, page 2) | Test |
| Supprimer → 204 + disparu de la liste | Test |

---

## 8. Checklist locale

- [ ] Créer modèle UserSavedResult + migration
- [ ] Ajouter user_id nullable sur ScoredGrid + migration
- [ ] Ajouter user_id nullable sur Portfolio + migration
- [ ] Créer schemas/history.py
- [ ] Créer repositories/history_repository.py
- [ ] Créer services/history.py
- [ ] Créer api/v1/history.py (8 endpoints)
- [ ] Tests unitaires service (6 tests)
- [ ] Tests intégration API (6 tests)
- [ ] Enrichir HistoryPage.tsx (filtres, pagination, types)
- [ ] Enrichir FavoritesPage.tsx (multi-type)
- [ ] Créer composant SavedResultCard
- [ ] Créer composant HistoryFilters
- [ ] Créer composant SaveButton (réutilisable)
- [ ] Créer composant ReplayButton
- [ ] Intégrer SaveButton dans GridsPage, PortfolioPage, SimulationPage
- [ ] Politique de rétention (100 résultats max)
- [ ] Pagination côté API + frontend

Réf. : [27_Checklist_Globale_Evolutions](./27_Checklist_Globale_Evolutions.md)
