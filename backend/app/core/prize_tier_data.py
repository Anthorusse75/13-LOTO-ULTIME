"""Seed data for game prize tiers (DB-05, DB-06, DB-07)."""

# Loto FDJ — 9 rangs
LOTO_FDJ_TIERS = [
    {"rank": 1, "name": "5 + N°Chance", "match_numbers": 5, "match_stars": 1, "avg_prize": 2_000_000.0, "probability": 1 / 19_068_840},
    {"rank": 2, "name": "5", "match_numbers": 5, "match_stars": 0, "avg_prize": 100_000.0, "probability": 1 / 2_118_760},
    {"rank": 3, "name": "4 + N°Chance", "match_numbers": 4, "match_stars": 1, "avg_prize": 1_000.0, "probability": 1 / 86_677},
    {"rank": 4, "name": "4", "match_numbers": 4, "match_stars": 0, "avg_prize": 500.0, "probability": 1 / 9_631},
    {"rank": 5, "name": "3 + N°Chance", "match_numbers": 3, "match_stars": 1, "avg_prize": 50.0, "probability": 1 / 2_016},
    {"rank": 6, "name": "3", "match_numbers": 3, "match_stars": 0, "avg_prize": 20.0, "probability": 1 / 224},
    {"rank": 7, "name": "2 + N°Chance", "match_numbers": 2, "match_stars": 1, "avg_prize": 10.0, "probability": 1 / 144},
    {"rank": 8, "name": "2", "match_numbers": 2, "match_stars": 0, "avg_prize": 5.0, "probability": 1 / 16},
    {"rank": 9, "name": "1 + N°Chance", "match_numbers": 1, "match_stars": 1, "avg_prize": 2.20, "probability": 1 / 16},
]

# EuroMillions — 13 rangs
EUROMILLIONS_TIERS = [
    {"rank": 1, "name": "5 + 2 étoiles", "match_numbers": 5, "match_stars": 2, "avg_prize": 50_000_000.0, "probability": 1 / 139_838_160},
    {"rank": 2, "name": "5 + 1 étoile", "match_numbers": 5, "match_stars": 1, "avg_prize": 300_000.0, "probability": 1 / 6_991_908},
    {"rank": 3, "name": "5", "match_numbers": 5, "match_stars": 0, "avg_prize": 50_000.0, "probability": 1 / 3_107_515},
    {"rank": 4, "name": "4 + 2 étoiles", "match_numbers": 4, "match_stars": 2, "avg_prize": 5_000.0, "probability": 1 / 621_503},
    {"rank": 5, "name": "4 + 1 étoile", "match_numbers": 4, "match_stars": 1, "avg_prize": 200.0, "probability": 1 / 31_075},
    {"rank": 6, "name": "3 + 2 étoiles", "match_numbers": 3, "match_stars": 2, "avg_prize": 100.0, "probability": 1 / 14_125},
    {"rank": 7, "name": "4", "match_numbers": 4, "match_stars": 0, "avg_prize": 50.0, "probability": 1 / 13_811},
    {"rank": 8, "name": "2 + 2 étoiles", "match_numbers": 2, "match_stars": 2, "avg_prize": 20.0, "probability": 1 / 985},
    {"rank": 9, "name": "3 + 1 étoile", "match_numbers": 3, "match_stars": 1, "avg_prize": 15.0, "probability": 1 / 706},
    {"rank": 10, "name": "3", "match_numbers": 3, "match_stars": 0, "avg_prize": 13.0, "probability": 1 / 314},
    {"rank": 11, "name": "1 + 2 étoiles", "match_numbers": 1, "match_stars": 2, "avg_prize": 10.0, "probability": 1 / 188},
    {"rank": 12, "name": "2 + 1 étoile", "match_numbers": 2, "match_stars": 1, "avg_prize": 8.0, "probability": 1 / 49},
    {"rank": 13, "name": "2", "match_numbers": 2, "match_stars": 0, "avg_prize": 4.0, "probability": 1 / 22},
]

# PowerBall — 9 rangs
POWERBALL_TIERS = [
    {"rank": 1, "name": "5 + PowerBall", "match_numbers": 5, "match_stars": 1, "avg_prize": 200_000_000.0, "probability": 1 / 292_201_338},
    {"rank": 2, "name": "5", "match_numbers": 5, "match_stars": 0, "avg_prize": 1_000_000.0, "probability": 1 / 11_688_054},
    {"rank": 3, "name": "4 + PowerBall", "match_numbers": 4, "match_stars": 1, "avg_prize": 50_000.0, "probability": 1 / 913_129},
    {"rank": 4, "name": "4", "match_numbers": 4, "match_stars": 0, "avg_prize": 100.0, "probability": 1 / 36_525},
    {"rank": 5, "name": "3 + PowerBall", "match_numbers": 3, "match_stars": 1, "avg_prize": 100.0, "probability": 1 / 14_494},
    {"rank": 6, "name": "3", "match_numbers": 3, "match_stars": 0, "avg_prize": 7.0, "probability": 1 / 580},
    {"rank": 7, "name": "2 + PowerBall", "match_numbers": 2, "match_stars": 1, "avg_prize": 7.0, "probability": 1 / 701},
    {"rank": 8, "name": "1 + PowerBall", "match_numbers": 1, "match_stars": 1, "avg_prize": 4.0, "probability": 1 / 92},
    {"rank": 9, "name": "PowerBall seul", "match_numbers": 0, "match_stars": 1, "avg_prize": 4.0, "probability": 1 / 38},
]

# Mega Millions — 9 rangs
MEGA_MILLIONS_TIERS = [
    {"rank": 1, "name": "5 + Mega Ball", "match_numbers": 5, "match_stars": 1, "avg_prize": 200_000_000.0, "probability": 1 / 302_575_350},
    {"rank": 2, "name": "5", "match_numbers": 5, "match_stars": 0, "avg_prize": 1_000_000.0, "probability": 1 / 12_607_306},
    {"rank": 3, "name": "4 + Mega Ball", "match_numbers": 4, "match_stars": 1, "avg_prize": 10_000.0, "probability": 1 / 931_001},
    {"rank": 4, "name": "4", "match_numbers": 4, "match_stars": 0, "avg_prize": 500.0, "probability": 1 / 38_792},
    {"rank": 5, "name": "3 + Mega Ball", "match_numbers": 3, "match_stars": 1, "avg_prize": 200.0, "probability": 1 / 14_547},
    {"rank": 6, "name": "3", "match_numbers": 3, "match_stars": 0, "avg_prize": 10.0, "probability": 1 / 606},
    {"rank": 7, "name": "2 + Mega Ball", "match_numbers": 2, "match_stars": 1, "avg_prize": 10.0, "probability": 1 / 693},
    {"rank": 8, "name": "1 + Mega Ball", "match_numbers": 1, "match_stars": 1, "avg_prize": 4.0, "probability": 1 / 89},
    {"rank": 9, "name": "Mega Ball seul", "match_numbers": 0, "match_stars": 1, "avg_prize": 2.0, "probability": 1 / 37},
]

# Keno Gagnant à Vie — 10 rangs (for 10-spot play)
KENO_TIERS = [
    {"rank": 1, "name": "10/10", "match_numbers": 10, "match_stars": 0, "avg_prize": 200_000.0, "probability": 1 / 8_911_711},
    {"rank": 2, "name": "9/10", "match_numbers": 9, "match_stars": 0, "avg_prize": 10_000.0, "probability": 1 / 163_381},
    {"rank": 3, "name": "8/10", "match_numbers": 8, "match_stars": 0, "avg_prize": 1_000.0, "probability": 1 / 7_384},
    {"rank": 4, "name": "7/10", "match_numbers": 7, "match_stars": 0, "avg_prize": 100.0, "probability": 1 / 621},
    {"rank": 5, "name": "6/10", "match_numbers": 6, "match_stars": 0, "avg_prize": 25.0, "probability": 1 / 87},
    {"rank": 6, "name": "5/10", "match_numbers": 5, "match_stars": 0, "avg_prize": 5.0, "probability": 1 / 19},
    {"rank": 7, "name": "4/10", "match_numbers": 4, "match_stars": 0, "avg_prize": 2.0, "probability": 1 / 6},
    {"rank": 8, "name": "3/10", "match_numbers": 3, "match_stars": 0, "avg_prize": 1.0, "probability": 1 / 3},
    {"rank": 9, "name": "2/10", "match_numbers": 2, "match_stars": 0, "avg_prize": 0.0, "probability": 0.2952},
    {"rank": 10, "name": "0/10", "match_numbers": 0, "match_stars": 0, "avg_prize": 2.0, "probability": 0.0458},
]

# Mapping slug → tier data
PRIZE_TIERS_BY_SLUG: dict[str, list[dict]] = {
    "loto-fdj": LOTO_FDJ_TIERS,
    "euromillions": EUROMILLIONS_TIERS,
    "powerball": POWERBALL_TIERS,
    "mega-millions": MEGA_MILLIONS_TIERS,
    "keno": KENO_TIERS,
}
