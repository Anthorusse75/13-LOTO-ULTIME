# 03 — Audit de l'Existant et Écarts

> État des lieux complet, bugs critiques, dettes techniques/UX/documentaires, écarts entre l'existant et la cible.

---

## Références croisées

- [00_Index_Evolutions](./00_Index_Evolutions.md)
- [01_Vision_Evolutions](./01_Vision_Evolutions.md) — Vision cible
- [02_Strategie_Produit](./02_Strategie_Produit.md) — Positionnement
- [04_Priorisation_Evolutions](./04_Priorisation_Evolutions.md) — Impact sur la priorisation
- [16_Impacts_Backend](./16_Impacts_Backend.md) — Impacts backend
- [24_Strategie_Non_Regression](./24_Strategie_Non_Regression.md) — Protection existant
- [27_Checklist_Globale_Evolutions](./27_Checklist_Globale_Evolutions.md)

---

## 1. Objectif du document

Réaliser un **audit factuel et complet** du système en production. Identifier les bugs, les dettes, les écarts, et les risques qui impactent la capacité à évoluer.

---

## 2. Périmètre exact

- 7 modèles SQLAlchemy, 41 endpoints API, 7 moteurs statistiques, 6 critères de scoring, 5 optimiseurs, 2 simulateurs
- 13 pages frontend, 40+ composants, 6 hooks, 3 stores, 10 services API
- 9 jobs planifiés, 5 scrapers, 5 configurations de jeux
- 337 tests, CI/CD, Docker, Prometheus + Grafana

---

## 3. Bugs critiques en production

### BUG-01 : Multi-loterie non fonctionnel (CRITIQUE)

| Attribut | Détail |
|----------|--------|
| **Localisation** | Couche de routage API — résolution game_id |
| **Symptôme** | Tous les endpoints utilisent la première config de jeu (Loto FDJ) même quand game_id pointe vers EuroMillions |
| **Impact** | Les 4 autres loteries (EuroMillions, PowerBall, Mega Millions, Keno) sont inutilisables en production |
| **Cause** | `game_id` ignoré dans le service layer, config chargée en dur |
| **Risque** | Invalide l'intégralité du support multi-loterie |
| **Priorité** | **P0 — Correction immédiate** |
| **Classification** | Correction |
| **Dépendances** | Aucune |
| **Tests requis** | Test E2E avec game_id EuroMillions → vérifier config 5/50+2/12 |

### BUG-02 : Method Selector bloqué sur « genetic » (CRITIQUE)

| Attribut | Détail |
|----------|--------|
| **Localisation** | `backend/app/engines/optimization/method_selector.py` |
| **Symptôme** | `select_method()` retourne toujours `"genetic"` |
| **Impact** | Le Simulated Annealing (50 000 itérations, cooling 0.9995) n'est jamais exécuté en production |
| **Cause** | Logique conditionnelle absente ou incorrecte |
| **Risque** | L'algorithme potentiellement meilleur pour grands ensembles est inaccessible |
| **Priorité** | **P0 — Correction immédiate** |
| **Classification** | Correction |

### BUG-03 : Profil de scoring non transmis au backend (CRITIQUE)

| Attribut | Détail |
|----------|--------|
| **Localisation** | `frontend/src/pages/GridsPage.tsx` → `frontend/src/services/gridService.ts` |
| **Symptôme** | Le sélecteur de profil affiche 5 options mais la valeur sélectionnée n'est jamais envoyée dans la requête API |
| **Impact** | L'utilisateur reçoit toujours le profil « equilibre » même s'il choisit « frequence », « gaps », « cooccurrence » ou « balance » |
| **Cause** | La mutation `generate` n'inclut pas le champ `profile` dans le payload |
| **Risque** | 4 profils sur 5 sont factuellement inutilisables |
| **Priorité** | **P0 — Correction immédiate** |
| **Classification** | Correction |

---

## 4. Dettes techniques

### DT-01 : Pas de versioning API

| Attribut | Détail |
|----------|--------|
| **Constat** | Les routes sont sous `/api/v1/` mais aucune stratégie de versionning n'est définie |
| **Risque** | Les futures évolutions (wheeling, budget) peuvent casser les clients existants |
| **Recommandation** | Documenter la politique de v1 (backward compatible), prévoir v2 si breaking changes |
| **Priorité** | P2 |
| **Classification** | Dette technique |

### DT-02 : Token blacklist en mémoire

| Attribut | Détail |
|----------|--------|
| **Constat** | `core/token_blacklist.py` utilise un set en mémoire |
| **Risque** | Perte du blacklist au redémarrage ; pas de partage multi-instance |
| **Recommandation** | Migration vers Redis ou table DB dédiée |
| **Priorité** | P2 |
| **Classification** | Dette technique |

### DT-03 : Pas de cache applicatif

| Attribut | Détail |
|----------|--------|
| **Constat** | Les snapshots statistiques sont recalculés ou requêtés DB à chaque appel |
| **Risque** | Latence inutile, surtout pour les 7 engines qui ne changent qu'une fois par jour |
| **Recommandation** | Cache TTL (Redis ou in-memory pour mono-instance) pour `GET /statistics` |
| **Priorité** | P2 |
| **Classification** | Dette technique |

### DT-04 : Absence de rate limiting granulaire

| Attribut | Détail |
|----------|--------|
| **Constat** | Rate limiting global configuré mais pas par endpoint |
| **Risque** | Les endpoints coûteux (generate, simulations) peuvent être abusés |
| **Recommandation** | Rate limit spécifique pour `/grids/generate`, `/simulations/*`, `/portfolios/generate` |
| **Priorité** | P1 |
| **Classification** | Dette technique |

### DT-05 : Pas de pagination sur les endpoints de liste

| Attribut | Détail |
|----------|--------|
| **Constat** | `GET /draws`, `GET /grids/top`, `GET /grids/favorites` retournent toutes les lignes |
| **Risque** | Performance dégradée avec la croissance des données |
| **Recommandation** | Ajouter `?page=1&per_page=50` avec réponse paginée |
| **Priorité** | P1 |
| **Classification** | Dette technique |

---

## 5. Dettes UX

### DUX-01 : Tooltips insuffisants

| Attribut | Détail |
|----------|--------|
| **Constat** | Le composant `InfoTooltip` existe mais est sous-utilisé |
| **Impact** | Utilisateur novice perdu devant les termes techniques |
| **Priorité** | P1 |
| **Classification** | Dette UX |
| **Réf.** | [13_Evolution_Tooltips_Aide_Contextuelle](./13_Evolution_Tooltips_Aide_Contextuelle.md) |

### DUX-02 : Pas de mode simplifié / expert

| Attribut | Détail |
|----------|--------|
| **Constat** | Interface unique, même densité d'information pour tous |
| **Impact** | Novices submergés, experts frustrés par le manque de détails |
| **Priorité** | P2 |
| **Classification** | Dette UX |
| **Réf.** | [07_Evolutions_UI_UX](./07_Evolutions_UI_UX.md) |

### DUX-03 : Empty states non guidants

| Attribut | Détail |
|----------|--------|
| **Constat** | Les pages sans données affichent des messages génériques |
| **Impact** | L'utilisateur ne sait pas quoi faire pour générer du contenu |
| **Priorité** | P1 |
| **Classification** | Dette UX |

### DUX-04 : Pas de feedback progressif sur les calculs longs

| Attribut | Détail |
|----------|--------|
| **Constat** | Génération de grilles / simulation affiche un spinner sans indication de progression |
| **Impact** | Utilisateur incertain si le système travaille ou a planté |
| **Priorité** | P2 |
| **Classification** | Dette UX |

---

## 6. Dettes documentaires

### DDOC-01 : Pas de documentation des profils de scoring

| Constat | Les 5 profils (equilibre, frequence, gaps, cooccurrence, balance) ne sont documentés nulle part pour l'utilisateur |
| Priorité | P1 |
| Classification | Dette documentaire |

### DDOC-02 : Pas de guide de contribution

| Constat | Aucun CONTRIBUTING.md, pas de guide de style code |
| Priorité | P3 |
| Classification | Dette documentaire |

### DDOC-03 : Documentation existante partiellement obsolète

| Constat | Les docs 01→18 dans `docs/` datent de la phase initiale et n'intègrent pas les évolutions récentes (timezone, favoris, played) |
| Priorité | P3 |
| Classification | Dette documentaire |

---

## 7. Écarts fonctionnels (existant vs cible)

| Fonctionnalité cible | Existant | Écart |
|----------------------|----------|-------|
| Système réduit / Wheeling | ❌ Absent | Chantier complet à créer |
| Mode budget intelligent | ❌ Absent | Chantier complet à créer |
| Comparateur de stratégies | ⚠️ Comparaison aléatoire seule | Manque comparaison inter-stratégies |
| Historique riche | ⚠️ Basique (favoris, played) | Manque : sauvegarde portefeuilles, sélections, systèmes réduits, relance |
| Explicabilité | ⚠️ Score breakdown existe | Manque : textes, panneaux, « pourquoi ce résultat » |
| Tooltips premium | ⚠️ InfoTooltip existe | Utilisé sur ~30 % des endroits pertinents |
| Espace pédagogique | ⚠️ HowItWorks + Glossary | Très basique, manque profondeur |
| Automatisation | ⚠️ Scheduler nightly | Pas de suggestions utilisateur, pas d'alertes, pas de récurrence personnalisée |
| Mode simplifié / expert | ❌ Absent | Interface unique pour tous |
| Calibration algorithmique | ❌ Non formalisée | Poids et seuils codés en dur |

---

## 8. Matrice de risques de l'existant

| Risque | Probabilité | Impact | Action |
|--------|-------------|--------|--------|
| Données EuroMillions corrompues (BUG-01) | Certaine | Critique | Corriger avant toute évolution |
| Profil scoring inopérant (BUG-03) | Certaine | Majeur | Corriger immédiatement |
| Perte token blacklist au redémarrage (DT-02) | Haute | Modéré | Migrer vers DB/Redis en phase A |
| Réponses API volumineuses (DT-05) | Croissante | Modéré | Pagination en phase A |
| Utilisateurs perdus (DUX-01, DUX-03) | Haute | Fort | Tooltips + empty states en phase A |

---

## 9. Recommandations

### Immédiates (avant toute évolution)
1. **Corriger BUG-01** — Multi-loterie fonctionnel
2. **Corriger BUG-02** — Method selector opérationnel
3. **Corriger BUG-03** — Profil de scoring transmis

### Phase A (quick wins, fondation)
4. Pagination des endpoints de liste (DT-05)
5. Rate limiting granulaire (DT-04)
6. Tooltips sur les 70 % restants (DUX-01)
7. Empty states guidants (DUX-03)

### Phase B (stabilisation)
8. Cache statistiques (DT-03)
9. Token blacklist persistant (DT-02)
10. Mode simplifié / expert (DUX-02)

---

## 10. Checklist locale

- [ ] Corriger BUG-01 : multi-loterie — résolution game_id dans service layer
- [ ] Écrire tests E2E multi-loterie (Loto + EuroMillions minimum)
- [ ] Corriger BUG-02 : method_selector retourne le bon algorithme
- [ ] Écrire tests unitaires method_selector avec n_grids variable
- [ ] Corriger BUG-03 : transmettre profile du sélecteur au payload API
- [ ] Écrire test E2E génération avec profil « frequence »
- [ ] Ajouter pagination sur GET /draws, GET /grids/top, GET /grids/favorites
- [ ] Ajouter rate limiting sur /grids/generate, /simulations/*, /portfolios/generate
- [ ] Documenter politique de versioning API v1

Réf. : [27_Checklist_Globale_Evolutions](./27_Checklist_Globale_Evolutions.md)
