# 26 — Roadmap des Évolutions

> Planning détaillé par phases, avec dépendances, jalons, critères de passage, et estimations d'effort.

---

## Références croisées

- [00_Index_Evolutions](./00_Index_Evolutions.md)
- [04_Priorisation_Evolutions](./04_Priorisation_Evolutions.md) — Scoring et phases
- [03_Audit_Existant_et_Ecarts](./03_Audit_Existant_et_Ecarts.md) — Bugs prioritaires
- [27_Checklist_Globale_Evolutions](./27_Checklist_Globale_Evolutions.md) — Tâches atomiques

---

## 1. Vue d'ensemble

### Phases

```
P0 ─── Bugs critiques & stabilisation           ┐
  A ─── Quick wins techniques                    │  Socle
  B ─── Fondations fonctionnelles                ┘
  C ─── Cœur produit (Wheeling, Budget)          ┐
  D ─── Profondeur (Comparateur, Automatisation) │  Valeur
  E ─── Premium (Pédagogie avancée)              ┘
```

### Timeline estimée

```
Semaine   1   2   3   4   5   6   7   8   9  10  11  12  13  14  15  16  17
          ├───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┤
Phase P0  ████                                                              
Phase A       ████                                                          
Phase B           ████████████                                              
Phase C                       ████████                                      
Phase D                               ████████                              
Phase E                                       ████████                      
Buffer                                                ████                  
Total     ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
```

---

## 2. Phase P0 — Bugs critiques & stabilisation (Semaine 1)

**Objectif** : Corriger les 3 bugs critiques. Le produit existant fonctionne correctement.

| Tâche                                 | Docs   | Effort | Détail                                              |
| ------------------------------------- | ------ | ------ | --------------------------------------------------- |
| BUG-01 : Fix multi-lottery game_id    | 03, 16 | 3j     | Propager game_id dans tous services, engines, stats |
| BUG-02 : Fix method_selector          | 03, 16 | 0.5j   | Corriger logique de sélection d'algorithme          |
| BUG-03 : Fix scoring profile frontend | 03, 17 | 0.5j   | Envoyer profile dans GridsPage → API                |
| Snapshots de non-régression           | 24     | 1j     | Capturer SNAP-01 à SNAP-04 avant/après              |

**Effort total** : 5 jours (1 semaine)

**Jalon P0** : ✅ 337 tests passent + 3 bugs corrigés + snapshots capturés

**Critère de passage** :
- Les 337 tests existants passent
- BUG-01 : EuroMillions génère des scores différents de Loto FDJ
- BUG-02 : method_selector retourne des méthodes variées selon les paramètres
- BUG-03 : Le profile sélectionné en frontend est envoyé à l'API

---

## 3. Phase A — Quick wins techniques (Semaine 2)

**Objectif** : Corriger les dettes techniques fondamentales.

| Tâche                                 | Docs   | Effort | Détail                                             |
| ------------------------------------- | ------ | ------ | -------------------------------------------------- |
| DT-02 : Token blacklist PostgreSQL    | 21     | 1j     | Table + service + migration                        |
| DT-04 : Rate limiting (slowapi)       | 21, 18 | 1j     | Installation + configuration par route             |
| DT-05 : Pagination                    | 18     | 1j     | PaginationParams + endpoints draws, grids          |
| DT-03 : Cache applicatif (cachetools) | 22     | 0.5j   | Stats, games, prize_tiers                          |
| Index DB existants                    | 19, 22 | 0.5j   | scored_grids(game_id, score), draws(game_id, date) |
| DT-01 : Uniformiser /api/v1/          | 18     | 0.5j   | Vérifier tous les routers                          |

**Effort total** : 4.5 jours (~1 semaine)

**Jalon A** : ✅ Rate limiting actif + pagination + cache + token blacklist persisté

**Critère de passage** :
- 11ème requête /grids/generate en 1 min → 429
- GET /draws?limit=10&offset=20 fonctionne
- 2ème appel GET /statistics → cache hit (< 5ms)
- Token blacklisté survit à un redémarrage backend

---

## 4. Phase B — Fondations fonctionnelles (Semaines 3–5)

**Objectif** : Poser les fondations pour toutes les évolutions : modèles DB, historique, explicabilité, aide contextuelle, dashboard enrichi.

### B.1–B.3 : Semaine 3

| Tâche                                              | Docs   | Effort |
| -------------------------------------------------- | ------ | ------ |
| Migration : game_prize_tiers + seed Loto/EM        | 19, 08 | 1j     |
| Migration : user_saved_results                     | 19, 11 | 0.5j   |
| Migration : user_id sur scored_grids et portfolios | 19, 11 | 0.5j   |
| HistoryService + 8 endpoints                       | 11, 18 | 2j     |
| SaveButton + ReplayButton composants               | 11, 17 | 1j     |

### B.4–B.5 : Semaine 4

| Tâche                                                     | Docs   | Effort |
| --------------------------------------------------------- | ------ | ------ |
| engines/explainability/ (5 explainers)                    | 12, 16 | 2j     |
| ExplanationPanel composant                                | 12, 17 | 0.5j   |
| Intégration explanation dans grids, portfolio, simulation | 12, 18 | 1j     |
| helpTexts.ts + EmptyState/LoadingState/ErrorState         | 13, 17 | 1j     |
| Enrichir tooltips sur toutes les pages existantes         | 13     | 0.5j   |

### B.6–B.9 : Semaine 5

| Tâche                                                                 | Docs   | Effort |
| --------------------------------------------------------------------- | ------ | ------ |
| PED-01 + PED-02 : Sections pédagogiques (scores, simulations)         | 14     | 1j     |
| PED-03 + PED-05 + PED-06 : Stratégies, Loto vs EM, limites            | 14     | 1j     |
| Design tokens CSS variables                                           | 07     | 0.5j   |
| DataTable<T> générique                                                | 07     | 1j     |
| Dashboard enrichi (LatestDraw, TopGrids, PortfolioSummary, StatOfDay) | 15, 17 | 1.5j   |

**Effort total Phase B** : ~15 jours (3 semaines)

**Jalon B** : ✅ Historique fonctionnel + explicabilité inline + tooltips complets + dashboard enrichi + pédagogie scores/simulations

**Critères de passage** :
- Un utilisateur peut sauvegarder, lister, filtrer, rejouer un résultat
- Chaque grille générée a une explication L1
- Toutes les pages ont des tooltips et des empty states enrichis
- Dashboard affiche les 5 blocs dynamiques
- Section pédagogique accessible depuis HowItWorksPage

---

## 5. Phase C — Cœur produit (Semaines 6–8)

**Objectif** : Les 2 fonctionnalités cœur — Wheeling et Budget.

### C.1–C.2 : Semaine 6

| Tâche                                                           | Docs   | Effort |
| --------------------------------------------------------------- | ------ | ------ |
| engines/wheeling/ (greedy_cover, coverage, cost, gain_analyzer) | 08, 16 | 3j     |
| WheelingService (preview, generate, history, delete)            | 08, 16 | 1j     |
| 6 endpoints wheeling                                            | 08, 18 | 1j     |

### C.3 : Semaine 7

| Tâche                                                     | Docs   | Effort |
| --------------------------------------------------------- | ------ | ------ |
| WheelingPage + 8 composants frontend                      | 08, 17 | 3j     |
| NumberGrid, StarsGrid, CoverageMatrix, GainScenariosTable | 08, 17 | inclus |
| Tests wheeling (16 tests)                                 | 25     | 1j     |
| Migration wheeling_systems                                | 19     | 0.5j   |

### C.4 : Semaine 8

| Tâche                                   | Docs   | Effort |
| --------------------------------------- | ------ | ------ |
| engines/budget/ (optimizer, strategies) | 09, 16 | 2j     |
| BudgetService + 4 endpoints             | 09, 18 | 1j     |
| BudgetPage + 5 composants frontend      | 09, 17 | 1.5j   |
| Tests budget (10 tests)                 | 25     | 0.5j   |
| Migration budget_plans                  | 19     | Inclus |

**Effort total Phase C** : ~14 jours (~3 semaines)

**Jalon C** : ✅ Wheeling fonctionnel (preview + generate + résultats + export) + Budget intelligent (3 stratégies)

**Critères de passage** :
- Wheeling : sélectionner 10 numéros, garantie 3, générer → système réduit avec couverture > 95%
- Budget : entrer 10€ → 3 recommandations (top, portfolio, wheeling)
- Wheeling : n=20 → réponse en < 10s
- Budget : optimisation en < 5s
- Historique wheeling et budget consultable

---

## 6. Phase D — Profondeur (Semaines 9–11)

**Objectif** : Comparateur, automatisation, notifications.

### D.1 : Semaine 9

| Tâche                                                 | Docs   | Effort |
| ----------------------------------------------------- | ------ | ------ |
| ComparisonService                                     | 10, 16 | 1.5j   |
| 1 endpoint comparison                                 | 10, 18 | 0.5j   |
| ComparatorPage + 5 composants (table, radar, scatter) | 10, 17 | 2j     |
| Tests comparateur (8 tests)                           | 25     | 1j     |

### D.2–D.3 : Semaine 10

| Tâche                                    | Docs   | Effort |
| ---------------------------------------- | ------ | ------ |
| check_played_grids job                   | 15, 20 | 1j     |
| Migration grid_draw_results              | 19     | 0.5j   |
| PlayedGridsResults composant (Dashboard) | 15, 17 | 1j     |
| SuggestionService + endpoint             | 15, 16 | 1j     |
| DailySuggestionCard composant            | 15, 17 | 0.5j   |
| Extension nightly_pipeline               | 15, 20 | 1j     |

### D.4 : Semaine 11

| Tâche                                   | Docs   | Effort |
| --------------------------------------- | ------ | ------ |
| NotificationService + 4 endpoints       | 15, 18 | 1j     |
| Migration user_notifications            | 19     | 0.25j  |
| NotificationBell + NotificationDropdown | 15, 17 | 1j     |
| create_*_notifications jobs             | 15, 20 | 1j     |
| Tests automatisation (10 tests)         | 25     | 0.5j   |
| Mode simplifié/expert toggle            | 07     | 1j     |

**Effort total Phase D** : ~14 jours (~3 semaines)

**Jalon D** : ✅ Comparateur + vérification auto grilles + suggestions + notifications + mode expert/simplifié

**Critères de passage** :
- Comparer 3 stratégies → radar chart avec 8 axes
- Grille jouée + nouveau tirage → résultat automatique sur Dashboard
- Notification "Nouveau tirage" visible dans la cloche
- Toggle simplifié/expert modifie l'affichage

---

## 7. Phase E — Premium (Semaines 12–14)

**Objectif** : Finitions, pédagogie avancée, thème clair, onboarding.

| Tâche                                        | Docs | Effort |
| -------------------------------------------- | ---- | ------ |
| PED-04 : Systèmes réduits (pédagogie)        | 14   | 1j     |
| PED-07 : Coûts et compromis                  | 14   | 0.5j   |
| Enrichir GlossaryPage avec liens             | 14   | 0.5j   |
| Navigation restructurée (sidebar catégories) | 07   | 1.5j   |
| Breadcrumbs                                  | 07   | 0.5j   |
| Thème clair (light mode)                     | 07   | 1.5j   |
| Responsive amélioré (sm/md breakpoints)      | 07   | 1.5j   |
| Onboarding tour enrichi                      | 07   | 1j     |
| Star scoring séparé                          | 06   | 1.5j   |
| Multi-format export (PDF, CSV, JSON)         | 06   | 1.5j   |
| Code splitting React.lazy                    | 22   | 0.5j   |
| Documentation opérationnelle (runbooks)      | 23   | 1j     |

**Effort total Phase E** : ~12 jours (~2.5 semaines)

**Jalon E** : ✅ Produit complet, tous chantiers livrés

---

## 8. Buffer (Semaine 15–17)

**Objectif** : Absorber les retards, corriger les bugs découverts, finaliser.

| Activité                                   | Effort   |
| ------------------------------------------ | -------- |
| Correction bugs découverts en phases C-D-E | Variable |
| Tests E2E (optionnel)                      | 2j       |
| Optimisation performance (si nécessaire)   | 2j       |
| Documentation finale                       | 1j       |
| Revue globale qualité                      | 1j       |

---

## 9. Graphe de dépendances

```
P0 ──→ A ──→ B ──→ C ──→ D ──→ E
              │         │
              │         ├── C dépend de B (game_prize_tiers)
              │         └── C dépend de A (pagination, cache)
              │
              ├── B.history dépend de A (pagination)
              └── B.dashboard dépend de A (cache)

D.comparateur dépend de C (wheeling strategy comparée)
D.notifications dépend de B (historique)
D.check_grids dépend de B (game_prize_tiers)
E.star_scoring indépendant (peut être anticipé)
```

---

## 10. Jalons récapitulatifs

| Jalon | Semaine | Critère clé                                    | Tests |
| ----- | ------- | ---------------------------------------------- | ----- |
| P0    | S1      | 3 bugs corrigés, 337 tests                     | 337   |
| A     | S2      | Rate limit + pagination + cache + blacklist    | ~345  |
| B     | S5      | Historique + explicabilité + dashboard enrichi | ~375  |
| C     | S8      | Wheeling + Budget fonctionnels                 | ~401  |
| D     | S11     | Comparateur + auto + notifications             | ~411  |
| E     | S14     | Produit complet, toutes finitions              | ~420  |
| Final | S17     | Buffer absorbé, qualité validée                | ~420  |

---

## 11. Risques planning

| Risque                                           | Impact     | Mitigation                                |
| ------------------------------------------------ | ---------- | ----------------------------------------- |
| BUG-01 fix plus complexe que prévu (transversal) | +2-3 jours | Buffer semaine 1                          |
| Wheeling algorithmique complexe                  | +3-5 jours | Commencer avec greedy basique, ILP en E   |
| Comparateur simulation trop lent                 | +1-2 jours | Simulation allégée 100 iter               |
| Frontend : 43 nouveaux composants                | +3-5 jours | Réutiliser DataTable, design tokens       |
| Intégration dashboard 7 blocs                    | +2 jours   | Développer par bloc, déployer incrémental |

---

## 12. Checklist locale

- [ ] P0 : 3 bugs corrigés + snapshots capturés
- [ ] A : 5 dettes techniques corrigées
- [ ] B : Historique + explicabilité + tooltips + dashboard + pédagogie
- [ ] C : Wheeling + Budget
- [ ] D : Comparateur + automatisation + notifications
- [ ] E : Finitions + thème + responsive + nav + export
- [ ] Buffer : Bugs, E2E, optim, doc finale
- [ ] Chaque jalon validé avec critères de passage
- [ ] Tests passent à chaque jalon

Réf. : [27_Checklist_Globale_Evolutions](./27_Checklist_Globale_Evolutions.md)
