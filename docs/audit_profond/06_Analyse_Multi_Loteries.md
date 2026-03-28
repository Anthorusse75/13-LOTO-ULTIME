# 6. Analyse Détaillée de la Partie Multi-Loteries

## 6.1 Contexte

LOTO ULTIME ambitionne de supporter plusieurs loteries. Aujourd'hui, deux jeux sont configurés :

| Jeu | Pool principal | Tirés | Pool secondaire | Tirés | Fréquence |
|-----|---------------|-------|-----------------|-------|-----------|
| **Loto FDJ** | 1-49 | 5 | 1-10 (N° Chance) | 1 | Lun/Mer/Sam |
| **EuroMillions** | 1-50 | 5 | 1-12 (Étoiles) | 2 | Mar/Ven |

La différence structurelle entre les deux jeux est significative :
- Pool principal quasi-identique (49 vs 50) mais pool secondaire très différent (1×10 vs 2×12)
- L'EuroMillions a un espace combinatoire beaucoup plus grand : C(50,5)×C(12,2) = 139,838,160 vs C(49,5)×C(10,1) = 19,068,840 pour le Loto
- Les règles de gains sont différentes

---

## 6.2 Ce qui est en place

### Configuration YAML

Chaque jeu est défini dans un fichier YAML (`loto-fdj.yaml`, `euromillions.yaml`) avec tous les paramètres nécessaires :

```yaml
name: "EuroMillions"
slug: "euromillions"
numbers_pool: 50
numbers_drawn: 5
min_number: 1
max_number: 50
stars_pool: 12
stars_drawn: 2
star_name: "étoile"
draw_frequency: "mardi, vendredi"
```

Ce système de configuration est bien pensé : ajouter un nouveau jeu (Keno, Swiss Lotto, etc.) nécessite uniquement un nouveau fichier YAML.

### Modèle de données

La base de données est structurée pour le multi-jeu :
- `GameDefinition` table centrale avec `id`, `slug`, et tous les paramètres
- Toutes les tables (`Draw`, `StatisticsSnapshot`, `ScoredGrid`, `Portfolio`) ont un `game_id` FK
- Contrainte d'unicité `(game_id, draw_date)` sur les tirages

### Scrapers séparés

Chaque jeu a son propre scraper (`FDJLotoScraper`, `EuroMillionsScraper`) qui gère le parsing spécifique (1 numéro chance vs 2 étoiles).

### Scheduler adapté

Le scheduler a des horaires différenciés :
- Loto : lundi, mercredi, samedi à 22h
- EuroMillions : mardi, vendredi à 22h

### Jobs multi-jeux

Les jobs `compute_stats`, `compute_scoring`, `compute_top_grids` et `optimize_portfolio` itèrent sur **tous les jeux actifs** et traitent chacun individuellement.

---

## 6.3 Ce qui ne fonctionne PAS

### 🔴 Bug critique : Résolution de configuration

C'est le problème le plus grave du projet. La fonction `_get_game_config()` utilisée dans les routes API ne résout pas correctement le jeu :

```python
def _get_game_config(game_id: int):
    configs = list(_game_configs.values())
    for cfg in configs:
        return cfg  # ← Retourne TOUJOURS le premier jeu
```

**Impact concret** :
- Un utilisateur sur la page EuroMillions qui génère des grilles reçoit des grilles Loto FDJ (5 numéros parmi 49 au lieu de 5 parmi 50, 1 N° Chance au lieu de 2 étoiles)
- Les scores EuroMillions sont calculés avec les paramètres Loto
- Les simulations EuroMillions utilisent les probabilités Loto
- Toute la chaîne analytique EuroMillions est **factuellement incorrecte**

**Pourquoi ce bug existe** : La fonction itère sur un dictionnaire et retourne immédiatement le premier élément, sans jamais comparer le `game_id` passé en paramètre. C'est probablement un stub de développement qui n'a jamais été complété.

**Correction** :
```python
def _get_game_config(game_id: int) -> GameConfig:
    # Option 1: Résolution par lookup DB
    game = await game_repo.get(game_id)
    config = configs.get(game.slug)
    
    # Option 2: Index par game_id créé au démarrage
    config = _game_configs_by_id.get(game_id)
    
    if config is None:
        raise HTTPException(404, f"No config for game_id={game_id}")
    return config
```

**Classement** : 🔧 Correction critique — invalide 50% de la fonctionnalité du produit

---

### ⚠️ Étoiles insuffisamment intégrées dans les moteurs

Les moteurs statistiques et de scoring travaillent principalement sur la matrice `numbers` (les 5 numéros principaux). Le traitement des étoiles est inégal :

| Moteur | Traitement des étoiles |
|--------|----------------------|
| FrequencyEngine | ❌ Numéros principaux uniquement |
| GapEngine | ❌ Numéros principaux uniquement |
| CooccurrenceEngine | ❌ Numéros principaux uniquement |
| DistributionEngine | ❌ Numéros principaux uniquement |
| BayesianEngine | ❌ Numéros principaux uniquement |
| GraphEngine | ❌ Numéros principaux uniquement |
| TemporalEngine | ❌ Numéros principaux uniquement |
| Scoring (tous) | ❌ Numéros principaux uniquement |
| MonteCarloSimulator | ⚠️ Paramètre stars_pool accepté mais traitement minimal |
| PortfolioOptimizer | ⚠️ Stars stockées mais pas optimisées |

**Conséquence** : Pour l'EuroMillions, les 2 étoiles (qui représentent un espace combinatoire de C(12,2) = 66 combinaisons) sont essentiellement ignorées par l'analyse statistique et le scoring. Un joueur qui utilise LOTO ULTIME pour l'EuroMillions reçoit une optimisation sur les 5 numéros principaux seulement — les étoiles sont choisies aléatoirement ou par défaut.

Or, les étoiles sont le facteur le plus discriminant de l'EuroMillions : la différence entre matcher 5+0 étoiles (1/2,118,760) et 5+2 étoiles (1/139,838,160) est un facteur 66.

**Ce qui est nécessaire** :
- Étendre `get_numbers_matrix()` pour retourner deux matrices (numbers + stars)
- Dupliquer les analyses statistiques pour les étoiles (fréquences, gaps, co-occurrences séparées)
- Intégrer les étoiles dans le scoring : score_total = 0.7 × score_numbers + 0.3 × score_stars
- Optimiser les étoiles conjointement avec les numéros

**Classement** : 📈 Amélioration structurante pour la crédibilité EuroMillions

---

### ⚠️ Frontend : sélection de jeu déconnectée

Le header affiche un sélecteur de jeu (dropdown Loto / EuroMillions) qui modifie le `currentGameId` dans le store Zustand. Les requêtes API utilisent ensuite ce `gameId` dans l'URL (`/api/v1/games/{game_id}/...`).

**Ce qui fonctionne** :
- Le dropdown est visuellement présent
- Le store est mis à jour
- Les requêtes partent avec le bon `game_id`

**Ce qui ne fonctionne pas** :
- Côté backend, `game_id` est ignoré par `_get_game_config()` (bug ci-dessus)
- L'interface ne s'adapte pas visuellement au jeu sélectionné :
  - Le label « N° Chance » vs « Étoiles » n'est pas conditionnel
  - Les composants `DrawBalls` n'affichent pas les étoiles séparément pour l'EuroMillions
  - Les plages de numéros dans les heatmaps sont identiques (1-49) pour les deux jeux
  - Le disclaimer ne mentionne pas le jeu courant

**Classement** : 📈 Amélioration nécessaire pour une expérience multi-jeu crédible

---

## 6.4 Évaluation de maturité par composant

```
                              Loto FDJ    EuroMillions
Configuration YAML              ✅           ✅
Modèle de données               ✅           ✅
Scraper ingestion               ✅           ✅
Données en base (tirages)       ✅ (1000)    ✅ (642)
Résolution config API           ✅           🔴 CASSÉ
Moteurs stats (5 numeros)       ✅           ⚠️ (utilise config Loto)
Moteurs stats (étoiles)         n/a          ❌ Non implémenté
Scoring (5 numéros)             ✅           ⚠️ (utilise config Loto)
Scoring (étoiles)               n/a          ❌ Non implémenté
Optimisation grilles            ✅           ⚠️ (pool incorrect)
Simulation Monte Carlo          ✅           ⚠️ (probabilités incorrectes)
Portefeuille                    ✅           ⚠️ (diversité calculée sur numbers seulement)
Interface adaptée               ⚠️           ❌ Pas d'adaptation
Scheduler (fetch)               ✅           ✅
Scheduler (compute)             ✅           ⚠️ (calculs sur mauvaise config)
```

---

## 6.5 Plan de remédiation multi-loteries

### Phase 1 : Corrections critiques (immédiat)
1. Corriger `_get_game_config()` pour résoudre correctement par `game_id`
2. Vérifier que les routes statistiques, grids, portfolios et simulations utilisent la bonne config
3. Ajouter un test d'intégration : générer une grille EuroMillions et vérifier qu'elle a 5 numéros ≤ 50 + 2 étoiles ≤ 12

### Phase 2 : Intégration des étoiles (court terme)
4. Modifier `DrawRepository.get_numbers_matrix()` pour retourner (numbers_matrix, stars_matrix)
5. Créer des variantes stats pour les étoiles (fréquences étoiles, gaps étoiles, co-occurrences étoiles)
6. Intégrer les étoiles dans le snapshot statistique
7. Étendre le scoring pour inclure un score_stars

### Phase 3 : Adaptation UI (court terme)
8. Adapter les composants pour afficher les étoiles séparément (boules jaunes)
9. Adapter le NumberHeatmap pour le pool d'étoiles (1-12)
10. Conditionner les labels selon le jeu (N° Chance / Étoiles)
11. Afficher les métriques étoiles dans les onglets statistiques

### Phase 4 : Extensibilité (moyen terme)
12. Documenter le processus d'ajout d'un nouveau jeu (guide développeur)
13. Ajouter un jeu test (ex: EuroDreams ou Keno) pour valider l'extensibilité
14. Gérer les jeux avec des règles spéciales (bonus, multiplicateurs)

---

## 6.6 Synthèse

Le support multi-loteries de LOTO ULTIME est **architecturalement prêt** mais **fonctionnellement cassé**. L'effort de structuration (YAML configs, game_id FK partout, scrapers séparés, scheduler différencié) est excellent et montre une vision claire. Mais un seul bug dans la résolution de configuration invalide l'intégralité du pipeline EuroMillions.

Au-delà du bug, l'absence de traitement des étoiles/numéros complémentaires est une lacune fondamentale pour tout jeu qui n'est pas du Loto simple. C'est l'investissement le plus important pour faire de LOTO ULTIME un vrai produit multi-loteries, et pas seulement un produit Loto avec un menu déroulant.
