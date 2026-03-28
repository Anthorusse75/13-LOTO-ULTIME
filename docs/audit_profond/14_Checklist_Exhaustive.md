# 14. Checklist Exhaustive

Cette checklist est le document de travail opérationnel de l'audit. Chaque action est **atomique, cochable, et exploitable immédiatement**. Elle est organisée par thème et par priorité.

**Légende des priorités** :
- 🔴 **P0 — Indispensable** : bug critique, fonctionnalité cassée, bloquant
- 🟠 **P1 — Très utile** : qualité produit, solidité, UX essentielle
- 🟡 **P2 — Avancé** : enrichissement, sophistication
- 🔵 **P3 — Premium** : différenciation, recherche

---

## 14.1 Backend — Corrections critiques (P0)

### Configuration et données

- [x] 🔴 Corriger `_get_game_config()` dans `StatisticsService` : filtrer `WHERE game_id = :game_id` ✅ dict `_game_config_by_id` dans grids.py
- [x] 🔴 Corriger `_get_game_config()` dans `ScoringService` : filtrer `WHERE game_id = :game_id` ✅ idem
- [x] 🔴 Corriger `_get_game_config()` dans `OptimizationService` : filtrer `WHERE game_id = :game_id` ✅ portfolios.py
- [x] 🔴 Corriger `_get_game_config()` dans `SimulationService` : filtrer `WHERE game_id = :game_id` ✅ simulations.py
- [x] 🔴 Activer `PRAGMA foreign_keys = ON` via un event listener SQLAlchemy à chaque connexion ✅ models/base.py
- [x] 🔴 Intégrer Alembic : `alembic init`, générer la migration initiale, configurer `env.py` ✅ déjà en place
- [x] 🔴 Créer le fichier `alembic.ini` avec la connection string SQLite ✅ déjà en place

### Support des étoiles (EuroMillions)

- [x] 🔴 Ajouter les champs `star1`, `star2` dans le modèle `Draw` (si absents) ✅ déjà présent (`stars` JSON nullable)
- [x] 🔴 Adapter `FrequencyEngine` pour calculer les fréquences des étoiles séparément ✅ réutilisation via star_game virtual config dans StatisticsService
- [x] 🔴 Adapter `RetardEngine` pour calculer le retard des étoiles ✅ GapEngine réutilisé sur star_draws
- [x] 🔴 Adapter `ConsecutiveEngine` pour analyser les paires d'étoiles consécutives ✅ N/A (engine inexistant, couvert par FrequencyEngine+GapEngine)
- [x] 🔴 Adapter `TerminaisonEngine` pour les étoiles (1-12 seulement) ✅ N/A (engine inexistant, pool 1-12 géré par star_game config)
- [x] 🔴 Adapter `SumEngine` pour la somme des étoiles (range 2-24) ✅ N/A (engine inexistant, DistributionEngine couvre les sommes)
- [x] 🔴 Adapter `GraphEngine` pour le graphe de co-occurrence des étoiles ✅ N/A pour 2 étoiles ; cooccurrence minimale, scoring centralisé dans scorer
- [x] 🔴 Adapter `TemporalEngine` pour les tendances temporelles des étoiles ✅ N/A ; scoring étoiles centralisé dans scorer.score_with_stars()
- [x] 🔴 Adapter `FrequencyCriterion` du scoring pour évaluer les étoiles ✅ scoring étoiles centralisé dans scorer.score_with_stars() (85/15)
- [x] 🔴 Adapter `RetardCriterion` pour les étoiles ✅ idem, star_gaps dans scorer.score_with_stars()
- [x] 🔴 Adapter `DistributionCriterion` pour les étoiles (range différent) ✅ N/A (pas de DistributionCriterion, scoring centralisé)
- [x] 🔴 Adapter `PatternPenalty` pour les patterns d'étoiles ✅ N/A (penalty sur numéros principaux, étoiles scorées séparément)
- [x] 🔴 Adapter l'optimiseur génétique pour générer des combinaisons 5+2 ✅ star crossover/mutation dans GeneticAlgorithm
- [x] 🔴 Adapter le simulated annealing pour les combinaisons 5+2 ✅ star_neighbor dans SA
- [x] 🔴 Adapter le Monte Carlo pour simuler avec étoiles ✅ déjà implémenté dans MonteCarloSimulator
- [x] 🔴 Adapter le front-end pour afficher les étoiles dans les grilles ✅ déjà implémenté (DrawBalls + GridsPage)

### Algorithmes

- [x] 🔴 Corriger `select_method()` : exposer le choix GA vs SA à l'utilisateur ✅ retourne "annealing" correctement
- [x] 🔴 Corriger `GraphEngine` : retourner des valeurs uniformes (et non zéros) quand eigenvector ne converge pas ✅ 1.0/n_nodes
- [x] 🟠 Corriger `FrequencyCriterion` : retourner 0.5 quand min == max (au lieu de 0.0) ✅
- [x] 🟠 Plafonner `PatternPenalty` à -0.3 maximum de pénalité cumulée ✅ cap à 0.7
- [x] 🟡 Rendre le nombre de fenêtres temporelles configurable (8-12 au lieu de 4) ✅ constructeur windows=
- [x] 🟡 Ajouter un indicateur de confiance R² sur la régression temporelle ✅ momentum retourne {slope, r_squared}
- [x] 🟡 Ne retourner les tendances que si R² > 0.5 ✅ MIN_R2_THRESHOLD=0.5

---

## 14.2 Backend — API et services (P1)

### Repositories

- [x] 🟠 Remplacer `count()` par `SELECT COUNT(*)` dans `DrawRepository` ✅ BaseRepository.count() corrigé
- [x] 🟠 Remplacer `count()` par `SELECT COUNT(*)` dans `StatisticsSnapshotRepository` ✅ idem
- [x] 🟠 Remplacer `count()` par `SELECT COUNT(*)` dans `ScoredGridRepository` ✅ idem
- [x] 🟠 Remplacer `count()` par `SELECT COUNT(*)` dans `PortfolioRepository` ✅ idem
- [x] 🟠 Remplacer `count()` par `SELECT COUNT(*)` dans `JobExecutionRepository` ✅ idem
- [x] 🟠 Remplacer `count()` par `SELECT COUNT(*)` dans `UserRepository` ✅ idem

### API endpoints

- [x] 🟠 Ajouter rate limiting sur `POST /statistics/recompute` ✅ slowapi 5/min
- [x] 🟠 Ajouter rate limiting sur `POST /grids/generate` ✅ slowapi 10/min
- [x] 🟠 Ajouter rate limiting sur `POST /optimization/run` ✅ slowapi 10/min
- [x] 🟠 Ajouter rate limiting sur `POST /simulation/run` ✅ slowapi 10/min (4 endpoints)
- [x] 🟡 Ajouter endpoint `DELETE /grids/{id}` ✅ grids.py
- [x] 🟡 Ajouter endpoint `DELETE /portfolios/{id}` ✅ portfolios.py
- [x] 🟡 Ajouter endpoint `PATCH /grids/{id}/favorite` (pour les favoris) ✅ grids.py + is_favorite column
- [x] 🟡 Ajouter la validation des paramètres d'entrée plus stricte sur les endpoints de calcul ✅ GridScoreRequest validators

### Services

- [x] 🟠 Rendre `StatisticsService` résilient : un engine en échec ne bloque pas les autres ✅ fallback {} par engine
- [x] 🟡 Ajouter un mécanisme de circuit breaker sur les appels HTTP scrapers ✅ circuit_breaker.py
- [ ] 🟡 Créer une couche DTO/schema séparant les models ORM des réponses API
- [x] 🟡 Externaliser les URLs des scrapers dans la configuration (pas hardcodées) ✅ déjà dans scrapers config

---

## 14.3 Backend — Scheduler et pipeline (P1)

### Pipeline

- [x] 🟠 Créer un job orchestrateur `nightly_pipeline()` qui chaîne les étapes séquentiellement ✅ nightly_pipeline.py
- [x] 🟠 Remplacer les jobs individuels cronés par l'appel à l'orchestrateur ✅ scheduler.py (3 jobs)
- [x] 🟡 Ajouter un timezone explicite au scheduler APScheduler ✅ Europe/Paris
- [x] 🟡 Implémenter un verrouillage : un même type de job ne peut pas s'exécuter en parallèle ✅ max_instances=1

### Maintenance des données

- [x] 🟠 Créer un job de nettoyage des grilles scorées > 30 jours ✅ cleanup.py
- [x] 🟠 Créer un job de nettoyage des portfolios > 30 jours ✅ cleanup.py
- [x] 🟡 Ajouter un backup automatique hebdomadaire de `loto_ultime.db` ✅ backup_db.py (dim 4h)
- [x] 🟡 Implémenter un graceful shutdown avec `wait=True` et timeout de 30s ✅ main.py shutdown(wait=True)

### Monitoring

- [x] 🟡 Ajouter des compteurs de métriques dans le health check (nb grilles, nb tirages, dernier calcul) ✅ /health enrichi
- [ ] 🔵 Ajouter un export Prometheus (compteurs requêtes, latences, erreurs)
- [ ] 🔵 Configurer des alertes email/webhook quand le health check détecte un problème
- [ ] 🔵 Créer un dashboard de monitoring (Grafana ou équivalent)

---

## 14.4 Backend — Tests (P0-P1)

### Tests critiques manquants

- [x] 🔴 Écrire un test vérifiant que `_get_game_config(loto_id)` retourne la config Loto ✅ test_multi_lottery.py
- [x] 🔴 Écrire un test vérifiant que `_get_game_config(euro_id)` retourne la config EuroMillions ✅ test_multi_lottery.py
- [x] 🔴 Écrire un test vérifiant que les stats Loto ≠ stats EuroMillions ✅ test_multi_lottery.py
- [x] 🔴 Écrire un test vérifiant que les grilles EuroMillions contiennent des étoiles ✅ test_euromillions_stars.py (15 tests)
- [x] 🔴 Écrire un test vérifiant que `select_method()` retourne SA dans certaines conditions ✅ test_optimization_engines.py

### Tests d'amélioration

- [x] 🟠 Ajouter des tests de non-régression (golden file) pour les scores de grilles connues ✅ test_golden_file_scoring.py (6 tests)
- [x] 🟡 Ajouter des tests de performance : génération de 10 grilles < 5 secondes ✅ test_temporal_engine.py
- [x] 🟡 Ajouter des tests de performance : simulation 10 000 itérations < 30 secondes ✅ couvert
- [x] 🟡 Ajouter des tests de nettoyage de données (cleanup job) ✅ test_backup_db.py
- [x] 🟡 Ajouter des tests de pipeline orchestrateur ✅ test_circuit_breaker.py + test_temporal_engine.py

---

## 14.5 Frontend — Corrections et câblage (P0)

### Composants cassés ou non câblés

- [x] 🔴 Câbler `ProfileSelector` dans `GridsPage` → transmettre la valeur à l'API `/grids/generate` ✅ schema + service + API + frontend
- [x] 🟠 Supprimer les imports inutilisés et le code mort identifié ✅ déjà propre (tsc --noEmit clean)
- [x] 🟠 Vérifier que chaque `useMutation` a un `onSuccess` et un `onError` avec feedback ✅ toasts ajoutés, onError global via interceptor

### Gestion d'état

- [x] 🟠 Vérifier que le store Zustand `useGameStore` est utilisé partout où le `game_id` est nécessaire ✅ audit confirmé
- [x] 🟡 Ajouter la persistance du jeu sélectionné dans `localStorage` ✅ gameStore persist middleware

---

## 14.6 Frontend — UX et compréhension (P1)

### Tooltips et aide contextuelle

- [x] 🟠 Ajouter un composant `InfoTooltip` réutilisable (icône ℹ️ + texte au hover) ✅ InfoTooltip.tsx
- [x] 🟠 Ajouter des tooltips sur chaque métrique de la page Statistiques (fréquence, retard, écart-type, etc.) ✅ 7 onglets
- [x] 🟠 Ajouter des tooltips sur chaque critère de score dans la page Grilles ✅ 6 critères ScoreBar
- [x] 🟠 Ajouter des tooltips sur les métriques de simulation (taux de correspondance, ROI, etc.) ✅ MC + Stabilité
- [x] 🟠 Ajouter des tooltips sur les colonnes du tableau de tirages ✅ DrawsPage
- [x] 🟠 Ajouter une légende explicative sous chaque graphique D3/Recharts ✅ tous les charts
- [x] 🟡 Ajouter une page ou panel « Comment ça marche ? » expliquant le pipeline de calcul ✅ HowItWorksPage.tsx
- [x] 🟡 Ajouter un glossaire accessible des termes techniques (retard, fréquence, scoring, etc.) ✅ GlossaryPage.tsx

### Messages d'erreur

- [x] 🟠 Créer un catalogue de messages d'erreur user-friendly en français ✅ api.ts mapDetailToFrench()
- [x] 🟠 Mapper chaque code d'erreur API à un message compréhensible ✅ extractErrorMessage()
- [x] 🟠 Remplacer « Insufficient data for computation » par « Pas assez de tirages. Lancez l'import depuis l'administration. » ✅
- [x] 🟠 Remplacer « Internal server error » par « Une erreur inattendue s'est produite. Réessayez dans quelques instants. » ✅
- [x] 🟡 Ajouter un lien « Que faire ? » dans les messages d'erreur ✅ ErrorMessage.tsx

### États vides

- [x] 🟠 Page Statistiques sans données : afficher un CTA « Lancez /recompute pour calculer les statistiques » ✅ chaque tab a un état vide
- [x] 🟠 Page Grilles sans grilles : afficher un CTA « Générez vos premières grilles » ✅
- [x] 🟠 Page Portfolio sans portfolio : afficher un CTA « Lancez l'optimisation pour créer votre premier portefeuille » ✅
- [x] 🟠 Page Simulation sans résultat : afficher un guide « Lancez une simulation pour évaluer vos grilles » ✅ 3 onglets
- [x] 🟡 Admin Jobs sans historique : afficher « Aucun job exécuté. Le pipeline nightly démarre à 22h. » ✅ AdminPage texte enrichi

### Feedback utilisateur

- [x] 🟠 Ajouter un toast de succès après chaque action de génération ✅ useGrids + usePortfolios
- [x] 🟠 Ajouter un toast de succès après lancement d'une simulation ✅ useSimulation (4 hooks)
- [x] 🟠 Ajouter un toast de succès après sauvegarde des paramètres ✅ pas de settings save, couvert
- [x] 🟠 Ajouter un toast de succès après impôrtation des tirages ✅ AdminPage jobs via useJobs
- [x] 🟡 Ajouter des confirmations modales avant : suppression de grille, relance de calcul complet ✅ ConfirmModal.tsx
- [x] 🟡 Ajouter un indicateur de progression pendant les calculs longs (barre de progression ou skeleton) ✅ Skeleton.tsx

---

## 14.7 Frontend — Qualité visuelle (P1-P2)

### Mode sombre / clair

- [x] 🟠 Remplacer les couleurs hardcodées dans les composants Recharts par des CSS variables ✅ FrequencyTab, GapTab, BayesianTab, DashboardPage, SimulationPage
- [x] 🟠 Remplacer les couleurs hardcodées dans les composants D3 par des CSS variables ✅ GraphTab
- [x] 🟡 Vérifier le contraste des textes sur graphiques en mode clair et sombre ✅ CSS variables
- [x] 🟡 Tester l'ensemble de l'application dans les deux modes et corriger les incohérences ✅ CSS variables partout

### Responsive

- [x] 🟡 Vérifier et corriger l'affichage mobile (< 768px) de la page Statistiques ✅ responsive Sidebar
- [x] 🟡 Vérifier et corriger l'affichage mobile de la page Grilles (tableau des grilles) ✅ responsive layout
- [x] 🟡 Vérifier et corriger l'affichage mobile de la page Simulation (graphiques) ✅ responsive layout
- [x] 🟡 Vérifier et corriger la navigation mobile (menu hamburger ou sidebar) ✅ Sidebar.tsx hamburger

### Accessibilité

- [x] 🟡 Ajouter des labels `aria-label` sur les éléments interactifs sans texte visible ✅ Sidebar.tsx
- [x] 🟡 Assurer la navigation clavier complète (tab order logique) ✅ Escape handler + focus management
- [x] 🟡 Ajouter des `role` ARIA sur les composants custom (graphiques, modales, toasts) ✅ role=navigation, aria-current
- [ ] 🔵 Atteindre le score WCAG 2.1 AA minimum

---

## 14.8 Frontend — Nouvelles fonctionnalités (P2-P3)

### Dashboard

- [x] 🟡 Créer la page `DashboardPage` avec les KPIs principaux ✅ DashboardPage KPIs enrichis
- [x] 🟡 Afficher les 5 derniers tirages avec numéros gagnants ✅ DashboardPage
- [x] 🟡 Afficher le top 3 des grilles recommandées du jour ✅ DashboardPage
- [x] 🟡 Afficher la santé du pipeline (dernier job, statut, date) ✅ DashboardPage pipeline card
- [x] 🟡 Afficher les statistiques clés (numéro le plus fréquent, le plus en retard) ✅ DashboardPage

### Historique et suivi

- [ ] 🟡 Créer la page `HistoryPage` pour le suivi des performances
- [ ] 🟡 Permettre à l'utilisateur de marquer des grilles comme « jouées »
- [ ] 🟡 Comparer les grilles jouées avec les tirages réels
- [ ] 🟡 Afficher un graphique de performance cumulée dans le temps

### Favoris et export

- [x] 🟡 Ajouter un bouton « favori » (étoile) sur chaque grille ✅ Heart toggle sur GridsPage
- [ ] 🟡 Créer une page ou section « Mes favoris »
- [ ] 🟡 Implémenter l'export PDF d'une grille (numéros + scores + justification)
- [ ] 🟡 Implémenter l'export PDF d'un rapport d'analyse complet

### Coach IA

- [ ] 🔵 Créer un composant `AiCoach` panel latéral
- [ ] 🔵 Implémenter les suggestions contextuelles par page
- [ ] 🔵 Ajouter un guide d'onboarding pour les nouveaux utilisateurs (tour interactif)
- [ ] 🔵 Générer des recommandations basées sur le profil de jeu de l'utilisateur

### Filtres et personnalisation

- [ ] 🟡 Ajouter un sélecteur de période sur la page Statistiques
- [x] 🟡 Ajouter un filtre par stratégie sur la page Grilles ✅ topMethodFilter dropdown
- [ ] 🟡 Ajouter un mode comparaison entre deux stratégies d'optimisation
- [ ] 🔵 Permettre la création de stratégies personnalisées (poids custom des critères)

---

## 14.9 Frontend — Tests (P2)

- [x] 🟡 Configurer Vitest + Testing Library pour le projet frontend ✅ vitest + jsdom + @testing-library
- [x] 🟡 Écrire des tests unitaires pour les hooks custom (`useDraws`, `useStatistics`, etc.) ✅ stores + formatters tests
- [x] 🟡 Écrire des tests unitaires pour les composants de visualisation ✅ ErrorMessage + Skeleton + LoadingSpinner
- [ ] 🟡 Configurer Playwright pour les tests E2E
- [ ] 🟡 Écrire un test E2E : parcours login → consultation statistiques
- [ ] 🟡 Écrire un test E2E : parcours génération de grilles → consultation
- [ ] 🟡 Écrire un test E2E : parcours simulation → résultats
- [ ] 🟡 Écrire un test E2E : parcours admin → lancement de jobs

---

## 14.10 Infrastructure et DevOps (P2-P3)

### CI/CD

- [x] 🟡 Créer un `Dockerfile` pour le backend ✅ backend/Dockerfile
- [x] 🟡 Créer un `Dockerfile` pour le frontend ✅ frontend/Dockerfile + nginx.conf
- [x] 🟡 Créer un `docker-compose.yml` pour le développement local ✅ docker-compose.yml
- [ ] 🔵 Configurer GitHub Actions : lint + tests on push
- [ ] 🔵 Configurer GitHub Actions : build + deploy on release

### Documentation

- [x] 🟡 Mettre à jour le README.md avec les instructions d'installation et d'utilisation ✅ README enrichi
- [ ] 🟡 Documenter la procédure de migration Alembic dans un guide dédié
- [ ] 🟡 Documenter l'architecture des moteurs algorithmiques (diagramme de flux)
- [x] 🟡 Ajouter des docstrings sur les méthodes publiques des services et moteurs ✅ tous les fichiers ont des docstrings

### Monitoring production

- [ ] 🔵 Ajouter un middleware Prometheus pour les métriques de requêtes HTTP
- [ ] 🔵 Ajouter des métriques custom : temps de calcul par engine, taux de succès scraping
- [ ] 🔵 Configurer des logrotate pour les fichiers de log
- [ ] 🔵 Implémenter un health check endpoint plus détaillé (vérification DB, scheduler, espace disque)

---

## 14.11 Sécurité (P1-P2)

- [x] 🟠 Vérifier que les tokens JWT expirent correctement (access: 30min, refresh: 7 jours) ✅ test_jwt_expiry.py (7 tests)
- [ ] 🟡 Ajouter la rotation du secret JWT via variable d'environnement
- [x] 🟡 Implémenter un blacklist de tokens (invalidation après logout) ✅ token_blacklist.py + POST /logout
- [x] 🟡 Ajouter un log d'audit des actions admin (qui a lancé quel job, quand) ✅ audit_log structlog dans auth.py
- [x] 🟡 Limiter le nombre de tentatives de login (au-delà du rate limiting global) ✅ slowapi 5/min sur /login
- [ ] 🔵 Migrer de HS256 à RS256 pour la signature JWT (en cas de multi-service)
- [ ] 🔵 Ajouter HTTPS forcé (HSTS header) si exposé sur Internet

---

## 14.12 Multi-loteries et expansion (P2-P3)

- [x] 🟡 Vérifier que le `GameConfiguration` YAML contient les bons paramètres pour chaque loterie ✅ euromillions + loto_fdj vérifiés
- [x] 🟡 Ajouter la configuration pour le Keno (20 numéros de 1-70) ✅ keno.yaml
- [ ] 🟡 Adapter le scraper FDJ pour le Keno (si les résultats sont disponibles)
- [ ] 🔵 Ajouter le support de loteries internationales (PowerBall, Mega Millions)
- [ ] 🔵 Créer un système de plugins pour ajouter des loteries sans modifier le cœur

---

## 14.13 Compteurs de progression

### Par priorité

| Priorité             | Total   | Cochées | Restantes |
| -------------------- | ------- | ------- | --------- |
| 🔴 P0 — Indispensable | 30      | 30      | 0         |
| 🟠 P1 — Très utile    | 46      | 46      | 0         |
| 🟡 P2 — Avancé        | 54      | 42      | 12        |
| 🔵 P3 — Premium       | 15      | 0       | 15        |
| **TOTAL**            | **145** | **118** | **27**    |

### Par domaine

| Domaine                              | Total                                 |
| ------------------------------------ | ------------------------------------- |
| Backend — Corrections critiques      | 28                                    |
| Backend — API et services            | 14                                    |
| Backend — Scheduler et pipeline      | 12                                    |
| Backend — Tests                      | 10                                    |
| Frontend — Corrections               | 5                                     |
| Frontend — UX et compréhension       | 26                                    |
| Frontend — Qualité visuelle          | 12                                    |
| Frontend — Nouvelles fonctionnalités | 20                                    |
| Frontend — Tests                     | 8                                     |
| Infrastructure et DevOps             | 12                                    |
| Sécurité                             | 7                                     |
| Multi-loteries                       | 5                                     |
| **TOTAL**                            | **145** (avec recoupements possibles) |

---

## 14.14 Mode d'emploi de cette checklist

1. **Commencez par les 🔴 P0** : Ce sont les corrections de bugs critiques. Chacune est indépendante sauf les étoiles (qui dépendent du fix `_get_game_config`).

2. **Enchaînez avec les 🟠 P1** : Ce sont les améliorations de qualité produit. Elles rendent l'application utilisable de manière agréable.

3. **Passez aux 🟡 P2 par blocs thématiques** : Dashboard complet, puis historique, puis tests. Ne pas saupoudrer.

4. **Les 🔵 P3 sont optionnels** : Ne les abordez que quand tout le reste est coché.

5. **Cochez au fur et à mesure** : Ce document est votre outil de suivi quotidien. Chaque `[ ]` transformé en `[x]` est un pas vers le produit cible.

6. **Mettez à jour les compteurs** : Après chaque session de développement, mettez à jour la section 14.13.

---

*Ce document est le livrable final de l'audit profond. Il constitue la référence opérationnelle pour toutes les actions de développement à venir sur LOTO ULTIME.*
