# 15 — Évolution : Automatisation & Vie du Produit

> Centre d'activité, alertes utilisateur, suggestions récurrentes, pré-générations, animations de rétention.

---

## Références croisées

- [00_Index_Evolutions](./00_Index_Evolutions.md)
- [02_Strategie_Produit](./02_Strategie_Produit.md) — KPIs rétention, personas
- [11_Evolution_Historique_Favoris](./11_Evolution_Historique_Favoris.md) — Historique / Résultats sauvegardés
- [20_Impacts_Scheduler_Jobs](./20_Impacts_Scheduler_Jobs.md)
- [23_Impacts_Production_Exploitation](./23_Impacts_Production_Exploitation.md)

---

## 1. Objectif

Faire vivre le produit au-delà de la session utilisateur : alertes post-tirage, suggestions pré-tirage, activité quotidienne, pré-calculs automatiques. Transformer l'usage ponctuel en habitude de consultation.

---

## 2. État actuel

### Scheduler existant (9 jobs)

| Job                  | Fréquence               | Détail                   |
| -------------------- | ----------------------- | ------------------------ |
| `fetch_draws`        | Quotidien 23:00         | Scraping résultats FDJ   |
| `compute_statistics` | Après fetch             | StatisticsSnapshot       |
| `compute_scoring`    | Après stats             | Scoring toutes grilles   |
| `compute_top_grids`  | Après scoring           | Top N persistées         |
| `optimize_portfolio` | Après top               | Portfolio optimisé       |
| `health_check`       | 5 min                   | Santé système            |
| `backup_db`          | Quotidien 02:00         | Backup PostgreSQL        |
| `cleanup`            | Quotidien 03:00         | Purge données anciennes  |
| `nightly_pipeline`   | Quotidien orchestrateur | Chaîne fetch → portfolio |

### Manques identifiés

- Aucune notification utilisateur
- Aucun contenu pré-calculé visible au login
- Aucune suggestion proactive
- Le centre d'activité n'existe pas (pas de Dashboard avec contenu dynamique)

---

## 3. Évolutions proposées

### AUTO-01 : Centre d'activité (Dashboard amélioré)

**Contenu du Dashboard enrichi** :

| Bloc                        | Source                                    | Calcul                                   |
| --------------------------- | ----------------------------------------- | ---------------------------------------- |
| Dernier tirage              | Draw la plus récente                      | Affichage direct                         |
| Prochaine date de tirage    | GameDefinition.draw_schedule              | Calcul jour suivant                      |
| Résultat grilles jouées     | ScoredGrid (is_played=true) × Draw récent | Comparaison numéros                      |
| Top 3 grilles du jour       | ScoredGrid triées par score               | Top 3                                    |
| Score moyen du portefeuille | Portfolio.expected_score                  | Direct                                   |
| Statistique du jour         | StatisticsSnapshot dernier                | Numéro le plus chaud / le plus en retard |
| Suggestion du jour          | Calcul algorithmique                      | Grille suggérée avec explication         |

**Composants** :

```
DashboardPage (enrichi)
├── LatestDrawCard        — Dernier tirage avec numéros + gains
├── NextDrawCountdown     — Compte à rebours + date
├── PlayedGridsResults    — Vos grilles vs dernier tirage
├── DailyTopGridsCard     — Top 3 grilles pré-calculées
├── PortfolioSummaryCard  — Résumé portefeuille
├── StatOfTheDay          — Stat du jour (fun fact)
└── DailySuggestionCard   — Grille suggérée avec explication L1
```

### AUTO-02 : Vérification automatique des grilles jouées

**Fonctionnement** :
1. L'utilisateur marque des grilles comme « jouées » (existant : `is_played`, `played_at`)
2. À chaque nouveau tirage scrappé, le système compare automatiquement
3. Résultat stocké : nombre de numéros matchés, rang de gain, montant estimé

**Modèle additionnel** :

```python
class GridDrawResult(Base):
    __tablename__ = "grid_draw_results"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    scored_grid_id: Mapped[int] = mapped_column(ForeignKey("scored_grids.id"))
    draw_id: Mapped[int] = mapped_column(ForeignKey("draws.id"))
    matched_numbers: Mapped[list[int]] = mapped_column(JSON)
    matched_stars: Mapped[list[int]] = mapped_column(JSON, nullable=True)
    match_count: Mapped[int]
    star_match_count: Mapped[int] = mapped_column(default=0)
    prize_rank: Mapped[int | None]  # rang de gain ou None
    estimated_prize: Mapped[float] = mapped_column(default=0.0)
    checked_at: Mapped[datetime]
```

**Job** : `check_played_grids` — après `fetch_draws`, compare toutes grilles `is_played=true` non encore vérifiées.

### AUTO-03 : Pré-génération quotidienne

**Principe** : à chaque nuit, le pipeline calcule et persiste des résultats prêts à consulter.

| Pré-calcul                                 | Stockage                       | Usage         |
| ------------------------------------------ | ------------------------------ | ------------- |
| Top 10 grilles par jeu                     | ScoredGrid (tag: daily_top)    | DashboardPage |
| Portefeuille optimal par jeu               | Portfolio (tag: daily_optimal) | DashboardPage |
| Statistiques résumées                      | StatisticsSnapshot             | StatOfTheDay  |
| Numéros chauds / froids (top 5 + bottom 5) | JSON dans StatisticsSnapshot   | DashboardPage |

**Extension nightly_pipeline** :

```
fetch_draws → compute_statistics → compute_scoring → compute_top_grids
                                                   → pre_generate_daily_content
                                                   → check_played_grids
                                                   → optimize_portfolio
```

### AUTO-04 : Suggestion récurrente

**Logique** :
- À chaque visite J+1 après un tirage, l'utilisateur voit une suggestion de grille
- La suggestion est basée sur le scoring du jour, diversifiée par rapport aux grilles déjà jouées
- Accompagnée d'une explication L1 (cf. doc 12)

**Service** :

```python
class SuggestionService:
    async def get_daily_suggestion(
        self, game_id: int, user_id: int | None
    ) -> SuggestedGrid:
        # 1. Récupérer le top scoring du jour
        # 2. Si user_id: exclure les grilles déjà jouées récemment
        # 3. Retourner la meilleure grille non vue + explication L1
        pass
```

### AUTO-05 : Alertes et notifications

**Phase 1 — In-app uniquement** (pas de push/email) :

| Alerte                    | Déclencheur          | Affichage                 |
| ------------------------- | -------------------- | ------------------------- |
| Nouveau tirage disponible | fetch_draws complété | Banner en haut de page    |
| Résultat vos grilles      | check_played_grids   | Badge sur DashboardPage   |
| Nouvelle suggestion dispo | pre_generate         | Point sur menu Suggestion |
| Stats recalculées         | compute_statistics   | Indicateur discret        |

**Modèle** :

```python
class UserNotification(Base):
    __tablename__ = "user_notifications"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    type: Mapped[str]  # "new_draw", "grid_result", "suggestion", "stats_updated"
    title: Mapped[str]
    message: Mapped[str]
    data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    is_read: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime]
```

**Endpoints** :

| Méthode | Route                                | Détail                          |
| ------- | ------------------------------------ | ------------------------------- |
| GET     | `/api/v1/notifications`              | Liste notifications (paginated) |
| PATCH   | `/api/v1/notifications/{id}/read`    | Marquer comme lue               |
| POST    | `/api/v1/notifications/read-all`     | Tout marquer comme lu           |
| GET     | `/api/v1/notifications/unread-count` | Nombre non lues (badge)         |

**Composants frontend** :

```
Header
└── NotificationBell          — Icône cloche + badge count
    └── NotificationDropdown  — Liste déroulante des notifications
        └── NotificationItem  — Ligne individuelle
```

---

## 4. Phasage

| Phase | Contenu                                               | Effort   | Dépendances             |
| ----- | ----------------------------------------------------- | -------- | ----------------------- |
| B.9   | AUTO-01 Dashboard enrichi (sans vérification grilles) | 2 jours  | —                       |
| B.10  | AUTO-02 Vérification auto grilles jouées              | 2 jours  | GamePrizeTier (doc 08)  |
| B.11  | AUTO-03 Pré-génération quotidienne                    | 1 jour   | Pipeline existant       |
| D.2   | AUTO-04 Suggestions récurrentes                       | 1.5 jour | AUTO-03 + Explicabilité |
| D.3   | AUTO-05 Notifications in-app                          | 2 jours  | AUTH existant           |

---

## 5. Impacts

| Axe         | Impact                                                                                                     |
| ----------- | ---------------------------------------------------------------------------------------------------------- |
| Backend     | +2 modèles (GridDrawResult, UserNotification), +1 service (SuggestionService), +1 job (check_played_grids) |
| Frontend    | Dashboard redesigné (7 blocs), +NotificationBell/Dropdown                                                  |
| API         | +4 endpoints notifications, +1 GET suggestion                                                              |
| Base        | +2 tables, extension nightly_pipeline                                                                      |
| Scheduler   | +1 job check_played_grids, extension pré-génération                                                        |
| Performance | Vérification grilles : O(grilles_jouées × 1) par tirage — négligeable                                      |

---

## 6. Risques

| Risque                             | Probabilité | Impact   | Mitigation                                                 |
| ---------------------------------- | ----------- | -------- | ---------------------------------------------------------- |
| Dashboard trop chargé              | Moyenne     | Moyen    | Layout responsive, collapsible, mode simplifié             |
| Notifications spam                 | Faible      | Moyen    | Limiter à 4 types, pas de push externe                     |
| Suggestion perçue comme prédiction | Moyenne     | Critique | Accompagner systématiquement d'un disclaimer + explication |

---

## 7. Critères d'acceptation

| Critère                                                       | Test                       |
| ------------------------------------------------------------- | -------------------------- |
| Dashboard affiche 7 blocs dynamiques                          | Test visuel                |
| Grilles jouées vérifiées automatiquement après nouveau tirage | Test intégration scheduler |
| Pré-génération produit des données consultables au login      | Test pipeline              |
| Notifications créées et affichables                           | Test API + frontend        |
| Suggestion accompagnée d'explication L1 et disclaimer         | Vérification contenu       |

---

## 8. Checklist locale

- [ ] AUTO-01 : Créer LatestDrawCard (dernier tirage)
- [ ] AUTO-01 : Créer NextDrawCountdown (compte à rebours)
- [ ] AUTO-01 : Créer PlayedGridsResults (comparaison grilles vs tirage)
- [ ] AUTO-01 : Créer DailyTopGridsCard (top 3 du jour)
- [ ] AUTO-01 : Créer StatOfTheDay (stat fun fact)
- [ ] AUTO-01 : Créer DailySuggestionCard
- [ ] AUTO-01 : Mise en page Dashboard responsive
- [ ] AUTO-02 : Modèle GridDrawResult + migration
- [ ] AUTO-02 : Job check_played_grids dans scheduler
- [ ] AUTO-02 : Logique de comparaison numéros/étoiles vs tirage
- [ ] AUTO-02 : Endpoint GET résultats pour grilles jouées
- [ ] AUTO-03 : Extension nightly_pipeline (pré-génération)
- [ ] AUTO-03 : Tag daily_top / daily_optimal sur grilles/portfolios
- [ ] AUTO-04 : SuggestionService + endpoint GET
- [ ] AUTO-04 : Intégration explication L1 dans la suggestion
- [ ] AUTO-05 : Modèle UserNotification + migration
- [ ] AUTO-05 : 4 endpoints notifications
- [ ] AUTO-05 : NotificationBell + NotificationDropdown composants
- [ ] AUTO-05 : Déclenchement notifications depuis les jobs

Réf. : [27_Checklist_Globale_Evolutions](./27_Checklist_Globale_Evolutions.md)
