"""Portfolio explainer — personalized explanation for a generated portfolio."""

from app.engines.explainability import Explanation


_STRATEGY_LABELS = {
    "balanced": "équilibré",
    "max_diversity": "maximisant la diversité",
    "max_coverage": "maximisant la couverture",
    "min_correlation": "minimisant les corrélations",
}


def explain_portfolio(
    strategy: str,
    grid_count: int,
    diversity_score: float,
    coverage_score: float,
    avg_grid_score: float,
    min_hamming_distance: float | None = None,
    computation_time_ms: float = 0,
    method: str = "genetic",
) -> Explanation:
    """Generate a personalized explanation for a portfolio."""

    strat_label = _STRATEGY_LABELS.get(strategy, strategy)
    hamming_str = f"{min_hamming_distance:.1f}" if min_hamming_distance else "N/A"

    # ── L1: Summary with actual metrics ──
    if diversity_score >= 0.7:
        verdict = "très diversifié"
    elif diversity_score >= 0.4:
        verdict = "équilibré"
    else:
        verdict = "peu diversifié"

    summary = (
        f"Portfolio {verdict} — {grid_count} grilles, "
        f"diversité {diversity_score:.0%}, couverture {coverage_score:.0%}, "
        f"score moyen {avg_grid_score:.1f}/10."
    )

    # ── L2: Interpretation with contextual analysis ──
    lines = [
        f"Ce portfolio {strat_label} contient {grid_count} grilles avec une diversité de {diversity_score:.1%} "
        f"et une couverture de {coverage_score:.1%}.",
        f"Le score moyen des grilles est de {avg_grid_score:.1f}/10.",
    ]

    if min_hamming_distance is not None:
        if min_hamming_distance >= 3:
            lines.append(
                f"La distance minimum entre deux grilles est de {min_hamming_distance:.0f} — "
                "aucune paire ne se ressemble trop."
            )
        else:
            lines.append(
                f"La distance minimum entre deux grilles est seulement de {min_hamming_distance:.0f} — "
                "certaines grilles partagent beaucoup de numéros."
            )

    if diversity_score >= 0.7:
        lines.append("Excellente diversité — vos grilles couvrent bien l'espace numérique.")
    elif diversity_score >= 0.4:
        lines.append("Diversité correcte — un bon compromis entre qualité et couverture.")
    else:
        lines.append("Diversité faible — vos grilles se ressemblent trop. Essayez la stratégie « Max diversité ».")

    interpretation = " ".join(lines)

    # ── L3: Technical ──
    technical = (
        f"Stratégie : {strat_label} | Grilles : {grid_count}\n"
        f"Diversité : {diversity_score:.4f} | Couverture : {coverage_score:.4f}\n"
        f"Score moyen : {avg_grid_score:.2f}/10 | Hamming min : {hamming_str}\n"
        f"Temps : {computation_time_ms:.0f}ms | Méthode : {method}"
    )

    # ── Highlights ──
    highlights: list[str] = []
    if diversity_score >= 0.7:
        highlights.append(
            f"Diversité excellente ({diversity_score:.0%}) — "
            "vos grilles sont bien différentes les unes des autres"
        )
    if coverage_score >= 0.7:
        highlights.append(
            f"Couverture de {coverage_score:.0%} des numéros du jeu — "
            "très peu de « trous » dans votre couverture"
        )
    if avg_grid_score >= 7.0:
        highlights.append(
            f"Score moyen élevé ({avg_grid_score:.1f}/10) — "
            "chaque grille est individuellement de bonne qualité"
        )
    if min_hamming_distance is not None and min_hamming_distance >= 4:
        highlights.append(
            f"Distance de Hamming minimum de {min_hamming_distance:.0f} — "
            "aucune redondance entre les grilles"
        )

    # ── Warnings ──
    warnings: list[str] = []
    if diversity_score < 0.4:
        warnings.append(
            f"Diversité faible ({diversity_score:.0%}) — les grilles se chevauchent trop. "
            "Passez à la stratégie « Max diversité » ou augmentez le nombre de grilles."
        )
    if coverage_score < 0.4:
        warnings.append(
            f"Couverture de seulement {coverage_score:.0%}. "
            "Ajoutez plus de grilles pour couvrir davantage de numéros."
        )
    if avg_grid_score < 5.0:
        warnings.append(
            f"Score moyen faible ({avg_grid_score:.1f}/10). "
            "Essayez la stratégie « Équilibré » pour de meilleures grilles."
        )
    warnings.append("Le hasard reste le facteur déterminant — aucune méthode ne garantit un gain.")

    return Explanation(
        summary=summary,
        interpretation=interpretation,
        technical=technical,
        highlights=highlights,
        warnings=warnings,
    )
