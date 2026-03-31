from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass(frozen=True)
class GameConfig:
    """Configuration d'un jeu de loterie (chargée depuis YAML)."""

    name: str
    slug: str
    numbers_pool: int
    numbers_drawn: int
    min_number: int
    max_number: int
    stars_pool: int | None = None
    stars_drawn: int | None = None
    star_name: str | None = None
    grid_price: float = 2.20
    draw_frequency: str = ""
    historical_source: str = ""
    description: str = ""


def load_game_config(path: Path) -> GameConfig:
    """Charge une configuration de jeu depuis un fichier YAML."""
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return GameConfig(**data)


def load_all_game_configs(
    config_dir: Path | None = None,
    include_plugins: bool = True,
) -> dict[str, GameConfig]:
    """Charge toutes les configurations de jeu depuis un dossier.

    If *include_plugins* is True (default), configs provided by registered
    :class:`~app.plugins.base.LotteryPlugin` instances are merged in after
    the YAML configs.  Plugin configs do **not** override YAML configs that
    share the same slug.
    """
    if config_dir is None:
        config_dir = Path(__file__).resolve().parent.parent.parent / "game_configs"

    configs: dict[str, GameConfig] = {}
    if config_dir.exists():
        for yaml_file in sorted(config_dir.glob("*.yaml")):
            config = load_game_config(yaml_file)
            configs[config.slug] = config

    if include_plugins:
        try:
            from app.plugins.registry import get_registry  # local import avoids circular dep

            for slug, cfg in get_registry().game_configs().items():
                if slug not in configs:  # YAML configs take precedence
                    configs[slug] = cfg
        except Exception:  # pragma: no cover
            pass  # Plugin registry unavailable — degrade gracefully

    return configs
