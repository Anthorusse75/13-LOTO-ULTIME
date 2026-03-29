"""Mega Millions scraper — fetches draw results from the official Mega Millions JSON API.

The official Mega Millions website exposes a JSON endpoint that returns recent draws.
Historical CSV archives are also available at:
  https://www.megamillions.com/previous-results

NOTE: This scraper is a functional stub. Activate it by uncommenting it in
      scrapers/__init__.py and verifying the current endpoint URLs.
"""

from datetime import date, datetime

import httpx
import structlog

from app.scrapers.base import BaseScraper, DrawValidator, RawDraw

logger = structlog.get_logger(__name__)

# Official Mega Millions results JSON endpoint (recent draws)
# Source: https://www.megamillions.com/api/v1/numbers/megamillions/recent
MEGA_MILLIONS_API_URL = "https://www.megamillions.com/api/v1/numbers/megamillions/recent"

# Historical endpoint:
# https://www.megamillions.com/api/v1/numbers/megamillions/history?starting=1/1/2000
MEGA_MILLIONS_HISTORY_URL = (
    "https://www.megamillions.com/api/v1/numbers/megamillions/history?starting=1/1/2000"
)


class MegaMillionsScraper(BaseScraper):
    """Scraper for Mega Millions (5/70 + 1/25) draw results.

    Mega Millions rules:
    - Draw 5 numbers from 1 to 70 (white balls)
    - Draw 1 number from 1 to 25 (gold Mega Ball)
    - Draws: Tuesday, Friday
    """

    def __init__(
        self,
        api_url: str = MEGA_MILLIONS_API_URL,
        history_url: str = MEGA_MILLIONS_HISTORY_URL,
        timeout: float = 30.0,
    ):
        self._api_url = api_url
        self._history_url = history_url
        self._timeout = timeout
        self._validator = DrawValidator(
            min_number=1,
            max_number=70,
            numbers_drawn=5,
            stars_pool=25,
            stars_drawn=1,
        )

    async def fetch_latest_draws(self, since_date: date | None = None) -> list[RawDraw]:
        """Fetch Mega Millions draws since the given date."""
        if since_date is None:
            since_date = date(2002, 5, 17)  # First Mega Millions draw under current brand

        log = logger.bind(scraper="mega-millions", since=str(since_date))
        log.info("scraper_fetch_start")

        try:
            async with httpx.AsyncClient(timeout=self._timeout, follow_redirects=True) as client:
                response = await client.get(
                    self._api_url,
                    headers={"User-Agent": "Mozilla/5.0 (LOTO-ULTIME/1.0)"},
                )
                response.raise_for_status()

            draws = self._parse_response(response.json(), since_date)
            log.info("scraper_fetch_done", count=len(draws))
            return draws

        except httpx.HTTPStatusError as exc:
            log.error("scraper_fetch_http_error", status=exc.response.status_code)
            raise
        except Exception as exc:
            log.error("scraper_fetch_error", error=str(exc))
            raise

    def _parse_response(
        self, data: list[dict], since_date: date
    ) -> list[RawDraw]:
        """Parse the Mega Millions JSON API response into RawDraw objects.

        Expected JSON format (array of draw records):
        [
            {
                "field_draw_date": "2024-01-05T00:00:00",
                "field_winning_numbers": "10 21 32 43 54",
                "field_mega_ball": "15",
                "field_megaplier": "3"
            },
            ...
        ]
        """
        draws: list[RawDraw] = []

        for record in data:
            try:
                # Parse draw date
                date_str: str = record.get("field_draw_date", "")
                draw_date = datetime.fromisoformat(date_str).date()

                if draw_date < since_date:
                    continue

                # Parse white balls (space-separated)
                numbers_str: str = record.get("field_winning_numbers", "")
                numbers = [int(n) for n in numbers_str.split() if n.isdigit()]

                # Parse Mega Ball (gold ball — stored as star)
                mega_ball_str: str = record.get("field_mega_ball", "")
                mega_ball = int(mega_ball_str) if mega_ball_str.isdigit() else None
                stars = [mega_ball] if mega_ball is not None else None

                raw = RawDraw(
                    draw_date=draw_date,
                    draw_number=None,
                    numbers=numbers,
                    stars=stars,
                )
                validated = self._validator.validate(raw)
                draws.append(validated)

            except (ValueError, KeyError) as exc:
                logger.warning("scraper_parse_skip", record=str(record)[:80], error=str(exc))
                continue

        # Sort by date ascending (oldest first)
        draws.sort(key=lambda d: d.draw_date)
        return draws
