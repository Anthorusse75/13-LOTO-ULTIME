"""Unit tests for scrapers (base, FDJ, EuroMillions)."""

import io
import zipfile
from datetime import date
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.scrapers.base import DrawValidator, RawDraw


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


def _make_loto_zip(rows: list[dict]) -> bytes:
    """Build an in-memory ZIP containing a Loto CSV."""
    header = (
        "annee_numero_de_tirage;jour_de_tirage;date_de_tirage;"
        "date_de_forclusion;boule_1;boule_2;boule_3;boule_4;boule_5;"
        "numero_chance;combinaison_gagnante_en_ordre_croissant;"
        "nombre_de_gagnant_au_rang1;rapport_du_rang1;devise;\n"
    )
    buf = io.StringIO()
    buf.write(header)
    for r in rows:
        buf.write(
            f"{r['num']};{r['jour']};{r['date']};{r.get('forcl', '')};"
            f"{r['b1']};{r['b2']};{r['b3']};{r['b4']};{r['b5']};"
            f"{r['chance']};{r.get('combo', '')};0;0;eur;\n"
        )
    zbuf = io.BytesIO()
    with zipfile.ZipFile(zbuf, "w") as zf:
        zf.writestr("loto_201911.csv", buf.getvalue())
    return zbuf.getvalue()


def _make_euromillions_zip(rows: list[dict]) -> bytes:
    """Build an in-memory ZIP containing an EuroMillions CSV."""
    header = (
        "annee_numero_de_tirage;jour_de_tirage;date_de_tirage;"
        "numéro_de_tirage_dans_le_cycle;date_de_forclusion;"
        "boule_1;boule_2;boule_3;boule_4;boule_5;etoile_1;etoile_2;"
        "boules_gagnantes_en_ordre_croissant;etoiles_gagnantes_en_ordre_croissant;\n"
    )
    buf = io.StringIO()
    buf.write(header)
    for r in rows:
        buf.write(
            f"{r['num']};{r['jour']};{r['date']};1;{r.get('forcl', '')};"
            f"{r['b1']};{r['b2']};{r['b3']};{r['b4']};{r['b5']};"
            f"{r['e1']};{r['e2']};-;-;\n"
        )
    zbuf = io.BytesIO()
    with zipfile.ZipFile(zbuf, "w") as zf:
        zf.writestr("euromillions_202002.csv", buf.getvalue())
    return zbuf.getvalue()


class TestFDJLotoScraper:
    """Tests for FDJ Loto scraper with mocked HTTP."""

    @pytest.fixture
    def mock_zip_data(self):
        return _make_loto_zip(
            [
                {
                    "num": "2024001",
                    "jour": "LUNDI",
                    "date": "15/01/2024",
                    "b1": "5",
                    "b2": "12",
                    "b3": "23",
                    "b4": "34",
                    "b5": "45",
                    "chance": "7",
                },
                {
                    "num": "2024000",
                    "jour": "SAMEDI",
                    "date": "13/01/2024",
                    "b1": "1",
                    "b2": "8",
                    "b3": "19",
                    "b4": "28",
                    "b5": "40",
                    "chance": "3",
                },
            ]
        )

    @pytest.mark.asyncio
    async def test_fetch_latest_draws(self, mock_zip_data):
        from app.scrapers.fdj_loto import FDJLotoScraper

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = mock_zip_data
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
        assert draws[0].numbers == [5, 12, 23, 34, 45]
        assert draws[0].stars == [7]

    @pytest.mark.asyncio
    async def test_fetch_with_since_date(self, mock_zip_data):
        from app.scrapers.fdj_loto import FDJLotoScraper

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = mock_zip_data
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
            assert d.draw_date > date(2024, 1, 14)


class TestEuroMillionsScraper:
    """Tests for EuroMillions scraper with mocked HTTP."""

    @pytest.mark.asyncio
    async def test_fetch_latest_draws(self):
        from app.scrapers.euromillions import EuroMillionsScraper

        zip_data = _make_euromillions_zip(
            [
                {
                    "num": "2024002",
                    "jour": "MARDI",
                    "date": "16/01/2024",
                    "b1": "3",
                    "b2": "15",
                    "b3": "27",
                    "b4": "38",
                    "b5": "49",
                    "e1": "2",
                    "e2": "11",
                },
            ]
        )

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = zip_data
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
