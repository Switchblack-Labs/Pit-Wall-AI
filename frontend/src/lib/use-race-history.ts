"use client";
import { useEffect, useMemo, useState } from "react";
import { useLiveTelemetry } from "./use-live";
import type { RaceEventFrame } from "./types";

export type SectorLap = {
  lap: number;
  s1?: number;
  s2?: number;
  s3?: number;
  total?: number;
};



export function useRaceHistory() {
  const { data } = useLiveTelemetry();
  const [laps, setLaps] = useState<Map<number, SectorLap>>(new Map());
  const [events, setEvents] = useState<RaceEventFrame[]>([]);

  useEffect(() => {
    if (!data) return;
    if (data.sector_times && data.sector_times.length) {
      setLaps((prev) => {
        const next = new Map(prev);
        const lap = data.lap;
        const cur: SectorLap = next.get(lap) ?? { lap };
        const [s1, s2, s3] = data.sector_times!;
        if (s1 != null) cur.s1 = s1;
        if (s2 != null) cur.s2 = s2;
        if (s3 != null) cur.s3 = s3;
        if (data.last_lap_time != null && lap > 0) {
          const prevLap = next.get(lap - 1) ?? { lap: lap - 1 };
          prevLap.total = data.last_lap_time;
          next.set(lap - 1, prevLap);
        }
        next.set(lap, cur);
        return next;
      });
    }
    if (data.race_events && data.race_events.length) {
      setEvents((prev) => {
        
        const seen = new Set(prev.map((e) => `${e.lap}|${e.kind}`));
        const incoming = data.race_events!.filter(
          (e) => !seen.has(`${e.lap}|${e.kind}`)
        );
        return incoming.length ? [...prev, ...incoming] : prev;
      });
    }
  }, [data]);

  const lapRows = useMemo(
    () => Array.from(laps.values()).sort((a, b) => b.lap - a.lap),
    [laps]
  );

  return { telemetry: data, lapRows, events };
}
