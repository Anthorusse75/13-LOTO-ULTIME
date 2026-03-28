# 13. Trajectoire Produit

Ce chapitre dessine la **feuille de route concrète** du projet LOTO ULTIME, organisée en phases de développement qui s'enchaînent logiquement. Chaque phase a un objectif clair, un livrable identifiable, et un critère de succès mesurable.

---

## 13.1 Vision produit revisitée

### Le décalage actuel entre promesse et réalité

LOTO ULTIME se positionne comme un **outil d'analyse combinatoire de pointe pour les loteries**, combinant statistiques avancées, scoring intelligent et optimisation de portefeuille. C'est une promesse ambitieuse et pertinente.

**Ce qui est tenu** :
- ✅ Architecture cohérente et moderne (FastAPI + React + TypeScript)
- ✅ Pipeline de calcul complet (stats → scoring → optimisation → simulation)
- ✅ 20 moteurs algorithmiques interconnectés
- ✅ Système d'authentification avec RBAC
- ✅ Scheduler automatisé pour les mises à jour quotidiennes
- ✅ Interface graphique avec visualisations D3/Recharts

**Ce qui n'est pas encore tenu** :
- ❌ Support multi-loteries réel (EuroMillions cassé)
- ❌ Aide contextuelle pour comprendre les données
- ❌ Profils de jeu fonctionnels
- ❌ Dashboard de synthèse
- ❌ Suivi de performance dans le temps
- ❌ Qualité produit « finie » (tooltips, messages, accessibilité)

### Repositionnement recommandé

Plutôt que d'ajouter de nouvelles fonctionnalités, la priorité est de **consolider ce qui existe** pour que chaque fonctionnalité annoncée soit réellement opérationnelle, fiable et compréhensible.

L'objectif de la trajectoire : passer de **« prototype avancé fonctionnel »** à **« produit analytique de qualité pour passionné de loterie »**.

---

## 13.2 Phase 10 — Corrections critiques et stabilisation

**Durée estimée** : 2 semaines
**Objectif** : Corriger tout ce qui est cassé ou trompeur.

### Sprint 10.1 — Fondations (3-4 jours)

| Action | Livrable | Critère de succès |
|--------|----------|-------------------|
| Corriger `_get_game_config()` | Filtrage par `game_id` | Tests multi-loteries passants |
| Intégrer Alembic | Migration initiale + config | `alembic upgrade head` fonctionne |
| Activer PRAGMA FK | Config SQLAlchemy event | Tests d'intégrité FK passants |
| Corriger `count()` | `SELECT COUNT(*)` partout | Benchmark : count() < 10ms |
| Corriger GraphEngine fallback | Valeurs uniformes au lieu de zéros | Test avec fréquences identiques |

### Sprint 10.2 — EuroMillions complet (5-7 jours)

| Action | Livrable | Critère de succès |
|--------|----------|-------------------|
| Intégrer les étoiles dans les 7 moteurs stats | Statistiques séparées numéros + étoiles | Tests statistiques étoiles |
| Intégrer les étoiles dans le scoring | Critères étoiles | Score composite numéros + étoiles |
| Intégrer les étoiles dans l'optimiseur | Grilles avec étoiles | Grilles 5+2 générées |
| Intégrer les étoiles dans la simulation | Simulation complète | Monte Carlo avec étoiles |
| Écrire 20+ tests multi-loteries | Suite de tests dédiée | Différences Loto/Euro détectées |

### Sprint 10.3 — UX minimale viable (2-3 jours)

| Action | Livrable | Critère de succès |
|--------|----------|-------------------|
| Câbler le sélecteur de profil | Profil → stratégie d'optimisation | Changement de profil change les grilles |
| Corriger `select_method()` | SA accessible | Option visible dans l'UI |
| Rate limiting endpoints calcul | slowapi sur /recompute, /generate, /run | Tests de rate limit passants |
| Supprimer code mort frontend | Composants inutilisés retirés | 0 import inutilisé |

**Critère de fin de phase** : EuroMillions produit des résultats différents du Loto, tous les tests passent, aucun composant UI trompeur.

---

## 13.3 Phase 11 — Qualité produit et expérience utilisateur

**Durée estimée** : 2-3 semaines
**Objectif** : Transformer le prototype en un produit que l'on a plaisir à utiliser.

### Sprint 11.1 — Compréhension (3-4 jours)

| Action | Livrable | Critère de succès |
|--------|----------|-------------------|
| Tooltips sur toutes les métriques statistiques | InfoTooltip component réutilisable | Chaque valeur a une explication |
| Tooltips sur les scores de grille | Explication de chaque critère de scoring | L'utilisateur comprend pourquoi une grille est recommandée |
| Légendes des graphiques enrichies | Labels explicites + descriptions | Aucun graphique n'est muet |
| Messages d'erreur user-friendly | Catalogue de messages en français | 0 message technique exposé à l'utilisateur |

### Sprint 11.2 — Polish visuel (2-3 jours)

| Action | Livrable | Critère de succès |
|--------|----------|-------------------|
| Couleurs CSS variables pour les graphiques | Theme-aware charts | Mode clair et sombre cohérents |
| États vides enrichis (CTA + guide) | Composant EmptyState réutilisable | Chaque page sans données guide l'utilisation |
| Confirmations avant actions destructives | Modal de confirmation | Aucune action irréversible sans confirmation |
| Feedback toast sur toutes les actions | Toast sur chaque mutation API | L'utilisateur sait toujours ce qui s'est passé |

### Sprint 11.3 — Robustesse opérationnelle (2-3 jours)

| Action | Livrable | Critère de succès |
|--------|----------|-------------------|
| Pipeline séquentiel (orchestrateur) | Job orchestrateur | Les étapes s'enchaînent au lieu de dépendre du timing |
| Nettoyage automatique des vieilles données | Job de cleanup | Grilles > 30 jours supprimées automatiquement |
| Backup automatique SQLite | Job hebdomadaire | Fichier .bak daté dans un dossier backup |
| Graceful shutdown | wait=True + timeout 30s | Jobs en cours finalisés proprement |

### Sprint 11.4 — Qualité algorithmique (2 jours)

| Action | Livrable | Critère de succès |
|--------|----------|-------------------|
| Temporal regression configurable (8+ fenêtres, R²) | Config `n_windows`, indicateur R² | Tendances significatives seulement |
| PatternPenalty plafonné | Max -0.3 | Pas de score négatif |
| Normalisation z-score en option | Choix min-max/z-score | Stabilité sur distributions plates |

**Critère de fin de phase** : L'utilisateur comprend chaque donnée affichée, l'interface est cohérente visuellement, le pipeline est robuste.

---

## 13.4 Phase 12 — Fonctionnalités analytiques avancées

**Durée estimée** : 3-4 semaines
**Objectif** : Enrichir l'expérience avec des fonctionnalités qui différencient le produit.

### Sprint 12.1 — Dashboard et synthèse (3-4 jours)

| Action | Livrable | Critère de succès |
|--------|----------|-------------------|
| Dashboard principal | Page d'accueil avec KPIs | Derniers tirages, top grilles, santé pipeline en un coup d'œil |
| Filtres temporels sur les statistiques | Sélecteur de période | Analyse sur 3 mois, 6 mois, 1 an, tout |
| Mode comparaison entre stratégies | Side-by-side grids | Deux stratégies visibles simultanément |

### Sprint 12.2 — Engagement utilisateur (3-4 jours)

| Action | Livrable | Critère de succès |
|--------|----------|-------------------|
| Historique de performance | Page suivi des résultats | Grilles jouées vs tirages réels |
| Système de favoris pour les grilles | Bookmark de grilles | Grilles favorites persistent |
| Export PDF des grilles et analyses | Bouton export PDF | PDF imprimable généré |

### Sprint 12.3 — Coach IA contextuel (5 jours)

| Action | Livrable | Critère de succès |
|--------|----------|-------------------|
| Assistant contextuel basique | Panel d'aide par page | Explications adaptées au contexte |
| Recommandations personnalisées | « Votre profil suggère... » | Suggestions basées sur l'historique |
| Guide interactif premier lancement | Onboarding tour | Nouvel utilisateur guidé pas à pas |

### Sprint 12.4 — Tests et qualité (3-4 jours)

| Action | Livrable | Critère de succès |
|--------|----------|-------------------|
| Tests E2E Playwright (parcours critiques) | 5-10 scénarios E2E | Login → stats → grilles → simulation |
| Tests unitaires frontend (composants clés) | Vitest + Testing Library | Couverture composants critiques |
| Tests de performance (benchmarks) | Fichier benchmarks | Temps de calcul sous seuil |

**Critère de fin de phase** : Le produit offre une expérience analytique complète avec dashboard, historique et aide contextuelle.

---

## 13.5 Phase 13 — Expansion et sophistication

**Durée estimée** : 4-6 semaines
**Objectif** : Élargir le périmètre et explorer des pistes avancées.

| Sprint | Contenu | Durée |
|--------|---------|-------|
| 13.1 | Support de loteries supplémentaires (Keno, etc.) | 5j |
| 13.2 | Backtesting historique avec rapport détaillé | 5j |
| 13.3 | Notifications temps réel (WebSocket) | 3j |
| 13.4 | Internationalisation (i18n français/anglais) | 3j |
| 13.5 | Conteneurisation Docker + CI/CD | 2j |
| 13.6 | API publique améliorée + documentation Swagger | 3j |
| 13.7 | Modèle ML de tendances (recherche) | 10j |
| 13.8 | Simulation multi-agent (recherche) | 5j |

---

## 13.6 Timeline visuelle

```
                    MOIS 1          MOIS 2          MOIS 3          MOIS 4-6
                ┌───────────┐   ┌───────────┐   ┌───────────┐   ┌───────────┐
 PHASE 10       │ ████████  │   │           │   │           │   │           │
 Corrections    │ Sem 1-2   │   │           │   │           │   │           │
                ├───────────┤   ├───────────┤   │           │   │           │
 PHASE 11       │           │   │ ████████  │   │ ██        │   │           │
 Qualité        │           │   │ Sem 3-5   │   │           │   │           │
                │           │   ├───────────┤   ├───────────┤   │           │
 PHASE 12       │           │   │           │   │ ████████  │   │ ██        │
 Analytique     │           │   │           │   │ Sem 6-9   │   │           │
                │           │   │           │   ├───────────┤   ├───────────┤
 PHASE 13       │           │   │           │   │           │   │ ████████  │
 Expansion      │           │   │           │   │           │   │ Sem 10+   │
                └───────────┘   └───────────┘   └───────────┘   └───────────┘
```

---

## 13.7 Jalons et métriques de suivi

| Jalon | Phase | Métrique de succès | Date cible |
|-------|-------|--------------------|------------|
| EuroMillions fonctionnel | 10 | Tests multi-loteries : 100% pass | Fin semaine 2 |
| Zéro bug critique | 10 | 0 item 🔴 dans la checklist | Fin semaine 2 |
| UX compréhensible | 11 | Tooltips sur 100% des métriques | Fin semaine 5 |
| Pipeline robuste | 11 | 0 incohérence temporelle sur 30 jours | Fin semaine 5 |
| Dashboard opérationnel | 12 | Page d'accueil avec KPIs | Fin semaine 7 |
| Coach IA v1 | 12 | Aide contextuelle sur 100% des pages | Fin semaine 9 |
| Multi-loteries étendu | 13 | 3+ loteries supportées | Mois 4 |
| Tests couverture | 12 | 80% backend + E2E critiques | Fin semaine 9 |

---

## 13.8 Principes directeurs

1. **Stabiliser avant d'innover** : Chaque phase ne démarre que quand la précédente est complète. Pas de nouvelles fonctionnalités tant que les bugs critiques existent.

2. **Valider par les tests** : Chaque correction importante a un test associé. Le nombre de tests doit croître à chaque phase.

3. **Mesurer l'impact** : Chaque modification algorithmique est benchmarkée (temps de calcul, qualité de scoring) avant et après.

4. **Documenter les décisions** : Les choix de design et d'algorithme sont documentés dans le code et dans les docs.

5. **Garder la simplicité** : SQLite, mono-utilisateur, déploiement local — tant que ce n'est pas un frein avéré, pas de migration prématurée.

---

## 13.9 Le produit cible à 6 mois

Si la trajectoire est suivie, LOTO ULTIME à 6 mois sera :

- **Un outil analytique complet** pour le Loto et l'EuroMillions, avec des statistiques correctement calculées pour chaque loterie, incluant les étoiles
- **Un produit compréhensible** où chaque donnée est expliquée, chaque action a un retour, et l'utilisateur est guidé
- **Un produit fiable** avec un pipeline automatisé sans faille, des données nettoyées, des migrations gérées, et des tests solides
- **Un produit engageant** avec un dashboard de synthèse, un historique de performance, et un assistant contextuel
- **Un produit extensible** capable d'intégrer de nouvelles loteries et de nouvelles méthodes analytiques sans refactoring majeur

C'est un objectif ambitieux mais réaliste, car l'architecture de base est saine et la dette technique identifiée est concentrée et remédiable.
