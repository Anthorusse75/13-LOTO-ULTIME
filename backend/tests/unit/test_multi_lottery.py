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


class TestGameConfigById:
    """Verify the _game_config_by_id mapping matches the DB-seeded order."""

    def _build_config_by_id(self):
        configs = load_all_game_configs()
        return {i + 1: cfg for i, cfg in enumerate(configs.values())}

    def test_game_id_1_is_euromillions(self):
        by_id = self._build_config_by_id()
        assert by_id[1].slug == "euromillions"
        assert by_id[1].numbers_pool == 50
        assert by_id[1].stars_drawn == 2

    def test_game_id_2_is_keno(self):
        by_id = self._build_config_by_id()
        assert by_id[2].slug == "keno"
        assert by_id[2].numbers_pool == 70
        assert by_id[2].stars_drawn == 0

    def test_unknown_game_id_returns_none(self):
        by_id = self._build_config_by_id()
        assert by_id.get(99) is None

    def test_configs_differ(self):
        by_id = self._build_config_by_id()
        assert by_id[1] != by_id[2]
        assert by_id[1].stars_pool != by_id[2].stars_pool


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
