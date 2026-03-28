# 13 — Architecture UI/UX

> **Projet** : LOTO ULTIME  
> **Version** : 1.0  
> **Date** : 2026-03-27  
> **Références croisées** : [04_Frontend](04_Architecture_Frontend.md) · [06_API_Design](06_API_Design.md) · [08_Scoring](08_Moteur_Scoring.md) · [12_Securite](12_Securite_et_Authentification.md)

---

## 1. Principes de Design

### 1.1 Lignes directrices

| Principe | Description |
|---|---|
| **Dark by default** | Thème sombre comme mode principal, toggle clair disponible |
| **Data-first** | L'information statistique est au centre de chaque vue |
| **Progressive disclosure** | Info simplifiée d'abord, détails à la demande |
| **Responsive** | Desktop-first, adaptatif tablette et mobile |
| **Accessible** | WCAG 2.1 AA minimum |
| **Performance** | Rendu perçu < 200ms, pas de skeleton inutile |

### 1.2 Système de Couleurs

```
/* Palette Dark Mode */
--background:      #0a0a0b      /* Fond principal */
--surface:         #141416      /* Cartes, panneaux */
--surface-hover:   #1c1c1f      /* Survol */
--border:          #27272a      /* Bordures subtiles */
--text-primary:    #fafafa      /* Texte principal */
--text-secondary:  #a1a1aa      /* Texte secondaire */
--accent-blue:     #3b82f6      /* Actions principales */
--accent-green:    #22c55e      /* Succès, valeurs hautes */
--accent-amber:    #f59e0b      /* Attention, valeurs moyennes */
--accent-red:      #ef4444      /* Erreur, valeurs basses */
--accent-purple:   #a855f7      /* Éléments spéciaux */
```

### 1.3 Typographie

| Usage | Police | Taille | Poids |
|---|---|---|---|
| Titres H1 | Inter | 28px | 700 |
| Titres H2 | Inter | 22px | 600 |
| Corps | Inter | 14px | 400 |
| Données numériques | JetBrains Mono | 14px | 500 |
| Labels | Inter | 12px | 500 |

---

## 2. Layout Principal

### 2.1 Structure

```
┌─────────────────────────────────────────────────────────────┐
│  Top Bar    [Logo LOTO ULTIME]    [Game Selector ▼] [User] │
├──────────┬──────────────────────────────────────────────────┤
│          │                                                  │
│  Sidebar │               Main Content Area                  │
│          │                                                  │
│  📊 Dash │  ┌──────────┐ ┌──────────┐ ┌──────────┐        │
│  🎱 Tir. │  │  Card 1  │ │  Card 2  │ │  Card 3  │        │
│  📈 Stat │  └──────────┘ └──────────┘ └──────────┘        │
│  🎯 Gril │                                                  │
│  💼 Port │  ┌────────────────────────────────────────┐      │
│  🎰 Simu │  │         Main Chart / Table             │      │
│  ⚙  Adm  │  │                                        │      │
│          │  └────────────────────────────────────────┘      │
│          │                                                  │
├──────────┴──────────────────────────────────────────────────┤
│  Status Bar                                    v1.0 | API ● │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Sidebar

- **Largeur** : 240px (expanded) / 64px (collapsed)
- **Toggle** : Bouton hamburger en haut
- **Icônes** : Lucide icons (cohérence Shadcn)
- **Indicateur actif** : Trait accent-blue à gauche
- **Responsive** : Drawer overlay sur mobile (< 768px)

### 2.3 Top Bar

- Logo et nom à gauche
- **Game Selector** : Dropdown pour choisir le jeu actif (Loto FDJ, EuroMillions)
- Badge de notification (nombre de nouveaux tirages)
- Menu utilisateur (profil, thème, logout)

---

## 3. Pages & Wireframes

### 3.1 Dashboard (Page d'accueil)

```
┌────────────────────────────────────────────────────────────┐
│  Dashboard — Loto FDJ                                      │
├────────────┬────────────┬────────────┬────────────────────│
│  Dernier   │  Prochain  │  Grilles   │  Score moyen       │
│  tirage    │  tirage    │  actives   │  portefeuille      │
│  5-12-23-  │  dans 2j   │    15      │    7.84/10         │
│  34-45 ★3  │  08h       │            │                    │
├────────────┴────────────┴────────────┴────────────────────│
│                                                            │
│  ┌─ Fréquences (Top 10) ─────────────────────────────┐   │
│  │  ████████████  12  (freq: 0.24)                    │   │
│  │  ██████████    23  (freq: 0.21)                    │   │
│  │  █████████     05  (freq: 0.20)                    │   │
│  │  ████████      34  (freq: 0.19)                    │   │
│  │  ...                                               │   │
│  └────────────────────────────────────────────────────┘   │
│                                                            │
│  ┌─ Tendances ──────────┐ ┌─ Écarts Critiques ─────────┐ │
│  │  ↗ En hausse: 5,12   │ │  ⚠ Num 47 : écart 28      │ │
│  │  ↘ En baisse: 38,2   │ │  ⚠ Num 03 : écart 25      │ │
│  │  → Stables: 23,34    │ │  Moy théorique: 9.8       │ │
│  └──────────────────────┘ └────────────────────────────┘  │
│                                                            │
│  ┌─ Derniers tirages ────────────────────────────────┐    │
│  │  #2025-036  05 12 23 34 45  ★3   2025-03-24      │    │
│  │  #2025-035  02 15 28 33 41  ★7   2025-03-22      │    │
│  │  #2025-034  07 11 19 36 49  ★1   2025-03-19      │    │
│  └───────────────────────────────────────────────────┘    │
└────────────────────────────────────────────────────────────┘
```

### 3.2 Tirages

```
┌────────────────────────────────────────────────────────────┐
│  Historique des Tirages — Loto FDJ                         │
├────────────────────────────────────────────────────────────┤
│  [Filtres: Date début ▼] [Date fin ▼] [🔍 Rechercher]     │
├─────┬──────────────┬───────────────┬──────┬───────────────┤
│ #   │ Date         │ Numéros       │ Comp │ Jackpot       │
├─────┼──────────────┼───────────────┼──────┼───────────────┤
│ 036 │ 2025-03-24   │ ⑤ ⑫ ㉓ ㉞ ㊺ │  ★3  │ 4 000 000 €  │
│ 035 │ 2025-03-22   │ ② ⑮ ㉘ ㉝ ㊶ │  ★7  │ 2 000 000 €  │
│ 034 │ 2025-03-19   │ ⑦ ⑪ ⑲ ㊱ ㊾ │  ★1  │ 13 000 000 € │
│ ... │              │               │      │               │
├─────┴──────────────┴───────────────┴──────┴───────────────┤
│  ◀ 1 2 3 ... 45 ▶                         50 par page ▼  │
└────────────────────────────────────────────────────────────┘
```

### 3.3 Statistiques

Divisée en onglets :

```
┌────────────────────────────────────────────────────────────┐
│  Statistiques — Loto FDJ                                   │
│  [Fréquences] [Écarts] [Cooccurrences] [Tendances]        │
│  [Distribution] [Bayésien] [Graphe]                        │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  Onglet "Fréquences" :                                     │
│  ┌────────────────────────────────────────────────────┐   │
│  │   Heatmap numéros 1-49                             │   │
│  │   ┌──┬──┬──┬──┬──┬──┬──┬──┬──┬──┐                │   │
│  │   │01│02│03│04│05│06│07│08│09│10│ ...              │   │
│  │   │▓▓│░░│▒▒│░░│▓▓│▒▒│▓▓│░░│▒▒│░░│                │   │
│  │   └──┴──┴──┴──┴──┴──┴──┴──┴──┴──┘                │   │
│  │   Couleur = fréquence relative (rouge→vert)       │   │
│  └────────────────────────────────────────────────────┘   │
│                                                            │
│  ┌─ Top fréquences ──────┐ ┌─ Bottom fréquences ───────┐ │
│  │ 12: 0.245 (▲ +0.02)   │ │ 47: 0.098 (▼ -0.01)      │ │
│  │ 05: 0.231 (→ +0.00)   │ │ 39: 0.102 (→ +0.00)      │ │
│  └────────────────────────┘ └───────────────────────────┘ │
│                                                            │
│  Onglet "Cooccurrences" :                                  │
│  ┌────────────────────────────────────────────────────┐   │
│  │   Matrice triangulaire interactive                 │   │
│  │   Survol = détail paire (fréquence, affinité)     │   │
│  │   Clic = filtre les triplets contenant la paire   │   │
│  └────────────────────────────────────────────────────┘   │
│                                                            │
│  Onglet "Graphe" :                                         │
│  ┌────────────────────────────────────────────────────┐   │
│  │   Graphe NetworkX rendu D3.js                      │   │
│  │   Nœuds = numéros (taille = centralité)           │   │
│  │   Arêtes = affinités (épaisseur = force)          │   │
│  │   Couleurs = communautés (Louvain)                 │   │
│  │   Zoom, pan, drag interactifs                      │   │
│  └────────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────────┘
```

### 3.4 Génération de Grilles

```
┌────────────────────────────────────────────────────────────┐
│  Génération de Grilles — Loto FDJ                          │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  Paramètres                                                │
│  ┌─ Nombre de grilles ─┐  ┌─ Méthode d'optimisation ───┐ │
│  │  [10     ] ▲▼       │  │  [Recuit simulé         ▼] │ │
│  └─────────────────────┘  └────────────────────────────┘  │
│                                                            │
│  ┌─ Profil de scoring ────────────────────────────────┐   │
│  │  ○ Équilibré  ○ Tendance  ○ Contrarian  ○ Custom  │   │
│  └────────────────────────────────────────────────────┘   │
│                                                            │
│  ┌─ Poids personnalisés (mode Custom) ───────────────┐   │
│  │  Fréquence    [====|========] 0.20                 │   │
│  │  Écart        [======|======] 0.20                 │   │
│  │  Cooccurrence [========|====] 0.20                 │   │
│  │  Structure    [====|========] 0.15                 │   │
│  │  Équilibre    [====|========] 0.15                 │   │
│  │  Pénalité     [==|==========] 0.10                 │   │
│  └────────────────────────────────────────────────────┘   │
│                                                            │
│  [Contraintes avancées ▼]                                  │
│    Exclure numéros: [                ]                     │
│    Forcer numéros:  [                ]                     │
│                                                            │
│  [ 🎲 Générer ]                                            │
│                                                            │
│  ┌─ Résultats ───────────────────────────────────────┐    │
│  │ # │ Numéros         │ ★ │ Score │ Détail         │    │
│  │ 1 │ 05 12 23 34 45  │ 3 │ 8.72  │ [Voir ▶]      │    │
│  │ 2 │ 07 11 28 33 49  │ 7 │ 8.45  │ [Voir ▶]      │    │
│  │ 3 │ 02 15 19 36 41  │ 1 │ 8.21  │ [Voir ▶]      │    │
│  │ ...                                               │    │
│  └───────────────────────────────────────────────────┘    │
└────────────────────────────────────────────────────────────┘
```

### 3.5 Détail d'une Grille

```
┌────────────────────────────────────────────────────────────┐
│  Grille #1 — Score: 8.72/10                                │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  Numéros :  ⓹  ⑫  ㉓  ㉞  ㊺   Complémentaire : ★③      │
│                                                            │
│  ┌─ Décomposition du Score ──────────────────────────┐    │
│  │                                                    │    │
│  │  Fréquence     ████████████████░░░░  8.2  (x0.20) │    │
│  │  Écart         ██████████████████░░  9.1  (x0.20) │    │
│  │  Cooccurrence  ███████████████░░░░░  7.8  (x0.20) │    │
│  │  Structure     █████████████████░░░  8.9  (x0.15) │    │
│  │  Équilibre     ██████████████████░░  9.0  (x0.15) │    │
│  │  Pénalité      ░░░░░░░░░░░░░░░░░░░  0.0  (x0.10) │    │
│  │                                                    │    │
│  │  Score pondéré final : 8.72                        │    │
│  └────────────────────────────────────────────────────┘    │
│                                                            │
│  ┌─ Propriétés ─────────────┐ ┌─ Simulation ──────────┐  │
│  │  Somme    : 119           │ │  Prob(≥2 bons): 12.3% │  │
│  │  Pair/Imp : 2/3           │ │  Prob(≥3 bons): 2.1%  │  │
│  │  Bas/Haut : 2/3           │ │  Espérance    : 1.02   │  │
│  │  Span     : 40            │ └────────────────────────┘  │
│  │  Décades  : 1,2,3,4       │                             │
│  └───────────────────────────┘                             │
└────────────────────────────────────────────────────────────┘
```

### 3.6 Portefeuille

```
┌────────────────────────────────────────────────────────────┐
│  Portefeuille — Loto FDJ                                   │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  Paramètres                                                │
│  Taille: [7  ▲▼]  Stratégie: [Couverture max ▼]           │
│  [ 🎯 Générer portefeuille ]                               │
│                                                            │
│  ┌─ Portefeuille actuel ──────────────────────────────┐   │
│  │ Score moyen : 8.12  │ Diversité : 0.87             │   │
│  │ Couverture  : 82%   │ Corrélation moy : 0.23       │   │
│  ├─────────────────────────────────────────────────────┤   │
│  │ # │ Numéros         │ ★ │ Score │                  │   │
│  │ 1 │ 05 12 23 34 45  │ 3 │ 8.72  │ ████████▓░      │   │
│  │ 2 │ 07 11 28 33 49  │ 7 │ 8.45  │ ████████▒░      │   │
│  │ 3 │ 02 15 19 36 41  │ 1 │ 8.21  │ ████████░░      │   │
│  │ ...                                                │   │
│  └────────────────────────────────────────────────────┘   │
│                                                            │
│  ┌─ Couverture numérique ─────────────────────────────┐   │
│  │  Heatmap 1-49 : numéros couverts en vert           │   │
│  │  ┌──┬──┬──┬──┬──┬──┬──┬──┬──┬──┐                 │   │
│  │  │▓▓│  │▓▓│  │▓▓│  │▓▓│  │  │  │ ...             │   │
│  │  └──┴──┴──┴──┴──┴──┴──┴──┴──┴──┘                 │   │
│  └────────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────────┘
```

### 3.7 Simulation Monte Carlo

```
┌────────────────────────────────────────────────────────────┐
│  Simulation Monte Carlo — Loto FDJ                         │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  Paramètres                                                │
│  Tirages simulés: [100000 ▲▼]  Seed: [42     ]            │
│  Cible: ○ Grille unique  ○ Portefeuille complet            │
│  [ ▶ Lancer simulation ]                                   │
│                                                            │
│  ┌─ Résultats ───────────────────────────────────────┐    │
│  │  ┌─ Distribution des correspondances ──────────┐  │    │
│  │  │  0 bons:  ██████████████████████  52.3%     │  │    │
│  │  │  1 bon :  ████████████████░░░░░░  33.1%     │  │    │
│  │  │  2 bons:  █████░░░░░░░░░░░░░░░░  11.8%     │  │    │
│  │  │  3 bons:  █░░░░░░░░░░░░░░░░░░░░   2.4%     │  │    │
│  │  │  4 bons:  ░░░░░░░░░░░░░░░░░░░░░   0.33%    │  │    │
│  │  │  5 bons:  ░░░░░░░░░░░░░░░░░░░░░   0.017%   │  │    │
│  │  └─────────────────────────────────────────────┘  │    │
│  │                                                    │    │
│  │  ┌─ Comparaison ─────────────────────────────┐    │    │
│  │  │         Grille optimisée  vs  Aléatoire   │    │    │
│  │  │  ≥2 :      12.3%              11.9%       │    │    │
│  │  │  ≥3 :       2.1%               1.8%       │    │    │
│  │  │  p-value :  0.042                          │    │    │
│  │  └────────────────────────────────────────────┘    │    │
│  └────────────────────────────────────────────────────┘    │
└────────────────────────────────────────────────────────────┘
```

---

## 4. Composants UI Clés

### 4.1 DrawBalls — Affichage des numéros

```tsx
interface DrawBallsProps {
  numbers: number[];
  complementary?: number[];
  size?: "sm" | "md" | "lg";
  highlight?: number[];
}

// Rendu : cercles colorés avec numéros
// - Taille sm=28px, md=36px, lg=48px
// - Fond accent-blue pour numéros principaux
// - Fond accent-purple pour complémentaires
// - Bordure accent-green si highlight
// - Police JetBrains Mono
```

### 4.2 ScoreBar — Barre de score

```tsx
interface ScoreBarProps {
  value: number;       // 0-10
  max?: number;        // default 10
  label: string;
  weight?: number;     // Poids affiché à droite
  colorScheme?: "gradient" | "mono";
}

// Barre horizontale avec dégradé rouge → jaune → vert
// Animation d'entrée de gauche à droite
```

### 4.3 NumberHeatmap — Heatmap numérique

```tsx
interface NumberHeatmapProps {
  data: Map<number, number>;  // numéro → valeur
  range: [number, number];    // min, max numéro
  colorScale: "frequency" | "gap" | "score";
  onNumberClick?: (num: number) => void;
}

// Grille de cellules carrées, couleur proportionnelle à la valeur
// Survol : tooltip avec détails
// Clic : sélection/filtre
```

### 4.4 CooccurrenceMatrix — Matrice de cooccurrences

```tsx
interface CooccurrenceMatrixProps {
  data: { num1: number; num2: number; count: number; affinity: number }[];
  range: [number, number];
}

// Matrice triangulaire (D3.js)
// Cellule survol : bulle avec détails paire
// Zoom brush pour sous-zones
```

### 4.5 NetworkGraph — Graphe de réseau

```tsx
interface NetworkGraphProps {
  nodes: { id: number; centrality: number; community: number }[];
  edges: { source: number; target: number; weight: number }[];
  layout?: "force" | "circular";
}

// D3.js force-directed graph
// Interactif : zoom, pan, drag nodes
// Legende : couleurs par communauté
```

---

## 5. Interactions & Feedback

### 5.1 États de chargement

| État | Composant | Comportement |
|---|---|---|
| Loading initial | Skeleton | Placeholder animé pulsant |
| Calcul long (> 2s) | Progress spinner | Barre de progression si durée estimée |
| Erreur réseau | Toast + retry | Message rouge + bouton réessayer |
| Pas de données | Empty state | Illustration + message explicatif |
| Succès action | Toast | Message vert, auto-dismiss 3s |

### 5.2 Notifications Toast

```tsx
// Position : top-right
// Types : success (vert), error (rouge), warning (ambre), info (bleu)
// Auto-dismiss : 3s (success/info), sticky (error/warning)
// Stack : max 3 toasts simultanés
```

### 5.3 Modales de confirmation

- **Génération** : "Générer X grilles avec le profil Y ?"
- **Simulation** : "Lancer N simulations ? (estimé ~Xs)"
- **Actions admin** : Double confirmation pour les opérations destructrices

---

## 6. Responsive Design

| Breakpoint | Largeur | Adaptation |
|---|---|---|
| Desktop | ≥ 1280px | Layout complet, sidebar expanded |
| Laptop | ≥ 1024px | Sidebar collapsed by default |
| Tablet | ≥ 768px | Sidebar drawer, grilles 2 colonnes |
| Mobile | < 768px | Navigation bottom tab, 1 colonne |

### 6.1 Adaptations mobiles

- Tableau tirages → cartes empilées
- Matrice cooccurrences → non affichée (trop dense)
- Graphe → simplifié (top 20 nœuds)
- Formulaires → plein écran
- Heatmap → scrollable horizontalement

---

## 7. Accessibilité

| Critère | Implémentation |
|---|---|
| Contraste | Ratio ≥ 4.5:1 texte normal, ≥ 3:1 gros texte |
| Clavier | Navigation complète tab/enter/esc |
| Screen reader | aria-labels sur tous les composants interactifs |
| Focus visible | Anneau bleu visible sur tout élément focusé |
| Alternatives | Texte alt pour graphiques, données tabulaires en option |
| Animations | Respect `prefers-reduced-motion` |

---

## 8. Références

| Document | Contenu |
|---|---|
| [04_Architecture_Frontend](04_Architecture_Frontend.md) | Structure technique React |
| [06_API_Design](06_API_Design.md) | Données alimentant l'UI |
| [08_Moteur_Scoring](08_Moteur_Scoring.md) | Détails scores affichés |
| [14_Performance_et_Scalabilite](14_Performance_et_Scalabilite.md) | Temps de rendu cibles |
| [12_Securite_et_Authentification](12_Securite_et_Authentification.md) | Flux auth côté UI |

---

*Fin du document 13_Architecture_UI_UX.md*
