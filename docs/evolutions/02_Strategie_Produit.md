# 02 — Stratégie Produit

> Positionnement, segmentation utilisateur, différenciation, et logique produit guidant les choix d'évolution.

---

## Références croisées

- [00_Index_Evolutions](./00_Index_Evolutions.md)
- [01_Vision_Evolutions](./01_Vision_Evolutions.md) — Vision & principes
- [03_Audit_Existant_et_Ecarts](./03_Audit_Existant_et_Ecarts.md) — Écarts identifiés
- [04_Priorisation_Evolutions](./04_Priorisation_Evolutions.md) — Hiérarchisation
- [07_Evolutions_UI_UX](./07_Evolutions_UI_UX.md) — Design & modes
- [26_Roadmap_Evolutions](./26_Roadmap_Evolutions.md) — Planning

---

## 1. Objectif du document

Définir la **stratégie produit** qui gouverne les choix d'évolution : pour qui construit-on, quel est le positionnement, qu'est-ce qui nous différencie, et comment organiser les fonctionnalités par valeur.

---

## 2. Positionnement

### 2.1 — Formule de positionnement

> LOTO ULTIME est une **plateforme d'aide à la décision combinatoire** pour les joueurs de loteries qui souhaitent **comprendre, optimiser et maîtriser** leur approche du jeu — sans promesse de gain, avec transparence totale.

### 2.2 — Marché

- **Cible primaire** : Joueurs réguliers de loteries francophones (Loto FDJ, EuroMillions) cherchant un outil sérieux et structuré.
- **Cible secondaire** : Curieux mathématiques / passionnés de combinatoire souhaitant explorer les statistiques de loteries.
- **Cible tertiaire** : Développeurs / analystes souhaitant comprendre la modélisation combinatoire.

### 2.3 — Compétiteurs et différenciation

| Compétiteur type | Limite | Notre différence |
|------------------|--------|-------------------|
| Sites de statistiques FDJ | Données brutes sans analyse | 7 moteurs statistiques + scoring multi-critères |
| Générateurs aléatoires | Aucune intelligence | 5 algorithmes d'optimisation + profils |
| Apps de « prédiction » | Fausses promesses | Honnêteté scientifique + explicabilité |
| Feuilles Excel manuelles | Fastidieux, limité | Automatisation + UX + covering design |

---

## 3. Segmentation utilisateur

### 3.1 — Personas

**Persona A — Le joueur régulier (70 %)**
- Joue 1 à 3 fois par semaine
- Budget : 5–20 € par tirage
- Besoin : « Quels numéros jouer ? Comment optimiser mes chances ? »
- Niveau technique : Faible
- Attente UX : Simplicité, guidage, résultats clairs

**Persona B — Le joueur analytique (20 %)**
- Joue régulièrement avec méthode
- Budget : 10–50 € par tirage
- Besoin : « Je veux comprendre les stats et construire ma propre stratégie »
- Niveau technique : Moyen
- Attente UX : Profondeur, personnalisation, exports

**Persona C — Le passionné combinatoire (10 %)**
- Intéressé par les maths plus que par le jeu lui-même
- Budget jeu : Variable
- Besoin : « Je veux explorer tous les paramètres et comprendre chaque algorithme »
- Niveau technique : Élevé
- Attente UX : Mode expert, détails complets, documentation technique

### 3.2 — Implications sur les évolutions

| Persona | Fonctionnalités prioritaires | Mode UX |
|---------|------------------------------|---------|
| A | Wheeling simplifié, budget intelligent, tooltips, pédagogie | Mode simplifié |
| B | Comparateur, historique complet, explicabilité, profils avancés | Mode standard |
| C | Paramétrage fin, algorithmes avancés, exports, documentation | Mode expert |

---

## 4. Pyramide de valeur fonctionnelle

```
                    ┌─────────────────┐
                    │  DIFFÉRENCIATION │  Wheeling / Covering Design
                    │      FORTE       │  Mode Budget Intelligent
                    ├─────────────────┤
                    │    PREMIUM       │  Comparateur de stratégies
                    │                  │  Automatisation & alertes
                    ├─────────────────┤
                    │  FONCTIONNEL     │  Historique / Favoris avancé
                    │    CŒUR          │  Explicabilité
                    │                  │  Améliorations algorithmiques
                    ├─────────────────┤
                    │   FONDATION      │  Tooltips & aide contextuelle
                    │                  │  UI/UX profonde
                    │                  │  Espace pédagogique
                    └─────────────────┘
```

**Logique** : On construit les fondations (phase A–B), puis le cœur fonctionnel (phase B–C), puis la valeur premium et différenciation (phase C–E).

---

## 5. Stratégie de monétisation (perspective)

Ce document ne traite pas de monétisation active, mais pose les bases pour un futur modèle :

| Tier | Accès | Fonctionnalités |
|------|-------|-----------------|
| **Gratuit** | Consultation statistiques, top 10, tirages, pédagogie | Lecture seule |
| **Standard** | Génération de grilles, scoring, favoris, historique | Utilisation active |
| **Premium** | Wheeling, budget intelligent, comparateur, automatisation | Aide à la décision complète |

> Cette segmentation est indicative et ne sera pas implémentée dans les phases A–C. Elle guide simplement l'architecture (RBAC, features conditionnelles).

---

## 6. Engagement éthique

### 6.1 — Pas de dark patterns

- Pas de compteurs urgence (« plus que 2 h avant le tirage ! »)
- Pas de faux indicateurs de performance (« 85 % de réussite »)
- Pas de notifications push agressives
- Pas de gamification incitant à la surenchère

### 6.2 — Vocabulaire contraint

| ❌ Interdit | ✅ Autorisé |
|-------------|-------------|
| « Gagnez plus » | « Optimisez votre couverture combinatoire » |
| « Numéros chanceux » | « Numéros fréquents dans l'historique » |
| « Prédiction » | « Analyse statistique » |
| « Garantie » | « Scénario théorique conditionnel » |
| « Chance augmentée » | « Couverture de sous-combinaisons améliorée » |

### 6.3 — Mention légale

Chaque page générant des grilles ou systèmes doit afficher :

> « Ce système est un outil d'aide à la décision basé sur l'analyse combinatoire. Les résultats d'une loterie sont aléatoires et aucun système ne peut garantir un gain. Jouez de manière responsable. »

---

## 7. Indicateurs produit (KPI cibles)

| KPI | Baseline actuel | Cible post-évolutions |
|-----|-----------------|----------------------|
| Pages par session | ~3 | 5–7 |
| Taux de rétention J+7 | Non mesuré | ≥ 30 % |
| Grilles générées / session | ~1 | 2–5 |
| Usage wheeling / session (post-launch) | 0 | ≥ 20 % des sessions |
| Temps avant première grille | Non mesuré | < 2 min |
| Taux d'erreur API | < 1 % | < 0.5 % |

---

## 8. Risques produit

| Risque | Probabilité | Impact | Mitigation |
|--------|-------------|--------|------------|
| Complexité perçue trop élevée | Moyenne | Fort | Mode simplifié, pédagogie, onboarding |
| Mauvaise interprétation (« outil de prédiction ») | Haute | Critique | Vocabulaire contraint, disclaimers, éducation |
| Surcharge calcul (wheeling grands ensembles) | Moyenne | Moyen | Bornes, timeouts, feedback progressif |
| Manque d'engagement (pas de raison de revenir) | Moyenne | Fort | Automatisation, suggestions récurrentes, historique |

---

## 9. Critères d'acceptation

| Critère | Mesure |
|---------|--------|
| 3 personas documentés et pris en compte | Ce document |
| Mode simplifié / expert défini | [07_Evolutions_UI_UX](./07_Evolutions_UI_UX.md) |
| Vocabulaire contraint formalisé | Section 6.2 ci-dessus |
| Pyramide de valeur utilisée pour prioriser | [04_Priorisation_Evolutions](./04_Priorisation_Evolutions.md) |
| Disclaimers intégrés dans les maquettes | Vérification frontend |

---

## 10. Checklist locale

- [ ] Valider les 3 personas avec feedback utilisateur réel
- [ ] Intégrer la mention légale sur les pages concernées (Grilles, Portfolio, Wheeling, Budget)
- [ ] Documenter le vocabulaire contraint dans le guide de contribution
- [ ] Configurer les KPI produit dans l'observabilité (Grafana)
- [ ] Vérifier l'absence de dark patterns sur chaque nouvelle page

Réf. : [27_Checklist_Globale_Evolutions](./27_Checklist_Globale_Evolutions.md)
