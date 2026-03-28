"""Unit tests for scrapers (base, FDJ, EuroMillions)."""

from datetime import date
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.scrapers.base import BaseScraper, DrawValidator, RawDraw


class TestDrawValidator:
    """Tests for draw data validation."""

    def setup_method(self):
        self.validator = DrawValidator(
            min_number=1,
            max_number=49,
            numbers_drawn=5,
            stars_pool=10,
            stars_drawn=1,
        )

    def test_validate_valid_draw(self):
        raw = RawDraw(
            draw_date=date(2024, 1, 15),
            draw_number=2024001,
            numbers=[5, 12, 23, 34, 45],
            stars=[7],
        )
        validated = self.validator.validate(raw)
        assert validated.numbers == [5, 12, 23, 34, 45]
        assert validated.stars == [7]

    def test_validate_preserves_order(self):
        raw = RawDraw(
            draw_date=date(2024, 1, 15),
            draw_number=2024001,
            numbers=[45, 12, 5, 34, 23],
            stars=[7],
        )
        validated = self.validator.validate(raw)
        assert validated.numbers == [45, 12, 5, 34, 23]  # Not sorted by validator

    def test_validate_wrong_count(self):
        raw = RawDraw(
            draw_date=date(2024, 1, 15),
            draw_number=2024001,
            numbers=[5, 12, 23, 34],  # Only 4 numbers
            stars=[7],
        )
        with pytest.raises(ValueError, match="numbers"):
            self.validator.validate(raw)

    def test_validate_number_out_of_range(self):
        raw = RawDraw(
            draw_date=date(2024, 1, 15),
            draw_number=2024001,
            numbers=[5, 12, 23, 34, 55],  # 55 > max 49
            stars=[7],
        )
        with pytest.raises(ValueError, match="range"):
            self.validator.validate(raw)

    def test_validate_duplicate_numbers(self):
        raw = RawDraw(
            draw_date=date(2024, 1, 15),
            draw_number=2024001,
            numbers=[5, 12, 12, 34, 45],  # duplicate 12
            stars=[7],
        )
        with pytest.raises(ValueError, match="Duplicate"):
            self.validator.validate(raw)

    def test_validate_wrong_star_count(self):
        raw = RawDraw(
            draw_date=date(2024, 1, 15),
            draw_number=2024001,
            numbers=[5, 12, 23, 34, 45],
            stars=[7, 3],  # 2 stars, expected 1
        )
        with pytest.raises(ValueError, match="stars"):
            self.validator.validate(raw)

    def test_validate_star_out_of_range(self):
        raw = RawDraw(
            draw_date=date(2024, 1, 15),
            draw_number=2024001,
            numbers=[5, 12, 23, 34, 45],
            stars=[15],  # > stars_pool 10
        )
        with pytest.raises(ValueError, match="range"):
            self.validator.validate(raw)

    def test_validate_no_stars_when_none_expected(self):
        validator = DrawValidator(
            min_number=1,
            max_number=49,
            numbers_drawn=5,
            stars_pool=0,
            stars_drawn=0,
        )
        raw = RawDraw(
            draw_date=date(2024, 1, 15),
            draw_number=2024001,
            numbers=[5, 12, 23, 34, 45],
            stars=[],
        )
        validated = validator.validate(raw)
        assert validated.stars == []

    def test_validate_euromillions_format(self):
        validator = DrawValidator(
            min_number=1,
            max_number=50,
            numbers_drawn=5,
            stars_pool=12,
            stars_drawn=2,
        )
        raw = RawDraw(
            draw_date=date(2024, 1, 16),
            draw_number=2024002,
            numbers=[3, 15, 27, 38, 49],
            stars=[2, 11],
        )
        validated = validator.validate(raw)
        assert validated.numbers == [3, 15, 27, 38, 49]
        assert validated.stars == [2, 11]


class TestFDJLotoScraper:
    """Tests for FDJ Loto scraper with mocked HTTP."""

    @pytest.fixture
    def mock_response_data(self):
        return [
            {
                "date": "2024-01-15",
                "numero": 2024001,
                "numeros": [5, 12, 23, 34, 45],
                "numero_chance": 7,
            },
            {
                "date": "2024-01-13",
                "numero": 2024000,
                "numeros": [1, 8, 19, 28, 40],
                "numero_chance": 3,
            },
        ]

    @pytest.mark.asyncio
    async def test_fetch_latest_draws(self, mock_response_data):
        from app.scrapers.fdj_loto import FDJLotoScraper

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_response_data
        mock_response.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch("httpx.AsyncClient", return_value=mock_client):
            scraper = FDJLotoScraper()
            draws = await scraper.fetch_latest_draws(since_date=date(2024, 1, 1))

        assert len(draws) >= 1
        assert all(isinstance(d, RawDraw) for d in draws)

    @pytest.mark.asyncio
    async def test_fetch_with_since_date(self, mock_response_data):
        from app.scrapers.fdj_loto import FDJLotoScraper

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_response_data
        mock_response.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch("httpx.AsyncClient", return_value=mock_client):
            scraper = FDJLotoScraper()
            draws = await scraper.fetch_latest_draws(since_date=date(2024, 1, 14))

        # Should only return draws after since_date
        for d in draws:
            assert d.draw_date >= date(2024, 1, 14)


class TestEuroMillionsScraper:
    """Tests for EuroMillions scraper with mocked HTTP."""

    @pytest.mark.asyncio
    async def test_fetch_latest_draws(self):
        from app.scrapers.euromillions import EuroMillionsScraper

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "date": "2024-01-16",
                "numero": 2024002,
                "numeros": [3, 15, 27, 38, 49],
                "etoiles": [2, 11],
            }
        ]
        mock_response.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch("httpx.AsyncClient", return_value=mock_client):
            scraper = EuroMillionsScraper()
            draws = await scraper.fetch_latest_draws(since_date=date(2024, 1, 1))

        assert len(draws) == 1
        assert draws[0].stars == [2, 11]

    @pytest.mark.asyncio
    async def test_http_error_raises(self):
        import httpx

        from app.scrapers.euromillions import EuroMillionsScraper

        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Server Error",
            request=MagicMock(),
            response=mock_response,
        )

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch("httpx.AsyncClient", return_value=mock_client):
            scraper = EuroMillionsScraper()
            with pytest.raises(httpx.HTTPStatusError):
                await scraper.fetch_latest_draws()


class TestScraperFactory:
    """Tests for the scraper factory."""

    def test_get_scraper_loto(self):
        from app.scrapers import get_scraper
        from app.scrapers.fdj_loto import FDJLotoScraper

        scraper = get_scraper("loto-fdj")
        assert isinstance(scraper, FDJLotoScraper)

    def test_get_scraper_euromillions(self):
        from app.scrapers import get_scraper
        from app.scrapers.euromillions import EuroMillionsScraper

        scraper = get_scraper("euromillions")
        assert isinstance(scraper, EuroMillionsScraper)

    def test_get_scraper_unknown(self):
        from app.scrapers import get_scraper

        with pytest.raises(ValueError, match="No scraper"):
            get_scraper("unknown-game")
