# 00 — Index Central des Évolutions

> **Porte d'entrée principale** de la base documentaire d'évolution de LOTO ULTIME.  
> Ce document référence tous les documents, leur rôle, leurs dépendances, et permet de naviguer dans l'ensemble du dossier sans angle mort.

**Dernière mise à jour** : 31 mars 2026  
**Version** : 1.0  
**Statut** : Référence active — Produit en production

---

## 1. Vue d'ensemble

LOTO ULTIME est une plateforme d'analyse combinatoire de loteries (Loto FDJ, EuroMillions, PowerBall, Mega Millions, Keno), déjà **en production** avec :

- **Backend** : FastAPI + SQLAlchemy 2.0 async, 41 endpoints, 7 moteurs statistiques, 6 critères de scoring, 5 algorithmes d'optimisation, 2 moteurs de simulation, 9 jobs planifiés
- **Frontend** : React 19 + TypeScript 5.9 + Tailwind v4, 13 pages, 40+ composants, 6 hooks, 3 stores Zustand
- **Infrastructure** : Docker + PostgreSQL 16, CI/CD GitHub Actions, Prometheus + Grafana
- **Tests** : 337 tests (unit + intégration), couverture ≥ 80 %
- **Rôles** : ADMIN, UTILISATEUR, CONSULTATION

Ce dossier d'évolution définit **10 chantiers majeurs** organisés en 5 phases, avec une analyse d'impacts transversale sur 8 axes techniques.

---

## 2. Structure documentaire

### 2.1 — Documents stratégiques

| # | Document | Rôle |
|---|----------|------|
| [00](./00_Index_Evolutions.md) | **Index central** | Navigation, vue d'ensemble, dépendances |
| [01](./01_Vision_Evolutions.md) | **Vision des évolutions** | Pourquoi évoluer, ambition produit, principes directeurs |
| [02](./02_Strategie_Produit.md) | **Stratégie produit** | Positionnement, segmentation, différenciation |
| [03](./03_Audit_Existant_et_Ecarts.md) | **Audit existant & écarts** | État des lieux, bugs critiques, dettes, écarts feature |
| [04](./04_Priorisation_Evolutions.md) | **Priorisation** | Matrice valeur/effort, scoring, hiérarchie |

### 2.2 — Évolutions transversales

| # | Document | Rôle |
|---|----------|------|
| [05](./05_Evolutions_Algorithmiques.md) | **Évolutions algorithmiques** | Scoring, optimisation, simulation, calibration |
| [06](./06_Evolutions_Fonctionnelles.md) | **Évolutions fonctionnelles** | Nouvelles capacités métier transversales |
| [07](./07_Evolutions_UI_UX.md) | **Évolutions UI/UX** | Design system, navigation, modes, composants |

### 2.3 — Évolutions détaillées (chantiers)

| # | Document | Chantier | Phase |
|---|----------|----------|-------|
| [08](./08_Evolution_Systeme_Reduit_Wheeling.md) | **Système réduit / Wheeling** | Covering design interactif | C |
| [09](./09_Evolution_Mode_Budget_Intelligent.md) | **Mode budget intelligent** | Optimisation sous contrainte budgétaire | C |
| [10](./10_Evolution_Comparateur_Strategies.md) | **Comparateur de stratégies** | Tableau de bord comparatif | C |
| [11](./11_Evolution_Historique_Favoris.md) | **Historique / Favoris / Rejouer** | Persistance utilisateur avancée | B |
| [12](./12_Evolution_Explicabilite.md) | **Explicabilité** | Couche d'explication premium | B |
| [13](./13_Evolution_Tooltips_Aide_Contextuelle.md) | **Tooltips & aide contextuelle** | Micro-copy, guidance UX | A |
| [14](./14_Evolution_Espace_Pedagogique.md) | **Espace pédagogique** | Pages de compréhension | B |
| [15](./15_Evolution_Automatisation_Produit.md) | **Automatisation & vie du produit** | Alertes, suggestions, récurrence | D |

### 2.4 — Analyses d'impacts techniques

| # | Document | Périmètre |
|---|----------|-----------|
| [16](./16_Impacts_Backend.md) | **Impacts backend** | Services, engines, endpoints, repos, jobs |
| [17](./17_Impacts_Frontend.md) | **Impacts frontend** | Pages, composants, hooks, stores, services |
| [18](./18_Impacts_API.md) | **Impacts API** | Endpoints, schémas, validation, compatibilité |
| [19](./19_Impacts_Base_De_Donnees.md) | **Impacts base de données** | Tables, colonnes, migrations, seed data |
| [20](./20_Impacts_Scheduler_Jobs.md) | **Impacts scheduler / jobs** | Nouveaux jobs, recalculs, purges |
| [21](./21_Impacts_Securite_Roles.md) | **Impacts sécurité / rôles** | RBAC, rate-limiting, validation |
| [22](./22_Impacts_Performance_Scalabilite.md) | **Impacts performance / scalabilité** | Temps calcul, cache, async, volume |
| [23](./23_Impacts_Production_Exploitation.md) | **Impacts production / exploitation** | Logs, métriques, déploiement, rollback |

### 2.5 — Qualité, roadmap et pilotage

| # | Document | Rôle |
|---|----------|------|
| [24](./24_Strategie_Non_Regression.md) | **Stratégie de non-régression** | Protection de l'existant, smoke tests |
| [25](./25_Strategie_Tests_Evolutions.md) | **Stratégie de tests des évolutions** | Tests unitaires, intégration, E2E |
| [26](./26_Roadmap_Evolutions.md) | **Roadmap d'évolutions** | Phases A→E, jalons, estimations |
| [27](./27_Checklist_Globale_Evolutions.md) | **Checklist globale** | Tâches atomiques cochables + références croisées |

---

## 3. Cartographie des dépendances

```
01_Vision ──────────► 02_Stratégie ──────► 04_Priorisation
                          │                      │
03_Audit ─────────────────┘                      │
                                                 ▼
                    ┌────────────────────────────────────────────┐
                    │  Chantiers détaillés (08 → 15)             │
                    │  Chaque chantier référence :               │
                    │   • 05 (algo), 06 (fonctionnel), 07 (UX)  │
                    │   • 16→23 (impacts techniques)             │
                    │   • 24, 25 (tests / non-régression)        │
                    └────────────────────┬───────────────────────┘
                                         │
                    26_Roadmap ◄──────────┘
                         │
                    27_Checklist ◄── Tous les documents
```

---

## 4. Matrice évolutions × impacts

| Évolution | Backend | Frontend | API | DB | Scheduler | Sécurité | Perf | Prod |
|-----------|:-------:|:--------:|:---:|:--:|:---------:|:--------:|:----:|:----:|
| 08 Wheeling | ●●● | ●●● | ●●● | ●● | ● | ● | ●●● | ● |
| 09 Budget | ●●● | ●●● | ●● | ● | ● | ● | ●● | ● |
| 10 Comparateur | ●● | ●●● | ●● | ○ | ○ | ○ | ●● | ○ |
| 11 Historique | ●● | ●● | ●● | ●●● | ● | ●● | ● | ● |
| 12 Explicabilité | ●● | ●●● | ● | ○ | ○ | ○ | ● | ○ |
| 13 Tooltips | ○ | ●●● | ○ | ○ | ○ | ○ | ○ | ○ |
| 14 Pédagogie | ○ | ●● | ○ | ○ | ○ | ○ | ○ | ○ |
| 15 Automatisation | ●●● | ●● | ●● | ●● | ●●● | ●● | ●● | ●● |

_Légende : ○ aucun · ● mineur · ●● modéré · ●●● majeur_

---

## 5. Conventions documentaires

- **Références croisées** : chaque document commence par un bloc `Références croisées` listant les documents liés
- **Checklists** : format `[ ] action claire et vérifiable` avec référence au document source
- **Identifiants de tâche** : préfixe par domaine — `B-xx` (backend), `F-xx` (frontend), `DB-xx` (base), `S-xx` (scheduler), `T-xx` (tests), `UX-xx` (UX), `DOC-xx` (documentation)
- **Niveaux de priorité** : P0 (critique), P1 (important), P2 (utile), P3 (nice-to-have)
- **Classification** : correction · amélioration UX · amélioration fonctionnelle · amélioration algorithmique · amélioration produit · différenciation forte · dette technique · dette UX · dette documentaire · chantier premium · chantier long terme

---

## 6. Liens rapides

| Besoin | Document |
|--------|----------|
| Comprendre la vision | [01_Vision_Evolutions](./01_Vision_Evolutions.md) |
| Voir les bugs à corriger | [03_Audit_Existant_et_Ecarts](./03_Audit_Existant_et_Ecarts.md) |
| Savoir quoi faire en premier | [04_Priorisation_Evolutions](./04_Priorisation_Evolutions.md) |
| Planifier le développement | [26_Roadmap_Evolutions](./26_Roadmap_Evolutions.md) |
| Suivre l'avancement | [27_Checklist_Globale_Evolutions](./27_Checklist_Globale_Evolutions.md) |
| Vérifier l'impact DB | [19_Impacts_Base_De_Donnees](./19_Impacts_Base_De_Donnees.md) |
| Protéger l'existant | [24_Strategie_Non_Regression](./24_Strategie_Non_Regression.md) |
