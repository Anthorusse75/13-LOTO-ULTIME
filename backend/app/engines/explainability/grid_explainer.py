"""Grid explainer — explains a scored grid result with personalized data."""

from app.engines.explainability import Explanation


_CRITERIA_NAMES = {
    "frequency": "fréquence",
    "gap": "écart",
    "cooccurrence": "cooccurrence",
    "structure": "structure",
    "balance": "équilibre",
    "pattern_penalty": "pénalité de pattern",
}

_METHOD_LABELS = {
    "auto": "automatique",
    "genetic": "algorithme génétique",
    "annealing": "recuit simulé",
    "tabu": "recherche tabou",
    "hill_climbing": "hill climbing",
    "bayesian": "bayésien",
    "score": "scoring direct",
}

_PROFILE_LABELS = {
    "equilibre": "Équilibré",
    "tendance": "Tendance",
    "contrarian": "Contrariant",
    "structurel": "Structurel",
}


def explain_grid(
    score: float,
    breakdown: dict[str, float],
    method: str = "auto",
    profile: str = "equilibre",
    numbers: list[int] | None = None,
    stars: list[int] | None = None,
    star_name: str | None = None,
) -> Explanation:
    """Generate a truly personalized explanation for a scored grid."""

    nums_str = ", ".join(str(n) for n in numbers) if numbers else "—"
    _star_label = star_name or "étoile"
    _star_label_plural = f"{_star_label}s" if stars and len(stars) > 1 else _star_label
    stars_str = f" + {_star_label_plural} {', '.join(str(s) for s in stars)}" if stars else ""
    method_label = _METHOD_LABELS.get(method, method)
    profile_label = _PROFILE_LABELS.get(profile, profile)

    # Sort criteria by value (excluding penalty)
    sorted_criteria = sorted(
        [(k, v) for k, v in breakdown.items() if k != "pattern_penalty"],
        key=lambda x: x[1],
        reverse=True,
    )
    strong = [(k, v) for k, v in sorted_criteria[:2] if v > 0.5]
    weak = [(k, v) for k, v in sorted_criteria if v < 0.5]

    # Percentile estimation
    if score >= 7.5:
        percentile = "top 10%"
        verdict = "excellente"
    elif score >= 5.5:
        percentile = "top 30%"
        verdict = "bonne"
    elif score >= 3.5:
        percentile = "moyenne"
        verdict = "correcte"
    else:
        percentile = "en dessous de la moyenne"
        verdict = "faible"

    # ── L1: Summary — personalized with actual numbers ──
    summary = (
        f"Grille [{nums_str}]{stars_str} — score {score:.1f}/10 ({verdict}). "
        f"Méthode : {method_label}, profil : {profile_label}."
    )

    # ── L2: Interpretation — references actual criteria values ──
    strong_parts = []
    for k, v in strong:
        name = _CRITERIA_NAMES.get(k, k)
        strong_parts.append(f"{name} ({v:.2f})")
    weak_parts = []
    for k, v in weak:
        name = _CRITERIA_NAMES.get(k, k)
        weak_parts.append(f"{name} ({v:.2f})")

    strong_str = " et ".join(strong_parts) if strong_parts else "aucun critère dominant"
    weak_str = " et ".join(weak_parts) if weak_parts else "aucun"

    interpretation_lines = [
        f"Cette grille obtient {score:.1f}/10, ce qui la place dans le {percentile} des grilles analysées.",
    ]
    if strong_parts:
        interpretation_lines.append(
            f"Ses points forts sont {strong_str}."
        )
    if weak_parts:
        interpretation_lines.append(
            f"Les axes d'amélioration sont {weak_str}."
        )
    if numbers:
        even_count = sum(1 for n in numbers if n % 2 == 0)
        odd_count = len(numbers) - even_count
        low = sum(1 for n in numbers if n <= 25)
        high = len(numbers) - low
        interpretation_lines.append(
            f"Répartition : {even_count} pairs / {odd_count} impairs, {low} bas (≤25) / {high} hauts (>25)."
        )

    interpretation = " ".join(interpretation_lines)

    # ── L3: Technical — full breakdown with values ──
    breakdown_parts = [
        f"{_CRITERIA_NAMES.get(k, k)}={v:.2f}" for k, v in sorted_criteria
    ]
    penalty = breakdown.get("pattern_penalty", 0)
    technical = (
        f"Score total : {score:.2f}/10 | Méthode : {method_label} | Profil : {profile_label}\n"
        f"Détail des critères : {', '.join(breakdown_parts)}\n"
        f"Pénalité de pattern : {penalty:.2f}\n"
        f"Numéros : [{nums_str}]{stars_str}"
    )

    # ── Highlights — dynamic based on actual values ──
    highlights: list[str] = []
    freq = breakdown.get("frequency", 0)
    gap = breakdown.get("gap", 0)
    balance = breakdown.get("balance", 0)
    structure = breakdown.get("structure", 0)
    cooc = breakdown.get("cooccurrence", 0)

    if freq > 0.7:
        highlights.append(f"Fréquence excellente ({freq:.2f}) — vos numéros font partie des plus tirés historiquement")
    elif freq > 0.5:
        highlights.append(f"Bonne fréquence ({freq:.2f}) — numéros régulièrement tirés")

    if gap > 0.7:
        highlights.append(f"Écarts faibles ({gap:.2f}) — vos numéros sont sortis récemment, bon timing")
    elif gap > 0.5:
        highlights.append(f"Écarts corrects ({gap:.2f}) — numéros ni trop anciens ni trop récents")

    if balance > 0.7:
        highlights.append(f"Très bon équilibre pair/impair et haut/bas ({balance:.2f})")

    if structure > 0.7:
        highlights.append(f"Structure numérique solide ({structure:.2f}) — bonne répartition sur la grille")

    if cooc > 0.7:
        highlights.append(f"Cooccurrences favorables ({cooc:.2f}) — ces numéros sortent souvent ensemble")

    if score >= 7.5:
        highlights.append("Cette grille fait partie des 10% meilleures combinaisons possibles")

    # ── Warnings — actionable ──
    warnings: list[str] = []

    if penalty > 0.5:
        warnings.append(
            f"Pénalité de pattern élevée ({penalty:.2f}) — la grille contient des suites ou motifs suspects. "
            "Essayez de varier davantage les numéros."
        )

    if freq < 0.3:
        warnings.append(
            f"Fréquence faible ({freq:.2f}) — ces numéros sont rarement tirés. "
            "Passez au profil « Tendance » pour favoriser les numéros fréquents."
        )

    if gap < 0.3:
        warnings.append(
            f"Écarts élevés ({gap:.2f}) — certains numéros n'ont pas été tirés depuis longtemps."
        )

    if score < 4.0:
        warnings.append(
            f"Score global faible ({score:.1f}/10). "
            "Essayez une autre méthode d'optimisation ou changez de profil."
        )

    warnings.append("Le hasard reste le facteur déterminant — aucune méthode ne garantit un gain.")

    return Explanation(
        summary=summary,
        interpretation=interpretation,
        technical=technical,
        highlights=highlights,
        warnings=warnings,
    )
