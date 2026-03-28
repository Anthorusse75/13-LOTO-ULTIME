"""Job: fetch draws from external source for a given game."""

import structlog

from app.core.game_definitions import load_all_game_configs
from app.models.base import get_session
from app.models.draw import Draw
from app.repositories.draw_repository import DrawRepository
from app.repositories.game_repository import GameRepository
from app.scrapers import DrawValidator, get_scraper
from app.scheduler.runner import execute_with_tracking

logger = structlog.get_logger(__name__)


async def fetch_draws_job(game_slug: str) -> None:
    """Scheduled job: fetch new draws for a game and chain compute_stats."""
    # Resolve game from DB
    async for session in get_session():
        game_repo = GameRepository(session)
        game = await game_repo.get_by_slug(game_slug)
        if game is None:
            logger.error("fetch_draws.game_not_found", slug=game_slug)
            return
        game_id = game.id
        break

    await execute_with_tracking(
        job_name=f"fetch_draws_{game_slug}",
        func=_do_fetch,
        game_slug=game_slug,
        game_id=game_id,
        triggered_by="scheduler",
    )


async def _do_fetch(game_slug: str) -> dict:
    """Core fetch logic — returns result summary."""
    # Load game config from YAML
    configs = load_all_game_configs()
    config = configs.get(game_slug)
    if config is None:
        raise ValueError(f"No game config found for slug '{game_slug}'")

    async for session in get_session():
        game_repo = GameRepository(session)
        draw_repo = DrawRepository(session)

        game = await game_repo.get_by_slug(game_slug)
        if game is None:
            raise ValueError(f"Game '{game_slug}' not found in database")

        # Get last known draw to fetch only new ones
        latest_draws = await draw_repo.get_latest(game.id, limit=1)
        since_date = latest_draws[0].draw_date if latest_draws else None

        # Fetch from external source
        scraper = get_scraper(game_slug)
        raw_draws = await scraper.fetch_latest_draws(since_date=since_date)

        # Validate and save
        validator = DrawValidator(
            min_number=config.min_number,
            max_number=config.max_number,
            numbers_drawn=config.numbers_drawn,
            stars_pool=config.stars_pool,
            stars_drawn=config.stars_drawn,
        )

        saved_count = 0
        skipped = 0
        errors = 0

        for raw in raw_draws:
            try:
                validated = validator.validate(raw)
            except ValueError as exc:
                logger.warning("fetch_draws.validation_failed", error=str(exc))
                errors += 1
                continue

            if await draw_repo.exists(game.id, validated.draw_date):
                skipped += 1
                continue

            draw = Draw(
                game_id=game.id,
                draw_date=validated.draw_date,
                draw_number=validated.draw_number,
                numbers=validated.numbers,
                stars=validated.stars,
            )
            await draw_repo.create(draw)
            saved_count += 1

        await session.commit()
        break

    return {
        "fetched": len(raw_draws),
        "saved": saved_count,
        "duplicates": skipped,
        "validation_errors": errors,
    }
