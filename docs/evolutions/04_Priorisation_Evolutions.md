# 04 — Priorisation des Évolutions

> Matrice valeur/effort, scoring de chaque chantier, hiérarchisation argumentée.

---

## Références croisées

- [00_Index_Evolutions](./00_Index_Evolutions.md)
- [01_Vision_Evolutions](./01_Vision_Evolutions.md) — Principes directeurs
- [02_Strategie_Produit](./02_Strategie_Produit.md) — Pyramide de valeur
- [03_Audit_Existant_et_Ecarts](./03_Audit_Existant_et_Ecarts.md) — Bugs P0 à corriger d'abord
- [26_Roadmap_Evolutions](./26_Roadmap_Evolutions.md) — Résultat de la priorisation

---

## 1. Objectif du document

Fournir une **hiérarchisation objective et argumentée** de tous les chantiers d'évolution, en distinguant clairement ce qui est critique, utile, premium, et nice-to-have.

---

## 2. Méthodologie de scoring

Chaque chantier est évalué sur 5 axes (note 1–5) :

| Axe                    | Description                                       | Poids |
| ---------------------- | ------------------------------------------------- | ----- |
| **Valeur utilisateur** | Impact direct sur l'expérience et la satisfaction | 30 %  |
| **Différenciation**    | Ce que les concurrents n'ont pas                  | 20 %  |
| **Faisabilité**        | Complexité technique, risques, dépendances        | 20 %  |
| **Fondation**          | Déblocage d'autres évolutions                     | 15 %  |
| **Urgence**            | Dettes, bugs, attentes utilisateur                | 15 %  |

**Score pondéré** = (V × 0.30) + (D × 0.20) + (F × 0.20) + (Fo × 0.15) + (U × 0.15)

> _Faisabilité inversée : 5 = facile, 1 = très complexe._

---

## 3. Prérequis absolus (hors scoring)

Avant toute évolution, les **3 bugs P0** de l'audit doivent être corrigés :

| Ref    | Bug                           | Impact                           |
| ------ | ----------------------------- | -------------------------------- |
| BUG-01 | Multi-loterie non fonctionnel | Bloque toute évolution multi-jeu |
| BUG-02 | Method selector bloqué        | Bloque benchmark algorithmique   |
| BUG-03 | Profil scoring non transmis   | Bloque comparaison profils       |

**Estimation** : 1–2 jours de développement + tests.

---

## 4. Matrice de scoring

| #   | Chantier                        | V (30%) | D (20%) | F (20%) | Fo (15%) | U (15%) | **Score** |
| --- | ------------------------------- | :-----: | :-----: | :-----: | :------: | :-----: | :-------: |
| 13  | Tooltips & aide contextuelle    |    4    |    2    |    5    |    4     |    5    | **3.95**  |
| 11  | Historique / Favoris / Rejouer  |    4    |    3    |    4    |    5     |    4    | **3.95**  |
| 12  | Explicabilité                   |    5    |    4    |    4    |    3     |    3    | **3.95**  |
| 08  | Système réduit / Wheeling       |    5    |    5    |    2    |    3     |    2    | **3.55**  |
| 07  | Amélioration UI/UX profonde     |    4    |    2    |    4    |    4     |    4    | **3.50**  |
| 09  | Mode budget intelligent         |    5    |    5    |    2    |    2     |    2    | **3.35**  |
| 10  | Comparateur de stratégies       |    4    |    4    |    3    |    3     |    2    | **3.25**  |
| 14  | Espace pédagogique              |    3    |    2    |    5    |    3     |    3    | **3.15**  |
| 05  | Améliorations algorithmiques    |    3    |    3    |    3    |    4     |    3    | **3.15**  |
| 15  | Automatisation & vie du produit |    4    |    4    |    2    |    2     |    2    | **2.95**  |

---

## 5. Classification par type

### Corrections (P0 — avant tout)
- BUG-01 : Multi-loterie
- BUG-02 : Method selector
- BUG-03 : Profil scoring

### Quick wins (Phase A — 1 à 2 semaines)
- **13 — Tooltips & aide contextuelle** : composant InfoTooltip déjà existant, il suffit de l'étendre
- **07 — UI/UX** : pagination, empty states, feedback loading → améliorations ponctuelles immédiates

### Fondations (Phase B — 2 à 4 semaines)
- **11 — Historique / Favoris / Rejouer** : prérequis pour sauvegarder wheeling, budgets, comparaisons
- **12 — Explicabilité** : couche de texte sur l'existant, pas de nouveau calcul
- **14 — Espace pédagogique** : pages de contenu, faible complexité technique

### Cœur produit (Phase C — 4 à 8 semaines)
- **08 — Système réduit / Wheeling** : chantier le plus structurant, nécessite moteur combinatoire
- **09 — Mode budget intelligent** : s'appuie sur wheeling + scoring existant
- **10 — Comparateur de stratégies** : agrège les résultats des autres fonctionnalités

### Approfondissement (Phase D — 2 à 4 semaines)
- **05 — Améliorations algorithmiques** : calibration, benchmark, profils avancés

### Premium (Phase E — long terme)
- **15 — Automatisation & vie du produit** : alertes, suggestions récurrentes, pré-générations

---

## 6. Graphe de dépendances

```
Corrections P0 ──────► Phase A (Tooltips, UX quick wins)
                            │
                            ▼
                       Phase B (Historique, Explicabilité, Pédagogie)
                            │
                    ┌───────┼───────┐
                    ▼       ▼       ▼
              Wheeling  Budget   Comparateur    ← Phase C
              (08)      (09)     (10)
                │         │         │
                └────┬────┘         │
                     ▼              │
              Phase D (Algo)  ◄─────┘
                     │
                     ▼
              Phase E (Automatisation)
```

**Dépendances critiques** :
- Le **mode budget (09)** dépend du **wheeling (08)** pour la génération de systèmes réduits
- Le **comparateur (10)** dépend de **08 + 09 + historique (11)** pour avoir des stratégies à comparer
- L'**historique (11)** est un prérequis de **08, 09, 10** pour la persistance des résultats
- Les **tooltips (13)** et l'**explicabilité (12)** doivent être posés avant les nouveaux chantiers pour maintenir la cohérence UX

---

## 7. Distinction des niveaux

| Niveau            | Chantiers              | Justification                          |
| ----------------- | ---------------------- | -------------------------------------- |
| **Indispensable** | Corrections P0, 13, 11 | Bugs bloquants + fondation             |
| **Important**     | 12, 07, 14, 08         | Core value + prérequis différenciation |
| **Utile**         | 09, 10, 05             | Fonctionnalités à forte valeur perçue  |
| **Premium**       | 15                     | Long terme, valeur de rétention        |

---

## 8. Estimation d'effort par phase

| Phase | Contenu                                     | Effort estimé | Risque        |
| ----- | ------------------------------------------- | ------------- | ------------- |
| P0    | Corrections bugs                            | 1–2 jours     | Faible        |
| A     | Tooltips, UX quick wins, pagination         | 1–2 semaines  | Faible        |
| B     | Historique étendu, explicabilité, pédagogie | 2–4 semaines  | Faible        |
| C     | Wheeling + Budget + Comparateur             | 6–10 semaines | Moyen à élevé |
| D     | Calibration algo, profils avancés           | 2–4 semaines  | Moyen         |
| E     | Automatisation, alertes, récurrence         | 3–5 semaines  | Moyen         |

**Total estimé** : 15–27 semaines de développement.

---

## 9. Critères d'acceptation

| Critère                                      | Mesure                                              |
| -------------------------------------------- | --------------------------------------------------- |
| Chaque chantier a un score pondéré documenté | Matrice section 4                                   |
| Les dépendances sont identifiées             | Graphe section 6                                    |
| Les phases sont réalistes                    | Estimations section 8                               |
| La roadmap résultante est cohérente          | [26_Roadmap_Evolutions](./26_Roadmap_Evolutions.md) |

---

## 10. Checklist locale

- [ ] Valider les scores avec les priorités métier réelles
- [ ] Confirmer les dépendances inter-chantiers
- [ ] Ajuster les estimations après les corrections P0
- [ ] Valider l'ordre des phases avec l'équipe
- [ ] Reporter les résultats dans [26_Roadmap_Evolutions](./26_Roadmap_Evolutions.md)

Réf. : [27_Checklist_Globale_Evolutions](./27_Checklist_Globale_Evolutions.md)
