"""
Driver aggression profiles derived from historical race data.

Aggression score (0-1) is computed from three empirical factors:
1. Stint extension: how long a driver stays out vs field average
2. Close combat overtake rate: success rate when within 3s of car ahead
3. SC/VSC pit aggression: willingness to pit under safety car

No ML training needed — purely derived from data we already have.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ml_engine.data.schema import get_connection

MIN_PITS = 20
MIN_COMBAT_LAPS = 50
MIN_SC_LAPS = 5

# Weights for composite score
W_STINT = 0.35
W_OVERTAKE = 0.40
W_SC = 0.25


def compute_aggression_profiles(conn=None):
    """
    Compute per-driver aggression profiles from race_states.
    Returns dict: {driver_code: {aggression, stint_ext, overtake_rate, sc_pit_rate, ...}}
    """
    own_conn = conn is None
    if own_conn:
        conn = get_connection()

    drivers = {}

    # 1. Stint extension tendency (higher = stays out longer = more aggressive)
    global_avg_tyre = conn.execute(
        "SELECT AVG(tyre_life) FROM race_states WHERE decision_made LIKE '%PIT%'"
    ).fetchone()[0] or 18.0

    rows = conn.execute("""
        SELECT driver, AVG(tyre_life) as avg_tyre_at_pit, COUNT(*) as n_pits
        FROM race_states
        WHERE decision_made LIKE '%PIT%'
        GROUP BY driver HAVING n_pits >= ?
    """, (MIN_PITS,)).fetchall()

    stint_scores = {}
    if rows:
        vals = [r[1] for r in rows]
        mn, mx = min(vals), max(vals)
        rng = mx - mn if mx > mn else 1.0
        for r in rows:
            stint_scores[r[0]] = {
                "raw": r[1],
                "normalized": (r[1] - mn) / rng,
                "vs_avg": r[1] - global_avg_tyre,
                "n_pits": r[2],
            }

    # 2. Close combat overtake rate (within 3s)
    rows = conn.execute("""
        SELECT driver,
               AVG(CASE WHEN positions_delta_5 > 0 THEN 1.0 ELSE 0.0 END) as overtake_rate,
               AVG(positions_delta_5) as avg_pos_delta,
               COUNT(*) as n
        FROM race_states
        WHERE positions_delta_5 IS NOT NULL
          AND gap_ahead_s IS NOT NULL AND gap_ahead_s < 3.0
        GROUP BY driver HAVING n >= ?
    """, (MIN_COMBAT_LAPS,)).fetchall()

    overtake_scores = {}
    if rows:
        vals = [r[1] for r in rows]
        mn, mx = min(vals), max(vals)
        rng = mx - mn if mx > mn else 1.0
        for r in rows:
            overtake_scores[r[0]] = {
                "raw": r[1],
                "normalized": (r[1] - mn) / rng,
                "avg_pos_delta": r[2],
                "combat_laps": r[3],
            }

    # 3. SC/VSC pit tendency (higher = more willing to gamble on pit)
    rows = conn.execute("""
        SELECT driver,
               SUM(CASE WHEN decision_made LIKE '%PIT%' THEN 1 ELSE 0 END) as pitted,
               COUNT(*) as total_sc_laps
        FROM race_states
        WHERE track_status IN ('4', '6', 'SafetyCar', 'VSC')
        GROUP BY driver HAVING total_sc_laps >= ?
    """, (MIN_SC_LAPS,)).fetchall()

    sc_scores = {}
    if rows:
        vals = [r[1] / r[2] for r in rows]
        mn, mx = min(vals), max(vals)
        rng = mx - mn if mx > mn else 1.0
        for r in rows:
            rate = r[1] / r[2]
            sc_scores[r[0]] = {
                "raw": rate,
                "normalized": (rate - mn) / rng,
                "pitted": r[1],
                "sc_laps": r[2],
            }

    # Combine all drivers that appear in at least 2 of 3 factors
    all_drivers = set(stint_scores) | set(overtake_scores) | set(sc_scores)

    for drv in all_drivers:
        s = stint_scores.get(drv)
        o = overtake_scores.get(drv)
        sc = sc_scores.get(drv)

        components = []
        if s:
            components.append(("stint_extension", s["normalized"], W_STINT))
        if o:
            components.append(("overtake_rate", o["normalized"], W_OVERTAKE))
        if sc:
            components.append(("sc_pit_aggression", sc["normalized"], W_SC))

        if len(components) < 2:
            continue

        # Weighted average, renormalized
        total_w = sum(c[2] for c in components)
        aggression = sum(c[1] * c[2] for c in components) / total_w

        drivers[drv] = {
            "aggression": round(aggression, 3),
            "stint_extension": round(s["normalized"], 3) if s else None,
            "avg_tyre_life_at_pit": round(s["raw"], 1) if s else None,
            "stint_vs_field_avg": round(s["vs_avg"], 1) if s else None,
            "overtake_rate": round(o["raw"], 3) if o else None,
            "overtake_normalized": round(o["normalized"], 3) if o else None,
            "avg_pos_delta_combat": round(o["avg_pos_delta"], 2) if o else None,
            "combat_laps": o["combat_laps"] if o else 0,
            "sc_pit_rate": round(sc["raw"], 3) if sc else None,
            "sc_normalized": round(sc["normalized"], 3) if sc else None,
            "n_pits": s["n_pits"] if s else 0,
        }

    if own_conn:
        conn.close()

    return drivers


def get_aggression(driver_code, profiles=None):
    """Get aggression score for a driver (0-1). Returns 0.5 if unknown."""
    if profiles is None:
        profiles = compute_aggression_profiles()
    p = profiles.get(driver_code)
    return p["aggression"] if p else 0.5


def print_profiles(profiles):
    """Pretty print driver profiles sorted by aggression."""
    ranked = sorted(profiles.items(), key=lambda x: x[1]["aggression"], reverse=True)
    print(f"\n{'Driver':<6} {'Aggr':>5} {'Stint':>6} {'OT Rate':>8} {'OT Δpos':>7} {'SC Pit':>7}")
    print("-" * 50)
    for drv, p in ranked:
        stint = f"{p['stint_vs_field_avg']:+.1f}" if p['stint_vs_field_avg'] is not None else "  N/A"
        ot = f"{p['overtake_rate']:.2f}" if p['overtake_rate'] is not None else " N/A"
        ot_delta = f"{p['avg_pos_delta_combat']:+.2f}" if p['avg_pos_delta_combat'] is not None else "  N/A"
        sc = f"{p['sc_pit_rate']:.2f}" if p['sc_pit_rate'] is not None else " N/A"
        print(f"{drv:<6} {p['aggression']:>5.3f} {stint:>6} {ot:>8} {ot_delta:>7} {sc:>7}")


if __name__ == "__main__":
    profiles = compute_aggression_profiles()
    print_profiles(profiles)

    import json
    out_path = os.path.join(os.path.dirname(__file__), "saved", "aggression_profiles.json")
    with open(out_path, "w") as f:
        json.dump(profiles, f, indent=2)
    print(f"\nSaved {len(profiles)} profiles to {out_path}")
