"""Abstract base class for LOTO ULTIME lottery plugins."""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.core.game_definitions import GameConfig
    from app.scrapers.base import BaseScraper


class LotteryPlugin(ABC):
    """Base class for lottery plugins.

    A plugin packages all the data and behaviour needed to support a new
    lottery game without touching the core codebase.

    Minimum implementation
    ~~~~~~~~~~~~~~~~~~~~~~
    Subclasses *must* implement :attr:`game_config`.  Everything else is
    optional and falls back to sensible defaults.
    """

    # ── Required ─────────────────────────────────────────────────────────────

    @property
    @abstractmethod
    def game_config(self) -> "GameConfig":
        """Return the :class:`~app.core.game_definitions.GameConfig` for this game."""

    # ── Optional — scraper ───────────────────────────────────────────────────

    @property
    def scraper_class(self) -> "type[BaseScraper] | None":
        """Return the scraper class for this game, or *None* to skip scraping.

        When *None*, the scheduler will not attempt to fetch draws
        automatically.  Historical data must be imported manually.
        """
        return None

    # ── Optional — metadata ──────────────────────────────────────────────────

    @property
    def version(self) -> str:
        """Plugin version string (semver recommended)."""
        return "1.0.0"

    @property
    def author(self) -> str:
        """Plugin author."""
        return "Unknown"

    @property
    def description(self) -> str:
        """Human-readable plugin description."""
        return self.game_config.description or self.game_config.name

    # ── Lifecycle ────────────────────────────────────────────────────────────

    def on_register(self) -> None:
        """Called once when the plugin is registered.

        Override to perform one-time initialisation (e.g. warming up a cache).
        The default implementation does nothing.
        """

    # ── Helpers ──────────────────────────────────────────────────────────────

    @property
    def slug(self) -> str:
        """Shorthand for ``game_config.slug``."""
        return self.game_config.slug

    def __repr__(self) -> str:
        return f"<{type(self).__name__} slug={self.slug!r} v{self.version}>"
