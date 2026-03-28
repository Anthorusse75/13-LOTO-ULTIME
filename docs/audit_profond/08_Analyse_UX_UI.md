# 8. Analyse Détaillée UX / UI

Cette section évalue l'interface non pas comme du code, mais comme une **expérience produit**. La question n'est pas « est-ce que ça compile ? » mais « est-ce que l'utilisateur comprend, est guidé, et perçoit de la valeur ? ».

---

## 8.1 Première impression

### Ce que voit un nouvel utilisateur

Un utilisateur qui se connecte pour la première fois arrive sur le **DashboardPage**. Il voit :

1. Un header avec le nom de l'application, un sélecteur de jeu et un toggle thème
2. Une sidebar avec 7 entrées de navigation
3. Une section KPI (4 cartes avec chiffres) 
4. Un graphique de fréquences
5. Une liste des derniers tirages

**La première impression est correcte** : l'application ressemble à un dashboard analytique. Le design dark mode est sobre et professionnel. Les couleurs accent (bleu) guident le regard.

**Mais l'impression se dégrade rapidement** quand l'utilisateur commence à explorer :
- Il clique sur « Statistiques » → 7 onglets de données brutes sans explication
- Il clique sur « Grilles » → des options qu'il ne comprend pas (profil, méthode)
- Il clique sur « Portefeuille » → des métriques cryptiques (Hamming, diversity)
- Il clique sur « Simulation » → doit saisir des numéros sans guidance

**Diagnostic** : L'interface est visuellement correcte mais **silencieuse**. Elle affiche des données mais n'aide pas l'utilisateur à les comprendre ni à les utiliser.

---

## 8.2 Analyse par critère UX

### Lisibilité — 3/5

**Ce qui est bon** :
- Typographie cohérente (système de tailles text-xs/sm/base/lg)
- Contraste correct en dark mode (texte clair sur fond sombre)
- Icônes Lucide bien choisies et lisibles

**Ce qui pose problème** :
- Les nombres statistiques sont affichés avec trop de décimales (« 0.51234567 ») sans mise en forme
- Les tableaux de données ont des en-têtes en `text-xs text-text-secondary` qui deviennent difficilement lisibles sur petit écran
- Les graphiques Recharts ont des labels d'axe trop petits et parfois tronqués
- Le mode clair est **cassé** : les couleurs hardcodées dansles graphiques (Recharts, D3) sont calibrées pour le dark mode uniquement

### Hiérarchie visuelle — 2.5/5

La hiérarchie visuelle est le mécanisme par lequel l'œil est guidé vers les informations les plus importantes. C'est ce qui distingue un tableur d'un dashboard.

**Problèmes actuels** :
- Sur le DashboardPage, les 4 KPI cards ont toutes le même poids visuel. Rien n'indique lesquelles sont les plus importantes.
- Sur les pages de statistiques, tous les onglets ont le même traitement visuel. L'onglet « Fréquences » (le plus basique) et l'onglet « Bayésien » (le plus avancé) ont exactement la même apparence.
- Les scores des grilles (ScoreBar) utilisent un code couleur (rouge/ambre/vert) mais sans légende ni seuils explicites. Que signifie « vert » ? Un score > 7/10 ? > 8/10 ?
- Les alertes (numéros en retard, patterns détectés) ne sont pas mises en évidence visuellement par rapport aux données normales.

**Ce qu'il faudrait** :
- Des badges d'importance (« 🔥 En retard », « ✨ Fréquent »)
- Une section « Points clés » en haut de chaque page
- Des tailles de texte différenciées pour les données principales vs secondaires

### Compréhension immédiate — 1.5/5

C'est la faiblesse la plus critique de l'interface. L'application utilise une terminologie technique sans jamais l'expliquer :

| Terme affiché                | Compréhensible sans expertise ? | Explication absente                                             |
| ---------------------------- | ------------------------------- | --------------------------------------------------------------- |
| Affinité                     | Non                             | Mesure statistique de la force d'association entre deux numéros |
| Momentum                     | Peut-être                       | Tendance hausse/baisse de la fréquence d'un numéro              |
| Entropie de Shannon          | Non                             | Mesure de la diversité/équilibre d'une distribution             |
| Uniformité                   | Vaguement                       | Score indiquant si les numéros sont répartis équitablement      |
| Centralité (degree)          | Non                             | Nombre de connexions d'un numéro dans le graphe                 |
| Betweenness                  | Non                             | Mesure d'intermédiation dans le réseau                          |
| Distance de Hamming          | Non                             | Nombre moyen de numéros différents entre deux grilles           |
| Intervalles crédibles (α, β) | Non                             | Paramètres du modèle bayésien Beta-Binomial                     |
| Z-score                      | Non                             | Écart standardisé par rapport à la moyenne                      |
| Monte Carlo                  | Vaguement                       | Méthode de simulation par tirages aléatoires                    |
| Bootstrap                    | Non                             | Technique de rééchantillonnage pour estimer l'incertitude       |

**Conséquence** : Un utilisateur non statisticien — c'est-à-dire la grande majorité des joueurs de loto — est **exclu** de 80% de la valeur du produit. Il peut voir des chiffres mais pas les interpréter.

**Solution** : Chaque métrique doit être accompagnée d'un tooltip (au survol sur desktop, au tap sur mobile) qui explique :
1. Ce que la métrique mesure
2. Comment l'interpréter (haut = bon ? bas = bon ?)
3. Un exemple concret

### Qualité perçue — 2.5/5

La qualité perçue est l'impression subjective de « polish » et de professionnalisme. C'est ce qui fait qu'un utilisateur fait confiance au produit.

**Ce qui contribue positivement** :
- Le design dark mode est sobre et cohérent
- Les composants DrawBalls sont visuellement plaisants
- Les transitions de page sont fluides
- Le disclaimer est bien visible

**Ce qui nuit** :
- Les cartes « À venir — Phase 9 » dans l'admin donnent une impression de chantier
- L'absence de toasts de succès donne l'impression que les actions n'ont pas fonctionné
- Le mode clair cassé (couleurs incorrectes) est immédiatement visible
- Les graphiques D3 ne sont pas interactifs (pas de zoom, pas de tooltip au survol des nœuds)
- Pas d'animation ou de transition lors de l'affichage des résultats (les données apparaissent « plouf »)

### Cohérence des composants — 3/5

Les composants suivent globalement le même design system (bordures arrondies, couleurs de fond surface, couleurs d'accent). Cependant :

- Les **tabs** (onglets) n'ont pas de pattern uniforme :
  - StatisticsPage : boutons avec fond transparent et border-bottom actif
  - AdminPage : boutons avec fond surface et couleur d'accent
  - SimulationPage : encore un autre style de tabs
- Les **tables** ont des styles légèrement différents selon la page
- Les **boutons d'action** (générer, simuler, lancer) n'ont pas de style unifié

**Recommandation** : Créer un composant `<Tabs>` réutilisable et un composant `<DataTable>` avec tri/pagination intégrés.

---

## 8.3 Feedback utilisateur — Analyse détaillée

Le feedback est le mécanisme par lequel le système confirme à l'utilisateur que son action a été prise en compte. C'est un pilier fondamental de l'UX.

### État actuel

| Action                     | Feedback existant               | Feedback attendu                                     |
| -------------------------- | ------------------------------- | ---------------------------------------------------- |
| Login réussi               | Redirection vers dashboard      | ✅ + toast « Bienvenue »                              |
| Login échoué               | Message d'erreur rouge          | ✅ Correct                                            |
| Génération de grilles      | Spinner pendant le chargement   | ⚠️ + toast « X grilles générées » + temps d'exécution |
| Génération de portefeuille | Spinner                         | ⚠️ + toast de confirmation                            |
| Lancement simulation       | Spinner                         | ⚠️ + toast + barre de progression                     |
| Création utilisateur       | Formulaire se ferme             | ❌ Aucun feedback de succès                           |
| Déclenchement job          | Toast « Job lancé avec succès » | ✅ Correct                                            |
| Changement de jeu          | Dropdown change                 | ❌ Aucune confirmation                                |
| Changement de thème        | Thème change visuellement       | ✅ Suffisant                                          |
| Erreur API                 | Toast d'erreur automatique      | ✅ Correct                                            |
| Logout                     | Redirection vers login          | ⚠️ Pas de confirmation                                |

**7 actions sur 11** n'ont pas de feedback de succès. C'est un déficit majeur.

### Solution : Enrichir les mutations TanStack Query

```typescript
// Exemple pour la génération de grilles
const mutation = useMutation({
  mutationFn: (params) => gridService.generate(gameId, params),
  onSuccess: (data) => {
    toast.success(`${data.grids.length} grilles générées en ${data.elapsed}ms`);
    queryClient.invalidateQueries(["grids", gameId]);
  },
  onError: (error) => {
    toast.error(`Échec de la génération : ${error.message}`);
  },
});
```

**Classement** : 🔧 Correction importante (feedback est attendu par tout utilisateur)

---

## 8.4 Accessibilité — Audit WCAG 2.1

### Problèmes critiques (empêchent l'utilisation par des personnes en situation de handicap)

1. **Pas de skip-to-main** : Un utilisateur au clavier doit traverser le header et toute la sidebar avant d'atteindre le contenu principal.

2. **Aucun `role="tablist"` / `role="tab"` / `role="tabpanel"`** sur les onglets (Statistics, Admin, Simulation). Les lecteurs d'écran ne reconnaissent pas ces éléments comme des onglets.

3. **ScoreBar sans ARIA** : La barre de score n'a ni `role="progressbar"`, ni `aria-valuenow`, ni `aria-valuemin/max`. Un lecteur d'écran lit juste un `<div>` vide.

4. **LoadingSpinner sans sémantique** : Pas de `role="status"`, `aria-busy="true"`. Un lecteur d'écran ne sait pas que la page charge.

5. **Focus non visible** : Tailwind supprime les outlines par défaut. Aucun `focus-visible:ring-*` n'est ajouté sur les éléments interactifs. Un utilisateur au clavier ne voit pas où il est.

### Problèmes modérés

6. **Labels implicites** : Les champs de formulaire utilisent des `<label>` mais pas de `<fieldset>/<legend>` pour regrouper les champs reliés.

7. **Contraste douteux** : Le `text-text-secondary` (#a1a1aa en dark, #71717a en light) pourrait ne pas respecter le ratio 4.5:1 minimum WCAG AA sur tous les fonds.

8. **Erreurs de formulaire non associées** : Les messages d'erreur de validation ne sont pas liés à leurs inputs via `aria-describedby`.

**Classement** : 📈 Amélioration nécessaire pour un produit professionnel. Certains points (skip-to-main, focus visible) sont rapides à corriger.

---

## 8.5 Dark mode / Light mode

### Architecture technique

Le système de thème repose sur des variables CSS :

```css
:root {
  --color-background: #0a0a0b;
  --color-surface: #141416;
  --color-text-primary: #fafafa;
  /* ... 13 variables */
}

.light {
  --color-background: #f8f8fa;
  --color-surface: #ffffff;
  --color-text-primary: #09090b;
}
```

Le toggle dans le header bascule la classe CSS sur `<html>`. Zustand persiste le choix.

**Le problème** : Les graphiques Recharts et D3 **n'utilisent pas ces variables CSS**. Ils ont des couleurs hardcodées :

```tsx
// Dans DashboardPage, FrequencyTab, GapTab, BayesianTab, SimulationPage...
<Tooltip contentStyle={{
  background: "#141416",      // ← Couleur dark mode en dur
  border: "1px solid #27272a" // ← Bordure dark mode en dur
}} />
<XAxis tick={{ fill: "#a1a1aa" }} />  // ← Couleur texte dark mode en dur
```

```tsx
// Dans GraphTab (D3)
.attr("fill", "#fafafa")    // ← Labels blancs en dur (invisible en mode clair)
.attr("stroke", "#0a0a0b")  // ← Traits noirs en dur (invisible en mode dark)
```

**Conséquence** : En mode clair, les graphiques ont du texte gris clair sur fond blanc (illisible) et les tooltips ont un fond noir sur une page blanche (incohérent).

**Solution** : Utiliser `getComputedStyle(document.documentElement).getPropertyValue('--color-*')` pour lire les variables CSS, ou définir un objet `themeColors` dans le settingsStore qui est mis à jour au changement de thème.

**Classement** : 🔧 Correction (le mode clair est factuellement cassé)

---

## 8.6 Responsive design

### Sur desktop (>1024px) — 4/5
L'application est conçue pour le desktop. La grille 4 colonnes, la sidebar fixe et les graphiques pleine largeur fonctionnent bien.

### Sur tablette (768-1024px) — 3/5
La sidebar se collapse, les grilles passent à 2 colonnes. Acceptable mais :
- Le graphe D3 n'est pas interactif au toucher
- Les tableaux avec beaucoup de colonnes nécessitent un scroll horizontal

### Sur mobile (<768px) — 2/5
- Les KPI cards du dashboard se stackent mais restent trop larges pour des valeurs longues
- Les graphiques Recharts ne s'adaptent pas bien (labels qui se chevauchent)
- Les tabs de simulation sont trop serrés sur une ligne
- Le NumberHeatmap (49 boutons) wrap de manière chaotique
- La sidebar n'a pas de mode hamburger menu sur mobile

**Classement** : 📈 Amélioration (le produit cible le desktop d'abord, mais le mobile ne devrait pas être cassé)

---

## 8.7 Proposition pour une interface « premium »

Pour passer d'une interface « dashboard de développeur » à un « logiciel analytique premium », voici les axes de transformation :

### Pédagogie intégrée

Chaque écran devrait comporter :
- **Un titre avec sous-titre explicatif** : « Statistiques de fréquences » → « Statistiques de fréquences — Découvrez quels numéros apparaissent le plus souvent »
- **Des tooltips sur chaque métrique** : icône ℹ️ à côté de chaque label technique
- **Un encart « Comment lire cette page ? »** (toggle collapse)
- **Des conclusions automatiques** : « 3 numéros sont exceptionnellement en retard : 7, 23, 41 »

### Visualisation enrichie

- **Heatmap temporelle** : matrice numéros × mois avec intensité = fréquence
- **Graphe interactif** : zoom, pan, clic sur un nœud pour voir les statistiques du numéro
- **Radar chart** par grille : visualisation multi-critères (fréquence, écart, diversité, structure, bayésien)
- **Comparaison côte-à-côte** : mettre deux grilles ou deux portefeuilles en vis-à-vis
- **Timeline** : évolution des scores d'une grille au fil du temps

### Navigation contextuelle

- **Breadcrumbs** ou **fil d'Ariane** sur chaque page
- **Liens croisés** : depuis un numéro dans un graphique, accéder directement à ses statistiques détaillées
- **Workflow guidé** : « Étape 1 : Consultez les statistiques → Étape 2 : Générez une grille → Étape 3 : Simulez → Étape 4 : Ajoutez au portefeuille »

### Feedback enrichi

- **Barre de progression** pour les calculs longs (au lieu d'un simple spinner)
- **Notifications** pour les événements système (« Nouveau tirage importé : Loto du 25/03 »)
- **Historique des actions** : « Vous avez généré 5 grilles il y a 2h — Score moyen : 7.1 »

---

## 8.8 Synthèse UX/UI

| Critère                  | Score actuel | Cible produit | Effort                                |
| ------------------------ | ------------ | ------------- | ------------------------------------- |
| Lisibilité               | 3/5          | 4.5/5         | Moyen                                 |
| Hiérarchie visuelle      | 2.5/5        | 4/5           | Élevé                                 |
| Compréhension immédiate  | 1.5/5        | 4/5           | **Élevé**                             |
| Qualité perçue           | 2.5/5        | 4.5/5         | Élevé                                 |
| Cohérence des composants | 3/5          | 4.5/5         | Moyen                                 |
| Feedback utilisateur     | 1.5/5        | 4/5           | **Faible** (toasts rapides à ajouter) |
| Accessibilité            | 1.5/5        | 3.5/5         | Moyen                                 |
| Dark/Light mode          | 2/5          | 4.5/5         | Faible (corriger hardcoded colors)    |
| Responsive               | 2.5/5        | 3.5/5         | Moyen                                 |

**Le levier le plus impactant pour le moindre effort** : ajouter des tooltips et des toasts de feedback. Ce sont des changements unitaires qui transforment radicalement la perception de « ça marche ? » en « ça marche et je comprends pourquoi ».
