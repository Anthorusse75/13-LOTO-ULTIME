# 12. Priorisation des Améliorations

Ce chapitre synthétise **toutes les actions identifiées** dans l'audit et les organise selon une matrice de priorisation à quatre niveaux. Chaque action est classée en utilisant deux axes :

- **Priorité** : Indispensable → Très utile → Avancé → Premium/Recherche
- **Nature** : 🔧 Correction (bug/dette) | 📈 Amélioration | 🚀 Feature | 🔬 Recherche

Le classement tient compte de l'**impact utilisateur**, de l'**effort de développement**, et des **dépendances** entre les actions.

---

## 12.1 Indispensable — À faire immédiatement

Ces actions sont des **prérequis** pour que le produit fonctionne correctement. Sans elles, des fonctionnalités annoncées sont cassées ou le développement futur est bloqué.

| #   | Action                                                                     | Nature | Effort | Impact       | Dépendances |
| --- | -------------------------------------------------------------------------- | ------ | ------ | ------------ | ----------- |
| 1   | Corriger `_get_game_config()` pour filtrer sur `game_id`                   | 🔧      | 2h     | 🔴 Critique   | Aucune      |
| 2   | Intégrer les étoiles dans tous les moteurs (stats, scoring, opti, simu)    | 🔧      | 3-5j   | 🔴 Critique   | Action 1    |
| 3   | Intégrer Alembic pour les migrations de base de données                    | 🔧      | 1j     | 🔴 Bloquant   | Aucune      |
| 4   | Câbler le sélecteur de profil dans GridsPage (ou le retirer)               | 🔧      | 0.5j   | 🔴 Visible    | Aucune      |
| 5   | Corriger `select_method()` pour que SA soit accessible                     | 🔧      | 0.5j   | 🟠            | Aucune      |
| 6   | Activer `PRAGMA foreign_keys = ON` dans la config SQLAlchemy               | 🔧      | 1h     | 🟠            | Aucune      |
| 7   | Corriger `count()` dans tous les repositories (`SELECT COUNT(*)`)          | 🔧      | 0.5j   | 🟠            | Aucune      |
| 8   | Ajouter le rate limiting sur les endpoints de calcul                       | 🔧      | 0.5j   | 🟠            | Aucune      |
| 9   | Écrire des tests multi-loteries (Loto vs EuroMillions)                     | 🔧      | 1j     | 🔴 Prévention | Action 1+2  |
| 10  | Corriger GraphEngine (eigenvector fallback → valeurs uniformes, pas zéros) | 🔧      | 2h     | 🟡            | Aucune      |

**Total estimé : 7-10 jours de développement**

**Séquence recommandée** :
1. Actions 1, 3, 6, 7, 8, 10 (rapides, indépendantes → en parallèle)
2. Action 2 (étoiles — le plus gros chantier, dépend de 1)
3. Actions 4 et 5 (UX et algo)
4. Action 9 (tests — après que 1+2 soient fonctionnels)

---

## 12.2 Très utile — Qualité produit et solidité

Ces actions transforment le prototype fonctionnel en un **produit fiable et agréable** à utiliser. Elles ne bloquent rien mais leur absence se ressent au quotidien.

| #   | Action                                                                     | Nature | Effort | Impact             |
| --- | -------------------------------------------------------------------------- | ------ | ------ | ------------------ |
| 11  | Ajouter des tooltips explicatifs partout (stats, scoring, grilles)         | 📈      | 2j     | 🟠 Compréhension    |
| 12  | Améliorer les états vides avec aide contextuelle (CTA, guide)              | 📈      | 1j     | 🟠 UX               |
| 13  | Remplacer les messages d'erreur techniques par des messages user-friendly  | 📈      | 1j     | 🟠 UX               |
| 14  | Ajouter un orchestrateur pipeline (chaînage séquentiel des jobs)           | 📈      | 1j     | 🟠 Robustesse       |
| 15  | Implémenter le nettoyage automatique des vieilles grilles et portfolios    | 📈      | 0.5j   | 🟠 Maintenance      |
| 16  | Corriger les couleurs hardcodées Recharts/D3 (CSS variables)               | 🔧      | 1j     | 🟡 UX visuelle      |
| 17  | Ajouter la régression temporelle configurable (8-12 fenêtres + R²)         | 📈      | 1j     | 🟡 Qualité algo     |
| 18  | Plafonner PatternPenalty stacking (-0.3 max)                               | 🔧      | 2h     | 🟡 Qualité scoring  |
| 19  | Ajouter la normalisation z-score en alternative à min-max                  | 📈      | 0.5j   | 🟡 Qualité scoring  |
| 20  | Ajouter le support du graceful shutdown (wait=True + timeout)              | 📈      | 2h     | 🟡 Robustesse       |
| 21  | Ajouter un backup automatique hebdomadaire de la base SQLite               | 📈      | 0.5j   | 🟡 Sécurité données |
| 22  | Configurer les URLs des scrapers en externe (fichier config ou DB)         | 📈      | 0.5j   | 🟡 Maintenabilité   |
| 23  | Supprimer le code mort frontend (composants importés mais non utilisés)    | 🔧      | 0.5j   | 🟡 Propreté         |
| 24  | Ajouter des confirmations avant actions destructives (supprimer portfolio) | 📈      | 0.5j   | 🟡 UX               |
| 25  | Ajouter les endpoints DELETE et PATCH manquants                            | 📈      | 1j     | 🟡 API complète     |
| 26  | Implémenter une DTO/schema layer séparant models des réponses API          | 📈      | 2j     | 🟡 Architecture     |

**Total estimé : 13-14 jours de développement**

---

## 12.3 Avancé — Profondeur et sophistication

Ces actions enrichissent le produit avec des fonctionnalités qui augmentent sa **valeur perçue** et sa **crédibilité analytique**. Elles construisent sur une base déjà solide.

| #   | Action                                                                     | Nature | Effort | Impact          |
| --- | -------------------------------------------------------------------------- | ------ | ------ | --------------- |
| 27  | Ajouter un dashboard synthétique (résumé en une page)                      | 🚀      | 3j     | 🟠 UX majeure    |
| 28  | Implémenter l'assistant/coach IA contextuel                                | 🚀      | 5j     | 🟠 Différenciant |
| 29  | Ajouter l'historique de performance (suivi des gains/pertes)               | 🚀      | 3j     | 🟠 Engagement    |
| 30  | Implémenter les filtres temporels sur les statistiques                     | 🚀      | 2j     | 🟠 Analyse       |
| 31  | Ajouter des tests E2E avec Playwright                                      | 📈      | 3j     | 🟡 Qualité       |
| 32  | Ajouter des tests unitaires frontend (Vitest + Testing Library)            | 📈      | 3j     | 🟡 Qualité       |
| 33  | Implémenter un système de favoris/bookmarks pour les grilles               | 🚀      | 2j     | 🟡 Engagement    |
| 34  | Ajouter l'export PDF des grilles et analyses                               | 🚀      | 2j     | 🟡 Utilitaire    |
| 35  | Implémenter les notifications temps réel (WebSocket) pour nouveaux tirages | 🚀      | 3j     | 🟡 Premium       |
| 36  | Ajouter un mode comparaison entre stratégies d'optimisation                | 🚀      | 2j     | 🟡 Analyse       |
| 37  | Implémenter le support de loteries supplémentaires (Keno, etc.)            | 🚀      | 5j     | 🟠 Expansion     |
| 38  | Ajouter des métriques Prometheus et un dashboard monitoring                | 📈      | 2j     | 🟡 Opérations    |
| 39  | Implémenter un cache Redis pour les résultats de calcul                    | 📈      | 2j     | 🟡 Performance   |
| 40  | Ajouter l'internationalisation (i18n)                                      | 🚀      | 3j     | 🟡 Expansion     |

**Total estimé : 40-45 jours de développement**

---

## 12.4 Premium / Recherche — Différenciation long terme

Ces actions positionnent le produit sur un segment premium ou explorent des pistes de recherche avancée. Elles requièrent une base solide et des données abondantes.

| #   | Action                                                                        | Nature | Effort | Impact             |
| --- | ----------------------------------------------------------------------------- | ------ | ------ | ------------------ |
| 41  | Intégrer un modèle ML de prédiction de tendances                              | 🔬      | 10j    | 🟡 Recherche        |
| 42  | Implémenter la simulation multi-agent (différentes stratégies en compétition) | 🔬      | 5j     | 🟡 Recherche        |
| 43  | Ajouter un moteur de clustering pour identifier les familles de tirages       | 🔬      | 3j     | 🟡 Analyse          |
| 44  | Implémenter le backtesting sur données historiques avec rapport détaillé      | 🚀      | 5j     | 🟠 Différenciant    |
| 45  | Ajouter une API publique documentée (OpenAPI/Swagger amélioré)                | 🚀      | 3j     | 🟡 Expansion        |
| 46  | Supporter le multi-utilisateur avec profils distincts                         | 🚀      | 5j     | 🟡 Expansion        |
| 47  | Migration vers PostgreSQL pour le multi-tenant                                | 📈      | 2j     | 🟡 Scalabilité      |
| 48  | Implémenter une Progressive Web App (PWA) avec mode offline                   | 🚀      | 3j     | 🟡 Mobile           |
| 49  | Ajouter un système de templating pour les stratégies utilisateur              | 🚀      | 3j     | 🟡 Personnalisation |
| 50  | Conteneurisation Docker + CI/CD GitHub Actions                                | 📈      | 2j     | 🟡 DevOps           |

**Total estimé : 40-50 jours de développement**

---

## 12.5 Matrice effort/impact

```
         ┌─────────────────────────────────────────────┐
         │                 IMPACT ÉLEVÉ                 │
         │                                              │
  EFFORT │  [1] game_config  [3] Alembic               │
  FAIBLE │  [6] FK pragma    [7] count()                │
         │  [5] select_method [8] rate limit            │
         │  [4] profil câblé                            │
●────────┼──────────────────────────────────────────────┤
         │  [2] Étoiles      [11] Tooltips              │
  EFFORT │  [9] Tests multi  [27] Dashboard             │
  MOYEN  │  [14] Pipeline    [28] Coach IA              │
         │  [13] Messages    [29] Historique            │
         │  [30] Filtres     [37] Loteries supp.        │
●────────┼──────────────────────────────────────────────┤
         │  [44] Backtesting [41] ML prédiction         │
  EFFORT │  [46] Multi-user  [42] Multi-agent           │
  ÉLEVÉ  │  [31] Tests E2E   [40] i18n                  │
         │                                              │
         └─────────────────────────────────────────────┘
```

**Les quick wins** (effort faible, impact élevé) sont les actions 1, 3, 4, 5, 6, 7, 8 — elles devraient être traitées en premier, possiblement dans une seule session de développement de 2-3 jours.

---

## 12.6 Synthèse par nature d'action

| Catégorie     | Corrections 🔧 | Améliorations 📈 | Features 🚀 | Recherche 🔬 | Total  |
| ------------- | ------------- | --------------- | ---------- | ----------- | ------ |
| Indispensable | 10            | 0               | 0          | 0           | **10** |
| Très utile    | 3             | 13              | 0          | 0           | **16** |
| Avancé        | 0             | 6               | 8          | 0           | **14** |
| Premium       | 0             | 2               | 5          | 3           | **10** |
| **Total**     | **13**        | **21**          | **13**     | **3**       | **50** |

**Lecture** : Sur 50 actions identifiées, 13 sont des corrections de bugs ou de dette technique. Le ratio corrections/nouvelles features est de 26%, ce qui est normal pour un projet en phase de consolidation. Les 10 actions indispensables sont **toutes des corrections**, confirmant que la priorité immédiate est de stabiliser l'existant avant d'ajouter du neuf.
