"""Tests for Pydantic schemas validation."""
from datetime import date, datetime

import pytest
from pydantic import ValidationError

from app.schemas.draw import DrawCreate, DrawResponse
from app.schemas.game import GameDefinitionCreate, GameDefinitionResponse
from app.schemas.grid import GridGenerateRequest


class TestGameSchemas:
    def test_game_create_valid(self):
        game = GameDefinitionCreate(
            name="Test",
            slug="test-game",
            numbers_pool=49,
            numbers_drawn=5,
            max_number=49,
        )
        assert game.slug == "test-game"
        assert game.min_number == 1

    def test_game_create_invalid_slug(self):
        with pytest.raises(ValidationError):
            GameDefinitionCreate(
                name="Test",
                slug="INVALID SLUG!",
                numbers_pool=49,
                numbers_drawn=5,
                max_number=49,
            )

    def test_game_create_pool_too_small(self):
        with pytest.raises(ValidationError):
            GameDefinitionCreate(
                name="Test",
                slug="test",
                numbers_pool=2,  # min 5
                numbers_drawn=1,
                max_number=2,
            )

    def test_game_response_from_attributes(self):
        class FakeGame:
            id = 1
            name = "Loto"
            slug = "loto"
            numbers_pool = 49
            numbers_drawn = 5
            min_number = 1
            max_number = 49
            stars_pool = 10
            stars_drawn = 1
            star_name = "chance"
            draw_frequency = "lun/mer"
            is_active = True

        resp = GameDefinitionResponse.model_validate(FakeGame())
        assert resp.id == 1
        assert resp.slug == "loto"


class TestDrawSchemas:
    def test_draw_create_valid(self):
        draw = DrawCreate(
            draw_date=date(2026, 1, 1),
            numbers=[1, 7, 23, 34, 45],
            stars=[3],
        )
        assert len(draw.numbers) == 5

    def test_draw_create_empty_numbers(self):
        with pytest.raises(ValidationError):
            DrawCreate(
                draw_date=date(2026, 1, 1),
                numbers=[],
            )


class TestGridSchemas:
    def test_grid_request_defaults(self):
        req = GridGenerateRequest()
        assert req.count == 10
        assert req.method == "auto"

    def test_grid_request_invalid_method(self):
        with pytest.raises(ValidationError):
            GridGenerateRequest(method="invalid_method")

    def test_grid_request_count_bounds(self):
        with pytest.raises(ValidationError):
            GridGenerateRequest(count=0)
        with pytest.raises(ValidationError):
            GridGenerateRequest(count=200)
