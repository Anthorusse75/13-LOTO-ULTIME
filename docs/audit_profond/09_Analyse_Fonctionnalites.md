# 9. Analyse Détaillée des Fonctionnalités

Cette section évalue chaque fonctionnalité utilisateur du point de vue du **parcours réel** : ce que l'utilisateur croit pouvoir faire, ce qu'il peut réellement faire, et là où le décalage se produit.

---

## 9.1 Parcours utilisateur principal

Le parcours attendu d'un utilisateur de LOTO ULTIME est :

```
1. Se connecter
2. Consulter les statistiques récentes
3. Identifier des patterns intéressants
4. Générer des grilles optimisées
5. Évaluer la qualité des grilles (simulation)
6. Construire un portefeuille diversifié
7. Jouer les grilles
8. Revenir après le tirage pour vérifier
```

Voyons à quel point chaque étape est fonctionnelle.

---

### Étape 1 : Se connecter ✅

**Fonctionnel** : L'utilisateur peut se connecter avec email ou username. Le JWT est émis, stocké et utilisé automatiquement pour les requêtes suivantes.

**Lacunes mineures** :
- Pas de « Se souvenir de moi » (le token expire en 60 min, le refresh token en 7 jours)
- Pas de récupération de mot de passe (acceptable pour un produit mono-utilisateur)

---

### Étape 2 : Consulter les statistiques ⚠️

**Fonctionnel** : L'utilisateur peut naviguer vers l'onglet Statistiques et parcourir 7 sous-sections.

**Problèmes** :
- Les données affichées sont valides mais **incompréhensibles** sans formation statistique
- Pas de « quick summary » : l'utilisateur doit parcourir 7 onglets pour comprendre l'état de l'historique
- Pas de liens entre les onglets (un numéro fréquent dans l'onglet Fréquences → quel est son gap dans l'onglet Gaps ?)
- Le recompute (calcul frais) nécessite un accès Admin, mais l'utilisateur ne sait pas si les stats sont à jour

**Ce qui manque fonctionnellement** :
- Un **résumé intelligent** : « Sur les 50 derniers tirages, les numéros 7, 14, 31 sont exceptionnellement fréquents. Les numéros 3, 22, 45 sont en retard. L'entropie est normale (0.98/1.0), la distribution est uniforme. »
- Des **filtres temporels** : voir les statistiques sur les 50, 100, 200, 500 derniers tirages
- Des **alertes visuelles** : surligner les numéros anormaux dans chaque onglet

---

### Étape 3 : Identifier des patterns ❌

**Pas fonctionnel** : Il n'existe pas de fonctionnalité qui croise les différentes analyses pour identifier des patterns exploitables. L'utilisateur doit manuellement :
1. Ouvrir l'onglet Fréquences → noter les numéros fréquents
2. Ouvrir l'onglet Gaps → noter les numéros en retard
3. Ouvrir l'onglet Co-occurences → vérifier les associations
4. Croiser mentalement ces informations

**Ce qui devrait exister** :
- Une page « Recommandations » qui synthétise automatiquement les analyses
- Un « nuage de numéros » interactif où la taille et la couleur reflètent un score composite
- La possibilité de sélectionner un numéro et voir TOUTES ses statistiques sur un seul écran

---

### Étape 4 : Générer des grilles optimisées ⚠️

**Partiellement fonctionnel** : L'utilisateur peut choisir un nombre de grilles et une méthode, puis générer.

**Problèmes fonctionnels** :
- Le **profil de scoring n'est pas branché** (toujours « équilibré »). L'utilisateur voit 4 options mais ne peut pas réellement choisir.
- La **méthode « auto »** utilise toujours l'algorithme génétique (bug `select_method`). L'utilisateur croit obtenir le meilleur algorithme, il obtient toujours le même.
- Pas d'explication du score obtenu : « Score 7.2/10 » ne dit pas POURQUOI cette grille est bonne.
- Pas de comparaison avec les grilles précédemment générées.
- Pas de possibilité de **modifier manuellement** une grille générée (remplacer un numéro tout en gardant le scoring en live).

---

### Étape 5 : Évaluer la qualité ⚠️

**Partiellement fonctionnel** : La simulation Monte Carlo permet de tester une grille.

**Problèmes** :
- L'utilisateur doit **saisir manuellement** les numéros de la grille dans le champ de simulation. Pourquoi ne pas pouvoir cliquer « Simuler » directement depuis une grille générée ?
- Les résultats bruts (10 000 simulations, 423 matchs de 3/5, 12 matchs de 4/5, 0 matchs de 5/5) ne sont pas mis en perspective. Est-ce bon ? Normal ?
- L'onglet « Comparaison random » est le plus utile (Z-score > 0 = mieux que la moyenne) mais son nom et sa position en 3ème onglet en font un feature quasi-invisible.

---

### Étape 6 : Construire un portefeuille ⚠️

**Fonctionnel** mais insuffisant en guidage :
- L'utilisateur peut choisir une stratégie et générer. Les résultats sont affichés.
- Mais **quelle stratégie choisir ?** Aucune aide. Un tooltip sur chaque stratégie est indispensable :
  - « Balanced : optimise l'équilibre entre score individuel et diversité globale »
  - « Max Diversity : maximise la couverture de l'espace de numéros (utile si vous jouez régulièrement) »
  - etc.
- Pas de comparaison entre stratégies côte à côte
- Pas de backtesting : « Si vous aviez joué ce portefeuille sur les 100 derniers tirages... »

---

### Étape 7 : Jouer les grilles ❌

**Non implémenté** : Le produit ne propose pas de export ou de récapitulatif « prêt à jouer ».

Ce qui serait utile :
- Export PDF/image d'un portefeuille avec les grilles formatées
- Lien ou QR code pour transposer les grilles sur le site FDJ
- Rappel de prochains tirages

**Classement** : 🎯 Repositionnement produit (transforme LOTO ULTIME en outil actionnable)

---

### Étape 8 : Vérifier après tirage ❌

**Non implémenté** : Après un tirage réel, l'utilisateur ne peut pas :
- Voir si ses grilles ont matché des numéros
- Voir combien il aurait gagné
- Voir comment ses grilles se sont comportées historiquement

**Ce qui devrait exister** :
- Saisir ou sélectionner un tirage réel
- Comparer automatiquement avec les grilles sauvegardées
- Afficher les correspondances (3/5, 4/5, etc.) et le gain théorique
- Historique de performance cumulé

**Classement** : 🎯 Repositionnement produit (la boucle feedback est ce qui fidélise l'utilisateur)

---

## 9.2 Fonctionnalités « vitrines » (affichées mais non fonctionnelles)

| Fonctionnalité                  | Présence visuelle                | État réel                   | Impact utilisateur                                  |
| ------------------------------- | -------------------------------- | --------------------------- | --------------------------------------------------- |
| Sélecteur de profil (GridsPage) | 4 boutons radio cliquables       | Jamais envoyé à l'API       | L'utilisateur croit choisir, mais il ne choisit pas |
| Sélection auto de méthode       | Option « auto » dans le dropdown | Toujours génétique          | L'utilisateur croit obtenir la meilleure méthode    |
| Cards admin « À venir »         | Visuellement présentes           | Contenu vide « Phase 9 »    | Donne une impression de chantier                    |
| Clic sur NumberHeatmap          | Boutons cliquables               | Handler non connecté        | Frustration si l'utilisateur clique                 |
| Sélecteur de jeu EuroMillions   | Dropdown fonctionnel             | Config non résolue côté API | Résultats EuroMillions erronés                      |

**Recommandation** : Chaque fonctionnalité doit être soit **pleinement opérationnelle**, soit **retirée de l'interface**. Afficher un contrôle non fonctionnel est pire que de ne pas l'afficher.

---

## 9.3 Fonctionnalités complètes et fonctionnelles

Pour être juste, voici ce qui fonctionne correctement de bout en bout :

| Fonctionnalité                    | Verdict       | Qualité                               |
| --------------------------------- | ------------- | ------------------------------------- |
| Login / Authentification          | ✅ Complet     | Bon                                   |
| Consultation des tirages (paginé) | ✅ Complet     | Bon                                   |
| Statistiques de fréquences        | ✅ Fonctionnel | Basique                               |
| Statistiques de gaps              | ✅ Fonctionnel | Correct                               |
| Statistiques co-occurrences       | ✅ Fonctionnel | Correct                               |
| Statistiques distribution         | ✅ Fonctionnel | Bon                                   |
| Statistiques bayésiennes          | ✅ Fonctionnel | Avancé                                |
| Statistiques graphe               | ✅ Fonctionnel | Avancé                                |
| Statistiques temporelles          | ✅ Fonctionnel | Fragile (4 points)                    |
| Génération de grilles             | ✅ Fonctionnel | Score correct mais profil non branché |
| Top grilles                       | ✅ Fonctionnel | Automatique via scheduler             |
| Génération de portefeuille        | ✅ Fonctionnel | 4 stratégies                          |
| Simulation Monte Carlo            | ✅ Fonctionnel | Résultats bruts                       |
| Simulation stabilité              | ✅ Fonctionnel | Bootstrap                             |
| Comparaison random                | ✅ Fonctionnel | Z-score correct                       |
| Administration jobs               | ✅ Fonctionnel | Trigger + historique                  |
| Administration utilisateurs       | ✅ Fonctionnel | Création + liste                      |
| Importation automatique tirages   | ✅ Fonctionnel | Scheduler + scrapers                  |
| Pipeline nightly                  | ✅ Fonctionnel | Stats → Scoring → Top → Portfolio     |

---

## 9.4 Fonctionnalités absentes mais attendues

| Fonctionnalité                                         | Priorité  | Justification                       |
| ------------------------------------------------------ | --------- | ----------------------------------- |
| Vérification post-tirage                               | 🔴 Haute   | Boucle de feedback essentielle      |
| Export PDF/image des grilles                           | 🟠 Moyenne | Rend le produit actionnable         |
| Résumé intelligent des analyses                        | 🔴 Haute   | Différencie le produit d'un tableur |
| Page profil numéro (toutes stats d'un seul numéro)     | 🟠 Moyenne | Navigation croisée entre analyses   |
| Backtesting de portefeuille                            | 🟠 Moyenne | Preuve de valeur du portefeuille    |
| Historique des grilles générées                        | 🟡 Basse   | Permet de suivre l'évolution        |
| Notifications nouveau tirage                           | 🟡 Basse   | Engage l'utilisateur                |
| Modification manuelle d'une grille avec rescoring live | 🟡 Basse   | Pour utilisateurs avancés           |
| Comparaison de deux portefeuilles                      | 🟡 Basse   | Aide à la décision                  |

---

## 9.5 Synthèse fonctionnelle

Le produit a une **couverture fonctionnelle large** (ingestion → analyse → optimisation → simulation → administration). C'est impressionnant pour un premier cycle. Mais la **profondeur fonctionnelle** de chaque étape reste limitée :

- Les statistiques sont affichées mais pas **interprétées**
- Les grilles sont générées mais pas **expliquées**
- Les simulations sont exécutées mais pas **contextualisées**
- Les portefeuilles sont construits mais pas **validés** (backtesting)
- La boucle feedback post-tirage est **totalement absente**

L'effort des prochaines phases devrait se concentrer non pas sur l'ajout de nouvelles fonctionnalités, mais sur l'**approfondissement** de celles qui existent. Un produit qui fait 10 choses superficiellement est moins utile qu'un produit qui fait 5 choses en profondeur.
