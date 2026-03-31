# 17 — Impacts Frontend

> Analyse complète des impacts de toutes les évolutions sur le frontend : pages, composants, hooks, stores, services API, routing, design system.

---

## Références croisées

- [00_Index_Evolutions](./00_Index_Evolutions.md)
- [07_Evolutions_UI_UX](./07_Evolutions_UI_UX.md) — Évolutions UX détaillées
- [13_Evolution_Tooltips_Aide_Contextuelle](./13_Evolution_Tooltips_Aide_Contextuelle.md) — Aide contextuelle
- [14_Evolution_Espace_Pedagogique](./14_Evolution_Espace_Pedagogique.md) — Pages pédagogiques
- [16_Impacts_Backend](./16_Impacts_Backend.md) — Vue backend
- [18_Impacts_API](./18_Impacts_API.md) — Vue API

---

## 1. État actuel du frontend

### Structure existante

```
frontend/src/
├── main.tsx                    # Point d'entrée
├── App.tsx                     # Router principal
├── pages/                      # 13 pages
│   ├── DashboardPage.tsx
│   ├── DrawsPage.tsx
│   ├── StatisticsPage.tsx
│   ├── GridsPage.tsx
│   ├── HistoryPage.tsx
│   ├── PortfolioPage.tsx
│   ├── SimulationPage.tsx
│   ├── FavoritesPage.tsx
│   ├── GlossaryPage.tsx
│   ├── HowItWorksPage.tsx
│   ├── AdminDBPage.tsx
│   ├── LoginPage.tsx
│   └── RegisterPage.tsx
├── components/                 # 40+ composants
│   ├── layout/                 # Header, Sidebar, Footer
│   ├── common/                 # PageIntro, LoadingSpinner, etc.
│   ├── auth/
│   ├── grids/
│   ├── draws/
│   └── statistics/
├── hooks/                      # 6 hooks
├── stores/                     # 3 Zustand stores
├── services/                   # 10 API services
├── types/                      # 9 type files
└── utils/                      # 3 utilitaires
```

### Métriques existantes

| Métrique       | Valeur                   |
| -------------- | ------------------------ |
| Pages          | 13                       |
| Composants     | ~40                      |
| Hooks          | 6                        |
| Stores Zustand | 3 (auth, game, settings) |
| Services API   | 10                       |
| Types          | 9 fichiers               |

---

## 2. Nouvelles pages

| Page             | Route         | Doc | Phase |
| ---------------- | ------------- | --- | ----- |
| `WheelingPage`   | `/wheeling`   | 08  | C.1   |
| `BudgetPage`     | `/budget`     | 09  | C.2   |
| `ComparatorPage` | `/comparator` | 10  | D.1   |

**Total pages** : 13 existantes + 3 nouvelles = **16 pages**

### Pages existantes modifiées

| Page             | Modifications                                                                                                 | Doc        |
| ---------------- | ------------------------------------------------------------------------------------------------------------- | ---------- |
| `DashboardPage`  | +7 blocs dynamiques (LatestDraw, Countdown, PlayedResults, TopGrids, StatOfDay, Suggestion, PortfolioSummary) | 15         |
| `GridsPage`      | +SaveButton, +explainButton, fix BUG-03 (envoyer profile), badge jouée/favorite, ReplayButton                 | 11, 12, 03 |
| `HistoryPage`    | Complètement enrichie : filtres, pagination, SavedResultCard, ReplayButton, 6 types de résultats              | 11         |
| `FavoritesPage`  | Converger vers HistoryPage filtrée (is_favorite=true)                                                         | 11         |
| `PortfolioPage`  | +SaveButton, +explainButton, affichage explication L1                                                         | 11, 12     |
| `SimulationPage` | +SaveButton, +explainButton, affichage explication L1                                                         | 11, 12     |
| `StatisticsPage` | Affichage étoiles séparées, StatOfTheDay, mode simplifié                                                      | 06, 15, 07 |
| `HowItWorksPage` | Enrichi en espace pédagogique (7 sections) + LearnTOC                                                         | 14         |
| `GlossaryPage`   | Enrichi avec liens vers sections pédagogiques                                                                 | 14         |
| `DrawsPage`      | Pagination (DT-05)                                                                                            | 03         |

---

## 3. Nouveaux composants

### Par module fonctionnel

#### Wheeling (doc 08) — 8 composants

| Composant            | Rôle                                         |
| -------------------- | -------------------------------------------- |
| `NumberGrid`         | Grille interactive sélection numéros         |
| `StarsGrid`          | Grille interactive sélection étoiles         |
| `SelectionSummary`   | Résumé de la sélection en cours              |
| `WheelingConfig`     | Formulaire de configuration (garantie, etc.) |
| `WheelingPreview`    | Aperçu avant génération                      |
| `WheelingResults`    | Résultats avec liste grilles + indicateurs   |
| `CoverageMatrix`     | Matrice visuelle de couverture               |
| `GainScenariosTable` | Tableau des scénarios de gains               |

#### Budget (doc 09) — 5 composants

| Composant                  | Rôle                                              |
| -------------------------- | ------------------------------------------------- |
| `BudgetInput`              | Saisie budget + slider                            |
| `ObjectiveSelector`        | Sélection objectif (couverture/diversité/scoring) |
| `BudgetRecommendationCard` | Carte recommandation par stratégie                |
| `BudgetResults`            | Vue résultats (3 stratégies comparées)            |
| `GainScenarioBar`          | Barre visuelle espérance de gain                  |

#### Comparateur (doc 10) — 5 composants

| Composant           | Rôle                                  |
| ------------------- | ------------------------------------- |
| `StrategySelector`  | Sélection de 2+ stratégies à comparer |
| `ComparisonTable`   | Tableau comparatif des axes           |
| `ComparisonRadar`   | Radar chart Recharts                  |
| `ComparisonScatter` | Scatter plot coût/score               |
| `ComparisonSummary` | Synthèse textuelle de comparaison     |

#### Historique / Favoris (doc 11) — 4 composants

| Composant         | Rôle                                      |
| ----------------- | ----------------------------------------- |
| `SaveButton`      | Bouton sauvegarder (réutilisable partout) |
| `ReplayButton`    | Bouton rejouer (recharger paramètres)     |
| `SavedResultCard` | Carte résultat sauvegardé (générique)     |
| `HistoryFilters`  | Filtres (type, date, favori, tags)        |

#### Explicabilité (doc 12) — 1 composant

| Composant          | Rôle                                                |
| ------------------ | --------------------------------------------------- |
| `ExplanationPanel` | Panneau 3 niveaux (résumé/interprétation/technique) |

#### Aide contextuelle (doc 13) — 3 composants

| Composant      | Rôle                              |
| -------------- | --------------------------------- |
| `EmptyState`   | État vide enrichi avec guidance   |
| `LoadingState` | État chargement contextuel        |
| `ErrorState`   | État erreur avec messages adaptés |

#### Automatisation / Dashboard (doc 15) — 9 composants

| Composant              | Rôle                             |
| ---------------------- | -------------------------------- |
| `LatestDrawCard`       | Dernier tirage avec numéros      |
| `NextDrawCountdown`    | Compte à rebours prochain tirage |
| `PlayedGridsResults`   | Résultats de vos grilles jouées  |
| `DailyTopGridsCard`    | Top 3 grilles du jour            |
| `StatOfTheDay`         | Statistique du jour              |
| `DailySuggestionCard`  | Grille suggérée avec explication |
| `PortfolioSummaryCard` | Résumé portefeuille              |
| `NotificationBell`     | Icône cloche + badge             |
| `NotificationDropdown` | Liste de notifications           |

#### UX transversal (doc 07) — 5 composants

| Composant          | Rôle                                         |
| ------------------ | -------------------------------------------- |
| `DataTable<T>`     | Tableau générique (sort, filter, pagination) |
| `StatCard`         | Carte statistique avec sparkline             |
| `GridCard`         | Carte grille enrichie                        |
| `ProgressFeedback` | Barre de progression pour actions longues    |
| `ModeToggle`       | Toggle simplifié/expert                      |

#### Pédagogie (doc 14) — 3 composants

| Composant            | Rôle                             |
| -------------------- | -------------------------------- |
| `LearnSection`       | Section pédagogique réutilisable |
| `LearnTOC`           | Table des matières interne       |
| `InteractiveExample` | Exemple interactif               |

**Total nouveaux composants** : **43 composants**
**Total global** : ~40 existants + 43 = **~83 composants**

---

## 4. Nouveaux hooks

| Hook                 | Rôle                                                | Doc |
| -------------------- | --------------------------------------------------- | --- |
| `useDisplayMode()`   | Retourne mode simplifié/expert depuis settingsStore | 07  |
| `useWheeling()`      | Gestion état local formulaire wheeling              | 08  |
| `useBudget()`        | Gestion état local budget                           | 09  |
| `useNotifications()` | Query notifications + badge count                   | 15  |
| `useSaveResult()`    | Mutation sauvegarde résultat (générique)            | 11  |

**Total hooks** : 6 existants + 5 = **11 hooks**

---

## 5. Stores Zustand modifiés

### settingsStore (existant — modifié)

```typescript
// Ajout :
displayMode: 'simplified' | 'expert'
setDisplayMode: (mode: 'simplified' | 'expert') => void
theme: 'dark' | 'light'  // doc 07 UX-07
setTheme: (theme: 'dark' | 'light') => void
```

### gameStore (existant — vérifié)

Doit correctement propager `selectedGameId` à TOUS les appels API. Correction BUG-01.

### Pas de nouveau store nécessaire

Les données spécifiques (wheeling, budget, comparateur) utilisent TanStack Query directement sans store global.

---

## 6. Nouveaux services API

| Service               | Fichier                       | Endpoints consommés        | Doc |
| --------------------- | ----------------------------- | -------------------------- | --- |
| `wheelingService`     | `services/wheelingApi.ts`     | 6 endpoints /wheeling      | 08  |
| `budgetService`       | `services/budgetApi.ts`       | 4 endpoints /budget        | 09  |
| `comparisonService`   | `services/comparisonApi.ts`   | 1 endpoint /comparison     | 10  |
| `historyService`      | `services/historyApi.ts`      | 8 endpoints /history       | 11  |
| `notificationService` | `services/notificationApi.ts` | 4 endpoints /notifications | 15  |
| `suggestionService`   | `services/suggestionApi.ts`   | 1 endpoint /suggestions    | 15  |

**Total services** : 10 existants + 6 = **16 services**

---

## 7. Nouveaux types TypeScript

| Fichier                 | Types principaux                                                                                        | Doc |
| ----------------------- | ------------------------------------------------------------------------------------------------------- | --- |
| `types/wheeling.ts`     | `WheelingSystem`, `WheelingConfig`, `WheelingPreview`, `WheelingResult`, `CoverageCell`, `GainScenario` | 08  |
| `types/budget.ts`       | `BudgetPlan`, `BudgetObjective`, `BudgetRecommendation`, `BudgetStrategy`                               | 09  |
| `types/comparison.ts`   | `ComparisonRequest`, `ComparisonResult`, `ComparisonAxis`, `StrategyType`                               | 10  |
| `types/history.ts`      | `SavedResult`, `SavedResultType`, `HistoryFilter`                                                       | 11  |
| `types/explanation.ts`  | `Explanation`, `ExplanationLevel`                                                                       | 12  |
| `types/notification.ts` | `Notification`, `NotificationType`                                                                      | 15  |
| `types/prizeTier.ts`    | `GamePrizeTier`                                                                                         | 08  |

**Total types** : 9 existants + 7 = **16 fichiers types**

---

## 8. Routing (App.tsx)

### Routes ajoutées

```typescript
// Nouvelles routes
<Route path="/wheeling" element={<WheelingPage />} />
<Route path="/budget" element={<BudgetPage />} />
<Route path="/comparator" element={<ComparatorPage />} />
```

### Navigation (Sidebar)

Restructuration par catégories (doc 07 UX-04) :

```
ANALYSE
├── Tirages
├── Statistiques
GÉNÉRATION
├── Grilles
├── Système réduit (nouveau)
├── Budget (nouveau)
ÉVALUATION
├── Portefeuille
├── Simulations
├── Comparateur (nouveau)
OUTILS
├── Historique
├── Favoris
├── Comment ça marche
├── Glossaire
ADMIN (si admin)
├── Base de données
```

---

## 9. Fichiers utilitaires impactés

| Fichier               | Modifications                                     |
| --------------------- | ------------------------------------------------- |
| `utils/constants.ts`  | Nouvelles couleurs, breakpoints, mode labels      |
| `utils/formatters.ts` | Formatters pour montants, pourcentages couverture |
| `utils/helpTexts.ts`  | Textes d'aide centralisés (doc 13) — NOUVEAU      |
| `utils/pdfExport.ts`  | Extension pour export wheeling, budget            |

---

## 10. Design System & Tokens (doc 07 UX-02)

### Variables CSS à définir

```css
:root {
  /* Couleurs primaires */
  --color-primary: #6366f1;
  --color-primary-hover: #4f46e5;
  --color-success: #22c55e;
  --color-warning: #f59e0b;
  --color-error: #ef4444;
  
  /* Mode sombre (défaut) */
  --color-bg: #0f172a;
  --color-surface: #1e293b;
  --color-text: #f8fafc;
  --color-text-muted: #94a3b8;
  
  /* Spacing */
  --space-xs: 0.25rem;
  --space-sm: 0.5rem;
  --space-md: 1rem;
  --space-lg: 1.5rem;
  --space-xl: 2rem;
}

/* Mode clair */
[data-theme="light"] {
  --color-bg: #f8fafc;
  --color-surface: #ffffff;
  --color-text: #0f172a;
  --color-text-muted: #64748b;
}
```

---

## 11. Matrice évolutions × impact frontend

| Évolution           | Pages    | Composants | Hooks | Services | Types |
| ------------------- | -------- | ---------- | ----- | -------- | ----- |
| Wheeling (08)       | +1       | +8         | +1    | +1       | +2    |
| Budget (09)         | +1       | +5         | +1    | +1       | +1    |
| Comparateur (10)    | +1       | +5         | —     | +1       | +1    |
| Historique (11)     | modif 4  | +4         | +1    | +1       | +1    |
| Explicabilité (12)  | modif 4  | +1         | —     | —        | +1    |
| Tooltips (13)       | modif ~8 | +3         | —     | —        | —     |
| Pédagogie (14)      | modif 2  | +3         | —     | —        | —     |
| Automatisation (15) | modif 1  | +9         | +1    | +2       | +1    |
| UX transversal (07) | modif ~5 | +5         | +1    | —        | —     |

---

## 12. Risques frontend

| Risque                                                    | Impact      | Mitigation                                      |
| --------------------------------------------------------- | ----------- | ----------------------------------------------- |
| 43 nouveaux composants → bundle size                      | Perf        | Code splitting par route (React.lazy)           |
| Incohérence visuelle entre anciens et nouveaux composants | UX          | Design tokens + composants partagés dès phase A |
| Complexité routing et navigation                          | Maintenance | Documentation routes + breadcrumbs              |
| Régression sur les pages existantes modifiées             | Qualité     | Tests snapshot + tests E2E sur flows critiques  |

---

## 13. Checklist locale

- [ ] Créer 3 nouvelles pages (Wheeling, Budget, Comparator)
- [ ] Créer 43 nouveaux composants répartis par module
- [ ] Créer 5 nouveaux hooks
- [ ] Créer 6 nouveaux services API
- [ ] Créer 7 nouveaux fichiers types
- [ ] Modifier settingsStore (displayMode, theme)
- [ ] Corriger BUG-03 : envoyer profile dans GridsPage
- [ ] Corriger BUG-01 côté frontend : propager gameId dans tous les appels
- [ ] Restructurer Sidebar par catégories
- [ ] Ajouter 3 nouvelles routes dans App.tsx
- [ ] Créer utils/helpTexts.ts centralisé
- [ ] Implémenter design tokens CSS variables
- [ ] Ajouter code splitting React.lazy pour nouvelles pages
- [ ] Enrichir DashboardPage avec 7 blocs dynamiques
- [ ] Enrichir HistoryPage avec filtres et pagination
- [ ] Enrichir HowItWorksPage avec 7 sections pédagogiques
- [ ] Enrichir GlossaryPage avec liens

Réf. : [27_Checklist_Globale_Evolutions](./27_Checklist_Globale_Evolutions.md)
