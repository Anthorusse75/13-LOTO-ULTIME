"""Plugin registry — central store for registered lottery plugins.

Plugins registered here are merged into the game-config catalogue at
application startup, extending :func:`~app.core.game_definitions.load_all_game_configs`
                              with any plugin-provided games.
"""

from __future__ import annotations

import structlog

from app.plugins.base import LotteryPlugin

logger = structlog.get_logger(__name__)


class PluginRegistry:
    """Thread-safe registry of :class:`~app.plugins.base.LotteryPlugin` instances.

    This is a singleton — use :func:`get_registry` to obtain the shared
    instance rather than constructing a new one.
    """

    def __init__(self) -> None:
        self._plugins: dict[str, LotteryPlugin] = {}

    # ── Registration ─────────────────────────────────────────────────────────

    def register(self, plugin_cls: type[LotteryPlugin]) -> None:
        """Instantiate and register *plugin_cls*.

        Raises
        ------
        TypeError
            If *plugin_cls* is not a subclass of :class:`LotteryPlugin`.
        ValueError
            If a plugin with the same slug is already registered.
        """
        if not (isinstance(plugin_cls, type) and issubclass(plugin_cls, LotteryPlugin)):
            raise TypeError(f"{plugin_cls!r} is not a LotteryPlugin subclass")

        instance = plugin_cls()
        slug = instance.slug

        if slug in self._plugins:
            raise ValueError(
                f"Plugin with slug '{slug}' is already registered "
                f"(registered by {type(self._plugins[slug]).__name__!r})"
            )

        instance.on_register()
        self._plugins[slug] = instance
        logger.info("plugin_registered", slug=slug, plugin=repr(instance))

    def unregister(self, slug: str) -> None:
        """Remove a plugin by slug (useful in tests)."""
        self._plugins.pop(slug, None)

    # ── Lookup ───────────────────────────────────────────────────────────────

    def get(self, slug: str) -> LotteryPlugin | None:
        """Return the plugin for *slug*, or *None* if not registered."""
        return self._plugins.get(slug)

    def all_plugins(self) -> list[LotteryPlugin]:
        """Return all registered plugin instances."""
        return list(self._plugins.values())

    # ── Integration with game_definitions ────────────────────────────────────

    def game_configs(self) -> dict[str, "GameConfig"]:  # type: ignore[name-defined]
        """Return a ``{slug: GameConfig}`` dict for all registered plugins.

        This dict can be *merged* with the YAML-loaded configs so that
        plugin games become first-class citizens in the engine pipeline.
        """
        from app.core.game_definitions import GameConfig  # local import to avoid circular

        return {slug: plugin.game_config for slug, plugin in self._plugins.items()}

    def scraper_map(self) -> dict[str, "type[BaseScraper]"]:  # type: ignore[name-defined]
        """Return a ``{slug: ScraperClass}`` dict for plugins that provide a scraper."""
        from app.scrapers.base import BaseScraper  # local import

        result: dict[str, type[BaseScraper]] = {}
        for slug, plugin in self._plugins.items():
            if plugin.scraper_class is not None:
                result[slug] = plugin.scraper_class
        return result

    # ── Dunder ───────────────────────────────────────────────────────────────

    def __len__(self) -> int:
        return len(self._plugins)

    def __contains__(self, slug: str) -> bool:
        return slug in self._plugins

    def __repr__(self) -> str:
        slugs = list(self._plugins)
        return f"<PluginRegistry plugins={slugs!r}>"


# ── Singleton ────────────────────────────────────────────────────────────────

_registry: PluginRegistry | None = None


def get_registry() -> PluginRegistry:
    """Return the application-wide :class:`PluginRegistry` singleton."""
    global _registry
    if _registry is None:
        _registry = PluginRegistry()
    return _registry


def register_plugin(plugin_cls: type[LotteryPlugin]) -> None:
    """Convenience shorthand for ``get_registry().register(plugin_cls)``."""
    get_registry().register(plugin_cls)
