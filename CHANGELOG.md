# Changelog

Toutes les modifications notables du projet sont documentées dans ce fichier.  
Format basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.1.0/).

---

## [1.0.0] — 2026-03-30

### Ajouté

#### Backend
- **7 moteurs statistiques** : fréquences, écarts, cooccurrences, tendances temporelles, distribution, inférence bayésienne, analyse de graphe (NetworkX)
- **Moteur de scoring** multicritères (6 critères + pénalités patterns) avec 4 profils prédéfinis et poids personnalisables
- **5 méta-heuristiques d'optimisation** : recuit simulé, algorithme génétique, recherche tabou, hill climbing, NSGA-II multi-objectif
- **Optimisation de portefeuille** avec 4 stratégies (balanced, max_diversity, max_coverage, min_correlation)
- **Simulations Monte Carlo** avec analyse de robustesse et validation bootstrap
- **Scheduler APScheduler** : pipeline nocturne automatique (import → stats → scoring → portefeuille)
- **Scrapers** pour 5 loteries : Loto FDJ, EuroMillions, Keno, Mega Millions, Powerball
- **Authentification JWT** (HS256/RS256) avec refresh tokens et rotation
- **RBAC** 3 niveaux : ADMIN, UTILISATEUR, CONSULTATION
- **Rate limiting** par endpoint (slowapi)
- **Admin initial** créé automatiquement au démarrage depuis variables d'environnement
- **Health check** endpoint avec vérification DB, scheduler et espace disque
- **API REST** complète (FastAPI) avec documentation Swagger/OpenAPI

#### Frontend
- **Dashboard** avec KPIs, graphiques fréquence, derniers tirages, top grilles, statut pipeline
- **Page Tirages** : liste paginée avec composant DrawBalls
- **Page Statistiques** : 7 onglets (fréquences, écarts, cooccurrences, tendances, distribution, bayésien, graphe D3.js)
- **Page Grilles** : génération, liste résultats, détail avec décomposition score
- **Page Portefeuille** : génération avec stratégies, visualisation couverture (NumberHeatmap)
- **Page Simulation** : Monte Carlo, stabilité bootstrap, comparaison aléatoire
- **Page Admin** : monitoring système, gestion jobs, gestion utilisateurs
- **Pages éducatives** : Comment ça marche, Glossaire
- **Dark mode** par défaut avec toggle clair/sombre
- **Sidebar** responsive avec collapse/expand (desktop) et drawer (mobile)
- **Onboarding tour** interactif pour les nouveaux utilisateurs
- **Coach IA** contextuel (règles statistiques, pas de ML)
- **Authentification** : login, guard de routes, gestion rôles

#### Infrastructure
- **Docker** : Dockerfiles multi-stage (backend Python 3.11 + frontend Nginx)
- **docker-compose** : stack complète avec healthchecks
- **Observabilité** : Prometheus + Grafana (profil monitoring)
- **CI/CD** : GitHub Actions (tests, lint, build)
- **18 documents d'architecture** détaillés

### Sécurité
- Protection OWASP Top 10 (injection SQL via ORM, XSS via React, CSRF via JWT, rate limiting)
- Headers de sécurité (X-Content-Type-Options, X-Frame-Options, HSTS, Referrer-Policy, Permissions-Policy)
- Validation mot de passe (min 8 car., majuscule, minuscule, chiffre)
- Throttle progressif sur login (backoff exponentiel par IP)
- Audit logging des actions sensibles

### Tests
- **455 tests backend** (unitaires + intégration) — couverture 84.65%
- **28 tests frontend** (Vitest)
- Tests E2E Playwright (login, statistiques, grilles, admin, simulation)

---

## [0.9.0] — 2026-03-28

### Ajouté
- Sécurité et authentification complètes (Phase 9)
- Interface frontend complète (Phase 7)
- Scheduler et jobs automatiques (Phase 8)

## [0.6.0] — 2026-03-27

### Ajouté
- Moteur de simulation Monte Carlo (Phase 6)
- Moteur d'optimisation avec 5 méta-heuristiques (Phase 5)
- Moteur de scoring multicritères (Phase 4)
- Moteur statistique 7 engines (Phase 3)
- Fondations backend FastAPI + SQLAlchemy (Phase 2)
- Architecture et documentation 18 docs (Phase 1)
