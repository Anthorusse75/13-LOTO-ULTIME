"""FDJ Loto scraper — fetches draw results from the FDJ historical CSV ZIP."""

import csv
import io
import zipfile
from datetime import date, datetime

import httpx
import structlog

from app.scrapers.base import BaseScraper, RawDraw

logger = structlog.get_logger(__name__)

# FDJ official historical data (ZIP containing CSV, semicolon-separated)
# Latest archive: Nov 2019 — present
FDJ_LOTO_ZIP_URL = (
    "https://www.sto.api.fdj.fr/anonymous/service-draw-info/v3/"
    "documentations/1a2b3c4d-9876-4562-b3fc-2c963f66afp6"
)


class FDJLotoScraper(BaseScraper):
    """Scraper for Loto FDJ draw results from official CSV archives."""

    def __init__(self, zip_url: str = FDJ_LOTO_ZIP_URL, timeout: float = 60.0):
        self._zip_url = zip_url
        self._timeout = timeout

    async def fetch_latest_draws(self, since_date: date | None = None) -> list[RawDraw]:
        """Fetch Loto FDJ draws since given date (default: all available)."""
        if since_date is None:
            since_date = date(2000, 1, 1)

        log = logger.bind(scraper="fdj_loto", since=str(since_date))
        log.info("scraper_fetch_start")

        draws: list[RawDraw] = []

        try:
            async with httpx.AsyncClient(timeout=self._timeout, follow_redirects=True) as client:
                response = await client.get(
                    self._zip_url,
                    headers={"User-Agent": "Mozilla/5.0 (LOTO-ULTIME/1.0)"},
                )
                response.raise_for_status()

            rows = self._extract_csv(response.content)

            for row in rows:
                try:
                    raw = self._parse_row(row)
                    if raw.draw_date > since_date:
                        draws.append(raw)
                except (KeyError, ValueError, TypeError, IndexError) as exc:
                    log.warning("scraper_parse_error", error=str(exc))
                    continue

        except httpx.HTTPError as exc:
            log.error("scraper_http_error", error=str(exc))
            raise

        log.info("scraper_fetch_complete", count=len(draws))
        return draws

    @staticmethod
    def _extract_csv(zip_bytes: bytes) -> list[dict[str, str]]:
        """Extract CSV rows from a ZIP archive."""
        with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
            csv_names = [n for n in zf.namelist() if n.endswith(".csv")]
            if not csv_names:
                raise ValueError("No CSV file found in ZIP archive")
            with zf.open(csv_names[0]) as f:
                text = f.read().decode("utf-8-sig")
                reader = csv.DictReader(io.StringIO(text), delimiter=";")
                return list(reader)

    @staticmethod
    def _parse_row(row: dict[str, str]) -> RawDraw:
        """Parse a single CSV row into a RawDraw.

        CSV columns: annee_numero_de_tirage;jour_de_tirage;date_de_tirage;
        date_de_forclusion;boule_1;boule_2;boule_3;boule_4;boule_5;
        numero_chance;...
        """
        draw_date = datetime.strptime(row["date_de_tirage"].strip(), "%d/%m/%Y").date()
        draw_number = int(row["annee_numero_de_tirage"].strip())

        numbers = sorted(
            [
                int(row["boule_1"]),
                int(row["boule_2"]),
                int(row["boule_3"]),
                int(row["boule_4"]),
                int(row["boule_5"]),
            ]
        )

        chance = int(row["numero_chance"])

        return RawDraw(
            draw_date=draw_date,
            draw_number=draw_number,
            numbers=numbers,
            stars=[chance],
        )
