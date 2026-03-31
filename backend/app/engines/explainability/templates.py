"""French text templates for explainability engine."""

# ── Grid explainer templates ──

GRID_SUMMARY_EXCELLENT = "Grille très bien équilibrée avec un score de {score:.1f}/10."
GRID_SUMMARY_GOOD = "Grille de bonne qualité avec un score de {score:.1f}/10."
GRID_SUMMARY_AVERAGE = "Grille correcte avec un score de {score:.1f}/10."
GRID_SUMMARY_WEAK = "Grille faible avec un score de {score:.1f}/10 — améliorations possibles."

GRID_INTERPRETATION = (
    "Cette grille obtient {score:.1f}/10, ce qui la place dans le {percentile} des grilles analysées. "
    "Les critères les plus forts sont {strong_criteria}, tandis que {weak_criteria} peuvent être améliorés. "
    "Cette note reflète la qualité statistique, pas une probabilité de gain."
)

GRID_TECHNICAL = (
    "Score total : {score:.2f}/10 | Méthode : {method} | "
    "Détail : fréquence={freq:.2f}, écart={gap:.2f}, cooccurrence={cooc:.2f}, "
    "structure={struct:.2f}, équilibre={bal:.2f}, pénalité_pattern={penalty:.2f}. "
    "Profil utilisé : {profile}."
)

# ── Portfolio explainer templates ──

PORTFOLIO_SUMMARY_HIGH = "Portfolio très diversifié ({grid_count} grilles, diversité {diversity:.0%})."
PORTFOLIO_SUMMARY_MEDIUM = "Portfolio équilibré ({grid_count} grilles, diversité {diversity:.0%})."
PORTFOLIO_SUMMARY_LOW = "Portfolio peu diversifié — les grilles se ressemblent trop."

PORTFOLIO_INTERPRETATION = (
    "Ce portfolio {strategy} contient {grid_count} grilles avec une diversité de {diversity:.1%} "
    "et une couverture de {coverage:.1%}. Le score moyen est de {avg_score:.1f}/10. "
    "{diversity_comment}"
)

PORTFOLIO_TECHNICAL = (
    "Stratégie : {strategy} | Grilles : {grid_count} | "
    "Diversité : {diversity:.4f} | Couverture : {coverage:.4f} | "
    "Score moyen : {avg_score:.2f} | Hamming min : {hamming}. "
    "Temps de calcul : {time_ms:.0f}ms | Méthode : {method}."
)

# ── Simulation explainer templates ──

SIMULATION_SUMMARY = "Simulation Monte Carlo : {avg_matches:.1f} numéros en moyenne sur {n_sims:,} tirages."

SIMULATION_INTERPRETATION = (
    "Sur {n_sims:,} tirages simulés, cette grille obtient en moyenne {avg_matches:.1f} bons numéros. "
    "La distribution montre {dist_comment}. "
    "L'espérance théorique est de {expected:.1f} numéros — votre grille est {comparison}."
)

SIMULATION_TECHNICAL = (
    "N={n_sims:,} | Moyenne matches={avg_matches:.3f} | Espérance={expected:.3f} | "
    "Distribution={distribution} | Temps={time_ms:.0f}ms."
)

# ── Wheeling explainer templates (Phase C) ──

WHEELING_SUMMARY = "Système réduit : {n_combos} combinaisons couvrant {guarantee}-parmi-{base} parmi {n_numbers} numéros."

WHEELING_INTERPRETATION = (
    "Ce système réduit utilise {n_numbers} numéros sélectionnés pour générer {n_combos} combinaisons "
    "qui garantissent au minimum {guarantee} bons numéros si {base} de vos numéros sont tirés. "
    "Coût total : {cost:.2f}€."
)

WHEELING_TECHNICAL = (
    "Type : T({n_numbers},{base},{guarantee}) | Combinaisons : {n_combos} | "
    "Couverture : {coverage:.1%} | Coût : {cost:.2f}€ | "
    "Méthode : {method} | Temps : {time_ms:.0f}ms."
)

# ── Comparison explainer templates (Phase C) ──

COMPARISON_SUMMARY = "Votre grille se classe {rank}e sur {n_random:,} grilles aléatoires comparées."

COMPARISON_INTERPRETATION = (
    "Parmi {n_random:,} grilles aléatoires générées, votre grille se situe dans le top {percentile:.0%}. "
    "Son score de {score:.1f}/10 {comparison}."
)

COMPARISON_TECHNICAL = (
    "Score grille : {score:.2f} | Rang : {rank}/{n_random} | "
    "Percentile : {percentile:.3f} | Moyenne random : {mean_random:.2f} | "
    "Écart-type : {std_random:.2f}."
)

# ── Helpers ──

HIGHLIGHT_HIGH_FREQUENCY = "Bonne répartition des fréquences"
HIGHLIGHT_LOW_GAP = "Numéros avec des écarts récents faibles"
HIGHLIGHT_HIGH_DIVERSITY = "Excellente diversité entre les grilles"
HIGHLIGHT_HIGH_COVERAGE = "Couverture numérique élevée"
HIGHLIGHT_GOOD_BALANCE = "Bon équilibre pair/impair et haut/bas"
HIGHLIGHT_GOOD_STRUCTURE = "Structure numérologique solide"

WARNING_LOW_SCORE = "Score en dessous de la moyenne"
WARNING_LOW_DIVERSITY = "Diversité faible — les grilles se chevauchent"
WARNING_HIGH_PENALTY = "Pénalité de pattern élevée (suite, multiples…)"
WARNING_REMINDER = "Le hasard reste le facteur déterminant — aucune méthode ne garantit un gain"
