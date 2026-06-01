"""
Collects race data from FastF1 for 2022-2025 seasons and stores in SQLite.
"""
import fastf1
import pandas as pd
import numpy as np
import sqlite3
import os
import time
from tqdm import tqdm
from ml_engine.config import SEASONS, FASTF1_CACHE, COMPOUNDS, canonical_circuit
from ml_engine.data.schema import get_connection, init_db

# Rate limiting: FastF1 allows 500 API calls/hour
# Each race uses ~15-20 calls. With 88 races that's ~1500 calls.
# We need to pace ourselves.
_call_count = 0
_call_window_start = time.time()
MAX_CALLS_PER_HOUR = 450  # leave some buffer
CALLS_PER_RACE = 20  # approximate


def setup_cache():
    os.makedirs(FASTF1_CACHE, exist_ok=True)
    fastf1.Cache.enable_cache(FASTF1_CACHE)


def get_race_schedule(year):
    schedule = fastf1.get_event_schedule(year)
    races = schedule[schedule["EventFormat"].isin(["conventional", "sprint_shootout", "sprint_qualifying", "sprint"])]
    return races


def _td_to_ms(td):
    if pd.isna(td):
        return None
    return td.total_seconds() * 1000


def _td_to_s(td):
    if pd.isna(td):
        return None
    return td.total_seconds()


def collect_race(year, event_name, conn):
    """Collect a single race session."""
    try:
        session = fastf1.get_session(year, event_name, "R")
        session.load(telemetry=False, messages=False)
    except Exception as e:
        print(f"  SKIP {year} {event_name}: {e}")
        return False

    raw_location = session.event.Location.lower().replace(" ", "_").replace("-", "_")
    circuit_key = canonical_circuit(raw_location)
    race_id = f"{year}_{circuit_key}_r"
    total_laps = int(session.total_laps) if hasattr(session, "total_laps") and session.total_laps else None

    if total_laps is None:
        laps_df = session.laps
        if len(laps_df) > 0:
            total_laps = int(laps_df["LapNumber"].max())
        else:
            return False

    # Insert race
    conn.execute(
        "INSERT OR REPLACE INTO races VALUES (?,?,?,?,?,?,?)",
        (race_id, year, circuit_key, circuit_key,
         total_laps, str(session.date.date()) if session.date else None,
         session.event.Country if hasattr(session.event, "Country") else None)
    )

    # Laps
    laps_df = session.laps
    if len(laps_df) == 0:
        return False

    for _, lap in laps_df.iterrows():
        driver = lap.get("Driver", None)
        if driver is None:
            continue

        compound = lap.get("Compound", None)
        if compound and compound.upper() not in COMPOUNDS:
            compound = None

        is_pit_in = 1 if pd.notna(lap.get("PitInTime")) else 0
        is_pit_out = 1 if pd.notna(lap.get("PitOutTime")) else 0
        track_status = str(lap.get("TrackStatus", "1")) if pd.notna(lap.get("TrackStatus")) else "1"

        conn.execute(
            "INSERT OR REPLACE INTO laps VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (race_id, int(lap["LapNumber"]), driver,
             lap.get("Team", None),
             int(lap["Position"]) if pd.notna(lap.get("Position")) else None,
             _td_to_ms(lap.get("LapTime")),
             _td_to_ms(lap.get("Sector1Time")),
             _td_to_ms(lap.get("Sector2Time")),
             _td_to_ms(lap.get("Sector3Time")),
             compound.upper() if compound else None,
             int(lap["TyreLife"]) if pd.notna(lap.get("TyreLife")) else None,
             1 if lap.get("FreshTyre") else 0,
             is_pit_in, is_pit_out, track_status,
             1 if lap.get("IsAccurate", True) else 0)
        )

    # Weather - map to lap numbers
    weather_df = session.weather_data
    if weather_df is not None and len(weather_df) > 0:
        laps_with_time = laps_df[laps_df["LapStartDate"].notna()].copy()
        if len(laps_with_time) > 0:
            for lap_num in range(1, total_laps + 1):
                lap_rows = laps_with_time[laps_with_time["LapNumber"] == lap_num]
                if len(lap_rows) == 0:
                    continue
                lap_time = lap_rows.iloc[0]["LapStartDate"]
                if pd.isna(lap_time):
                    continue
                # Find nearest weather reading
                time_diffs = abs(weather_df["Time"] - lap_time)
                nearest_idx = time_diffs.idxmin()
                w = weather_df.loc[nearest_idx]

                conn.execute(
                    "INSERT OR REPLACE INTO weather VALUES (?,?,?,?,?,?,?,?)",
                    (race_id, lap_num,
                     float(w.get("AirTemp", 0)) if pd.notna(w.get("AirTemp")) else None,
                     float(w.get("TrackTemp", 0)) if pd.notna(w.get("TrackTemp")) else None,
                     float(w.get("Humidity", 0)) if pd.notna(w.get("Humidity")) else None,
                     1 if w.get("Rainfall", False) else 0,
                     float(w.get("WindSpeed", 0)) if pd.notna(w.get("WindSpeed")) else None,
                     int(w.get("WindDirection", 0)) if pd.notna(w.get("WindDirection")) else None)
                )

    # Pit stops - derive from laps
    pit_laps = laps_df[laps_df["PitInTime"].notna()].copy()
    for _, pit in pit_laps.iterrows():
        driver = pit["Driver"]
        lap_num = int(pit["LapNumber"])
        pit_duration = None
        if pd.notna(pit.get("PitOutTime")) and pd.notna(pit.get("PitInTime")):
            pit_duration = (pit["PitOutTime"] - pit["PitInTime"]).total_seconds()

        # Get compound before and after
        compound_before = pit.get("Compound", None)
        if compound_before:
            compound_before = compound_before.upper()
        next_lap = laps_df[(laps_df["Driver"] == driver) & (laps_df["LapNumber"] == lap_num + 1)]
        compound_after = None
        if len(next_lap) > 0:
            compound_after = next_lap.iloc[0].get("Compound", None)
            if compound_after:
                compound_after = compound_after.upper()

        pos_before = int(pit["Position"]) if pd.notna(pit.get("Position")) else None
        next_lap_pos = None
        if len(next_lap) > 0:
            next_lap_pos = int(next_lap.iloc[0]["Position"]) if pd.notna(next_lap.iloc[0].get("Position")) else None

        conn.execute(
            "INSERT OR REPLACE INTO pit_stops VALUES (?,?,?,?,?,?,?,?)",
            (race_id, driver, lap_num, pit_duration,
             compound_before, compound_after, pos_before, next_lap_pos)
        )

    # Stints - derive from laps per driver
    for driver in laps_df["Driver"].unique():
        driver_laps = laps_df[laps_df["Driver"] == driver].sort_values("LapNumber")
        stint_num = 0
        stint_start = None
        current_compound = None

        for _, lap in driver_laps.iterrows():
            compound = lap.get("Compound", None)
            if compound:
                compound = compound.upper()

            if compound != current_compound or stint_start is None:
                # Save previous stint
                if stint_start is not None and current_compound:
                    _save_stint(conn, race_id, driver, stint_num, current_compound,
                               stint_start, int(lap["LapNumber"]) - 1, driver_laps)
                stint_num += 1
                stint_start = int(lap["LapNumber"])
                current_compound = compound

        # Save last stint
        if stint_start is not None and current_compound:
            _save_stint(conn, race_id, driver, stint_num, current_compound,
                        stint_start, int(driver_laps.iloc[-1]["LapNumber"]), driver_laps)

    conn.commit()
    return True


def _save_stint(conn, race_id, driver, stint_num, compound, start_lap, end_lap, driver_laps):
    stint_laps = driver_laps[
        (driver_laps["LapNumber"] >= start_lap) &
        (driver_laps["LapNumber"] <= end_lap) &
        (driver_laps["IsAccurate"] == True)
    ]

    num_laps = end_lap - start_lap + 1
    avg_deg = None
    base_pace = None

    if len(stint_laps) >= 3:
        times = stint_laps["LapTime"].apply(lambda x: x.total_seconds() * 1000 if pd.notna(x) else None).dropna()
        if len(times) >= 3:
            base_pace = float(times.iloc[:2].mean())
            # Linear deg rate: ms lost per lap
            lap_indices = np.arange(len(times))
            try:
                coeffs = np.polyfit(lap_indices, times.values, 1)
                avg_deg = float(coeffs[0])  # ms per lap degradation
            except (np.linalg.LinAlgError, ValueError):
                avg_deg = None

    conn.execute(
        "INSERT OR REPLACE INTO stints VALUES (?,?,?,?,?,?,?,?,?)",
        (race_id, driver, stint_num, compound, start_lap, end_lap, num_laps, avg_deg, base_pace)
    )


def _rate_limit():
    """Wait if we're approaching the API rate limit."""
    global _call_count, _call_window_start
    _call_count += CALLS_PER_RACE
    elapsed = time.time() - _call_window_start

    if _call_count >= MAX_CALLS_PER_HOUR:
        wait_time = max(0, 3600 - elapsed) + 60  # wait until window resets + buffer
        if wait_time > 0:
            print(f"\n  Rate limit approaching ({_call_count} calls in {elapsed:.0f}s). "
                  f"Waiting {wait_time:.0f}s...")
            time.sleep(wait_time)
            _call_count = 0
            _call_window_start = time.time()
    elif elapsed > 3600:
        # Window reset
        _call_count = CALLS_PER_RACE
        _call_window_start = time.time()


def collect_all(seasons=None, skip_existing=True):
    """Collect all race data for specified seasons."""
    global _call_count, _call_window_start
    _call_count = 0
    _call_window_start = time.time()

    if seasons is None:
        seasons = SEASONS
    setup_cache()
    init_db()
    conn = get_connection()

    # Get already-collected race IDs to skip
    existing = set()
    if skip_existing:
        existing = {r["race_id"] for r in conn.execute("SELECT race_id FROM races").fetchall()}
        if existing:
            print(f"Skipping {len(existing)} already-collected races")

    for year in seasons:
        print(f"\n{'='*60}")
        print(f"Collecting {year} season")
        print(f"{'='*60}")
        schedule = get_race_schedule(year)

        for _, event in tqdm(list(schedule.iterrows()), desc=f"{year}"):
            event_name = event["EventName"]

            # Check if already collected (approximate check via year)
            # We check after loading to get exact race_id, but can skip obvious ones
            print(f"\n  {event_name}...", end=" ")

            _rate_limit()
            ok = collect_race(year, event_name, conn)
            print("OK" if ok else "SKIPPED")

    conn.close()
    print(f"\nData collection complete.")


if __name__ == "__main__":
    collect_all()
