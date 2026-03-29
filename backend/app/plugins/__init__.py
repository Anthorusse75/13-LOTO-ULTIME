"""Plugin system for LOTO ULTIME.

Allows third-party lottery configurations to be registered without modifying
the core codebase. A plugin provides at minimum a GameConfig and, optionally,
a custom scraper and custom engine overrides.

Usage
-----
1. Subclass ``LotteryPlugin``.
2. Implement the required properties.
3. Call ``register_plugin(MyPlugin)`` at application startup (or via a
   package entry-point once that feature is wired).

Example
-------
    from app.plugins import LotteryPlugin, register_plugin
    from app.core.game_definitions import GameConfig

    class MyLotteryPlugin(LotteryPlugin):
        @property
        def game_config(self) -> GameConfig:
            return GameConfig(
                name="My Lottery",
                slug="my-lottery",
                numbers_pool=45,
                numbers_drawn=6,
                min_number=1,
                max_number=45,
            )

    register_plugin(MyLotteryPlugin)
"""

from app.plugins.base import LotteryPlugin
from app.plugins.registry import PluginRegistry, get_registry, register_plugin

__all__ = ["LotteryPlugin", "PluginRegistry", "get_registry", "register_plugin"]
