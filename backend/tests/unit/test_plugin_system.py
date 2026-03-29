"""Unit tests for the plugin system."""

import pytest

from app.core.game_definitions import GameConfig, load_all_game_configs
from app.plugins import LotteryPlugin, PluginRegistry, get_registry, register_plugin
from app.plugins.base import LotteryPlugin as BaseLotteryPlugin
from app.plugins.registry import _registry as _global_registry


# ── Fixtures ─────────────────────────────────────────────────────────────────


class _SimpleLotteryPlugin(LotteryPlugin):
    @property
    def game_config(self) -> GameConfig:
        return GameConfig(
            name="Test Lottery",
            slug="test-lottery",
            numbers_pool=45,
            numbers_drawn=6,
            min_number=1,
            max_number=45,
        )


class _WithScraperPlugin(LotteryPlugin):
    class _FakeScraper:
        pass

    @property
    def game_config(self) -> GameConfig:
        return GameConfig(
            name="Lottery With Scraper",
            slug="lottery-with-scraper",
            numbers_pool=49,
            numbers_drawn=6,
            min_number=1,
            max_number=49,
        )

    @property
    def scraper_class(self):
        return self._FakeScraper


@pytest.fixture()
def fresh_registry() -> PluginRegistry:
    """Return a fresh PluginRegistry (independent from the singleton)."""
    return PluginRegistry()


# ── Tests ─────────────────────────────────────────────────────────────────────


class TestLotteryPluginBase:
    def test_slug_shorthand(self):
        plugin = _SimpleLotteryPlugin()
        assert plugin.slug == "test-lottery"

    def test_default_scraper_class_is_none(self):
        plugin = _SimpleLotteryPlugin()
        assert plugin.scraper_class is None

    def test_default_version(self):
        plugin = _SimpleLotteryPlugin()
        assert plugin.version == "1.0.0"

    def test_repr(self):
        plugin = _SimpleLotteryPlugin()
        assert "test-lottery" in repr(plugin)

    def test_abstract_cannot_instantiate(self):
        with pytest.raises(TypeError):
            BaseLotteryPlugin()  # type: ignore[abstract]


class TestPluginRegistry:
    def test_register_plugin(self, fresh_registry: PluginRegistry):
        fresh_registry.register(_SimpleLotteryPlugin)
        assert "test-lottery" in fresh_registry
        assert len(fresh_registry) == 1

    def test_register_wrong_type_raises(self, fresh_registry: PluginRegistry):
        with pytest.raises(TypeError):
            fresh_registry.register(object)  # type: ignore[arg-type]

    def test_duplicate_slug_raises(self, fresh_registry: PluginRegistry):
        fresh_registry.register(_SimpleLotteryPlugin)
        with pytest.raises(ValueError, match="already registered"):
            fresh_registry.register(_SimpleLotteryPlugin)

    def test_unregister(self, fresh_registry: PluginRegistry):
        fresh_registry.register(_SimpleLotteryPlugin)
        fresh_registry.unregister("test-lottery")
        assert "test-lottery" not in fresh_registry

    def test_get_returns_instance(self, fresh_registry: PluginRegistry):
        fresh_registry.register(_SimpleLotteryPlugin)
        plugin = fresh_registry.get("test-lottery")
        assert plugin is not None
        assert isinstance(plugin, _SimpleLotteryPlugin)

    def test_get_unknown_slug_returns_none(self, fresh_registry: PluginRegistry):
        assert fresh_registry.get("unknown") is None

    def test_all_plugins(self, fresh_registry: PluginRegistry):
        fresh_registry.register(_SimpleLotteryPlugin)
        fresh_registry.register(_WithScraperPlugin)
        assert len(fresh_registry.all_plugins()) == 2

    def test_game_configs(self, fresh_registry: PluginRegistry):
        fresh_registry.register(_SimpleLotteryPlugin)
        configs = fresh_registry.game_configs()
        assert "test-lottery" in configs
        assert configs["test-lottery"].numbers_pool == 45

    def test_scraper_map_only_includes_games_with_scrapers(
        self, fresh_registry: PluginRegistry
    ):
        fresh_registry.register(_SimpleLotteryPlugin)
        fresh_registry.register(_WithScraperPlugin)
        scraper_map = fresh_registry.scraper_map()
        assert "test-lottery" not in scraper_map
        assert "lottery-with-scraper" in scraper_map

    def test_repr(self, fresh_registry: PluginRegistry):
        fresh_registry.register(_SimpleLotteryPlugin)
        assert "test-lottery" in repr(fresh_registry)


class TestPluginIntegrationWithGameConfigs:
    def test_plugin_configs_merged_into_load_all(self, fresh_registry: PluginRegistry):
        """Plugin games should appear in load_all_game_configs output."""
        import app.plugins.registry as reg_module

        # Temporarily swap the singleton
        original = reg_module._registry
        reg_module._registry = fresh_registry
        try:
            fresh_registry.register(_SimpleLotteryPlugin)
            configs = load_all_game_configs(include_plugins=True)
            assert "test-lottery" in configs
            assert configs["test-lottery"].numbers_pool == 45
        finally:
            reg_module._registry = original

    def test_yaml_config_takes_precedence_over_plugin(self, fresh_registry: PluginRegistry):
        """If a plugin slug matches a YAML slug, the YAML config wins."""
        import app.plugins.registry as reg_module

        class _EuroPlugin(LotteryPlugin):
            @property
            def game_config(self) -> GameConfig:
                # Same slug as the real EuroMillions but wrong pool size
                return GameConfig(
                    name="Fake Euro",
                    slug="euromillions",
                    numbers_pool=99,
                    numbers_drawn=5,
                    min_number=1,
                    max_number=99,
                )

        original = reg_module._registry
        reg_module._registry = fresh_registry
        try:
            fresh_registry.register(_EuroPlugin)
            configs = load_all_game_configs(include_plugins=True)
            # YAML value (50) must win over plugin value (99)
            assert configs["euromillions"].numbers_pool == 50
        finally:
            reg_module._registry = original

    def test_include_plugins_false_excludes_plugin_games(self, fresh_registry: PluginRegistry):
        import app.plugins.registry as reg_module

        original = reg_module._registry
        reg_module._registry = fresh_registry
        try:
            fresh_registry.register(_SimpleLotteryPlugin)
            configs = load_all_game_configs(include_plugins=False)
            assert "test-lottery" not in configs
        finally:
            reg_module._registry = original


class TestRegisterPluginHelper:
    def test_register_plugin_uses_singleton(self):
        """register_plugin() should write into the global singleton."""
        registry = get_registry()
        registry.unregister("test-lottery")  # ensure clean state

        try:
            register_plugin(_SimpleLotteryPlugin)
            assert "test-lottery" in registry
        finally:
            registry.unregister("test-lottery")


class TestEuroMillionsPluginExample:
    def test_euromillions_plugin_loads(self):
        from app.plugins.examples.euromillions_plugin import EuroMillionsPlugin

        plugin = EuroMillionsPlugin()
        assert plugin.slug == "euromillions-plugin"
        assert plugin.game_config.stars_drawn == 2
        assert plugin.scraper_class is not None

    def test_euromillions_plugin_register(self):
        from app.plugins.examples.euromillions_plugin import EuroMillionsPlugin

        registry = PluginRegistry()
        registry.register(EuroMillionsPlugin)
        assert "euromillions-plugin" in registry
        assert registry.get("euromillions-plugin").version == "1.0.0"
