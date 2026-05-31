"""Built-in simulated TORCS telemetry source.

Generates a realistic, evolving TORCS-format stream with **no TORCS install**
required: tires degrade, fuel burns down, laps and sectors progress, occasional
race events (PIT / VSC / SC) fire, and a small field of competitors maintains
gaps. This is the default source so the whole pipeline is demoable offline.

It deliberately produces values within the validation bounds of
:class:`app.schemas.torcs.TorcsTelemetry`.
"""

from __future__ import annotations

import asyncio
import math
import random
from datetime import datetime
from typing import AsyncIterator, List

from app.schemas.torcs import TorcsCompetitorGap, TorcsTelemetry

# Simple track model: lap split into 3 sectors of these nominal seconds.
_NOMINAL_SECTORS = [28.0, 31.0, 30.5]
_TOTAL_LAPS = 58
_TICK_SECONDS = 1.0
_TICKS_PER_LAP = 12  # frames emitted per simulated lap


class SimulatedTorcsSource:
    """Async generator of plausible TORCS telemetry frames."""

    name = "simulated"

    def __init__(
        self,
        *,
        tick_seconds: float = _TICK_SECONDS,
        total_laps: int = _TOTAL_LAPS,
        seed: int | None = None,
        num_competitors: int = 5,
    ) -> None:
        self.tick_seconds = tick_seconds
        self.total_laps = total_laps
        self.num_competitors = num_competitors
        self._rng = random.Random(seed)
        self._running = False

        # Evolving race state.
        self._lap = 1
        self._tick_in_lap = 0
        self._fuel = 100.0          # litres
        self._tire_wear = 0.05      # [0, 1]
        self._cur_lap_time = 0.0
        self._last_lap_time: float | None = None
        self._sector_times: List[float] = []

    def stop(self) -> None:
        self._running = False

    # ------------------------------------------------------------------ frame
    def _make_competitors(self) -> List[TorcsCompetitorGap]:
        comps: List[TorcsCompetitorGap] = []
        cumulative = 0.0
        for i in range(self.num_competitors):
            # Gaps grow with position; jitter each tick.
            cumulative += self._rng.uniform(0.4, 2.5)
            comps.append(
                TorcsCompetitorGap(
                    car_id=f"CAR_{i + 2}",  # ego car is implicitly P1-relative
                    position=i + 2,
                    gap=round(cumulative, 2),
                    pit_status=self._rng.random() < 0.03,
                    pace_delta=round(self._rng.uniform(-0.4, 0.4), 3),
                    tire_wear=round(min(1.0, max(0.0, self._tire_wear + self._rng.uniform(-0.1, 0.2))), 3),
                )
            )
        return comps

    def _events_for_tick(self) -> List[str]:
        events: List[str] = []
        roll = self._rng.random()
        if roll < 0.01:
            events.append("SC")        # safety car
        elif roll < 0.03:
            events.append("VSC")       # virtual safety car
        if self._tick_in_lap == 0 and self._tire_wear > 0.7 and self._rng.random() < 0.3:
            events.append("PIT")       # likely pit window
        return events

    def _build_frame(self) -> TorcsTelemetry:
        # Phase within the lap drives a speed/rpm profile (corners vs straights).
        phase = self._tick_in_lap / _TICKS_PER_LAP
        corner = (math.sin(phase * 2 * math.pi) + 1) / 2  # 0..1
        base_speed = 120 + corner * 190                   # 120..310 km/h
        speed = max(0.0, base_speed + self._rng.uniform(-8, 8))
        rpm = int(7000 + corner * 4500 + self._rng.uniform(-300, 300))
        gear = max(1, min(8, int(2 + corner * 6)))
        throttle = round(min(1.0, 0.3 + corner * 0.7 + self._rng.uniform(-0.05, 0.05)), 3)
        brake = round(max(0.0, (1 - corner) * 0.4 + self._rng.uniform(-0.05, 0.05)), 3)
        steering = round(self._rng.uniform(-0.25, 0.25), 3)
        track_pos = round(self._rng.uniform(-0.9, 0.9), 3)

        # Time + degradation accumulate each tick.
        dt = _NOMINAL_SECTORS[min(2, int(phase * 3))] / _TICKS_PER_LAP
        # Worn tires and traffic cost time.
        dt *= 1.0 + self._tire_wear * 0.08
        self._cur_lap_time += dt

        events = self._events_for_tick()
        if "PIT" in events:
            self._tire_wear = 0.05      # fresh tires
            self._fuel = min(100.0, self._fuel + 30.0)

        frame = TorcsTelemetry(
            speed=round(speed, 2),
            rpm=max(0, rpm),
            gear=gear,
            throttle=throttle,
            brake=brake,
            steering=steering,
            track_position=track_pos,
            lap=self._lap,
            fuel=round(max(0.0, self._fuel), 2),
            tire_wear=round(min(1.0, self._tire_wear), 3),
            cur_lap_time=round(self._cur_lap_time, 3),
            last_lap_time=self._last_lap_time,
            sector_times=list(self._sector_times),
            race_events=events,
            competitor_gaps=self._make_competitors(),
            timestamp=datetime.utcnow(),
        )

        # Advance per-tick state.
        self._fuel = max(0.0, self._fuel - 100.0 / (self.total_laps * _TICKS_PER_LAP))
        self._tire_wear = min(1.0, self._tire_wear + 0.9 / (self.total_laps * _TICKS_PER_LAP) * 2)
        self._tick_in_lap += 1

        # Record sector boundaries.
        sector_idx = int(phase * 3)
        if len(self._sector_times) <= sector_idx < 3:
            self._sector_times.append(round(self._cur_lap_time, 3))

        # Lap rollover.
        if self._tick_in_lap >= _TICKS_PER_LAP:
            self._last_lap_time = round(self._cur_lap_time, 3)
            self._cur_lap_time = 0.0
            self._sector_times = []
            self._tick_in_lap = 0
            self._lap += 1

        return frame

    async def frames(self) -> AsyncIterator[TorcsTelemetry]:
        self._running = True
        while self._running and self._lap <= self.total_laps:
            yield self._build_frame()
            await asyncio.sleep(self.tick_seconds)
        self._running = False
