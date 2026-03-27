"""Tests for repository layer."""

from datetime import date

import numpy as np
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.draw import Draw
from app.models.game import GameDefinition
from app.repositories.draw_repository import DrawRepository
from app.repositories.game_repository import GameRepository


class TestGameRepository:
    async def test_get_by_slug(self, db_session: AsyncSession, sample_game: GameDefinition):
        repo = GameRepository(db_session)
        game = await repo.get_by_slug("loto-fdj")
        assert game is not None
        assert game.name == "Loto FDJ"
        assert game.numbers_pool == 49

    async def test_get_by_slug_not_found(self, db_session: AsyncSession):
        repo = GameRepository(db_session)
        result = await repo.get_by_slug("nonexistent")
        assert result is None

    async def test_get_active_games(self, db_session: AsyncSession, sample_game: GameDefinition):
        repo = GameRepository(db_session)
        games = await repo.get_active_games()
        assert len(games) >= 1
        assert any(g.slug == "loto-fdj" for g in games)

    async def test_create_game(self, db_session: AsyncSession):
        repo = GameRepository(db_session)
        game = GameDefinition(
            name="Test Game",
            slug="test-game",
            numbers_pool=45,
            numbers_drawn=6,
            min_number=1,
            max_number=45,
            draw_frequency="daily",
            historical_source="test",
        )
        created = await repo.create(game)
        assert created.id is not None
        assert created.slug == "test-game"

    async def test_get_by_id(self, db_session: AsyncSession, sample_game: GameDefinition):
        repo = GameRepository(db_session)
        game = await repo.get(sample_game.id)
        assert game is not None
        assert game.slug == "loto-fdj"


class TestDrawRepository:
    async def test_get_latest(
        self, db_session: AsyncSession, sample_game: GameDefinition, sample_draws: list[Draw]
    ):
        repo = DrawRepository(db_session)
        latest = await repo.get_latest(sample_game.id, limit=3)
        assert len(latest) == 3
        # Should be ordered by date descending
        assert latest[0].draw_date >= latest[1].draw_date

    async def test_get_by_date_range(
        self, db_session: AsyncSession, sample_game: GameDefinition, sample_draws: list[Draw]
    ):
        repo = DrawRepository(db_session)
        draws = await repo.get_by_date_range(
            sample_game.id,
            start=date(2026, 1, 10),
            end=date(2026, 1, 20),
        )
        assert len(draws) >= 1
        for draw in draws:
            assert date(2026, 1, 10) <= draw.draw_date <= date(2026, 1, 20)

    async def test_get_numbers_matrix(
        self, db_session: AsyncSession, sample_game: GameDefinition, sample_draws: list[Draw]
    ):
        repo = DrawRepository(db_session)
        matrix = await repo.get_numbers_matrix(sample_game.id)
        assert isinstance(matrix, np.ndarray)
        assert matrix.shape == (10, 5)  # 10 draws, 5 numbers each

    async def test_get_numbers_matrix_empty(
        self, db_session: AsyncSession, sample_game: GameDefinition
    ):
        repo = DrawRepository(db_session)
        matrix = await repo.get_numbers_matrix(sample_game.id)
        assert matrix.shape == (0, 0)

    async def test_exists(
        self, db_session: AsyncSession, sample_game: GameDefinition, sample_draws: list[Draw]
    ):
        repo = DrawRepository(db_session)
        assert await repo.exists(sample_game.id, date(2026, 1, 5)) is True
        assert await repo.exists(sample_game.id, date(2099, 1, 1)) is False

    async def test_count(
        self, db_session: AsyncSession, sample_game: GameDefinition, sample_draws: list[Draw]
    ):
        repo = DrawRepository(db_session)
        count = await repo.count(game_id=sample_game.id)
        assert count == 10
