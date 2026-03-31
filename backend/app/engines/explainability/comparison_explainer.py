"""Comparison explainer — personalized grid comparison analysis."""

from app.engines.explainability import Explanation


def explain_comparison(
    score: float,
    rank: int,
    n_random: int,
    percentile: float,
    mean_random: float,
    std_random: float,
) -> Explanation:
    """Generate a personalized explanation for a grid vs random comparison."""

    advantage = score - mean_random
    sigma = (score - mean_random) / std_random if std_random > 0 else 0

    if percentile >= 0.9:
        verdict = "exceptionnelle"
        emoji = "🏆"
    elif percentile >= 0.75:
        verdict = "très bonne"
        emoji = "✅"
    elif percentile >= 0.5:
        verdict = "au-dessus de la moyenne"
        emoji = "👍"
    else:
        verdict = "en dessous de la moyenne"
        emoji = "⚠️"

    # ── L1: Summary ──
    summary = (
        f"{emoji} Votre grille se classe {rank}e sur {n_random:,} — "
        f"score {score:.1f}/10 vs {mean_random:.1f}/10 en moyenne ({verdict})."
    )

    # ── L2: Interpretation ──
    lines = [
        f"Parmi {n_random:,} grilles aléatoires, votre grille se situe dans le top {percentile:.0%}.",
        f"Votre score de {score:.1f}/10 est {'supérieur' if advantage > 0 else 'inférieur'} "
        f"à la moyenne aléatoire de {mean_random:.1f}/10 "
        f"({'+ ' if advantage > 0 else ''}{advantage:.2f} points).",
    ]
    if sigma > 2:
        lines.append(
            f"C'est {sigma:.1f} écarts-types au-dessus de la moyenne — "
            "un résultat statistiquement significatif."
        )
    elif sigma > 1:
        lines.append(
            f"C'est {sigma:.1f} écart-type au-dessus — un bon résultat mais dans la norme."
        )
    elif advantage < 0:
        lines.append(
            "Votre grille n'est pas optimale. Essayez une autre méthode d'optimisation."
        )

    interpretation = " ".join(lines)

    # ── L3: Technical ──
    technical = (
        f"Score grille : {score:.2f} | Rang : {rank}/{n_random:,}\n"
        f"Percentile : {percentile:.3f} | Moyenne random : {mean_random:.2f}\n"
        f"Écart-type : {std_random:.2f} | Z-score : {sigma:.2f}"
    )

    # ── Highlights ──
    highlights: list[str] = []
    if percentile >= 0.9:
        highlights.append(
            f"Top {100 - percentile * 100:.0f}% — votre grille surpasse {percentile * 100:.0f}% des grilles aléatoires"
        )
    if advantage > 0.5:
        highlights.append(
            f"+{advantage:.2f} points au-dessus de la moyenne aléatoire — "
            "l'optimisation apporte une vraie valeur ajoutée"
        )
    if sigma > 2:
        highlights.append(f"Z-score de {sigma:.1f} — résultat statistiquement significatif")

    # ── Warnings ──
    warnings: list[str] = []
    if advantage < 0:
        warnings.append(
            f"Score inférieur à la moyenne aléatoire ({advantage:.2f} points). "
            "Changez de méthode ou de profil."
        )
    if n_random < 100:
        warnings.append(
            f"Comparaison sur seulement {n_random} grilles — augmentez pour plus de fiabilité."
        )
    warnings.append("Le hasard reste le facteur déterminant — aucune méthode ne garantit un gain.")

    return Explanation(
        summary=summary,
        interpretation=interpretation,
        technical=technical,
        highlights=highlights,
        warnings=warnings,
    )
