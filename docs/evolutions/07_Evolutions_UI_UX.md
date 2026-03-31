# 07 — Évolutions UI/UX

> Design system, navigation, modes simplifié/expert, composants, tableaux, cartes, graphes, responsive. Tout ce qui touche à l'interface et l'expérience.

---

## Références croisées

- [00_Index_Evolutions](./00_Index_Evolutions.md)
- [02_Strategie_Produit](./02_Strategie_Produit.md) — Personas & modes
- [03_Audit_Existant_et_Ecarts](./03_Audit_Existant_et_Ecarts.md) — Dettes UX
- [12_Evolution_Explicabilite](./12_Evolution_Explicabilite.md) — Couche d'explication
- [13_Evolution_Tooltips_Aide_Contextuelle](./13_Evolution_Tooltips_Aide_Contextuelle.md) — Microcopy
- [17_Impacts_Frontend](./17_Impacts_Frontend.md) — Impacts composants
- [27_Checklist_Globale_Evolutions](./27_Checklist_Globale_Evolutions.md)

---

## 1. Objectif du document

Définir les **évolutions d'interface et d'expérience** pour rendre LOTO ULTIME plus premium, lisible, guidé et différenciant. Ce document couvre layout, navigation, composants, modes, responsive, et design system.

---

## 2. État actuel de l'UI/UX

### 2.1 — Points forts

- Dark mode cohérent
- Tailwind CSS v4 bien intégré
- Composants structurés (layout, common, domain)
- Sidebar avec navigation claire
- PageIntro avec termes expliqués (récemment enrichi)
- InfoTooltip disponible
- Recharts pour les graphes
- DrawBalls animé

### 2.2 — Faiblesses identifiées

| Faiblesse | Impact | Réf. |
|-----------|--------|------|
| Interface unique (pas de mode simplifié/expert) | Novices dépassés, experts sous-informés | DUX-02 |
| Density d'information inégale | Certaines pages denses, d'autres vides | — |
| Feedback des calculs longs (spinner seul) | Anxiété utilisateur | DUX-04 |
| Tableaux basiques (pas de tri, filtre, search) | Difficile de naviguer dans 50+ grilles | — |
| Pas de design tokens formalisés | Couleurs/spacings ad hoc | — |
| Responsive limité | Sidebar collapse, tableaux overflow sur mobile | — |
| Pas de skeleton loading cohérent | Skeleton existe mais peu utilisé | — |

---

## 3. Évolutions proposées

### UX-01 : Mode simplifié / Mode expert

**Description** : Toggle global dans le header ou les settings. Le mode simplifié masque les détails avancés, le mode expert les affiche tous.

**Comportement par mode** :

| Élément | Mode simplifié | Mode expert |
|---------|----------------|-------------|
| Score détaillé (6 critères) | Score global seul | Breakdown complet |
| Paramètres d'optimisation | Sélection pré-configurée | Tous les paramètres |
| Graphes statistiques | 3 tabs essentiels | 9 tabs complets |
| Wheeling config | Présets (débutant, intermédiaire) | Paramètres fins (n, t) |
| Simulation | Résultat synthétique | Tous les indicateurs |
| Tooltips | Affichés par défaut | Masqués (accessible au hover) |

**Implémentation** :
- Ajouter `displayMode: 'simple' | 'expert'` dans `settingsStore.ts`
- Hook `useDisplayMode()` retournant le mode actuel
- Chaque composant conditionne l'affichage : `{isExpert && <DetailPanel />}`
- Persist dans localStorage

**Phase** : B

---

### UX-02 : Design tokens & système de couleurs

**Description** : Formaliser les tokens de design (couleurs, espacements, bordures, ombres) pour garantir la cohérence.

**Tokens proposés** :

```css
/* Couleurs sémantiques */
--color-primary: #3B82F6;     /* blue-500 */
--color-success: #10B981;     /* emerald-500 */
--color-warning: #F59E0B;     /* amber-500 */
--color-danger: #EF4444;      /* red-500 */
--color-info: #6366F1;        /* indigo-500 */

/* Scores */
--color-score-excellent: #10B981;  /* ≥ 8 */
--color-score-good: #3B82F6;       /* ≥ 6 */
--color-score-average: #F59E0B;    /* ≥ 4 */
--color-score-poor: #EF4444;       /* < 4 */

/* Espacements */
--space-section: 2rem;
--space-card: 1.5rem;
--space-element: 1rem;
--space-tight: 0.5rem;
```

**Phase** : A

---

### UX-03 : Composants enrichis

**Tableaux améliorés** :
- Tri par colonne (clic header)
- Filtre texte
- Pagination intégrée
- Sélection de lignes
- Actions par ligne (favori, joué, supprimer, détail)

**Composant proposé** : `DataTable<T>` générique

```typescript
interface DataTableProps<T> {
  data: T[];
  columns: Column<T>[];
  sortable?: boolean;
  filterable?: boolean;
  paginated?: boolean;
  pageSize?: number;
  selectable?: boolean;
  actions?: RowAction<T>[];
}
```

**Cartes enrichies** :
- `StatCard` : valeur + tendance (↑↓) + sparkline mini
- `GridCard` : numéros visuels + score + actions
- `PortfolioCard` : résumé portefeuille + métriques clés

**Phase** : B

---

### UX-04 : Navigation améliorée

**Améliorations** :
- **Breadcrumbs** : `Dashboard > Grilles > Détail Grille #42`
- **Sidebar redesign** : groupement par catégorie (Analyse / Génération / Outils / Admin)
- **Quick actions** : raccourcis dans le header (générer grilles, voir top 10)
- **Game switcher** : sélecteur de loterie toujours visible dans le header

**Organisation sidebar proposée** :

```
📊 ANALYSE
  ├─ Dashboard
  ├─ Tirages
  └─ Statistiques

🎯 GÉNÉRATION
  ├─ Grilles
  ├─ Portefeuille
  ├─ Système réduit (NEW)
  └─ Budget intelligent (NEW)

📈 ÉVALUATION
  ├─ Simulation
  ├─ Comparateur (NEW)
  └─ Favoris

📚 OUTILS
  ├─ Historique
  ├─ Comment ça marche
  └─ Glossaire

⚙️ ADMIN (si admin)
  └─ Administration
```

**Phase** : B

---

### UX-05 : Feedback progressif (calculs longs)

**Description** : Remplacer les spinners simples par un feedback progressif pour les opérations longues.

**Composant** : `ProgressFeedback`

```
┌──────────────────────────────────┐
│  🔄 Génération en cours...       │
│                                  │
│  ████████████░░░░░  68%          │
│                                  │
│  Étape : Optimisation génétique  │
│  Grilles générées : 34 / 50     │
│  Temps écoulé : 3.2s             │
└──────────────────────────────────┘
```

**Implémentation** :
- Backend : ajouter header `X-Progress` ou SSE (Server-Sent Events) pour les endpoints longs
- Frontend : `ProgressFeedback` qui poll ou écoute SSE
- Alternative simple : estimation temps basée sur complexité + timer frontend

**Phase** : C

---

### UX-06 : Responsive mobile

**Améliorations** :
- Sidebar : collapse en hamburger menu
- Tableaux : mode carte sur mobile (stack vertical)
- Graphes : scroll horizontal + zoom tactile
- NumberGrid (wheeling) : billes de taille adaptée
- Formulaires : inputs pleine largeur

**Breakpoints** :
- `sm` (640px) : 1 colonne
- `md` (768px) : sidebar collapse
- `lg` (1024px) : layout complet

**Phase** : C

---

### UX-07 : Thème clair

**Description** : Le mode sombre est le défaut (et bien implémenté). Ajouter un mode clair pour les utilisateurs qui le préfèrent.

**Implémentation** :
- `settingsStore.ts` a déjà `theme: 'dark' | 'light'` et `toggleTheme()`
- S'assurer que TOUS les composants utilisent des classes Tailwind conditionnelles
- Vérifier contraste, lisibilité des graphes Recharts en mode clair
- Tester les DrawBalls, NumberHeatmap, ScoreBar en mode clair

**Phase** : D (polish)

---

### UX-08 : Onboarding enrichi

**Description** : Le composant `OnboardingTour` existe mais doit être enrichi pour les nouvelles features.

**Tour proposé** :
1. Welcome — Présentation générale
2. Game selector — Choisir sa loterie
3. Dashboard — Lire les statistiques clés
4. Grilles — Générer ses premières grilles
5. Wheeling — Construire un système réduit (post Phase C)
6. Budget — Optimiser son budget (post Phase C)

**Phase** : C

---

## 4. Synthèse par phase

| Phase | Évolutions UX |
|-------|---------------|
| A | UX-02 (design tokens) |
| B | UX-01 (mode simplifié/expert), UX-03 (composants), UX-04 (navigation) |
| C | UX-05 (feedback progressif), UX-06 (responsive), UX-08 (onboarding) |
| D | UX-07 (thème clair) |

---

## 5. Impacts

| UX | Frontend | Backend | API | Perf |
|----|----------|---------|-----|------|
| 01 (modes) | ●●● | ○ | ○ | ○ |
| 02 (tokens) | ●● | ○ | ○ | ○ |
| 03 (composants) | ●●● | ○ | ○ | ○ |
| 04 (navigation) | ●●● | ○ | ○ | ○ |
| 05 (feedback) | ●● | ●● | ●● | ● |
| 06 (responsive) | ●●● | ○ | ○ | ○ |
| 07 (thème clair) | ●● | ○ | ○ | ○ |
| 08 (onboarding) | ●● | ○ | ○ | ○ |

---

## 6. Risques

| Risque | Probabilité | Impact | Mitigation |
|--------|-------------|--------|------------|
| Mode simplifié trop simpliste | Moyenne | Moyen | Tests utilisateur, itérations |
| Incohérence visuelle mode clair | Haute | Moyen | Audit systématique de chaque composant |
| SSE complexe pour feedback progressif | Moyenne | Mineur | Fallback timer estimation côté front |
| Responsive casse layout existant | Moyenne | Moyen | Tests visuels sur breakpoints |

---

## 7. Critères d'acceptation

| Critère | Mesure |
|---------|--------|
| Mode simplifié/expert toggle fonctionne | Chaque page rend différemment selon le mode |
| Tokens de couleur utilisés partout | Audit CSS — pas de couleurs codées en dur |
| DataTable tri + filtre + pagination | Démo avec 100 lignes |
| Sidebar restructurée | Navigation testable |
| Mobile responsive | Test sur 375px, 768px, 1024px |

---

## 8. Checklist locale

- [ ] UX-01 : Ajouter displayMode dans settingsStore
- [ ] UX-01 : Créer hook useDisplayMode
- [ ] UX-01 : Adapter GridsPage pour mode simplifié
- [ ] UX-01 : Adapter SimulationPage pour mode simplifié
- [ ] UX-01 : Adapter StatisticsPage pour mode simplifié
- [ ] UX-02 : Créer design-tokens.css avec variables CSS
- [ ] UX-02 : Migrer couleurs codées en dur vers tokens
- [ ] UX-03 : Créer composant DataTable générique
- [ ] UX-03 : Créer composant StatCard avec sparkline
- [ ] UX-03 : Créer composant GridCard visuel
- [ ] UX-04 : Restructurer Sidebar par catégories
- [ ] UX-04 : Ajouter breadcrumbs
- [ ] UX-04 : Ajouter game switcher dans header
- [ ] UX-05 : Créer composant ProgressFeedback
- [ ] UX-05 : Implémenter estimation temps côté front
- [ ] UX-06 : Tester et corriger responsive sur 3 breakpoints
- [ ] UX-07 : Audit mode clair sur tous les composants
- [ ] UX-08 : Enrichir OnboardingTour avec étapes wheeling/budget

Réf. : [27_Checklist_Globale_Evolutions](./27_Checklist_Globale_Evolutions.md)
