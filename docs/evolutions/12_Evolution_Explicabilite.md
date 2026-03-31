# 12 — Évolution : Explicabilité

> Couche d'explication premium — pourquoi cette grille, pourquoi ce portefeuille, comment lire le score, comment interpréter les résultats.

---

## Références croisées

- [00_Index_Evolutions](./00_Index_Evolutions.md)
- [02_Strategie_Produit](./02_Strategie_Produit.md) — Différenciation par la transparence
- [07_Evolutions_UI_UX](./07_Evolutions_UI_UX.md) — Mode simplifié/expert
- [13_Evolution_Tooltips_Aide_Contextuelle](./13_Evolution_Tooltips_Aide_Contextuelle.md) — Aide contextuelle
- [14_Evolution_Espace_Pedagogique](./14_Evolution_Espace_Pedagogique.md) — Pages éducatives
- [17_Impacts_Frontend](./17_Impacts_Frontend.md)

---

## 1. Objectif

Ajouter une **couche d'explication structurée** sur chaque résultat produit par la plateforme, afin que l'utilisateur comprenne **pourquoi** il voit ce qu'il voit et **comment** lire les résultats.

---

## 2. Contexte

Le système calcule déjà un score breakdown (6 critères) mais ne fournit aucun texte d'interprétation. L'utilisateur voit « Balance: 7.2/10 » sans comprendre ce que ça signifie concrètement.

---

## 3. Description détaillée

### 3.1 — Niveaux d'explicabilité

| Niveau | Description | Cible |
|--------|-------------|-------|
| **L1 — Résumé** | Phrase courte synthétisant le résultat | Tout le monde |
| **L2 — Interprétation** | Paragraphe expliquant ce que signifie chaque métrique | Joueur régulier |
| **L3 — Détail technique** | Formule, poids, méthode utilisée | Joueur analytique/expert |

### 3.2 — Éléments à expliquer

#### Score de grille
```
L1: "Cette grille a un score de 7.8/10, ce qui est très bon."
L2: "Le score est élevé grâce à une bonne fréquence historique (8.1) 
     et un excellent équilibre (8.5). Les numéros couvrent bien toutes 
     les tranches (bas, milieu, haut). Le gap est moyen (5.2) — certains 
     numéros n'ont pas été tirés depuis longtemps."
L3: "Score = Σ(poids_i × critère_i). Profil: équilibré 
     (freq=0.20, balance=0.20, gap=0.15, cooc=0.20, struct=0.15, penalty=0.10).
     Normalisation: min-max sur l'ensemble des tirages."
```

#### Portefeuille
```
L1: "Portefeuille de 10 grilles bien diversifiées, score moyen 7.1."
L2: "Les 10 grilles ont été sélectionnées pour maximiser la diversité 
     (distance de Hamming moyenne: 6.8/10), ce qui signifie que chaque grille 
     couvre des numéros différents. La couverture totale atteint 32/49 numéros."
```

#### Système réduit
```
L1: "12 grilles couvrent toutes vos combinaisons de 3 numéros parmi vos 10 sélectionnés."
L2: "Avec une garantie de niveau 3, si au moins 3 de vos 10 numéros sont tirés, 
     au moins une de vos 12 grilles contiendra ces 3 numéros. Cela représente une 
     réduction de 95 % par rapport au jeu exhaustif (252 grilles)."
```

#### Simulation Monte Carlo
```
L1: "Sur 10 000 tirages simulés, cette grille matche en moyenne 1.8 numéros."
L2: "La simulation montre que cette grille a ~15% de chances de matcher 3+ numéros 
     (le seuil de gain au Loto). C'est 2.3× plus que l'aléatoire. Attention : ceci 
     est une analyse statistique, pas une prédiction."
```

#### Comparaison
```
L1: "Le portefeuille optimisé offre le meilleur rapport qualité/diversité."
L2: "Le portefeuille bat le Top 10 en diversité (+35%) tout en maintenant un score 
     comparable (-3%). Le système réduit offre la meilleure couverture mais coûte 
     2× plus. L'aléatoire est systématiquement en dessous sur tous les axes."
```

### 3.3 — Architecture d'explicabilité

```
Backend:
  engines/explainability/
  ├── __init__.py
  ├── grid_explainer.py       # Explications pour une grille scorée
  ├── portfolio_explainer.py  # Explications pour un portefeuille
  ├── wheeling_explainer.py   # Explications pour un système réduit
  ├── simulation_explainer.py # Explications pour une simulation
  ├── comparison_explainer.py # Explications pour une comparaison
  └── templates.py            # Templates de texte paramétrés
```

**Principe** : chaque explainer prend les données calculées et produit un objet `Explanation` :

```python
@dataclass
class Explanation:
    summary: str         # L1 — 1 phrase
    interpretation: str  # L2 — 1 paragraphe
    technical: str       # L3 — détails techniques
    highlights: list[str]  # points forts
    warnings: list[str]    # points d'attention
```

**Les textes sont des templates Python** (pas de GPT/IA) avec des variables injectées depuis les données calculées. Prédictibles, vérifiables, testables.

---

## 4. Intérêt utilisateur

| Persona | Bénéfice |
|---------|----------|
| Joueur régulier | Comprend ses résultats sans documentation externe |
| Joueur analytique | Voit les raisons derrière chaque score |
| Tous | Confiance : le système est transparent, pas une boîte noire |

---

## 5. Intérêt produit

- **Différenciation** : la plupart des outils montrent des chiffres sans explication
- **Confiance** : un utilisateur qui comprend revient
- **Réduction du support** : moins de questions « ça veut dire quoi ? »

---

## 6. Proposition d'implémentation

### 6.1 — Backend

- **Pas de nouvel endpoint** : les explications sont incluses dans les réponses existantes
- Ajouter un champ `explanation` dans les schémas de réponse :
  - `GridScoreResponse.explanation: Explanation`
  - `PortfolioGenerateResponse.explanation: Explanation`
  - `WheelingGenerateResponse.explanation: Explanation`
  - `SimulationResponse.explanation: Explanation`
  - `ComparisonResponse.explanation: Explanation`
- Chaque service appelle l'explainer correspondant après le calcul

### 6.2 — Frontend

#### Composant `ExplanationPanel`

```typescript
interface ExplanationPanelProps {
  explanation: Explanation;
  displayMode: 'simple' | 'expert';
}
```

- Mode simplifié : affiche `summary` seulement, bouton « En savoir plus » → `interpretation`
- Mode expert : affiche tout (summary + interpretation + technical)
- `highlights` → badges verts
- `warnings` → badges orange

#### Intégration

Ajouter `<ExplanationPanel>` dans :
- GridsPage (sous le détail de score)
- PortfolioPage (sous les métriques)
- WheelingPage (sous les résultats)
- SimulationPage (sous chaque résultat)
- ComparatorPage (en résumé)

---

## 7. Phasage

| Phase | Contenu | Effort |
|-------|---------|--------|
| B.4 | Backend : explainer grid + portfolio + templates | 2 jours |
| B.5 | Frontend : ExplanationPanel + intégration pages existantes | 2 jours |
| C.x | Explainers pour wheeling, budget, comparateur | inclus dans chaque chantier |

---

## 8. Risques

| Risque | Probabilité | Impact | Mitigation |
|--------|-------------|--------|------------|
| Textes inexacts ou trompeurs | Moyenne | Critique | Templates vérifiés + tests + vocabulaire contraint |
| Surcharge visuelle | Moyenne | Moyen | Mode simplifié = résumé seul |
| Maintenance des templates | Faible | Mineur | Templates centralisés, tests de smoke |

---

## 9. Critères d'acceptation

| Critère | Test |
|---------|------|
| Chaque grille scorée a un champ explanation | Test schema |
| Summary ≤ 150 caractères | Test template |
| Interpretation est cohérente avec les données | Test avec données connues |
| Aucun texte ne contient « garantie », « prédiction », « gagner » | Test vocabulaire |
| Mode simplifié affiche summary seul | Test frontend |

---

## 10. Checklist locale

- [ ] Créer engines/explainability/templates.py
- [ ] Créer engines/explainability/grid_explainer.py
- [ ] Créer engines/explainability/portfolio_explainer.py
- [ ] Créer engines/explainability/simulation_explainer.py
- [ ] Ajouter champ explanation dans GridScoreResponse
- [ ] Ajouter champ explanation dans PortfolioGenerateResponse
- [ ] Intégrer grid_explainer dans grid_service
- [ ] Intégrer portfolio_explainer dans portfolio_service
- [ ] Tests unitaires templates (pas de mots interdits)
- [ ] Tests unitaires grid_explainer avec données connues
- [ ] Créer composant ExplanationPanel
- [ ] Intégrer ExplanationPanel dans GridsPage
- [ ] Intégrer ExplanationPanel dans PortfolioPage
- [ ] Intégrer ExplanationPanel dans SimulationPage
- [ ] Créer wheeling_explainer.py (phase C)
- [ ] Créer comparison_explainer.py (phase C)

Réf. : [27_Checklist_Globale_Evolutions](./27_Checklist_Globale_Evolutions.md)
