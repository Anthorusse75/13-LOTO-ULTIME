# 06 — Évolutions Fonctionnelles

> Nouvelles capacités métier transversales : fonctionnalités cross-chantiers, extensions de l'existant, capacités partagées.

---

## Références croisées

- [00_Index_Evolutions](./00_Index_Evolutions.md)
- [02_Strategie_Produit](./02_Strategie_Produit.md) — Personas & besoins
- [03_Audit_Existant_et_Ecarts](./03_Audit_Existant_et_Ecarts.md) — Écarts fonctionnels
- [05_Evolutions_Algorithmiques](./05_Evolutions_Algorithmiques.md) — Moteurs sous-jacents
- [08_Evolution_Systeme_Reduit_Wheeling](./08_Evolution_Systeme_Reduit_Wheeling.md) à [15_Evolution_Automatisation_Produit](./15_Evolution_Automatisation_Produit.md) — Chantiers détaillés
- [18_Impacts_API](./18_Impacts_API.md) — Endpoints
- [19_Impacts_Base_De_Donnees](./19_Impacts_Base_De_Donnees.md) — Modèle de données

---

## 1. Objectif du document

Inventorier les **évolutions fonctionnelles transversales** — celles qui ne sont pas propres à un seul chantier mais enrichissent le produit globalement.

---

## 2. Périmètre exact

Ce document couvre les fonctionnalités partagées par plusieurs chantiers ou qui étendent les capacités existantes de manière horizontale.

---

## 3. Évolutions fonctionnelles identifiées

### FUNC-01 : Persistance étendue des résultats utilisateur

**Description** : Permettre à l'utilisateur de sauvegarder tout type de résultat (grilles, portefeuilles, systèmes réduits, simulations, comparaisons) et de les retrouver, dupliquer, relancer.

**Intérêt utilisateur** : Ne pas perdre son travail, construire un historique de stratégies.

**Intérêt produit** : Rétention, engagement, raison de revenir.

**Implémentation proposée** :
- Nouveau modèle générique `UserSavedItem` (type, payload JSON, metadata)
- Ou modèles spécifiques : `SavedWheelingSystem`, `SavedBudgetPlan`, `SavedComparison`
- Endpoints CRUD par type
- Frontend : bouton « Sauvegarder » sur chaque page de résultats

**Dépendances** : Auth (user_id), potentiellement quotas par rôle.

**Phase** : B (fondation pour C)

**Détail** : [11_Evolution_Historique_Favoris](./11_Evolution_Historique_Favoris.md)

---

### FUNC-02 : Export multi-format

**Description** : Exporter les résultats en PDF, CSV, JSON depuis n'importe quelle page de résultats.

**Intérêt utilisateur** : Imprimer ses grilles, partager, archiver hors plateforme.

**Intérêt produit** : Complétude fonctionnelle, usage offline.

**État actuel** : `pdfExport.ts` existe déjà (jsPDF) mais est limité.

**Implémentation proposée** :
- Enrichir `pdfExport.ts` pour chaque type de résultat (grilles, wheeling, budget, comparaison)
- Ajouter `csvExport.ts` — sérialisation tabulaire
- Ajouter `jsonExport.ts` — export brut pour integration externe
- Bouton unifié `ExportMenu` (dropdown PDF / CSV / JSON)

**Dépendances** : Aucune.

**Phase** : B

---

### FUNC-03 : Gestion multi-loterie effective

**Description** : Après correction du BUG-01, s'assurer que **chaque fonctionnalité** existante et future fonctionne correctement pour les 5 loteries configurées.

**Intérêt utilisateur** : Utiliser l'outil pour EuroMillions, PowerBall, Mega Millions et Keno en plus du Loto FDJ.

**Implémentation proposée** :
- Tests E2E systématiques avec au moins 2 jeux (Loto FDJ + EuroMillions)
- Validation des rules métier par jeu (taille grille, pool, étoiles)
- Adaptation des labels frontend (« numéro chance » vs « étoile » vs « PowerBall »)

**Dépendances** : BUG-01 corrigé.

**Phase** : A (correction) + vérification continue

---

### FUNC-04 : Tableaux de gains par loterie

**Description** : Intégrer les grilles de gains officielles (rangs, conditions, montants théoriques ou historiques) pour chaque loterie supportée.

**Intérêt utilisateur** : Comprendre ce que signifie « 3 bons numéros + 1 étoile » en euros.

**Intérêt produit** : Prérequis pour le wheeling (scénarios de gains) et le mode budget (rapport coût/gain potentiel).

**Implémentation proposée** :
- Nouvelle table `game_prize_tiers` (game_id, rank, name, match_numbers, match_stars, avg_prize, probability)
- Seed data pour Loto FDJ (9 rangs) et EuroMillions (13 rangs)
- Endpoint `GET /games/{slug}/prize-tiers`
- Frontend : tableau affiché dans info jeu + utilisé dans wheeling/budget

**Données Loto FDJ** :
| Rang | Condition | Gain moyen   |
| ---- | --------- | ------------ |
| 1    | 5+chance  | ~2 000 000 € |
| 2    | 5         | ~100 000 €   |
| 3    | 4+chance  | ~1 000 €     |
| 4    | 4         | ~500 €       |
| 5    | 3+chance  | ~50 €        |
| 6    | 3         | ~20 €        |
| 7    | 2+chance  | ~10 €        |
| 8    | 2         | ~5 €         |
| 9    | 1+chance  | ~2.20 €      |

**Données EuroMillions** :
| Rang | Condition | Gain moyen    |
| ---- | --------- | ------------- |
| 1    | 5+2★      | ~50 000 000 € |
| 2    | 5+1★      | ~300 000 €    |
| 3    | 5         | ~50 000 €     |
| 4    | 4+2★      | ~5 000 €      |
| 5    | 4+1★      | ~200 €        |
| 6    | 4         | ~100 €        |
| 7    | 3+2★      | ~75 €         |
| 8    | 2+2★      | ~20 €         |
| 9    | 3+1★      | ~15 €         |
| 10   | 3         | ~13 €         |
| 11   | 1+2★      | ~10 €         |
| 12   | 2+1★      | ~8 €          |
| 13   | 2         | ~4 €          |

**Dépendances** : Migration Alembic.

**Phase** : B (prérequis C)

---

### FUNC-05 : Gestion des coûts par loterie

**Description** : Connaître le prix d'une grille pour chaque loterie.

**Implémentation proposée** :
- Ajouter `grid_price` (Float) dans `GameDefinition` ou dans la config YAML
- Loto FDJ : 2.20 €, EuroMillions : 2.50 €, etc.
- Utilisé dans : wheeling (coût total), budget (nombre de grilles max), comparateur (coût/bénéfice)

**Phase** : A (simple ajout)

---

### FUNC-06 : Notation secondaire (étoiles / chance)

**Description** : Score distinct 0–10 pour les numéros complémentaires (étoiles, chance, PowerBall).

**Intérêt** : Actuellement le scoring ne traite que les numéros principaux. Les étoiles sont stockées mais pas scorées indépendamment.

**Implémentation proposée** :
- Nouveau critère `StarScoreCriterion` dans `engines/scoring/`
- Ajout `star_score` (Float, nullable) dans `ScoredGrid`
- Migration Alembic
- Frontend : affichage séparé dans le détail de score

**Phase** : C

---

### FUNC-07 : Partage de résultats

**Description** : Générer un lien de partage pour un résultat (grille, portefeuille, système réduit).

**Intérêt** : Viralité, discussion entre joueurs.

**Implémentation proposée** :
- Hash court unique pour chaque résultat sauvegardé
- Endpoint `GET /share/{hash}` → contenu public (lecture seule)
- Frontend : bouton « Partager » → copie URL
- Pas d'authentification requise pour la lecture

**Phase** : D (nice-to-have)

---

## 4. Synthèse par phase

| Phase | Fonctionnalités                                                       |
| ----- | --------------------------------------------------------------------- |
| A     | FUNC-03 (multi-loterie effective), FUNC-05 (prix grille)              |
| B     | FUNC-01 (persistance), FUNC-02 (exports), FUNC-04 (tableaux de gains) |
| C     | FUNC-06 (scoring étoiles)                                             |
| D     | FUNC-07 (partage)                                                     |

---

## 5. Impacts techniques

| FUNC | Backend | Frontend | API | DB  | Scheduler | Sécurité |
| ---- | ------- | -------- | --- | --- | --------- | -------- |
| 01   | ●●●     | ●●       | ●●● | ●●● | ○         | ●●       |
| 02   | ○       | ●●       | ○   | ○   | ○         | ○        |
| 03   | ●       | ●        | ●   | ○   | ○         | ○        |
| 04   | ●●      | ●●       | ●●  | ●●● | ○         | ○        |
| 05   | ●       | ●        | ●   | ●   | ○         | ○        |
| 06   | ●●      | ●        | ●   | ●●  | ●         | ○        |
| 07   | ●●      | ●●       | ●●  | ●   | ○         | ●        |

---

## 6. Risques

| Risque                                         | Probabilité | Impact | Mitigation                                           |
| ---------------------------------------------- | ----------- | ------ | ---------------------------------------------------- |
| Prolifération de modèles de persistance        | Moyenne     | Moyen  | Modèle générique `UserSavedItem` si possible         |
| Tableaux de gains qui changent                 | Faible      | Moyen  | Versionner par date, mettre à jour via admin         |
| Export PDF volumineux (wheeling 100+ grilles)  | Moyenne     | Mineur | Pagination dans PDF, limite                          |
| Lien de partage exposant des données sensibles | Faible      | Moyen  | Données publiques uniquement, pas d'info utilisateur |

---

## 7. Checklist locale

- [ ] FUNC-01 : Définir modèle de persistance (générique vs spécifique)
- [ ] FUNC-01 : Créer endpoints CRUD par type de résultat
- [ ] FUNC-02 : Enrichir pdfExport.ts pour grilles, wheeling, budget
- [ ] FUNC-02 : Créer csvExport.ts et jsonExport.ts
- [ ] FUNC-02 : Créer composant ExportMenu dropdown
- [ ] FUNC-03 : Tests E2E multi-loterie sur chaque fonctionnalité
- [ ] FUNC-04 : Créer table game_prize_tiers + migration + seed
- [ ] FUNC-04 : Endpoint GET /games/{slug}/prize-tiers
- [ ] FUNC-05 : Ajouter grid_price dans config YAML + GameDefinition
- [ ] FUNC-06 : Créer StarScoreCriterion + migration star_score
- [ ] FUNC-07 : Système de partage par hash court

Réf. : [27_Checklist_Globale_Evolutions](./27_Checklist_Globale_Evolutions.md)
