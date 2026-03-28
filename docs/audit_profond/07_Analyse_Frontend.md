# 7. Analyse Détaillée du Frontend

## 7.1 Stack technique

| Technologie | Version | Rôle | Verdict |
|------------|---------|------|---------|
| Vite | 8 | Build tool | ✅ Excellent choix (rapide, HMR, tree-shaking) |
| React | 18 | Framework UI | ✅ Standard |
| TypeScript | Strict | Typage | ✅ Typage complet |
| Tailwind CSS | v4 | Styling | ✅ Productif mais nécessite discipline |
| TanStack Query | v5 | Data fetching | ✅ Excellent (cache, refetch, mutations) |
| Zustand | — | État global | ✅ Léger, adapté au besoin |
| Axios | — | HTTP client | ✅ Intercepteurs bien configurés |
| Recharts | — | Graphiques | ⚠️ Fonctionnel mais couleurs hardcodées |
| D3.js | — | Graphe réseau | ⚠️ Puissant mais pas optimisé mobile |
| Sonner | — | Toasts | ⚠️ Intégré mais sous-utilisé |

**Build** : 817 KB JS + 27 KB CSS, 0 erreur TypeScript. La taille du bundle est raisonnable pour une SPA avec visualisations de données.

---

## 7.2 Structure des pages

### DashboardPage — Page d'accueil

**Ce qu'elle fait** : Vue d'ensemble avec 4 KPI cards (tirages, score moyen, dernier tirage, fréquences) + graphique de fréquences + liste des derniers tirages.

**Points forts** :
- Donne immédiatement une vue de l'état des données
- Les KPI sont visuellement distincts avec des icônes
- Le graphique Recharts est fonctionnel

**Points faibles** :
- Les 4 KPI montrent des données brutes sans contexte (« 1000 tirages » — et alors ? c'est beaucoup, peu ?)
- Le graphique de fréquences est identique à l'onglet Fréquences dans Statistiques — pas de valeur ajoutée spécifique au dashboard
- Pas de « story telling » : le dashboard n'aide pas l'utilisateur à comprendre l'état de ses analyses
- Les données ne changent quasiment jamais (sauf lors d'un nouveau tirage)

**Ce que devrait être un dashboard analytique** :
- Messages d'alerte : « 3 numéros sont en retard exceptionnel depuis plus de 30 tirages »
- Dernière action : « Dernière analyse le 25/03 — Score moyen de vos grilles : 7.2/10 »
- Suggestion : « Un nouveau tirage a été importé hier, les statistiques sont à jour »
- Comparaison : « Vos grilles ont un score supérieur à 85% des grilles aléatoires »

**Classement** : 📈 Amélioration structurante

### DrawsPage — Historique des tirages

**Ce qu'elle fait** : Tableau paginé des tirages avec date, numéros (DrawBalls) et pagination.

**Points forts** :
- Pagination fonctionnelle (Previous/Next)
- Affichage correct des boules avec couleurs
- État vide géré (« Aucun tirage disponible »)

**Points faibles** :
- Pas de recherche/filtrage (par date, par numéro)
- Pas de tri possible sur les colonnes
- Les tirages EuroMillions n'affichent pas les étoiles séparément
- Pas de mise en évidence des numéros remarquables (très fréquents, très en retard)

**Classement** : 📈 Amélioration

### StatisticsPage — Statistiques (7 onglets)

**Ce qu'elle fait** : 7 onglets correspondant aux 7 moteurs statistiques.

**Points forts** :
- Couverture fonctionnelle complète (chaque moteur a son onglet)
- Chaque onglet affiche les données de son moteur sous forme de tableau ou graphique
- Les onglets bayesien et graphe sont protégés par rôle (Utilisateur minimum)

**Points faibles critiques** :
- **Aucun tooltip** sur aucun onglet. L'utilisateur face à « affinité : 0.512 » ou « momentum : 0.034 » n'a aucune idée de ce que cela signifie.
- Le **GraphTab** utilise D3.js mais n'est pas interactif sur mobile (pas de touch events)
- Les **couleurs Recharts sont hardcodées** en dark mode — cassé en mode clair :
  ```tsx
  <XAxis tick={{ fill: "#a1a1aa", fontSize: 12 }} />
  <Tooltip contentStyle={{ background: "#141416", border: "1px solid #27272a" }} />
  ```
- Pas de possibilité de croiser les analyses (ex: quels numéros sont à la fois fréquents ET en retard ?)

**Classement** : 🔧 Correction (couleurs) + 📈 Amélioration (tooltips, interactivité)

### GridsPage — Génération de grilles

**Ce qu'elle fait** : Formulaire de génération (nombre, méthode) + affichage des grilles générées + top grilles.

**Points forts** :
- Inputs pour le nombre de grilles et la méthode
- Affichage avec DrawBalls et ScoreBar pour chaque grille

**Points faibles** :
- 🔴 **Le sélecteur de profil est non branché** : 4 options visuellement cliquables (équilibré, offensif, défensif, aléatoire) mais la valeur `profile` n'est jamais envoyée :
  ```tsx
  const [profile] = useState("equilibre");  // Déclaré mais jamais utilisé dans mutate()
  ```
- Pas de feedback de progression pendant la génération (peut prendre 10+ secondes)
- Pas de toast de confirmation après génération
- Pas d'explication sur la signification du score (que veut dire 7.2/10 ?)

**Classement** : 🔧 Correction (profil non branché) + 📈 Amélioration (feedback)

### PortfolioPage — Portefeuille

**Ce qu'elle fait** : Génération d'un portefeuille avec sélection de stratégie, affichage des métriques (diversity, coverage, Hamming distance) et des grilles du portefeuille.

**Points forts** :
- 4 stratégies disponibles (balanced, max_diversity, max_coverage, min_correlation)
- KPI cards avec metrics pertinentes
- NumberHeatmap pour visualiser la couverture

**Points faibles** :
- Les métriques ne sont pas expliquées :
  - « Diversity score : 0.847 » — sur quelle échelle ? C'est bon ou mauvais ?
  - « Hamming distance : 3.2 » — distance entre quoi et quoi ?
  - « Coverage score : 72% » — couverture de quoi ?
- Pas de comparaison entre stratégies (l'utilisateur doit générer 4 fois pour comparer)
- Le NumberHeatmap a un `onNumberClick` défini mais jamais connecté
- Pas de guide d'utilisation (« quelle stratégie choisir et pourquoi ? »)

**Classement** : 📈 Amélioration importante (pédagogie + comparaison)

### SimulationPage — Simulation Monte Carlo

**Ce qu'elle fait** : 3 onglets (Monte Carlo, Bootstrap stabilité, Comparaison random) avec inputs pour les numéros et les paramètres de simulation.

**Points forts** :
- Interface de saisie pour tester une grille personnalisée
- Validation des inputs (nombre correct de numéros)
- 3 types d'analyse complémentaires

**Points faibles** :
- Terminologie technique non expliquée (« Monte Carlo », « Bootstrap », « Z-score »)
- Pas de visualisation graphique des résultats (uniquement des nombres)
- L'utilisateur doit comprendre les statistiques pour interpréter les résultats
- Pas de conclusion en langage naturel (« Votre grille se comporte mieux que 78% des grilles aléatoires »)
- Les 3 onglets se ressemblent visuellement — pas de hiérarchie d'importance

**Classement** : 📈 Amélioration structurante (vulgarisation des résultats)

### AdminPage — Administration

**Ce qu'elle fait** : 3 onglets (Overview, Jobs, Users) pour l'administration du système.

**Points forts** :
- Vue d'ensemble avec statut des jobs et compteurs de données
- Déclenchement manuel des jobs avec feedback
- Gestion des utilisateurs (liste + création)

**Points faibles** :
- Les cartes « À venir — Phase 9 » dans l'overview sont visuellement présentes mais vides
- Pas de toast de succès après création d'un utilisateur
- Pas de modification/suppression d'utilisateurs
- Le job history montre un statut mais pas les détails du résultat

**Classement** : 📈 Amélioration

### LoginPage

**Points forts** :
- Design propre avec logo
- Accepte email ou username
- Gestion des erreurs (message rouge en cas d'échec)

**Points faibles** :
- Pas de « mot de passe oublié » (normal, pas d'email service)
- Pas de feedback visuel pendant la soumission (pas de loader sur le bouton)

**Classement** : ⬜ Acceptable en l'état

---

## 7.3 Composants réutilisables

### DrawBalls ✅
Composant bien conçu pour afficher les boules d'un tirage. Supporte 3 tailles (sm, md, lg) et la mise en évidence de numéros spécifiques (`highlight`). Manque : différenciation visuelle étoiles vs numéros principaux.

### ScoreBar ⚠️
Barre de score 0-10 avec code couleur (rouge/ambre/vert). Pas d'ARIA attributes (`role="progressbar"`, `aria-valuenow`). Les seuils de couleur sont hardcodés (0.4/0.7) — devraient être documentés.

### NumberHeatmap ⚠️
Grille de numéros avec code couleur d'intensité. Le prop `onNumberClick` est déclaré mais jamais connecté côté parent. Les boutons n'ont pas d'`aria-label`. Pas d'adaptation au pool de numéros du jeu courant.

### LoadingSpinner ⚠️
Simple spinner animé. Manque `role="status"`, `aria-busy="true"`, `aria-label="Chargement…"`.

### ErrorBoundary ✅
Catch les erreurs React avec affichage de secours. Manque `role="alert"`.

### Disclaimer ✅
Message important rappelant que l'outil ne prédit pas les résultats. Bien placé. Pourrait être `role="alert"`.

---

## 7.4 Hooks personnalisés

L'utilisation de TanStack Query via des hooks customisés est un pattern excellent :

```typescript
// useStatistics.ts
export function useStatistics(gameId: number) {
  return useQuery({
    queryKey: ["statistics", gameId],
    queryFn: () => api.get(`/games/${gameId}/statistics`).then(r => r.data),
    enabled: !!gameId,
    staleTime: 5 * 60 * 1000,  // 5 minutes cache
  });
}
```

**Points forts** :
- Chaque endpoint a son hook dédié
- Cache automatique avec `staleTime` approprié
- `enabled` conditionnel empêche les requêtes prématurées
- Les mutations (`useMutation`) invalident correctement le cache

**Points faibles** :
- Certains hooks n'ont pas de `staleTime` (refetch fréquent inutile)
- Pas de `retry` configuré (5 retries par défaut dans TanStack Query — trop pour un échec 500)

**Classement** : ⬜ Bon en l'état, ajustements mineurs

---

## 7.5 Gestion d'état global

### Zustand stores

**authStore** : Gère le token JWT, l'utilisateur courant, les méthodes login/logout/refresh. Persist le token dans localStorage. ✅ Complet.

**settingsStore** : Gère le thème (dark/light), le jeu courant (gameId, gameSlug). Persist les préférences. ✅ Complet.

**Verdict** : Le choix de Zustand est pertinent. Deux stores suffisent pour l'état global. Pas besoin de Redux pour cette complexité.

---

## 7.6 Service API (Axios)

Le fichier `api.ts` configure un client Axios avec :
- Base URL depuis les variables d'environnement
- Intercepteur request : ajoute le token JWT automatiquement
- Intercepteur response : toast d'erreur automatique sur 4xx/5xx
- Gestion du 401 : tente un refresh token, sinon logout

**Points forts** :
- Token injection automatique
- Retry transparent sur 401
- Centralisation des erreurs

**Points faibles** :
- Les messages d'erreur sont génériques (affiche `error.response.data.detail` brut)
- Pas de timeout configuré (un appel peut pendre indéfiniment)
- L'API base URL est hardcodée pour le dev (`http://localhost:8000`) — devrait utiliser `import.meta.env.VITE_API_URL`

**Classement** : 📈 Amélioration (timeout + URL configurable)

---

## 7.7 Code mort et inconsistances

| Fichier | Problème | Impact |
|---------|----------|--------|
| GridsPage.tsx | `const [profile] = useState("equilibre")` — déclaré, jamais utilisé | Fonctionnalité non branchée |
| NumberHeatmap.tsx | `onNumberClick` prop défini, jamais connecté | Feature morta |
| AdminPage.tsx | Cards « À venir — Phase 9 » | Affiche du contenu non fonctionnel |
| TemporalTab.tsx | `sortedPairs` basé sur `cooccurrences` au lieu de `temporal` (import croisé ?) | Possible bug de copier-coller |

**Classement** : 🔧 Corrections mineures

---

## 7.8 Performance frontend

**Points positifs** :
- TanStack Query cache les résultats et évite les requêtes redondantes
- React 18 avec automatic batching
- Tailwind v4 avec tree-shaking CSS
- `useMemo` utilisé dans les onglets statistiques pour les calculs dérivés

**Points d'attention** :
- Le GraphTab (D3.js) recrée le SVG entier à chaque rendu sans cleanup
- Le NumberHeatmap avec 49 ou 50 boutons ne pose pas de problème de performance
- Pas de lazy loading sur les pages (toutes chargées au démarrage)

**Recommandation** : Ajouter `React.lazy()` pour les pages lourdes (SimulationPage, AdminPage) afin de réduire le bundle initial.

**Classement** : 📈 Amélioration modérée

---

## 7.9 Synthèse frontend

| Aspect | Qualité | Priorité d'amélioration |
|--------|---------|------------------------|
| Stack technique | ★★★★☆ | Aucune |
| Architecture composants | ★★★☆☆ | Extraire les composants composites |
| Hooks / data fetching | ★★★★☆ | Ajustements mineurs |
| Gestion d'état | ★★★★☆ | Aucune |
| Pages fonctionnelles | ★★★☆☆ | Dashboard, Simulation, Portfolio |
| Composants UI | ★★★☆☆ | Accessibilité ARIA |
| Code quality | ★★★★☆ | Nettoyer le code mort |
| Performance | ★★★★☆ | Lazy loading |
| Mode clair | ★★☆☆☆ | Corriger couleurs Recharts/D3 |

Le frontend est **fonctionnel mais pas encore un produit**. La prochaine étape n'est pas d'ajouter des pages, mais d'**approfondir** celles qui existent avec du contexte, de la pédagogie et du feedback utilisateur.
