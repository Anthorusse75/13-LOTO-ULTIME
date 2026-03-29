"""Example plugin: EuroMillions.

This module re-packages the EuroMillions game as a :class:`LotteryPlugin`,
serving as a reference implementation for plugin authors.

It is **not** auto-registered at startup — the core YAML configs already cover
EuroMillions.  To load it explicitly (e.g. in tests):

    from app.plugins.examples.euromillions_plugin import EuroMillionsPlugin
    from app.plugins import register_plugin
    register_plugin(EuroMillionsPlugin)
"""

from app.core.game_definitions import GameConfig
from app.plugins.base import LotteryPlugin
from app.scrapers.euromillions import EuroMillionsScraper


class EuroMillionsPlugin(LotteryPlugin):
    """EuroMillions plugin — reference implementation.

    Demonstrates how to wrap an existing game + scraper into the plugin system.
    Slug: ``euromillions-plugin`` (distinct from the built-in ``euromillions``).
    """

    @property
    def game_config(self) -> GameConfig:
        return GameConfig(
            name="EuroMillions (Plugin)",
            slug="euromillions-plugin",
            numbers_pool=50,
            numbers_drawn=5,
            min_number=1,
            max_number=50,
            stars_pool=12,
            stars_drawn=2,
            star_name="étoile",
            draw_frequency="mar/ven",
            historical_source="euromillions",
            description="EuroMillions via plugin system (demo)",
        )

    @property
    def scraper_class(self) -> type[EuroMillionsScraper]:
        return EuroMillionsScraper

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def author(self) -> str:
        return "LOTO ULTIME Core Team"

    def on_register(self) -> None:
        import structlog

        structlog.get_logger(__name__).info("euromillions_plugin_registered", slug=self.slug)
