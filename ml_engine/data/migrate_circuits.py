"""Migrate existing DB entries to use canonical circuit names."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ml_engine.data.schema import get_connection
from ml_engine.config import canonical_circuit


def migrate():
    conn = get_connection()
    conn.execute("PRAGMA foreign_keys=OFF")

    # Get all races
    races = conn.execute("SELECT race_id, circuit FROM races").fetchall()

    for race in races:
        old_id = race["race_id"]
        old_circuit = race["circuit"]
        new_circuit = canonical_circuit(old_circuit)

        if old_circuit == new_circuit:
            continue

        # Build new race_id
        parts = old_id.split("_")
        year = parts[0]
        suffix = parts[-1]
        new_id = f"{year}_{new_circuit}_{suffix}"

        print(f"  {old_id} -> {new_id} (circuit: {old_circuit} -> {new_circuit})")

        # Update races table first
        conn.execute("UPDATE races SET race_id=?, circuit=?, circuit_short=? WHERE race_id=?",
                     (new_id, new_circuit, new_circuit, old_id))

        # Update child tables
        for table in ["laps", "weather", "pit_stops", "stints", "race_states"]:
            conn.execute(f"UPDATE {table} SET race_id=? WHERE race_id=?", (new_id, old_id))

        conn.execute("UPDATE race_states SET circuit=? WHERE race_id=?", (new_circuit, new_id))

    conn.commit()
    conn.execute("PRAGMA foreign_keys=ON")
    print(f"Migrated {len(races)} races")
    conn.close()


if __name__ == "__main__":
    migrate()
