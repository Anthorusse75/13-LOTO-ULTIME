"""Application-level caches — TTLCache instances for hot data."""

from cachetools import TTLCache

# Latest statistics snapshot per game_id — TTL 1h, max 5 games
stats_cache: TTLCache = TTLCache(maxsize=5, ttl=3600)

# Game definitions loaded from YAML — TTL 24h, single entry
game_defs_cache: TTLCache = TTLCache(maxsize=1, ttl=86400)
