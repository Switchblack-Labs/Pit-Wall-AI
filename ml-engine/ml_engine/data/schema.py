import sqlite3
import os
from ml_engine.config import DB_PATH


def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS races (
        race_id TEXT PRIMARY KEY,
        year INTEGER NOT NULL,
        circuit TEXT NOT NULL,
        circuit_short TEXT,
        total_laps INTEGER,
        date TEXT,
        country TEXT
    );

    CREATE TABLE IF NOT EXISTS laps (
        race_id TEXT NOT NULL,
        lap INTEGER NOT NULL,
        driver TEXT NOT NULL,
        team TEXT,
        position INTEGER,
        lap_time_ms REAL,
        s1_ms REAL,
        s2_ms REAL,
        s3_ms REAL,
        compound TEXT,
        tyre_life INTEGER,
        fresh_tyre INTEGER,
        is_pit_in INTEGER DEFAULT 0,
        is_pit_out INTEGER DEFAULT 0,
        track_status TEXT,
        is_accurate INTEGER DEFAULT 1,
        PRIMARY KEY (race_id, lap, driver),
        FOREIGN KEY (race_id) REFERENCES races(race_id)
    );

    CREATE TABLE IF NOT EXISTS weather (
        race_id TEXT NOT NULL,
        lap INTEGER NOT NULL,
        air_temp REAL,
        track_temp REAL,
        humidity REAL,
        rainfall INTEGER DEFAULT 0,
        wind_speed REAL,
        wind_direction INTEGER,
        PRIMARY KEY (race_id, lap),
        FOREIGN KEY (race_id) REFERENCES races(race_id)
    );

    CREATE TABLE IF NOT EXISTS pit_stops (
        race_id TEXT NOT NULL,
        driver TEXT NOT NULL,
        lap INTEGER NOT NULL,
        duration_s REAL,
        compound_before TEXT,
        compound_after TEXT,
        position_before INTEGER,
        position_after INTEGER,
        PRIMARY KEY (race_id, driver, lap),
        FOREIGN KEY (race_id) REFERENCES races(race_id)
    );

    CREATE TABLE IF NOT EXISTS stints (
        race_id TEXT NOT NULL,
        driver TEXT NOT NULL,
        stint_num INTEGER NOT NULL,
        compound TEXT,
        start_lap INTEGER,
        end_lap INTEGER,
        num_laps INTEGER,
        avg_deg_rate REAL,
        base_pace_ms REAL,
        PRIMARY KEY (race_id, driver, stint_num),
        FOREIGN KEY (race_id) REFERENCES races(race_id)
    );

    CREATE TABLE IF NOT EXISTS race_states (
        race_id TEXT NOT NULL,
        lap INTEGER NOT NULL,
        driver TEXT NOT NULL,
        team TEXT,
        position INTEGER,
        gap_ahead_s REAL,
        gap_behind_s REAL,
        gap_to_leader_s REAL,
        compound TEXT,
        tyre_life INTEGER,
        fresh_tyre INTEGER,
        lap_time_s REAL,
        lap_time_delta_vs_fresh REAL,
        s1_trend REAL,
        s2_trend REAL,
        s3_trend REAL,
        deg_rate REAL,
        track_temp REAL,
        air_temp REAL,
        rainfall INTEGER DEFAULT 0,
        track_status TEXT,
        laps_remaining INTEGER,
        total_laps INTEGER,
        pit_loss_s REAL,
        undercut_window REAL,
        overcut_viable INTEGER DEFAULT 0,
        compounds_used TEXT,
        stops_made INTEGER,
        projected_tyre_laps_remaining INTEGER,
        decision_made TEXT,
        decision_lap_offset INTEGER DEFAULT 0,
        positions_delta_5 INTEGER,
        positions_delta_10 INTEGER,
        outcome_rating TEXT,
        circuit TEXT,
        PRIMARY KEY (race_id, lap, driver),
        FOREIGN KEY (race_id) REFERENCES races(race_id)
    );

    CREATE INDEX IF NOT EXISTS idx_laps_race_driver ON laps(race_id, driver);
    CREATE INDEX IF NOT EXISTS idx_laps_compound ON laps(compound);
    CREATE INDEX IF NOT EXISTS idx_states_circuit ON race_states(circuit);
    CREATE INDEX IF NOT EXISTS idx_states_driver ON race_states(driver);
    CREATE INDEX IF NOT EXISTS idx_states_compound ON race_states(compound);
    """)
    conn.commit()
    conn.close()
