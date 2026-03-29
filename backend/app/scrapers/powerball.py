"""PowerBall scraper — fetches draw results from NY Open Data CSV.

Data source: New York State Gaming Commission via data.ny.gov
CSV endpoint: https://data.ny.gov/api/views/d6yy-54nr/rows.csv?accessType=DOWNLOAD

CSV format:
  Draw Date,Winning Numbers,Multiplier
  03/28/2026,11 42 43 59 61 25,4

Note: The 6th number in "Winning Numbers" is the PowerBall.
"""

import csv
import io
from datetime import date, datetime

import httpx
import structlog

from app.scrapers.base import BaseScraper, DrawValidator, RawDraw

logger = structlog.get_logger(__name__)

POWERBALL_CSV_URL = (
    "https://data.ny.gov/api/views/d6yy-54nr/rows.csv?accessType=DOWNLOAD"
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
        csv_url: str = POWERBALL_CSV_URL,
        timeout: float = 30.0,
    ):
        self._csv_url = csv_url
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
            since_date = date(1992, 4, 22)

        log = logger.bind(scraper="powerball", since=str(since_date))
        log.info("scraper_fetch_start")

        try:
            async with httpx.AsyncClient(timeout=self._timeout, follow_redirects=True) as client:
                response = await client.get(
                    self._csv_url,
                    headers={"User-Agent": "Mozilla/5.0 (LOTO-ULTIME/1.0)"},
                )
                response.raise_for_status()

            draws = self._parse_csv(response.text, since_date)
            log.info("scraper_fetch_complete", count=len(draws))
            return draws

        except httpx.HTTPStatusError as exc:
            log.error("scraper_fetch_http_error", status=exc.response.status_code)
            raise
        except Exception as exc:
            log.error("scraper_fetch_error", error=str(exc))
            raise

    def _parse_csv(self, text: str, since_date: date) -> list[RawDraw]:
        """Parse the NY Open Data CSV into RawDraw objects.

        CSV columns: Draw Date, Winning Numbers, Multiplier
        Date format: MM/DD/YYYY
        The 6th number in 'Winning Numbers' is the PowerBall.
        """
        draws: list[RawDraw] = []
        reader = csv.DictReader(io.StringIO(text))

        for row in reader:
            try:
                draw_date = datetime.strptime(row["Draw Date"], "%m/%d/%Y").date()

                if draw_date < since_date:
                    continue

                all_numbers = [int(n) for n in row["Winning Numbers"].split() if n.isdigit()]
                if len(all_numbers) < 6:
                    continue

                numbers = all_numbers[:5]
                powerball = all_numbers[5]
                stars = [powerball]

                raw = RawDraw(
                    draw_date=draw_date,
                    draw_number=None,
                    numbers=numbers,
                    stars=stars,
                )
                validated = self._validator.validate(raw)
                draws.append(validated)

            except (ValueError, KeyError) as exc:
                logger.warning("scraper_parse_skip", row=str(row)[:80], error=str(exc))
                continue

        draws.sort(key=lambda d: d.draw_date)
        return draws
