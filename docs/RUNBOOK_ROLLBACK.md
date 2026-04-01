# RUNBOOK — Rollback LOTO ULTIME

## Quand effectuer un rollback

- Erreur critique après déploiement (500 en cascade, DB corrompue)
- Régression fonctionnelle identifiée
- Tests de smoke échoués post-déploiement

## 1. Rollback applicatif (code)

```bash
# Identifier le dernier commit stable
git log --oneline -10

# Revenir au commit précédent
git checkout <commit-sha>

# Rebuild + redéployer
cd frontend && npm ci && npm run build
cd ../backend && pip install -r requirements.txt

# Relancer le serveur
sudo systemctl restart loto-ultime
```

## 2. Rollback de migration (base de données)

```bash
cd backend

# Voir l'état actuel
alembic current

# Voir l'historique
alembic history --verbose

# Revenir d'une migration
alembic downgrade -1

# Revenir à une révision spécifique
alembic downgrade <revision_id>

# Exemples de révisions connues :
# f1a2b3c4d5e6  — Phase C: budget_plans
# e5f6a7b8c9d0  — Phase C: wheeling_systems
# d4e5f6a7b8c9  — Phase B: models
# a1b2c3d4e5f6  — Phase E: secondary indexes
```

> **Attention** : Un `downgrade` supprime les index/tables créés par la migration.
> Sauvegarder les données critiques avant rollback si nécessaire.

## 3. Rollback Redis / Cache

```bash
# Vider le cache si des données incohérentes sont suspectées
redis-cli FLUSHDB

# Ou invalider un préfixe spécifique
redis-cli KEYS "loto:stats:*" | xargs redis-cli DEL
```

## 4. Rollback partiel (feature flag)

Si le problème est isolé à une fonctionnalité :

```bash
# Désactiver la feature via variable d'environnement
export FEATURE_WHEELING_ENABLED=false
export FEATURE_BUDGET_OPTIMIZER_ENABLED=false
export FEATURE_EXPORT_PDF_ENABLED=false

# Relancer sans redéployer le code
sudo systemctl restart loto-ultime
```

Voir `backend/app/core/feature_flags.py` pour la liste complète des flags.

## 5. Vérification post-rollback

```bash
# Health check
curl -s https://loto-ultime.example.com/api/v1/health | jq .

# Vérifier la version de migration
cd backend && alembic current

# Vérifier les logs d'erreur
journalctl -u loto-ultime --since "10 minutes ago" | grep ERROR

# Smoke tests manuels
curl -s https://loto-ultime.example.com/api/v1/games | jq '.[] | .name'
curl -s https://loto-ultime.example.com/api/v1/draws/loto-fdj/latest | jq .draw_date
```

## 6. Communication

Après un rollback :
1. Documenter l'incident (cause, impact, durée)
2. Créer une issue GitHub avec le label `incident`
3. Planifier le correctif avant re-déploiement

## 7. Points de contact

| Rôle | Responsabilité |
|------|---------------|
| Dev Backend | Rollback migrations, logs serveur |
| Dev Frontend | Rollback build, vérification UI |
| Ops | Infra, Nginx, monitoring Grafana |
