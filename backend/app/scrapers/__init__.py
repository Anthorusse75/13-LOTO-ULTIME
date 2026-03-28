"""Scraper factory — returns the appropriate scraper for a game slug."""

from app.scrapers.base import BaseScraper, DrawValidator, RawDraw
from app.scrapers.fdj_loto import FDJLotoScraper
from app.scrapers.euromillions import EuroMillionsScraper

SCRAPER_MAP: dict[str, type[BaseScraper]] = {
    "loto-fdj": FDJLotoScraper,
    "euromillions": EuroMillionsScraper,
}


def get_scraper(game_slug: str) -> BaseScraper:
    """Return the scraper instance for the given game slug."""
    scraper_cls = SCRAPER_MAP.get(game_slug)
    if scraper_cls is None:
        raise ValueError(f"No scraper available for game '{game_slug}'")
    return scraper_cls()


__all__ = ["BaseScraper", "DrawValidator", "RawDraw", "get_scraper"]
