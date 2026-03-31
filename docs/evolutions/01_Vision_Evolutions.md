# 01 — Vision des Évolutions

> Pourquoi évoluer, ambition produit à moyen–long terme, principes directeurs qui encadrent toutes les décisions.

---

## Références croisées

- [00_Index_Evolutions](./00_Index_Evolutions.md) — Navigation globale
- [02_Strategie_Produit](./02_Strategie_Produit.md) — Positionnement & segmentation
- [03_Audit_Existant_et_Ecarts](./03_Audit_Existant_et_Ecarts.md) — État des lieux
- [04_Priorisation_Evolutions](./04_Priorisation_Evolutions.md) — Hiérarchisation
- [26_Roadmap_Evolutions](./26_Roadmap_Evolutions.md) — Planification

---

## 1. Objectif du document

Formaliser la **vision d'évolution** de LOTO ULTIME : d'où vient-on, où va-t-on, pourquoi, et quels principes nous guident. Ce document est la boussole du projet.

---

## 2. Contexte — Où en sommes-nous ?

LOTO ULTIME est en production. Le produit couvre déjà :

| Capacité                                                                                          | Statut                                         |
| ------------------------------------------------------------------------------------------------- | ---------------------------------------------- |
| Import automatique des tirages (5 loteries)                                                       | ✅ Production                                   |
| 7 moteurs statistiques (fréquence, écart, cooccurrence, temporel, distribution, bayésien, graphe) | ✅ Production                                   |
| 6 critères de scoring + 5 profils de pondération                                                  | ✅ Production                                   |
| 5 algorithmes d'optimisation (génétique, recuit simulé, tabou, hill climbing, NSGA-II)            | ⚠️ Partiel (recuit simulé inaccessible en prod) |
| Portefeuille optimisé (greedy + Hamming)                                                          | ✅ Production                                   |
| Simulation Monte Carlo + robustesse + comparaison aléatoire                                       | ✅ Production                                   |
| Favoris, grilles jouées, historique                                                               | ✅ Production (basique)                         |
| Auth JWT, 3 rôles, admin panel                                                                    | ✅ Production                                   |
| Scheduler nightly (9 jobs)                                                                        | ✅ Production                                   |
| 13 pages front, 40+ composants, dark mode                                                         | ✅ Production                                   |

**Ce qui manque** : passage de « plateforme d'analyse » à « outil d'aide à la décision complet et premium ».

---

## 3. Ambition produit

### 3.1 — Vision à 6 mois

> Faire de LOTO ULTIME **la référence francophone** en matière d'aide à la décision combinatoire pour les loteries — un outil que le joueur régulier adopte comme compagnon de jeu permanent.

### 3.2 — Axes de différenciation

1. **Transparence algorithmique** — Pas de boîte noire. Chaque résultat est expliqué.
2. **Optimisation de couverture** — Systèmes réduits mathématiquement fondés (covering design).
3. **Pilotage budgétaire** — L'utilisateur maîtrise son investissement, pas l'inverse.
4. **Pédagogie** — Le joueur comprend ce qu'il fait, pourquoi, et les limites réelles.
5. **Profondeur analytique** — 7 moteurs statistiques, profils de scoring, simulation Monte Carlo.
6. **Honnêteté scientifique** — Aucune promesse de gain. Formulations exclusivement en termes d'optimisation et d'aide à la décision.

### 3.3 — Ce que le produit n'est PAS

- ❌ Un système de prédiction de résultats futurs
- ❌ Un outil garantissant un gain quelconque
- ❌ Un casino ou une plateforme de jeu
- ❌ Un outil de machine learning / IA générative

---

## 4. Dix chantiers d'évolution

| #   | Chantier                        | Classification             | Valeur |
| --- | ------------------------------- | -------------------------- | ------ |
| 1   | Système réduit / Wheeling       | Différenciation forte      | ★★★★★  |
| 2   | Mode budget intelligent         | Amélioration produit       | ★★★★☆  |
| 3   | Comparateur de stratégies       | Amélioration fonctionnelle | ★★★★☆  |
| 4   | Historique / Favoris / Rejouer  | Amélioration fonctionnelle | ★★★☆☆  |
| 5   | Explicabilité                   | Amélioration UX            | ★★★★☆  |
| 6   | Tooltips & aide contextuelle    | Amélioration UX            | ★★★☆☆  |
| 7   | Amélioration UI/UX profonde     | Amélioration UX            | ★★★☆☆  |
| 8   | Améliorations algorithmiques    | Amélioration algorithmique | ★★★★☆  |
| 9   | Espace pédagogique              | Amélioration produit       | ★★★☆☆  |
| 10  | Automatisation & vie du produit | Chantier premium           | ★★★★☆  |

---

## 5. Principes directeurs

### P1 — Production first
Tout changement doit être compatible avec un système en production. Pas de big-bang. Déploiement progressif, feature flags si nécessaire.

### P2 — Non-régression absolue
Les 337+ tests existants doivent passer à chaque étape. Tout nouveau code est testé. Les endpoints existants ne changent pas de signature sans versioning.

### P3 — Addition plutôt que modification
Préférer l'ajout de nouveaux modules, endpoints, composants à la modification de l'existant. Quand une modification est nécessaire, minimiser la surface d'impact.

### P4 — Honnêteté scientifique
Aucune formulation laissant entendre une prédiction ou une garantie de gain. Vocabulaire exclusif : « optimisation de couverture », « aide à la décision », « scénarios théoriques », « analyse combinatoire ».

### P5 — Pédagogie intégrée
Chaque nouvelle fonctionnalité doit être auto-explicative. L'utilisateur novice doit pouvoir comprendre sans documentation externe.

### P6 — Phasage réaliste
Roadmap en phases courtes (A→E), chaque phase livrable indépendamment. Valeur incrémentale à chaque livraison.

### P7 — Performances maîtrisées
Les calculs combinatoires (wheeling, budget) peuvent être coûteux. Toujours borner les entrées, mesurer les temps, et informer l'utilisateur.

---

## 6. Critères d'acceptation de la vision

| Critère                               | Vérifiable par                   |
| ------------------------------------- | -------------------------------- |
| Les 10 chantiers sont documentés      | Existence des documents 08→15    |
| Les impacts sont cartographiés        | Documents 16→23 complétés        |
| La roadmap existe et est phasée       | Document 26 validé               |
| Chaque chantier a une checklist       | Document 27 + checklists locales |
| Les tests protègent l'existant        | Document 24 appliqué             |
| L'honnêteté scientifique est garantie | Audit des formulations UX        |

---

## 7. Risques stratégiques

| Risque                            | Impact                         | Mitigation                                    |
| --------------------------------- | ------------------------------ | --------------------------------------------- |
| Over-engineering V1 des chantiers | Délais, complexité             | Phasage strict, MVP d'abord                   |
| Formulations trompeuses           | Réputation, légal              | Relecture systématique, vocabulaire contraint |
| Régression sur l'existant         | Perte de fonctionnalités       | Suite de tests, smoke tests, CI               |
| Explosion combinatoire (wheeling) | UX dégradée, serveur surchargé | Bornes strictes, feedback temps réel          |
| Scope creep                       | Jamais livré                   | Priorisation formelle (doc 04)                |
