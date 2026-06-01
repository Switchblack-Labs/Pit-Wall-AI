"""
Feature engineering: transforms raw laps/weather/pit data into race_states table.
"""
import sqlite3
import numpy as np
from tqdm import tqdm
from ml_engine.data.schema import get_connection
from ml_engine.config import PIT_LOSS_DEFAULTS, COMPOUND_ENCODING


def compute_gaps(conn, race_id, lap_num):
    """Compute gap to car ahead, behind, and leader for each driver on a given lap."""
    rows = conn.execute("""
        SELECT driver, position, lap_time_ms FROM laps
        WHERE race_id=? AND lap=? AND position IS NOT NULL
        ORDER BY position
    """, (race_id, lap_num)).fetchall()

    if not rows:
        return {}

    # Accumulate cumulative race time per driver up to this lap
    cum_times = {}
    drivers_this_lap = [r["driver"] for r in rows]

    for driver in drivers_this_lap:
        total = conn.execute("""
            SELECT SUM(lap_time_ms) FROM laps
            WHERE race_id=? AND driver=? AND lap<=? AND lap_time_ms IS NOT NULL
        """, (race_id, driver, lap_num)).fetchone()[0]
        cum_times[driver] = total if total else None

    # Sort by position
    sorted_drivers = sorted(
        [(r["driver"], r["position"], cum_times.get(r["driver"])) for r in rows],
        key=lambda x: x[1]
    )

    gaps = {}
    leader_time = sorted_drivers[0][2] if sorted_drivers[0][2] else 0

    for i, (driver, pos, cum_t) in enumerate(sorted_drivers):
        if cum_t is None:
            gaps[driver] = {"gap_ahead_s": None, "gap_behind_s": None, "gap_to_leader_s": None}
            continue

        gap_to_leader = (cum_t - leader_time) / 1000.0 if leader_time else 0
        gap_ahead = None
        gap_behind = None

        if i > 0 and sorted_drivers[i-1][2] is not None:
            gap_ahead = (cum_t - sorted_drivers[i-1][2]) / 1000.0

        if i < len(sorted_drivers) - 1 and sorted_drivers[i+1][2] is not None:
            gap_behind = (sorted_drivers[i+1][2] - cum_t) / 1000.0

        gaps[driver] = {
            "gap_ahead_s": gap_ahead,
            "gap_behind_s": gap_behind,
            "gap_to_leader_s": gap_to_leader,
        }

    return gaps


def compute_deg_rate(conn, race_id, driver, lap_num, window=5):
    """Compute degradation rate (s/lap) over the last `window` laps."""
    rows = conn.execute("""
        SELECT lap, lap_time_ms FROM laps
        WHERE race_id=? AND driver=? AND lap BETWEEN ? AND ?
        AND is_accurate=1 AND lap_time_ms IS NOT NULL
        AND track_status IN ('1', '2')
        ORDER BY lap
    """, (race_id, driver, max(1, lap_num - window + 1), lap_num)).fetchall()

    if len(rows) < 3:
        return None

    laps = np.array([r["lap"] for r in rows])
    times = np.array([r["lap_time_ms"] / 1000.0 for r in rows])

    try:
        coeffs = np.polyfit(laps, times, 1)
        return float(coeffs[0])  # seconds per lap
    except (np.linalg.LinAlgError, ValueError):
        return None


def compute_sector_trend(conn, race_id, driver, lap_num, sector_col, window=3):
    """Compute sector time trend over last `window` laps."""
    rows = conn.execute(f"""
        SELECT lap, {sector_col} FROM laps
        WHERE race_id=? AND driver=? AND lap BETWEEN ? AND ?
        AND is_accurate=1 AND {sector_col} IS NOT NULL
        ORDER BY lap
    """, (race_id, driver, max(1, lap_num - window), lap_num)).fetchall()

    if len(rows) < 2:
        return None

    times = [r[1] / 1000.0 for r in rows]
    return float(times[-1] - times[0]) / len(times)


def compute_lap_delta_vs_fresh(conn, race_id, driver, lap_num):
    """How much slower is current lap vs first clean lap of the current stint."""
    # Find current stint start
    stint = conn.execute("""
        SELECT start_lap, compound FROM stints
        WHERE race_id=? AND driver=? AND start_lap<=? AND end_lap>=?
    """, (race_id, driver, lap_num, lap_num)).fetchone()

    if not stint:
        return None

    # First clean lap of stint
    first_clean = conn.execute("""
        SELECT lap_time_ms FROM laps
        WHERE race_id=? AND driver=? AND lap>=? AND lap<=?
        AND is_accurate=1 AND lap_time_ms IS NOT NULL
        AND is_pit_out=0
        ORDER BY lap LIMIT 1
    """, (race_id, driver, stint["start_lap"], lap_num)).fetchone()

    current = conn.execute("""
        SELECT lap_time_ms FROM laps
        WHERE race_id=? AND driver=? AND lap=? AND lap_time_ms IS NOT NULL
    """, (race_id, driver, lap_num)).fetchone()

    if not first_clean or not current:
        return None

    return (current["lap_time_ms"] - first_clean["lap_time_ms"]) / 1000.0


def compute_pit_loss(conn, circuit):
    """Compute median pit loss at a circuit from all historical pit stops."""
    rows = conn.execute("""
        SELECT ps.duration_s FROM pit_stops ps
        JOIN races r ON ps.race_id = r.race_id
        WHERE r.circuit=? AND ps.duration_s IS NOT NULL AND ps.duration_s > 15 AND ps.duration_s < 40
    """, (circuit,)).fetchall()

    if len(rows) >= 3:
        return float(np.median([r["duration_s"] for r in rows]))
    return PIT_LOSS_DEFAULTS.get(circuit, 22.0)


def get_compounds_used(conn, race_id, driver, lap_num):
    """Get list of compounds used before current stint."""
    rows = conn.execute("""
        SELECT DISTINCT compound FROM stints
        WHERE race_id=? AND driver=? AND end_lap<? AND compound IS NOT NULL
    """, (race_id, driver, lap_num)).fetchall()
    return ",".join([r["compound"] for r in rows]) if rows else ""


def get_stops_made(conn, race_id, driver, lap_num):
    """Count pit stops made before this lap."""
    row = conn.execute("""
        SELECT COUNT(*) as cnt FROM pit_stops
        WHERE race_id=? AND driver=? AND lap<?
    """, (race_id, driver, lap_num)).fetchone()
    return row["cnt"] if row else 0


def compute_decision(conn, race_id, driver, lap_num, total_laps):
    """Determine what decision was made: PIT (within next 2 laps) or STAY_OUT."""
    pit = conn.execute("""
        SELECT lap FROM pit_stops
        WHERE race_id=? AND driver=? AND lap BETWEEN ? AND ?
    """, (race_id, driver, lap_num, min(lap_num + 2, total_laps))).fetchone()

    if pit:
        return "PIT", pit["lap"] - lap_num
    return "STAY_OUT", 0


def compute_outcome(conn, race_id, driver, lap_num, horizon=5):
    """Compute position change over next `horizon` laps."""
    current = conn.execute("""
        SELECT position FROM laps WHERE race_id=? AND driver=? AND lap=?
    """, (race_id, driver, lap_num)).fetchone()

    future = conn.execute("""
        SELECT position FROM laps WHERE race_id=? AND driver=? AND lap=?
    """, (race_id, driver, min(lap_num + horizon, 999))).fetchone()

    if not current or not future or current["position"] is None or future["position"] is None:
        return None
    return current["position"] - future["position"]  # positive = gained positions


def projected_tyre_laps(conn, race_id, driver, lap_num, deg_rate):
    """Estimate how many laps remain on current tyres before pace drops off cliff."""
    if deg_rate is None or deg_rate <= 0.01:
        return 30  # low deg, long stint possible

    current = conn.execute("""
        SELECT lap_time_ms, tyre_life FROM laps
        WHERE race_id=? AND driver=? AND lap=? AND lap_time_ms IS NOT NULL
    """, (race_id, driver, lap_num)).fetchone()

    if not current:
        return None

    # Cliff threshold: 2.5s slower than current pace
    cliff_delta_s = 2.5
    laps_to_cliff = int(cliff_delta_s / deg_rate) if deg_rate > 0 else 30
    return max(1, laps_to_cliff)


def engineer_race(conn, race_id):
    """Engineer features for all laps of a single race."""
    race = conn.execute("SELECT * FROM races WHERE race_id=?", (race_id,)).fetchone()
    if not race:
        return 0

    total_laps = race["total_laps"]
    circuit = race["circuit"]

    pit_loss = compute_pit_loss(conn, circuit)

    drivers = [r["driver"] for r in conn.execute(
        "SELECT DISTINCT driver FROM laps WHERE race_id=?", (race_id,)).fetchall()]

    count = 0
    for lap_num in range(1, total_laps + 1):
        gaps = compute_gaps(conn, race_id, lap_num)
        weather = conn.execute(
            "SELECT * FROM weather WHERE race_id=? AND lap=?",
            (race_id, lap_num)
        ).fetchone()

        for driver in drivers:
            lap_row = conn.execute("""
                SELECT * FROM laps WHERE race_id=? AND lap=? AND driver=?
            """, (race_id, lap_num, driver)).fetchone()

            if not lap_row or lap_row["lap_time_ms"] is None:
                continue

            driver_gaps = gaps.get(driver, {"gap_ahead_s": None, "gap_behind_s": None, "gap_to_leader_s": None})
            deg_rate = compute_deg_rate(conn, race_id, driver, lap_num)
            delta_vs_fresh = compute_lap_delta_vs_fresh(conn, race_id, driver, lap_num)
            s1_trend = compute_sector_trend(conn, race_id, driver, lap_num, "s1_ms")
            s2_trend = compute_sector_trend(conn, race_id, driver, lap_num, "s2_ms")
            s3_trend = compute_sector_trend(conn, race_id, driver, lap_num, "s3_ms")
            compounds_used = get_compounds_used(conn, race_id, driver, lap_num)
            stops_made = get_stops_made(conn, race_id, driver, lap_num)
            decision, offset = compute_decision(conn, race_id, driver, lap_num, total_laps)
            pos_delta_5 = compute_outcome(conn, race_id, driver, lap_num, 5)
            pos_delta_10 = compute_outcome(conn, race_id, driver, lap_num, 10)
            proj_tyre = projected_tyre_laps(conn, race_id, driver, lap_num, deg_rate)

            # Undercut window: gap_ahead - pit_loss (negative = undercut viable)
            undercut_window = None
            if driver_gaps["gap_ahead_s"] is not None:
                undercut_window = driver_gaps["gap_ahead_s"] - pit_loss

            # Overcut viability (simplified)
            overcut_viable = 0
            if driver_gaps["gap_behind_s"] is not None and deg_rate is not None:
                if driver_gaps["gap_behind_s"] > pit_loss * 0.5 and deg_rate < 0.05:
                    overcut_viable = 1

            outcome_rating = None
            if pos_delta_5 is not None:
                if pos_delta_5 > 0:
                    outcome_rating = "good"
                elif pos_delta_5 < 0:
                    outcome_rating = "bad"
                else:
                    outcome_rating = "neutral"

            laps_remaining = total_laps - lap_num

            conn.execute(
                "INSERT OR REPLACE INTO race_states VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (race_id, lap_num, driver, lap_row["team"],
                 lap_row["position"],
                 driver_gaps["gap_ahead_s"], driver_gaps["gap_behind_s"], driver_gaps["gap_to_leader_s"],
                 lap_row["compound"], lap_row["tyre_life"], lap_row["fresh_tyre"],
                 lap_row["lap_time_ms"] / 1000.0 if lap_row["lap_time_ms"] else None,
                 delta_vs_fresh,
                 s1_trend, s2_trend, s3_trend,
                 deg_rate,
                 weather["track_temp"] if weather else None,
                 weather["air_temp"] if weather else None,
                 weather["rainfall"] if weather else 0,
                 lap_row["track_status"],
                 laps_remaining, total_laps,
                 pit_loss, undercut_window, overcut_viable,
                 compounds_used, stops_made, proj_tyre,
                 decision, offset,
                 pos_delta_5, pos_delta_10, outcome_rating,
                 circuit)
            )
            count += 1

    conn.commit()
    return count


def engineer_all():
    """Run feature engineering for all collected races."""
    conn = get_connection()
    races = conn.execute("SELECT race_id FROM races ORDER BY year, date").fetchall()

    total = 0
    for race in tqdm(races, desc="Engineering features"):
        n = engineer_race(conn, race["race_id"])
        total += n
        print(f"  {race['race_id']}: {n} states")

    conn.close()
    print(f"\nTotal race states engineered: {total}")
    return total


if __name__ == "__main__":
    engineer_all()
