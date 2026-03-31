# 13 — Évolution : Tooltips et Aide Contextuelle Premium

> Stratégie UX complète de tooltips, microcopy, aide contextuelle, empty states, loading states, erreurs explicatives, panneaux « comment lire ».

---

## Références croisées

- [00_Index_Evolutions](./00_Index_Evolutions.md)
- [03_Audit_Existant_et_Ecarts](./03_Audit_Existant_et_Ecarts.md) — DUX-01, DUX-03, DUX-04
- [07_Evolutions_UI_UX](./07_Evolutions_UI_UX.md) — Design system
- [12_Evolution_Explicabilite](./12_Evolution_Explicabilite.md) — Couche d'explication
- [14_Evolution_Espace_Pedagogique](./14_Evolution_Espace_Pedagogique.md) — Pages dédiées
- [17_Impacts_Frontend](./17_Impacts_Frontend.md)

---

## 1. Objectif

Définir et implémenter une **stratégie d'aide contextuelle complète** couvrant tooltips, microcopy, empty states, loading states, erreurs, et panneaux d'aide sur chaque page.

---

## 2. État actuel

- Composant `InfoTooltip` : existant, fonctionnel
- `PageIntro` : récemment enrichi sur toutes les pages (session précédente)
- Empty states : améliorés sur certaines pages
- Tooltips : déployés sur ~60% des endroits pertinents (GridsPage, SimulationPage enrichis)
- Loading states : `LoadingSpinner` et `Skeleton` existent mais sous-utilisés
- Erreurs : `ErrorMessage` basique, pas d'explication contextuelle

---

## 3. Stratégie d'aide contextuelle

### 3.1 — Couches d'aide (du plus discret au plus visible)

| Couche               | Composant                 | Quand                     | Exemple                                                 |
| -------------------- | ------------------------- | ------------------------- | ------------------------------------------------------- |
| **Placeholder text** | input placeholder         | Champ vide                | « Ex: 10 grilles »                                      |
| **Microcopy**        | Texte sous un champ       | Toujours visible          | « Nombre de grilles à générer (1 à 100) »               |
| **InfoTooltip**      | Icône ⓘ au survol         | Hover / tap               | « Le score de fréquence mesure... »                     |
| **PageIntro**        | Bloc en haut de page      | Toujours visible          | Termes clés + exemples concrets                         |
| **Empty state**      | Bloc quand pas de données | Première visite           | « Pas encore de grilles. Cliquez ici pour en générer. » |
| **Comment lire**     | Panneau collapsible       | Sous un graphe ou tableau | « 📘 La courbe bleue représente... »                     |
| **Aide complète**    | Lien vers HowItWorks      | Fin de section            | « En savoir plus → Comment ça marche »                  |

### 3.2 — Inventaire des tooltips par page

#### DashboardPage
- [ ] Score moyen du jour : « Score global moyen des 10 meilleures grilles calculées cette nuit »
- [ ] Nombre de tirages : « Nombre total de tirages importés depuis le lancement »
- [ ] Dernière mise à jour : « Date du dernier calcul automatique (chaque nuit à 23h) »
- [ ] Carte « Meilleure grille » : « La grille avec le score le plus élevé du Top 10 »

#### DrawsPage
- [ ] Numéro de tirage : « Identifiant unique du tirage chez l'opérateur (FDJ, EuroMillions...) »
- [ ] Boutons de tri : « Trier par date décroissante / numéro de tirage »

#### StatisticsPage
- [ ] Chaque onglet : tooltip expliquant le moteur (déjà partiellement fait)
- [ ] Axes des graphiques : « Axe X = numéro, Axe Y = nombre d'apparitions »
- [ ] Heatmap : « Plus la cellule est colorée, plus les deux numéros apparaissent ensemble »
- [ ] Distribution : « Courbe de Poisson ajustée sur les fréquences observées »
- [ ] Bayésien : « Probabilité a posteriori de chaque numéro d'être tiré, tenant compte de l'historique »
- [ ] Graphe : « Réseau de co-apparitions. Chaque nœud est un numéro, les liens montrent les paires fréquentes »

#### GridsPage (enrichi récemment)
- [x] Méthode d'optimisation : tooltip sur le label ✅
- [x] Profil de scoring : tooltip sur le label ✅
- [x] Nombre de grilles : tooltip sur le label ✅
- [ ] Bouton « Générer » : microcopy « Génération de N grilles avec méthode X, profil Y »
- [ ] Détail score : interprétation contextuelle ✅ (fait en session UX)

#### SimulationPage (enrichi récemment)
- [x] Nombre de simulations : tooltip ✅
- [x] Nombre de grilles random : tooltip ✅
- [ ] CV (coefficient de variation) : tooltip ✅ (fait - CV coloré)
- [ ] Percentile : tooltip ✅ (fait - interprétation textuelle)

#### PortfolioPage
- [ ] Diversity score : « Score de diversité (0-1). Plus c'est élevé, plus les grilles sont variées »
- [ ] Coverage score : « Pourcentage de l'espace de numéros couvert par le portefeuille »
- [ ] Min Hamming distance : « Distance minimale entre deux grilles du portefeuille (nombre de numéros différents) »
- [ ] Heatmap : « Carte de couverture. Chaque cellule = un numéro. Couleur = nombre de grilles le contenant »

#### FavoritesPage
- [ ] Score étoiles : « Score distinct pour les numéros complémentaires (chance, étoiles) »

#### WheelingPage (nouveau, phase C)
- [ ] Garantie t : « Si t de vos numéros sont dans le tirage, au moins une grille contient ces t numéros »
- [ ] Couverture : « Pourcentage de sous-combinaisons de t numéros couvertes par le système »
- [ ] Réduction : « Ratio de grilles économisées par rapport au jeu exhaustif »

### 3.3 — Empty states enrichis

| Page           | Message actuel            | Message cible                                                                                                                                          |
| -------------- | ------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| FavoritesPage  | « Pas de favoris »        | « ❤️ Vous n'avez pas encore de grilles favorites. Allez dans Grilles, générez des grilles, puis cliquez sur le ❤️ pour les sauvegarder ici. »            |
| HistoryPage    | « Pas de grilles jouées » | « 📋 Votre historique est vide. Quand vous marquez une grille comme "jouée" ✓, elle apparaît ici avec la correspondance aux tirages réels. »            |
| PortfolioPage  | « Pas de portefeuille »   | « 📦 Pas de portefeuille généré. Un portefeuille est un ensemble de grilles diversifiées. Allez dans Grilles pour en générer, puis optimisez-les ici. » |
| SimulationPage | « Pas de résultats »      | « 🎲 Lancez votre première simulation. Choisissez une grille et simulez-la sur 10 000 tirages pour voir sa performance statistique. »                   |

### 3.4 — Loading states

| Page                         | Spinner actuel | Loading state cible                                                              |
| ---------------------------- | -------------- | -------------------------------------------------------------------------------- |
| GridsPage / Génération       | Spinner simple | « 🔄 Génération de N grilles avec algorithme X... Cela prend quelques secondes. » |
| SimulationPage / Monte Carlo | Spinner simple | « 🎲 Simulation de 10 000 tirages en cours... »                                   |
| StatisticsPage / Recompute   | Spinner simple | « 📊 Recalcul des 7 moteurs statistiques... 2/7 terminés »                        |

### 3.5 — Erreurs explicatives

| Erreur               | Message technique           | Message UX                                                                                                   |
| -------------------- | --------------------------- | ------------------------------------------------------------------------------------------------------------ |
| 422 (validation)     | « numbers count must be 5 » | « Le jeu Loto FDJ nécessite exactement 5 numéros entre 1 et 49. Vous en avez sélectionné 4. »                |
| 429 (rate limit)     | « Too many requests »       | « ⏱️ Trop de requêtes. Le système est protégé contre la surcharge. Réessayez dans 30 secondes. »              |
| 500 (erreur serveur) | « Internal server error »   | « ❌ Une erreur inattendue est survenue. L'équipe a été notifiée. Rechargez la page ou réessayez plus tard. » |
| Timeout              | « Request timeout »         | « ⏳ Le calcul a pris trop de temps. Essayez avec moins de grilles ou un ensemble plus petit. »               |

---

## 4. Proposition d'implémentation

### 4.1 — Fichier centralisé de textes

Créer `frontend/src/utils/helpTexts.ts` :

```typescript
export const HELP_TEXTS = {
  dashboard: {
    avgScore: "Score global moyen des 10 meilleures grilles calculées cette nuit.",
    drawCount: "Nombre total de tirages importés depuis le lancement.",
    // ...
  },
  grids: {
    method: "L'algorithme utilisé pour générer les grilles...",
    profile: "Le profil de scoring détermine les poids des critères...",
    // ...
  },
  // ...
};
```

### 4.2 — Composants enrichis

- `EnhancedInfoTooltip` : ajouter mode « click to pin » sur mobile
- `EmptyState` : composant réutilisable avec icône, titre, description, CTA
- `LoadingState` : composant avec message contextuel + timer
- `ErrorState` : composant avec message UX adapté au code HTTP

---

## 5. Phasage

| Phase         | Contenu                                                              | Effort     |
| ------------- | -------------------------------------------------------------------- | ---------- |
| A.1           | Centraliser helpTexts.ts                                             | 0.5 jour   |
| A.2           | Ajouter tooltips manquants (Dashboard, Draws, Statistics, Portfolio) | 1–2 jours  |
| A.3           | Enrichir empty states (4 pages)                                      | 0.5 jour   |
| A.4           | Enrichir loading states (3 pages)                                    | 0.5 jour   |
| A.5           | Créer ErrorState composant + mapping codes HTTP                      | 1 jour     |
| Total Phase A |                                                                      | ~3–4 jours |

---

## 6. Risques

| Risque                                       | Probabilité | Impact | Mitigation                                          |
| -------------------------------------------- | ----------- | ------ | --------------------------------------------------- |
| Surcharge visuelle (trop de tooltips)        | Moyenne     | Moyen  | Mode simplifié les réduit, mode expert les détaille |
| Textes obsolètes si fonctionnalités changent | Moyenne     | Mineur | Fichier centralisé, revue à chaque release          |
| Traduction si multi-langue                   | Future      | Moyen  | helpTexts.ts structuré pour i18n                    |

---

## 7. Critères d'acceptation

| Critère                                         | Test                                              |
| ----------------------------------------------- | ------------------------------------------------- |
| Chaque page a au moins 3 tooltips pertinents    | Audit visuel                                      |
| Chaque page a un empty state guidant            | Test (suppression données + vérification message) |
| Les erreurs 422/429/500 affichent un message UX | Test avec erreurs simulées                        |
| helpTexts.ts couvre toutes les pages            | Exhaustivité vérifiable                           |

---

## 8. Checklist locale

- [ ] Créer frontend/src/utils/helpTexts.ts centralisé
- [ ] DashboardPage : ajouter 4 tooltips
- [ ] DrawsPage : ajouter 2 tooltips
- [ ] StatisticsPage : compléter tooltips axes/graphes (6 onglets)
- [ ] PortfolioPage : ajouter 4 tooltips (diversity, coverage, hamming, heatmap)
- [ ] Créer composant EmptyState réutilisable
- [ ] Enrichir empty state FavoritesPage
- [ ] Enrichir empty state HistoryPage
- [ ] Enrichir empty state PortfolioPage
- [ ] Enrichir empty state SimulationPage
- [ ] Créer composant LoadingState contextuel
- [ ] Loading state GridsPage génération
- [ ] Loading state SimulationPage
- [ ] Créer composant ErrorState
- [ ] Mapping codes HTTP → messages UX
- [ ] Intégrer ErrorState dans ErrorBoundary

Réf. : [27_Checklist_Globale_Evolutions](./27_Checklist_Globale_Evolutions.md)
