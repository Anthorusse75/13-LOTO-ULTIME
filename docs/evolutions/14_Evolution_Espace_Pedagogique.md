# 14 — Évolution : Espace Pédagogique

> Pages dédiées à la compréhension : scores, simulations, stratégies, systèmes réduits, loteries, limites réelles.

---

## Références croisées

- [00_Index_Evolutions](./00_Index_Evolutions.md)
- [02_Strategie_Produit](./02_Strategie_Produit.md) — Engagement éthique, P5 pédagogie intégrée
- [12_Evolution_Explicabilite](./12_Evolution_Explicabilite.md) — Explication inline
- [13_Evolution_Tooltips_Aide_Contextuelle](./13_Evolution_Tooltips_Aide_Contextuelle.md) — Aide par tooltips
- [17_Impacts_Frontend](./17_Impacts_Frontend.md)

---

## 1. Objectif

Enrichir les pages existantes (`HowItWorksPage`, `GlossaryPage`) et créer de nouvelles sections pédagogiques pour que l'utilisateur **comprenne en profondeur** chaque concept du produit.

---

## 2. État actuel

- **HowItWorksPage** : page avec tour guidé des fonctionnalités, contenu basique
- **GlossaryPage** : liste de termes avec définitions courtes

---

## 3. Sections pédagogiques à créer ou enrichir

### PED-01 : Comprendre les scores

**Contenu** :
- Qu'est-ce qu'un score de grille ? (note 0 à 10)
- Les 6 critères détaillés avec exemples concrets
  - Fréquence : « Le numéro 7 a été tiré 342 fois sur 2000 tirages, soit 17.1 %. La moyenne est 10.2 %. Il est donc fréquent et obtient un bon score de fréquence. »
  - Balance : schéma de répartition bas/milieu/haut
  - Gap : timeline visuelle « dernière apparition »
  - Cooccurrence : mini-heatmap interactive
  - Structure : exemples de bonne/mauvaise structure
  - Pattern Penalty : exemples (consécutifs, palindromes)
- Les 5 profils de scoring avec radar comparatif
- Comment lire un score : paliers (★★★★★ ≥ 8, ★★★★ ≥ 6, ★★★ ≥ 4...)
- Ce que le score n'est PAS : pas une probabilité de gain

**Format** : Texte + schémas + exemples interactifs

### PED-02 : Comprendre les simulations

**Contenu** :
- Qu'est-ce que Monte Carlo ? Analogie de l'urne (10 000 tirages simulés)
- À quoi sert la simulation ? Évaluer la robustesse, pas prédire
- Comment lire un histogramme de résultats
- Qu'est-ce que le bootstrap ? Analogie du mélange
- CV (coefficient de variation) : stable, correct, fragile
- Percentiles : top 10%, top 20%, au-dessus de la moyenne
- Limites : passé ≠ futur, simulations ≠ réalité

### PED-03 : Comprendre les stratégies

**Contenu** :
- Top N : prendre les meilleures grilles du scoring
- Portefeuille : diversification (analogie boursière)
- Système réduit : couverture combinatoire (analogie couverture d'assurance)
- Budget intelligent : optimisation sous contrainte
- Aléatoire : la baseline — pourquoi c'est important de comparer
- Quand utiliser quelle stratégie ?

### PED-04 : Comprendre les systèmes réduits

**Contenu** :
- C'est quoi un système réduit ? (full wheel vs abbreviated wheel)
- Concept de couverture (covering design)
- Paramètre t : niveau de garantie
- Exemple concret visuel : 10 numéros, 5 par grille, garantie 3
  - Full wheel : 252 grilles
  - Système réduit t=3 : ~10 grilles
  - Que perd-on ? (la garantie t=5 : seule la garantie t=3 est certaine)
- Coûts et compromis : plus de numéros ↔ plus de grilles ↔ plus coûteux
- Lecture de la matrice de couverture
- Scénarios de gains : conditional, pas certain

### PED-05 : Comprendre Loto vs EuroMillions

**Contenu** :
- Loto FDJ : 5/49 + 1 chance /10
- EuroMillions : 5/50 + 2 étoiles /12
- Différences de probabilités
- Différences de gains (jackpots, rangs intermédiaires)
- Tableau comparatif des probabilités par rang
- Impact sur les stratégies : EuroMillions → les étoiles comptent beaucoup plus
- Extension aux autres loteries (PowerBall, Mega Millions, Keno)

### PED-06 : Comprendre les limites

**Contenu critique** :
- Les tirages sont aléatoires — aucun système ne peut prédire
- Le passé ne détermine pas le futur (indépendance des tirages)
- L'espérance mathématique est toujours négative (le joueur perd en moyenne)
- Ce que la plateforme fait réellement : optimiser la couverture, pas « augmenter les chances »
- Le jeu responsable : ne jouez que ce que vous pouvez perdre
- Liens vers les ressources d'aide (joueurs info service)

### PED-07 : Comprendre le coût et les compromis

**Contenu** :
- Prix d'une grille par loterie
- Comment calculer le coût d'un système réduit
- Rapport coût / couverture : graphe de diminishing returns
- Rapport coût / gain théorique : espérance conditionnelle
- Budget raisonnable : qu'est-ce qu'on peut « se permettre » ?

---

## 4. Proposition d'implémentation

### 4.1 — Architecture des pages

**Option A — Page unique avec onglets** (recommandé) :
- Enrichir `HowItWorksPage` avec des sections dédiées, navigables par ancres
- Sidebar secondaire (table of contents)

**Option B — Pages séparées** :
- `/learn/scores`, `/learn/simulations`, `/learn/strategies`, etc.

**Recommandation** : Option A pour la simplicité. `HowItWorksPage` devient un mini-wiki avec navigation interne.

### 4.2 — Composants

| Composant | Rôle |
|-----------|------|
| `LearnSection` | Section pédagogique avec titre, contenu, exemples |
| `LearnTOC` | Table of contents cliquable (ancres) |
| `InteractiveExample` | Exemple interactif (ex: mini-scoring en direct) |
| `ComparisonTable` | Tableau comparatif réutilisable |
| `MathFormula` | Rendu LaTeX (optionnel, KaTeX si besoin) |

### 4.3 — Enrichissement GlossaryPage

Ajouter pour chaque terme :
- Lien vers la section pédagogique pertinente
- Exemple concret
- « Où le trouver dans l'app »

---

## 5. Phasage

| Phase | Contenu | Effort |
|-------|---------|--------|
| B.6 | PED-01 (scores) + PED-02 (simulations) | 1–2 jours |
| B.7 | PED-03 (stratégies) + PED-05 (Loto vs EM) + PED-06 (limites) | 1–2 jours |
| C.x | PED-04 (systèmes réduits) + PED-07 (coûts) — après wheeling | 1 jour |
| B.8 | Enrichir GlossaryPage + LearnTOC | 0.5 jour |

---

## 6. Risques

| Risque | Probabilité | Impact | Mitigation |
|--------|-------------|--------|------------|
| Contenu trop long, personne ne lit | Moyenne | Moyen | Résumés en haut, accordéons, exemples visuels |
| Contenu obsolète si fonctionnalités changent | Moyenne | Mineur | Centraliser, versionner avec les features |
| Formulations trompeuses (même dans la pédagogie) | Faible | Critique | Relecture vocabulaire contraint |

---

## 7. Critères d'acceptation

| Critère | Test |
|---------|------|
| 7 sections pédagogiques présentes | Navigation vérifiable |
| Chaque section a un résumé + détail + exemple | Audit contenu |
| PED-06 (limites) est clairement visible | Vérifié |
| GlossaryPage enrichie avec liens | Vérification liens |
| Aucune formulation trompeuse | Audit vocabulaire |

---

## 8. Checklist locale

- [ ] PED-01 : Rédiger section « Comprendre les scores » avec exemples concrets
- [ ] PED-02 : Rédiger section « Comprendre les simulations » avec analogies
- [ ] PED-03 : Rédiger section « Comprendre les stratégies » avec comparatif
- [ ] PED-04 : Rédiger section « Comprendre les systèmes réduits » avec visuel
- [ ] PED-05 : Rédiger section « Loto vs EuroMillions » avec tableaux
- [ ] PED-06 : Rédiger section « Limites réelles » avec avertissements clairs
- [ ] PED-07 : Rédiger section « Coûts et compromis » avec graphe
- [ ] Créer composant LearnSection
- [ ] Créer composant LearnTOC (table of contents)
- [ ] Enrichir HowItWorksPage avec les 7 sections
- [ ] Enrichir GlossaryPage avec liens vers sections
- [ ] Ajouter mention joueurs info service dans PED-06

Réf. : [27_Checklist_Globale_Evolutions](./27_Checklist_Globale_Evolutions.md)
