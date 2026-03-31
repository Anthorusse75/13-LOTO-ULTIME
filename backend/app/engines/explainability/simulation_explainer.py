"""Simulation explainer — personalized Monte Carlo simulation explanation."""

from app.engines.explainability import Explanation


def explain_simulation(
    n_simulations: int,
    avg_matches: float,
    expected_matches: float,
    match_distribution: dict[int, int],
    computation_time_ms: float = 0,
) -> Explanation:
    """Generate a personalized explanation for a Monte Carlo simulation."""

    total = sum(match_distribution.values()) if match_distribution else 1
    max_match = max(match_distribution.keys()) if match_distribution else 0

    # Distribution analysis
    high_match_count = sum(v for k, v in match_distribution.items() if k >= 3)
    high_match_pct = high_match_count / total * 100 if total > 0 else 0
    zero_match_pct = match_distribution.get(0, 0) / total * 100 if total > 0 else 0

    # Comparison with expected
    delta = avg_matches - expected_matches
    if abs(delta) < 0.1:
        comparison = "conforme à l'espérance théorique"
        delta_label = "neutre"
    elif delta > 0:
        comparison = f"au-dessus de l'espérance (+{delta:.2f})"
        delta_label = "favorable"
    else:
        comparison = f"en dessous de l'espérance ({delta:.2f})"
        delta_label = "défavorable"

    # ── L1: Summary ──
    summary = (
        f"Monte Carlo : {avg_matches:.1f} bons numéros en moyenne sur {n_simulations:,} tirages simulés "
        f"(espérance : {expected_matches:.1f}). Résultat {delta_label}."
    )

    # ── L2: Interpretation ──
    lines = [
        f"Sur {n_simulations:,} tirages simulés, cette grille obtient en moyenne {avg_matches:.1f} bons numéros.",
        f"L'espérance théorique est de {expected_matches:.1f} — votre grille est {comparison}.",
    ]
    if high_match_pct > 0:
        lines.append(
            f"{high_match_pct:.1f}% des tirages donnent 3 bons numéros ou plus "
            f"({high_match_count:,} sur {total:,})."
        )
    if max_match >= 4:
        best_count = match_distribution.get(max_match, 0)
        lines.append(
            f"Meilleur résultat : {max_match} bons numéros, obtenu {best_count:,} fois."
        )
    if zero_match_pct > 50:
        lines.append(
            f"Attention : {zero_match_pct:.0f}% des tirages ne donnent aucune correspondance."
        )

    interpretation = " ".join(lines)

    # ── L3: Technical ──
    dist_sorted = dict(sorted(match_distribution.items()))
    dist_detail = ", ".join(f"{k} match{'es' if k > 1 else ''}={v:,}" for k, v in dist_sorted.items())
    technical = (
        f"N simulations : {n_simulations:,} | Moyenne : {avg_matches:.3f} | Espérance : {expected_matches:.3f}\n"
        f"Distribution : {dist_detail}\n"
        f"Temps : {computation_time_ms:.0f}ms"
    )

    # ── Highlights ──
    highlights: list[str] = []
    if delta >= 0.1:
        highlights.append(
            f"Performance supérieure à l'espérance (+{delta:.2f}) — "
            "cette grille a un léger avantage statistique"
        )
    elif abs(delta) < 0.1:
        highlights.append("Performance conforme à la théorie — résultat fiable et cohérent")
    if n_simulations >= 100_000:
        highlights.append(
            f"{n_simulations:,} simulations — résultat statistiquement très fiable"
        )
    elif n_simulations >= 10_000:
        highlights.append(f"{n_simulations:,} simulations — bonne fiabilité statistique")
    if max_match >= 5:
        highlights.append(
            f"Obtenu {max_match} bons numéros dans la simulation — "
            "ce scénario favorable existe, même s'il est rare"
        )

    # ── Warnings ──
    warnings: list[str] = []
    if n_simulations < 1000:
        warnings.append(
            f"Seulement {n_simulations:,} simulations — augmentez à 10 000+ pour un résultat fiable."
        )
    if delta < -0.2:
        warnings.append(
            f"Performance en dessous de l'espérance ({delta:.2f}). "
            "Ce n'est pas anormal sur un petit échantillon."
        )
    warnings.append("Le hasard reste le facteur déterminant — aucune méthode ne garantit un gain.")

    return Explanation(
        summary=summary,
        interpretation=interpretation,
        technical=technical,
        highlights=highlights,
        warnings=warnings,
    )
