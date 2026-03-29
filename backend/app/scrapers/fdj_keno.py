"""FDJ Keno scraper stub — fetches Keno draw results from FDJ historical CSV ZIP.

Keno FDJ rules:
- 20 numbers drawn from a pool of 1–70
- No bonus/star numbers
- Draws are identified by their date and draw_number (multiple per day)

Status: STUB — the FDJ API endpoint URL and CSV column names need to be
confirmed once the official FDJ historical archive for Keno is identified.
The structure mirrors FDJLotoScraper and is ready to be activated.
"""

import csv
import io
import zipfile
from datetime import date, datetime

import httpx
import structlog

from app.scrapers.base import BaseScraper, DrawValidator, RawDraw

logger = structlog.get_logger(__name__)

# FDJ Keno historical archives (ZIP containing CSV, semicolon-separated)
# Source: https://www.fdj.fr/jeux-de-tirage/keno/historique
# Multiple archives cover different periods — use the most recent as default.
KENO_ZIP_URL = (
    "https://www.sto.api.fdj.fr/anonymous/service-draw-info/v3/"
    "documentations/1a2b3c4d-9876-4562-b3fc-2c963f66bft6"  # Nov 2025 – present
)
# Older archives (if you need historical data prior to Nov 2025):
# Oct 2020 – Nov 2025: documentations/1a2b3c4d-9876-4562-b3fc-2c963f66aft6
# Nov 2018 – Oct 2020: documentations/1a2b3c4d-9876-4562-b3fc-2c963f66aet6

# Keno draw parameters
# FDJ CSV archive provides 16 drawn numbers (boule1..boule16)
KENO_NUMBERS_DRAWN = 16
KENO_MIN_NUMBER = 1
KENO_MAX_NUMBER = 70


class FDJKenoScraper(BaseScraper):
    """Scraper for FDJ Keno draw results from official CSV archives.

    Downloads the official FDJ ZIP archive for Keno and parses the
    semicolon-delimited CSV.  By default uses the current season archive
    (Nov 2025 – present).  Older archives can be fetched by passing a
    different ``zip_url`` in the constructor.
    """

    _validator = DrawValidator(
        min_number=KENO_MIN_NUMBER,
        max_number=KENO_MAX_NUMBER,
        numbers_drawn=KENO_NUMBERS_DRAWN,
    )

    def __init__(
        self,
        zip_url: str = KENO_ZIP_URL,
        timeout: float = 60.0,
    ):
        self._zip_url = zip_url
        self._timeout = timeout

    async def fetch_latest_draws(self, since_date: date | None = None) -> list[RawDraw]:
        """Fetch Keno draws since ``since_date``.

        Raises:
            httpx.HTTPError: On network failure.
        """
        if since_date is None:
            since_date = date(2000, 1, 1)

        log = logger.bind(scraper="fdj_keno", since=str(since_date))
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
                        validated = self._validator.validate(raw)
                        draws.append(validated)
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

        NOTE: Column names are placeholders. Inspect a real Keno CSV file
        to confirm the exact field names used by FDJ.

        Expected CSV structure (approximate):
          annee_de_tirage, mois_de_tirage, jour_de_tirage,
          numero_tirage, boule_1 … boule_20, multiplicateur
        """
        # Date parsing
        # TODO: Confirm actual date column names from FDJ Keno CSV
        draw_date_str = row.get("date_de_tirage") or row.get("DateTirage") or ""
        if not draw_date_str:
            # Fallback: build from year/month/day columns
            year = int(row["annee_de_tirage"])
            month = int(row["mois_de_tirage"])
            day = int(row["jour_de_tirage"])
            draw_date = date(year, month, day)
        else:
            # Try ISO format, then French format
            for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
                try:
                    draw_date = datetime.strptime(draw_date_str.strip(), fmt).date()
                    break
                except ValueError:
                    continue
            else:
                raise ValueError(f"Cannot parse date: {draw_date_str!r}")

        # Draw number (Keno can have multiple draws per day)
        draw_number_raw = (
            row.get("annee_numero_de_tirage")
            or row.get("numero_tirage")
            or row.get("NumeroTirage")
            or "0"
        )
        draw_number = int(draw_number_raw) if str(draw_number_raw).strip().isdigit() else None

        # Main numbers — FDJ Keno CSV provides boule1…boule16
        numbers: list[int] = []
        for i in range(1, KENO_NUMBERS_DRAWN + 1):
            for key in (f"boule{i}", f"boule_{i}", f"B{i}", f"Boule{i}"):
                if key in row and row[key].strip().isdigit():
                    numbers.append(int(row[key].strip()))
                    break

        if len(numbers) != KENO_NUMBERS_DRAWN:
            raise ValueError(
                f"Expected {KENO_NUMBERS_DRAWN} numbers, parsed {len(numbers)} "
                f"from row keys: {list(row.keys())}"
            )

        return RawDraw(
            draw_date=draw_date,
            draw_number=draw_number,
            numbers=sorted(numbers),  # sort for consistency
            stars=None,  # Keno has no bonus balls
        )
