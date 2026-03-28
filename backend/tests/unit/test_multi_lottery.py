"""Tests for multi-lottery support — ensure game_id dispatches correctly."""

import pytest

from app.core.game_definitions import GameConfig, load_all_game_configs


class TestLoadAllGameConfigs:
    """Verify YAML configs load and sort correctly."""

    def test_loads_three_games(self):
        configs = load_all_game_configs()
        assert len(configs) == 3

    def test_sorted_order_euromillions_first(self):
        configs = load_all_game_configs()
        slugs = list(configs.keys())
        assert slugs[0] == "euromillions"
        assert "loto-fdj" in slugs
        assert "keno" in slugs

    def test_euromillions_fields(self):
        configs = load_all_game_configs()
        em = configs["euromillions"]
        assert em.numbers_pool == 50
        assert em.numbers_drawn == 5
        assert em.stars_pool == 12
        assert em.stars_drawn == 2

    def test_loto_fdj_fields(self):
        configs = load_all_game_configs()
        loto = configs["loto-fdj"]
        assert loto.numbers_pool == 49
        assert loto.numbers_drawn == 5
        assert loto.stars_pool == 10
        assert loto.stars_drawn == 1


class TestGameConfigBySlug:
    """Verify load_all_game_configs returns configs keyed by slug."""

    def test_euromillions_config(self):
        configs = load_all_game_configs()
        assert "euromillions" in configs
        assert configs["euromillions"].numbers_pool == 50
        assert configs["euromillions"].stars_drawn == 2

    def test_loto_fdj_config(self):
        configs = load_all_game_configs()
        assert "loto-fdj" in configs
        assert configs["loto-fdj"].numbers_pool == 49
        assert configs["loto-fdj"].stars_drawn == 1

    def test_keno_config(self):
        configs = load_all_game_configs()
        assert "keno" in configs
        assert configs["keno"].numbers_pool == 70

    def test_unknown_slug_returns_none(self):
        configs = load_all_game_configs()
        assert configs.get("unknown") is None

    def test_configs_differ(self):
        configs = load_all_game_configs()
        assert configs["euromillions"] != configs["loto-fdj"]
        assert configs["euromillions"].stars_pool != configs["loto-fdj"].stars_pool


class TestGameConfigIsolation:
    """Ensure game configs are distinct and produce different constraints."""

    def test_euromillions_has_more_stars(self):
        configs = load_all_game_configs()
        em = configs["euromillions"]
        loto = configs["loto-fdj"]
        assert em.stars_drawn > loto.stars_drawn

    def test_max_number_differs(self):
        configs = load_all_game_configs()
        em = configs["euromillions"]
        loto = configs["loto-fdj"]
        assert em.max_number == 50
        assert loto.max_number == 49

    def test_star_names_differ(self):
        configs = load_all_game_configs()
        em = configs["euromillions"]
        loto = configs["loto-fdj"]
        assert em.star_name != loto.star_name
