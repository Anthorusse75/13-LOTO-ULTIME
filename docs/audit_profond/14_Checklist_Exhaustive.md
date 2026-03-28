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

- [ ] 🔴 Corriger `_get_game_config()` dans `StatisticsService` : filtrer `WHERE game_id = :game_id`
- [ ] 🔴 Corriger `_get_game_config()` dans `ScoringService` : filtrer `WHERE game_id = :game_id`
- [ ] 🔴 Corriger `_get_game_config()` dans `OptimizationService` : filtrer `WHERE game_id = :game_id`
- [ ] 🔴 Corriger `_get_game_config()` dans `SimulationService` : filtrer `WHERE game_id = :game_id`
- [ ] 🔴 Activer `PRAGMA foreign_keys = ON` via un event listener SQLAlchemy à chaque connexion
- [ ] 🔴 Intégrer Alembic : `alembic init`, générer la migration initiale, configurer `env.py`
- [ ] 🔴 Créer le fichier `alembic.ini` avec la connection string SQLite

### Support des étoiles (EuroMillions)

- [ ] 🔴 Ajouter les champs `star1`, `star2` dans le modèle `Draw` (si absents)
- [ ] 🔴 Adapter `FrequencyEngine` pour calculer les fréquences des étoiles séparément
- [ ] 🔴 Adapter `RetardEngine` pour calculer le retard des étoiles
- [ ] 🔴 Adapter `ConsecutiveEngine` pour analyser les paires d'étoiles consécutives
- [ ] 🔴 Adapter `TerminaisonEngine` pour les étoiles (1-12 seulement)
- [ ] 🔴 Adapter `SumEngine` pour la somme des étoiles (range 2-24)
- [ ] 🔴 Adapter `GraphEngine` pour le graphe de co-occurrence des étoiles
- [ ] 🔴 Adapter `TemporalEngine` pour les tendances temporelles des étoiles
- [ ] 🔴 Adapter `FrequencyCriterion` du scoring pour évaluer les étoiles
- [ ] 🔴 Adapter `RetardCriterion` pour les étoiles
- [ ] 🔴 Adapter `DistributionCriterion` pour les étoiles (range différent)
- [ ] 🔴 Adapter `PatternPenalty` pour les patterns d'étoiles
- [ ] 🔴 Adapter l'optimiseur génétique pour générer des combinaisons 5+2
- [ ] 🔴 Adapter le simulated annealing pour les combinaisons 5+2
- [ ] 🔴 Adapter le Monte Carlo pour simuler avec étoiles
- [ ] 🔴 Adapter le front-end pour afficher les étoiles dans les grilles

### Algorithmes

- [ ] 🔴 Corriger `select_method()` : exposer le choix GA vs SA à l'utilisateur
- [ ] 🔴 Corriger `GraphEngine` : retourner des valeurs uniformes (et non zéros) quand eigenvector ne converge pas
- [ ] 🟠 Corriger `FrequencyCriterion` : retourner 0.5 quand min == max (au lieu de 0.0)
- [ ] 🟠 Plafonner `PatternPenalty` à -0.3 maximum de pénalité cumulée
- [ ] 🟡 Rendre le nombre de fenêtres temporelles configurable (8-12 au lieu de 4)
- [ ] 🟡 Ajouter un indicateur de confiance R² sur la régression temporelle
- [ ] 🟡 Ne retourner les tendances que si R² > 0.5

---

## 14.2 Backend — API et services (P1)

### Repositories

- [ ] 🟠 Remplacer `count()` par `SELECT COUNT(*)` dans `DrawRepository`
- [ ] 🟠 Remplacer `count()` par `SELECT COUNT(*)` dans `StatisticsSnapshotRepository`
- [ ] 🟠 Remplacer `count()` par `SELECT COUNT(*)` dans `ScoredGridRepository`
- [ ] 🟠 Remplacer `count()` par `SELECT COUNT(*)` dans `PortfolioRepository`
- [ ] 🟠 Remplacer `count()` par `SELECT COUNT(*)` dans `JobExecutionRepository`
- [ ] 🟠 Remplacer `count()` par `SELECT COUNT(*)` dans `UserRepository`

### API endpoints

- [ ] 🟠 Ajouter rate limiting sur `POST /statistics/recompute`
- [ ] 🟠 Ajouter rate limiting sur `POST /grids/generate`
- [ ] 🟠 Ajouter rate limiting sur `POST /optimization/run`
- [ ] 🟠 Ajouter rate limiting sur `POST /simulation/run`
- [ ] 🟡 Ajouter endpoint `DELETE /grids/{id}`
- [ ] 🟡 Ajouter endpoint `DELETE /portfolios/{id}`
- [ ] 🟡 Ajouter endpoint `PATCH /grids/{id}/favorite` (pour les favoris)
- [ ] 🟡 Ajouter la validation des paramètres d'entrée plus stricte sur les endpoints de calcul

### Services

- [ ] 🟠 Rendre `StatisticsService` résilient : un engine en échec ne bloque pas les autres
- [ ] 🟡 Ajouter un mécanisme de circuit breaker sur les appels HTTP scrapers
- [ ] 🟡 Créer une couche DTO/schema séparant les models ORM des réponses API
- [ ] 🟡 Externaliser les URLs des scrapers dans la configuration (pas hardcodées)

---

## 14.3 Backend — Scheduler et pipeline (P1)

### Pipeline

- [ ] 🟠 Créer un job orchestrateur `nightly_pipeline()` qui chaîne les étapes séquentiellement
- [ ] 🟠 Remplacer les jobs individuels cronés par l'appel à l'orchestrateur
- [ ] 🟡 Ajouter un timezone explicite au scheduler APScheduler
- [ ] 🟡 Implémenter un verrouillage : un même type de job ne peut pas s'exécuter en parallèle

### Maintenance des données

- [ ] 🟠 Créer un job de nettoyage des grilles scorées > 30 jours
- [ ] 🟠 Créer un job de nettoyage des portfolios > 30 jours
- [ ] 🟡 Ajouter un backup automatique hebdomadaire de `loto_ultime.db`
- [ ] 🟡 Implémenter un graceful shutdown avec `wait=True` et timeout de 30s

### Monitoring

- [ ] 🟡 Ajouter des compteurs de métriques dans le health check (nb grilles, nb tirages, dernier calcul)
- [ ] 🔵 Ajouter un export Prometheus (compteurs requêtes, latences, erreurs)
- [ ] 🔵 Configurer des alertes email/webhook quand le health check détecte un problème
- [ ] 🔵 Créer un dashboard de monitoring (Grafana ou équivalent)

---

## 14.4 Backend — Tests (P0-P1)

### Tests critiques manquants

- [ ] 🔴 Écrire un test vérifiant que `_get_game_config(loto_id)` retourne la config Loto
- [ ] 🔴 Écrire un test vérifiant que `_get_game_config(euro_id)` retourne la config EuroMillions
- [ ] 🔴 Écrire un test vérifiant que les stats Loto ≠ stats EuroMillions
- [ ] 🔴 Écrire un test vérifiant que les grilles EuroMillions contiennent des étoiles
- [ ] 🔴 Écrire un test vérifiant que `select_method()` retourne SA dans certaines conditions

### Tests d'amélioration

- [ ] 🟠 Ajouter des tests de non-régression (golden file) pour les scores de grilles connues
- [ ] 🟡 Ajouter des tests de performance : génération de 10 grilles < 5 secondes
- [ ] 🟡 Ajouter des tests de performance : simulation 10 000 itérations < 30 secondes
- [ ] 🟡 Ajouter des tests de nettoyage de données (cleanup job)
- [ ] 🟡 Ajouter des tests de pipeline orchestrateur

---

## 14.5 Frontend — Corrections et câblage (P0)

### Composants cassés ou non câblés

- [ ] 🔴 Câbler `ProfileSelector` dans `GridsPage` → transmettre la valeur à l'API `/grids/generate`
- [ ] 🟠 Supprimer les imports inutilisés et le code mort identifié
- [ ] 🟠 Vérifier que chaque `useMutation` a un `onSuccess` et un `onError` avec feedback

### Gestion d'état

- [ ] 🟠 Vérifier que le store Zustand `useGameStore` est utilisé partout où le `game_id` est nécessaire
- [ ] 🟡 Ajouter la persistance du jeu sélectionné dans `localStorage`

---

## 14.6 Frontend — UX et compréhension (P1)

### Tooltips et aide contextuelle

- [ ] 🟠 Ajouter un composant `InfoTooltip` réutilisable (icône ℹ️ + texte au hover)
- [ ] 🟠 Ajouter des tooltips sur chaque métrique de la page Statistiques (fréquence, retard, écart-type, etc.)
- [ ] 🟠 Ajouter des tooltips sur chaque critère de score dans la page Grilles
- [ ] 🟠 Ajouter des tooltips sur les métriques de simulation (taux de correspondance, ROI, etc.)
- [ ] 🟠 Ajouter des tooltips sur les colonnes du tableau de tirages
- [ ] 🟠 Ajouter une légende explicative sous chaque graphique D3/Recharts
- [ ] 🟡 Ajouter une page ou panel « Comment ça marche ? » expliquant le pipeline de calcul
- [ ] 🟡 Ajouter un glossaire accessible des termes techniques (retard, fréquence, scoring, etc.)

### Messages d'erreur

- [ ] 🟠 Créer un catalogue de messages d'erreur user-friendly en français
- [ ] 🟠 Mapper chaque code d'erreur API à un message compréhensible
- [ ] 🟠 Remplacer « Insufficient data for computation » par « Pas assez de tirages. Lancez l'import depuis l'administration. »
- [ ] 🟠 Remplacer « Internal server error » par « Une erreur inattendue s'est produite. Réessayez dans quelques instants. »
- [ ] 🟡 Ajouter un lien « Que faire ? » dans les messages d'erreur

### États vides

- [ ] 🟠 Page Statistiques sans données : afficher un CTA « Lancez /recompute pour calculer les statistiques »
- [ ] 🟠 Page Grilles sans grilles : afficher un CTA « Générez vos premières grilles »
- [ ] 🟠 Page Portfolio sans portfolio : afficher un CTA « Lancez l'optimisation pour créer votre premier portefeuille »
- [ ] 🟠 Page Simulation sans résultat : afficher un guide « Lancez une simulation pour évaluer vos grilles »
- [ ] 🟡 Admin Jobs sans historique : afficher « Aucun job exécuté. Le pipeline nightly démarre à 22h. »

### Feedback utilisateur

- [ ] 🟠 Ajouter un toast de succès après chaque action de génération
- [ ] 🟠 Ajouter un toast de succès après lancement d'une simulation
- [ ] 🟠 Ajouter un toast de succès après sauvegarde des paramètres
- [ ] 🟠 Ajouter un toast de succès après impôrtation des tirages
- [ ] 🟡 Ajouter des confirmations modales avant : suppression de grille, relance de calcul complet
- [ ] 🟡 Ajouter un indicateur de progression pendant les calculs longs (barre de progression ou skeleton)

---

## 14.7 Frontend — Qualité visuelle (P1-P2)

### Mode sombre / clair

- [ ] 🟠 Remplacer les couleurs hardcodées dans les composants Recharts par des CSS variables
- [ ] 🟠 Remplacer les couleurs hardcodées dans les composants D3 par des CSS variables
- [ ] 🟡 Vérifier le contraste des textes sur graphiques en mode clair et sombre
- [ ] 🟡 Tester l'ensemble de l'application dans les deux modes et corriger les incohérences

### Responsive

- [ ] 🟡 Vérifier et corriger l'affichage mobile (< 768px) de la page Statistiques
- [ ] 🟡 Vérifier et corriger l'affichage mobile de la page Grilles (tableau des grilles)
- [ ] 🟡 Vérifier et corriger l'affichage mobile de la page Simulation (graphiques)
- [ ] 🟡 Vérifier et corriger la navigation mobile (menu hamburger ou sidebar)

### Accessibilité

- [ ] 🟡 Ajouter des labels `aria-label` sur les éléments interactifs sans texte visible
- [ ] 🟡 Assurer la navigation clavier complète (tab order logique)
- [ ] 🟡 Ajouter des `role` ARIA sur les composants custom (graphiques, modales, toasts)
- [ ] 🔵 Atteindre le score WCAG 2.1 AA minimum

---

## 14.8 Frontend — Nouvelles fonctionnalités (P2-P3)

### Dashboard

- [ ] 🟡 Créer la page `DashboardPage` avec les KPIs principaux
- [ ] 🟡 Afficher les 5 derniers tirages avec numéros gagnants
- [ ] 🟡 Afficher le top 3 des grilles recommandées du jour
- [ ] 🟡 Afficher la santé du pipeline (dernier job, statut, date)
- [ ] 🟡 Afficher les statistiques clés (numéro le plus fréquent, le plus en retard)

### Historique et suivi

- [ ] 🟡 Créer la page `HistoryPage` pour le suivi des performances
- [ ] 🟡 Permettre à l'utilisateur de marquer des grilles comme « jouées »
- [ ] 🟡 Comparer les grilles jouées avec les tirages réels
- [ ] 🟡 Afficher un graphique de performance cumulée dans le temps

### Favoris et export

- [ ] 🟡 Ajouter un bouton « favori » (étoile) sur chaque grille
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
- [ ] 🟡 Ajouter un filtre par stratégie sur la page Grilles
- [ ] 🟡 Ajouter un mode comparaison entre deux stratégies d'optimisation
- [ ] 🔵 Permettre la création de stratégies personnalisées (poids custom des critères)

---

## 14.9 Frontend — Tests (P2)

- [ ] 🟡 Configurer Vitest + Testing Library pour le projet frontend
- [ ] 🟡 Écrire des tests unitaires pour les hooks custom (`useDraws`, `useStatistics`, etc.)
- [ ] 🟡 Écrire des tests unitaires pour les composants de visualisation
- [ ] 🟡 Configurer Playwright pour les tests E2E
- [ ] 🟡 Écrire un test E2E : parcours login → consultation statistiques
- [ ] 🟡 Écrire un test E2E : parcours génération de grilles → consultation
- [ ] 🟡 Écrire un test E2E : parcours simulation → résultats
- [ ] 🟡 Écrire un test E2E : parcours admin → lancement de jobs

---

## 14.10 Infrastructure et DevOps (P2-P3)

### CI/CD

- [ ] 🟡 Créer un `Dockerfile` pour le backend
- [ ] 🟡 Créer un `Dockerfile` pour le frontend
- [ ] 🟡 Créer un `docker-compose.yml` pour le développement local
- [ ] 🔵 Configurer GitHub Actions : lint + tests on push
- [ ] 🔵 Configurer GitHub Actions : build + deploy on release

### Documentation

- [ ] 🟡 Mettre à jour le README.md avec les instructions d'installation et d'utilisation
- [ ] 🟡 Documenter la procédure de migration Alembic dans un guide dédié
- [ ] 🟡 Documenter l'architecture des moteurs algorithmiques (diagramme de flux)
- [ ] 🟡 Ajouter des docstrings sur les méthodes publiques des services et moteurs

### Monitoring production

- [ ] 🔵 Ajouter un middleware Prometheus pour les métriques de requêtes HTTP
- [ ] 🔵 Ajouter des métriques custom : temps de calcul par engine, taux de succès scraping
- [ ] 🔵 Configurer des logrotate pour les fichiers de log
- [ ] 🔵 Implémenter un health check endpoint plus détaillé (vérification DB, scheduler, espace disque)

---

## 14.11 Sécurité (P1-P2)

- [ ] 🟠 Vérifier que les tokens JWT expirent correctement (access: 30min, refresh: 7 jours)
- [ ] 🟡 Ajouter la rotation du secret JWT via variable d'environnement
- [ ] 🟡 Implémenter un blacklist de tokens (invalidation après logout)
- [ ] 🟡 Ajouter un log d'audit des actions admin (qui a lancé quel job, quand)
- [ ] 🟡 Limiter le nombre de tentatives de login (au-delà du rate limiting global)
- [ ] 🔵 Migrer de HS256 à RS256 pour la signature JWT (en cas de multi-service)
- [ ] 🔵 Ajouter HTTPS forcé (HSTS header) si exposé sur Internet

---

## 14.12 Multi-loteries et expansion (P2-P3)

- [ ] 🟡 Vérifier que le `GameConfiguration` YAML contient les bons paramètres pour chaque loterie
- [ ] 🟡 Ajouter la configuration pour le Keno (20 numéros de 1-70)
- [ ] 🟡 Adapter le scraper FDJ pour le Keno (si les résultats sont disponibles)
- [ ] 🔵 Ajouter le support de loteries internationales (PowerBall, Mega Millions)
- [ ] 🔵 Créer un système de plugins pour ajouter des loteries sans modifier le cœur

---

## 14.13 Compteurs de progression

### Par priorité

| Priorité | Total | Cochées | Restantes |
|----------|-------|---------|-----------|
| 🔴 P0 — Indispensable | 30 | 0 | 30 |
| 🟠 P1 — Très utile | 46 | 0 | 46 |
| 🟡 P2 — Avancé | 54 | 0 | 54 |
| 🔵 P3 — Premium | 15 | 0 | 15 |
| **TOTAL** | **145** | **0** | **145** |

### Par domaine

| Domaine | Total |
|---------|-------|
| Backend — Corrections critiques | 28 |
| Backend — API et services | 14 |
| Backend — Scheduler et pipeline | 12 |
| Backend — Tests | 10 |
| Frontend — Corrections | 5 |
| Frontend — UX et compréhension | 26 |
| Frontend — Qualité visuelle | 12 |
| Frontend — Nouvelles fonctionnalités | 20 |
| Frontend — Tests | 8 |
| Infrastructure et DevOps | 12 |
| Sécurité | 7 |
| Multi-loteries | 5 |
| **TOTAL** | **145** (avec recoupements possibles) |

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
