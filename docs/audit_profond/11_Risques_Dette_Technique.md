# 11. Risques et Dette Technique

Ce chapitre dresse l'inventaire complet des risques techniques, fonctionnels et produit qui pèsent sur LOTO ULTIME. Chaque risque est évalué selon son **impact** (gravité si le risque se matérialise) et sa **probabilité** (chances qu'il se matérialise dans l'année à venir).

---

## 11.1 Risques critiques (impact élevé × probabilité haute)

### R1. Bug `_get_game_config()` : EuroMillions utilise la config du Loto

**Description** : La méthode `_get_game_config()` dans `StatisticsService`, `ScoringService`, `OptimizationService` et `SimulationService` effectue un `select().limit(1)` au lieu de filtrer sur `game_id`. Résultat : tous les calculs EuroMillions utilisent les paramètres du Loto (5 numéros de 1-49 au lieu de 5 numéros de 1-50 + 2 étoiles de 1-12).

**Impact** : 🔴 CRITIQUE
- Les statistiques EuroMillions sont fausses (calculées sur un univers [1-49] au lieu de [1-50])
- Les étoiles ne sont pas du tout intégrées dans les calculs
- Les grilles générées pour EuroMillions sont incomplètes (pas d'étoiles)
- Le scoring de grilles EuroMillions est basé sur de mauvais paramètres
- La simulation EuroMillions est invalide

**Probabilité** : 100% — le bug est avéré et actif.

**Remédiation** :
```python
# Avant (bug)
result = await session.execute(select(GameConfiguration).limit(1))

# Après (correction)
result = await session.execute(
    select(GameConfiguration).where(GameConfiguration.game_id == game_id)
)
```
+ Ajouter le support des étoiles dans tous les moteurs.

**Effort** : 3-5 jours développement + tests

---

### R2. `select_method()` retourne toujours "genetic"

**Description** : La méthode de sélection dans l'optimiseur choisit entre "genetic" et "simulated_annealing" en comparant `n_grids >= 10`. Comme le nombre de grilles demandé est toujours ≥ 10 (valeur par défaut), l'algorithme génétique est systématiquement sélectionné.

**Impact** : 🟠 IMPORTANT
- Le simulated annealing (SA) est du code mort en production
- L'utilisateur ne peut pas bénéficier de SA, qui explore différemment l'espace des solutions
- Toute une branche algorithmique est développée mais jamais exécutée

**Probabilité** : 100% — la condition est toujours vraie.

**Remédiation** : Exposer le choix à l'utilisateur via l'API et l'UI, ou changer le critère de sélection pour être pertinent.

**Effort** : 1 jour

---

### R3. Pas de migration de base de données

**Description** : Le projet crée les tables via `Base.metadata.create_all()` au démarrage. Il n'y a pas d'Alembic ni d'outil de migration.

**Impact** : 🔴 CRITIQUE
- Toute modification de schéma (ajout de colonne, changement de type) nécessite de supprimer et recréer la base
- Avec 1642 tirages importés, une recréation prend du temps et risque une perte de données
- Le schéma ne peut pas évoluer de manière incrémentale

**Probabilité** : 100% — dès la prochaine modification de modèle.

**Remédiation** : Intégrer Alembic, générer la migration initiale from scratch, configurer l'auto-génération des migrations.

**Effort** : 1 jour d'intégration + discipline continue

---

## 11.2 Risques importants (impact modéré × probabilité haute)

### R4. Accumulation non contrôlée de données

**Description** : Les tables `scored_grids` et `portfolios` ne sont jamais nettoyées. Chaque exécution du pipeline nightly ajoute ~18 entrées (10 top grids + 8 portfolios).

**Impact** : 🟠 MODÉRÉ
- ~6500 entrées supplémentaires par an
- Les requêtes `get_all()` sans pagination deviendront lentes (déjà le pattern `count()` charge tout en mémoire)
- L'espace disque augmente progressivement

**Probabilité** : 100% — accumulation mécanique.

**Remédiation** : Ajouter une politique de rétention (ex : garder les 30 derniers jours de grilles, archiver les plus anciennes).

**Effort** : 0.5 jour

---

### R5. `count()` charge toutes les entités en mémoire

**Description** : La méthode `count()` de chaque repository fait `len(result.scalars().all())` au lieu d'un `SELECT COUNT(*)`.

**Impact** : 🟠 MODÉRÉ
- Avec 1642 tirages : transfert de ~1600 objets ORM en mémoire juste pour compter
- Avec 10 000 grilles : la mémoire utilisée explose pour un simple comptage
- Endpoints de listing (avec pagination) appellent `count()` à chaque requête

**Probabilité** : 100% — le code est déjà déployé.

**Remédiation** :
```python
# Avant (inefficace)
result = await session.execute(select(Draw))
return len(result.scalars().all())

# Après (correct)
result = await session.execute(select(func.count(Draw.id)))
return result.scalar_one()
```

**Effort** : 0.5 jour (tous les repositories)

---

### R6. Pas de rate limiting sur les endpoints de calcul

**Description** : Les endpoints `/recompute`, `/generate`, `/run` déclenchent des calculs CPU-intensifs. Seuls les endpoints d'auth ont du rate limiting (via slowapi).

**Impact** : 🟠 IMPORTANT
- Un utilisateur (ou un bot) peut lancer des centaines de calculs simultanément
- Risque de DoS CPU : le serveur devient non-responsive
- Avec l'auth en place, le risque est limité aux utilisateurs authentifiés, mais reste réel

**Probabilité** : 50% — faible pour un usage mono-utilisateur, mais réel si l'application est exposée.

**Remédiation** : Étendre slowapi ou middleware custom à tous les endpoints de calcul, avec un maximum de 5-10 requêtes/minute.

**Effort** : 0.5 jour

---

### R7. Sélecteur de profil non fonctionnel dans GridsPage

**Description** : Le `ProfileSelector` existe dans le code et est importé dans `GridsPage`, mais il n'est pas câblé à la logique de génération. Les profils semblent être des alias de stratégies d'optimisation, mais la sélection n'impacte pas le call API.

**Impact** : 🟠 IMPORTANT
- L'utilisateur voit un composant interactif qui ne fait rien → frustration, perte de confiance
- La promesse de « profils de jeu » n'est pas tenue

**Probabilité** : 100% — l'UI est affichée et le bouton est cliquable.

**Remédiation** : Soit câbler le sélecteur à l'API (transmettre le profil sélectionné comme `strategy` en paramètre), soit retirer le composant jusqu'à ce que la fonctionnalité soit prête.

**Effort** : 0.5-1 jour selon l'approche

---

## 11.3 Risques modérés (impact modéré × probabilité moyenne)

### R8. FrequencyCriterion normalisation instable

**Description** : Le critère de fréquence utilise une normalisation min-max. Quand toutes les fréquences sont identiques (min = max), la division par zéro est protégée (retourne 0.0), mais le comportement est incohérent : des numéros avec des fréquences identiques obtiennent un score de 0 au lieu de 0.5 (médian).

**Impact** : 🟡 MODÉRÉ
- Affecte la qualité du scoring dans les cas edge (peu de données, distribution très plate)
- Peut se produire après une réinitialisation de la base ou avec un filtre temporel étroit

**Probabilité** : 30% — nécessite des conditions spécifiques.

**Remédiation** : Retourner 0.5 (score neutre) quand min == max, ou utiliser z-score au lieu de min-max.

**Effort** : 0.5 jour

---

### R9. PatternPenalty stacking illimité

**Description** : Les pénalités de pattern s'additionnent sans plafond. Un pattern très commun peut accumuler -0.2 par critère × N critères déclenchés, poussant le score total dans les négatifs.

**Impact** : 🟡 MODÉRÉ
- Les grilles avec des patterns courants mais statistiquement valides sont excessivement pénalisées
- Le classement des top grilles est biaisé

**Probabilité** : 40% — se produit quand plusieurs patterns sont remplis simultanément.

**Remédiation** : Plafonner la pénalité totale à -0.3 (30% du score max) ou normaliser après stacking.

**Effort** : 0.5 jour

---

### R10. Temporal regression sur 4 points seulement

**Description** : Le `TemporalEngine` fait une régression linéaire sur les 4 dernières fenêtres temporelles. Avec si peu de points, la régression est statistiquement non significative et très sensible au bruit.

**Impact** : 🟡 MODÉRÉ
- Les tendances détectées peuvent être du bruit statistique
- Le moteur donne une fausse confiance dans ses prédictions

**Probabilité** : 100% — design actuel.

**Remédiation** : Permettre un nombre configurable de fenêtres (8-12 minimum), ajouter un indicateur de confiance (R²), et ne retourner la tendance que si R² > seuil.

**Effort** : 1 jour

---

### R11. SQLite en production

**Description** : SQLite est approprié pour le développement et le mono-utilisateur. Mais il n'est pas adapté si l'application doit supporter plusieurs utilisateurs simultanés.

**Impact** : 🟠 IMPORTANT si multi-user
- Write locking : un seul writer à la fois
- Pas de connexion réseau : l'application et la base doivent être sur la même machine
- Pas de réplication

**Probabilité** : 10% (actuellement mono-utilisateur, mais probable si le projet grandit).

**Remédiation** : Migration vers PostgreSQL (compatible avec SQLAlchemy async). Non prioritaire tant que le projet reste mono-utilisateur.

**Effort** : 1-2 jours (mise en place + migration des données)

---

### R12. Hardcoded colors dans Recharts et D3

**Description** : Les graphiques utilisent des couleurs codées en dur (`#10B981`, `#3B82F6`, etc.) qui ne s'adaptent pas au thème clair/sombre.

**Impact** : 🟡 MODÉRÉ
- En mode clair, certains graphiques deviennent illisibles (couleurs claires sur fond blanc)
- L'impression d'un produit fini est altérée

**Probabilité** : 100% — visible dès le switch de thème.

**Remédiation** : Extraire les couleurs dans des constantes issues des CSS custom properties.

**Effort** : 1 jour

---

## 11.4 Inventaire de la dette technique

La dette technique est classée par type :

### Dette de conception

| Élément | Description | Sévérité |
|---------|-------------|----------|
| game_config global | Config non filtrée par game_id | 🔴 Critique |
| select_method figé | SA jamais utilisé | 🟠 Important |
| Pipeline timing-based | Pas de chaînage des jobs | 🟡 Modéré |
| Pas de DTO couche service | Les models SQLAlchemy traversent toutes les couches | 🟡 Modéré |

### Dette d'implémentation

| Élément | Description | Sévérité |
|---------|-------------|----------|
| count() inefficace | Charge tout en mémoire | 🟠 Important |
| PRAGMA FK non activé | Intégrité non garantie | 🟠 Important |
| URLs scrapers hardcodées | Pas de configuration externe | 🟡 Modéré |
| Étoiles ignorées | EuroMillions incomplet | 🔴 Critique |

### Dette d'infrastructure

| Élément | Description | Sévérité |
|---------|-------------|----------|
| Pas d'Alembic | Pas de migration de schéma | 🔴 Critique |
| Pas de backup auto | Aucune sauvegarde de la base | 🟡 Modéré |
| Pas de CI/CD | Tests manuels uniquement | 🟡 Modéré |
| Pas de conteneurisation | Pas de Docker | 🟡 Faible |

### Dette de tests

| Élément | Description | Sévérité |
|---------|-------------|----------|
| 0 tests frontend | React sans tests | 🟠 Important |
| 0 tests multi-loteries | Bug game_config non détecté | 🔴 Critique |
| 0 tests E2E | Parcours utilisateur non vérifié | 🟡 Modéré |
| 0 tests de performance | Aucun benchmark | 🟡 Modéré |

### Dette UX

| Élément | Description | Sévérité |
|---------|-------------|----------|
| 0 tooltips | Données non expliquées | 🟠 Important |
| Messages d'erreur techniques | Non orientés utilisateur | 🟡 Modéré |
| Pas d'aide contextuelle | Pas de coach, pas de guide | 🟡 Modéré |
| États vides basiques | « Aucune donnée » sans aide | 🟡 Modéré |

---

## 11.5 Matrice des risques

```
PROBABILITÉ
  Élevée   │ R4,R5,R7,R9  │ R1,R2,R3,R10 │
            │               │    R12        │
  Moyenne   │ R8            │ R6            │
            │               │               │
  Faible    │               │ R11           │
            ├───────────────┼───────────────┤
            │   Modéré      │   Élevé       │
                        IMPACT
```

**Quadrant critique (impact élevé × probabilité élevée)** : R1, R2, R3, R10, R12
→ À traiter en priorité absolue.

**Quadrant attention (impact modéré × probabilité élevée)** : R4, R5, R7, R9
→ À traiter rapidement après les critiques.

---

## 11.6 Évaluation du risque projet global

| Dimension | Risque | Justification |
|-----------|--------|---------------|
| Fonctionnel | 🟠 Modéré-élevé | EuroMillions cassé, profil non câblé |
| Technique | 🟡 Modéré | Pas de migration, count inefficace |
| Performance | 🟢 Faible | SQLite tient la charge mono-user |
| Sécurité | 🟢 Faible | Auth solide, rate limiting partiel |
| Maintenabilité | 🟡 Modéré | Code propre mais dette cachée |
| Scalabilité | 🟠 Modéré | SQLite, accumulation, pas de cache |

**Verdict** : Le projet porte une dette technique concentrée autour du multi-loteries et des outils de développement (migrations, tests). L'architecture de base est saine et la dette est remboursable avec un effort ciblé de 2-3 semaines de développement focalisé.
