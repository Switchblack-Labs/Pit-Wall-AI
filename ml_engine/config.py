import os

DB_PATH = os.environ.get("PITWALL_DB", os.path.join(os.path.dirname(__file__), "data", "pitwall.db"))
FASTF1_CACHE = os.environ.get("FASTF1_CACHE", os.path.join(os.path.dirname(__file__), "data", "fastf1_cache"))
MODEL_DIR = os.environ.get("PITWALL_MODELS", os.path.join(os.path.dirname(__file__), "models", "saved"))

SEASONS = [2022, 2023, 2024, 2025]
FERRARI_DRIVERS = {
    2022: ["LEC", "SAI"],
    2023: ["LEC", "SAI"],
    2024: ["LEC", "SAI"],
    2025: ["LEC", "HAM"],
}
ALL_TEAMS = True  # collect all teams for gap/competitor context

COMPOUNDS = ["SOFT", "MEDIUM", "HARD", "INTERMEDIATE", "WET"]
COMPOUND_ENCODING = {c: i for i, c in enumerate(COMPOUNDS)}

# Average pit loss per circuit (seconds) - updated from 2022-2024 data
# Will be overwritten by actual computed values after data collection
PIT_LOSS_DEFAULTS = {
    "bahrain": 22.3, "jeddah": 24.1, "albert_park": 22.8,
    "baku": 23.5, "miami": 23.0, "imola": 23.2,
    "monaco": 21.5, "catalunya": 22.0, "montreal": 21.8,
    "silverstone": 21.0, "red_bull_ring": 20.5, "hungaroring": 22.5,
    "spa": 21.3, "zandvoort": 22.0, "monza": 24.5,
    "marina_bay": 29.0, "suzuka": 23.0, "losail": 22.8,
    "americas": 22.0, "mexico_city": 22.5, "interlagos": 21.5,
    "las_vegas": 23.0, "yas_marina": 22.0, "shanghai": 23.5,
}

# Circuits where overtaking is very difficult
LOW_OVERTAKE_CIRCUITS = {"monaco", "hungaroring", "marina_bay", "zandvoort"}
HIGH_OVERTAKE_CIRCUITS = {"monza", "spa", "bahrain", "jeddah", "shanghai", "baku"}

TRACK_STATUS_MAP = {
    "1": "AllClear", "2": "Yellow", "4": "SafetyCar",
    "5": "Red", "6": "VSC", "7": "VSCEnding",
}

# FastF1 location name -> canonical circuit name mapping
CIRCUIT_ALIASES = {
    "sakhir": "bahrain", "jeddah": "jeddah", "melbourne": "albert_park",
    "imola": "imola", "miami": "miami", "barcelona": "catalunya",
    "monaco": "monaco", "baku": "baku", "montréal": "montreal",
    "montreal": "montreal", "silverstone": "silverstone",
    "spielberg": "red_bull_ring", "le_castellet": "paul_ricard",
    "budapest": "hungaroring", "spa_francorchamps": "spa",
    "spa-francorchamps": "spa", "zandvoort": "zandvoort",
    "monza": "monza", "marina_bay": "marina_bay", "suzuka": "suzuka",
    "austin": "americas", "mexico_city": "mexico_city",
    "são_paulo": "interlagos", "sao_paulo": "interlagos",
    "yas_island": "yas_marina", "lusail": "losail", "losail": "losail",
    "las_vegas": "las_vegas", "shanghai": "shanghai",
    "portimão": "portimao", "istanbul": "istanbul",
    "djeddah": "jeddah",
}


def canonical_circuit(raw_name):
    """Convert FastF1 location name to canonical circuit name."""
    key = raw_name.lower().replace(" ", "_").replace("-", "_")
    return CIRCUIT_ALIASES.get(key, key)
