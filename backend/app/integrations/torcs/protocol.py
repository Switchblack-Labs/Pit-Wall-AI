"""TORCS / SCR sensor-string protocol helpers.

The TORCS "Simulated Car Racing" (SCR) competition server communicates over UDP
using a parenthesised string format, e.g.::

    (speed 83.5)(rpm 4200)(gear 3)(fuel 87.4)(trackPos 0.12)(angle 0.03)...

These helpers parse such strings into a dict and encode dicts back to the wire
format, plus a field map from SCR sensor names to our :class:`TorcsTelemetry`
fields. They are pure functions with no I/O so they are trivially testable and
reused by both the simulated and live sources.
"""

from __future__ import annotations

import re
from typing import Dict, List, Union

Number = Union[float, int, str]

SCR_FIELD_MAP: Dict[str, str] = {
    "speedX": "speed",
    "speed": "speed",
    "rpm": "rpm",
    "gear": "gear",
    "accel": "throttle",
    "brake": "brake",
    "steer": "steering",
    "trackPos": "track_position",
    "fuel": "fuel",
    "curLapTime": "cur_lap_time",
    "lastLapTime": "last_lap_time",
}

_TOKEN_RE = re.compile(r"\(([^()]*)\)")


def parse_sensors(sensor_string: str) -> Dict[str, List[Number]]:
    """Parse an SCR sensor string into ``{name: [values...]}``.

    Each ``(name v1 v2 ...)`` group becomes a list of parsed values (floats
    when numeric, else the raw token). Single-value sensors still return a
    one-element list, matching the SCR wire format.
    """
    out: Dict[str, List[Number]] = {}
    for group in _TOKEN_RE.findall(sensor_string):
        parts = group.split()
        if not parts:
            continue
        name, raw_values = parts[0], parts[1:]
        values: List[Number] = []
        for token in raw_values:
            try:
                values.append(float(token))
            except ValueError:
                values.append(token)
        out[name] = values
    return out


def encode_sensors(sensors: Dict[str, Union[Number, List[Number]]]) -> str:
    """Encode ``{name: value | [values]}`` into an SCR sensor string."""
    chunks: List[str] = []
    for name, value in sensors.items():
        if isinstance(value, (list, tuple)):
            joined = " ".join(str(v) for v in value)
        else:
            joined = str(value)
        chunks.append(f"({name} {joined})")
    return "".join(chunks)


def _first(values: List[Number], default: Number = 0.0) -> Number:
    return values[0] if values else default


def sensors_to_telemetry_dict(sensors: Dict[str, List[Number]]) -> Dict[str, Number]:
    """Map parsed SCR sensors to a partial :class:`TorcsTelemetry` kwargs dict.

    Only the directly-mapped scalar fields are filled; derived fields
    (sector_times, competitor_gaps, lap, tire_wear) are computed by the caller
    since SCR does not expose them directly.
    """
    mapped: Dict[str, Number] = {}
    for scr_name, field in SCR_FIELD_MAP.items():
        if scr_name in sensors:
            mapped[field] = _first(sensors[scr_name])
    if "speedX" in sensors:
        mapped["speed"] = abs(float(_first(sensors["speedX"]))) * 3.6
    if "gear" in mapped:
        mapped["gear"] = int(mapped["gear"])
    if "rpm" in mapped:
        mapped["rpm"] = int(mapped["rpm"])
    return mapped
