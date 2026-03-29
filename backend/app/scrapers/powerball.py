"""PowerBall scraper — fetches draw results from the official PowerBall JSON API.

The official PowerBall website exposes a JSON endpoint that returns recent draws.
Historical CSV archives are also available at:
  https://www.powerball.com/previous-results

NOTE: This scraper is a functional stub. Activate it by uncommenting it in
      scrapers/__init__.py and verifying the current endpoint URLs.
"""

from datetime import date, datetime

import httpx
import structlog

from app.scrapers.base import BaseScraper, DrawValidator, RawDraw

logger = structlog.get_logger(__name__)

# Official Powerball results JSON endpoint (recent draws)
# Source: https://www.powerball.com/api/v1/numbers/powerball/recent
POWERBALL_API_URL = "https://www.powerball.com/api/v1/numbers/powerball/recent"

# Historical CSV endpoint (full archive):
# https://www.powerball.com/api/v1/numbers/powerball/history?starting=1/1/2000
POWERBALL_HISTORY_URL = (
    "https://www.powerball.com/api/v1/numbers/powerball/history?starting=1/1/2000"
)


class PowerBallScraper(BaseScraper):
    """Scraper for PowerBall (5/69 + 1/26) draw results.

    PowerBall rules:
    - Draw 5 numbers from 1 to 69 (white balls)
    - Draw 1 number from 1 to 26 (red PowerBall)
    - Draws: Monday, Wednesday, Saturday
    """

    def __init__(
        self,
        api_url: str = POWERBALL_API_URL,
        history_url: str = POWERBALL_HISTORY_URL,
        timeout: float = 30.0,
    ):
        self._api_url = api_url
        self._history_url = history_url
        self._timeout = timeout
        self._validator = DrawValidator(
            min_number=1,
            max_number=69,
            numbers_drawn=5,
            stars_pool=26,
            stars_drawn=1,
        )

    async def fetch_latest_draws(self, since_date: date | None = None) -> list[RawDraw]:
        """Fetch PowerBall draws since the given date."""
        if since_date is None:
            since_date = date(1992, 4, 22)  # First PowerBall draw

        log = logger.bind(scraper="powerball", since=str(since_date))
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
        """Parse the PowerBall JSON API response into RawDraw objects.

        Expected JSON format (array of draw records):
        [
            {
                "field_draw_date": "2024-01-06T00:00:00",
                "field_winning_numbers": "12 23 34 45 56",
                "field_powerball": "7"
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

                # Parse PowerBall (red ball — stored as star)
                powerball_str: str = record.get("field_powerball", "")
                powerball = int(powerball_str) if powerball_str.isdigit() else None
                stars = [powerball] if powerball is not None else None

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
