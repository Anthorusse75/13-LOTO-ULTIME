"""FDJ Loto scraper — fetches draw results from the FDJ API."""

from datetime import date, timedelta

import httpx
import structlog

from app.scrapers.base import BaseScraper, RawDraw

logger = structlog.get_logger(__name__)

# FDJ provides a public JSON API for past draw results
FDJ_LOTO_API = "https://www.fdj.fr/api/loto/results"


class FDJLotoScraper(BaseScraper):
    """Scraper for Loto FDJ draw results."""

    def __init__(self, base_url: str = FDJ_LOTO_API, timeout: float = 30.0):
        self._base_url = base_url
        self._timeout = timeout

    async def fetch_latest_draws(self, since_date: date | None = None) -> list[RawDraw]:
        """Fetch Loto FDJ draws since given date (default: last 30 days)."""
        if since_date is None:
            since_date = date.today() - timedelta(days=30)

        log = logger.bind(scraper="fdj_loto", since=str(since_date))
        log.info("scraper_fetch_start")

        draws: list[RawDraw] = []

        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.get(
                    self._base_url,
                    params={"since": since_date.isoformat()},
                    headers={"Accept": "application/json", "User-Agent": "LOTO-ULTIME/1.0"},
                )
                response.raise_for_status()
                data = response.json()

            results = data if isinstance(data, list) else data.get("results", [])

            for entry in results:
                try:
                    raw = self._parse_entry(entry)
                    if raw.draw_date >= since_date:
                        draws.append(raw)
                except (KeyError, ValueError, TypeError) as exc:
                    log.warning("scraper_parse_error", entry=str(entry)[:200], error=str(exc))
                    continue

        except httpx.HTTPError as exc:
            log.error("scraper_http_error", error=str(exc))
            raise

        log.info("scraper_fetch_complete", count=len(draws))
        return draws

    def _parse_entry(self, entry: dict) -> RawDraw:
        """Parse a single draw entry from the FDJ API response."""
        # Adapt to actual FDJ API format — this handles common patterns
        draw_date = date.fromisoformat(str(entry.get("date", entry.get("draw_date", "")))[:10])
        draw_number = entry.get("draw_number", entry.get("numero", None))

        numbers = entry.get("numbers", entry.get("numeros", []))
        if isinstance(numbers, str):
            numbers = [int(n.strip()) for n in numbers.split(",")]

        stars = entry.get("stars", entry.get("numero_chance", entry.get("complementaire", None)))
        if isinstance(stars, int):
            stars = [stars]
        elif isinstance(stars, str):
            stars = [int(s.strip()) for s in stars.split(",")]

        return RawDraw(
            draw_date=draw_date,
            draw_number=int(draw_number) if draw_number is not None else None,
            numbers=sorted([int(n) for n in numbers]),
            stars=stars,
        )
