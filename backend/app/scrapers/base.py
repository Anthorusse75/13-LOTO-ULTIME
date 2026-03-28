"""Base scraper interface and draw validation."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date


@dataclass
class RawDraw:
    """Represents a draw fetched from an external source."""

    draw_date: date
    draw_number: int | None
    numbers: list[int]
    stars: list[int] | None = None


class BaseScraper(ABC):
    """Abstract base class for lottery draw scrapers."""

    @abstractmethod
    async def fetch_latest_draws(self, since_date: date | None = None) -> list[RawDraw]:
        """Fetch draws from the external source since the given date."""
        ...


class DrawValidator:
    """Validate scraped draw data against game rules."""

    def __init__(
        self,
        min_number: int,
        max_number: int,
        numbers_drawn: int,
        stars_pool: int | None = None,
        stars_drawn: int | None = None,
    ):
        self.min_number = min_number
        self.max_number = max_number
        self.numbers_drawn = numbers_drawn
        self.stars_pool = stars_pool
        self.stars_drawn = stars_drawn

    def validate(self, raw: RawDraw) -> RawDraw:
        """Validate and return the draw, raising ValueError if invalid."""
        # Check numbers count
        if len(raw.numbers) != self.numbers_drawn:
            raise ValueError(f"Expected {self.numbers_drawn} numbers, got {len(raw.numbers)}")

        # Check numbers range
        for n in raw.numbers:
            if not (self.min_number <= n <= self.max_number):
                raise ValueError(f"Number {n} out of range [{self.min_number}, {self.max_number}]")

        # Check uniqueness
        if len(set(raw.numbers)) != len(raw.numbers):
            raise ValueError(f"Duplicate numbers in {raw.numbers}")

        # Check stars if applicable
        if self.stars_drawn and self.stars_drawn > 0:
            if raw.stars is None:
                raise ValueError("Stars expected but not provided")
            if len(raw.stars) != self.stars_drawn:
                raise ValueError(f"Expected {self.stars_drawn} stars, got {len(raw.stars)}")
            for s in raw.stars:
                if not (1 <= s <= (self.stars_pool or 0)):
                    raise ValueError(f"Star {s} out of range [1, {self.stars_pool}]")

        return raw
