"use client";
import { useEffect, useRef, useState } from "react";
import { Bezel, Eyebrow } from "@/components/bezel";
import { useRaceHistory } from "@/lib/use-race-history";



export function LapDelta() {
  const { lapRows } = useRaceHistory();
  const [series, setSeries] = useState<number[]>([]);
  const seenLaps = useRef(new Set<number>());

  useEffect(() => {
    
    const completed = lapRows.filter((r) => r.total != null);
    if (completed.length === 0) return;
    const best = completed.reduce((m, r) => Math.min(m, r.total!), Infinity);
    for (const r of completed) {
      if (seenLaps.current.has(r.lap)) continue;
      seenLaps.current.add(r.lap);
      setSeries((s) => [...s.slice(-79), (r.total! - best)]);
    }
  }, [lapRows]);

  const max = Math.max(1, ...series.map(Math.abs));
  const min = -max;
  const w = 100, h = 100;
  const pts = series
    .map((v, i) => {
      const x = (i / Math.max(1, series.length - 1)) * w;
      const y = h - ((v - min) / (max - min)) * h;
      return `${x.toFixed(2)},${y.toFixed(2)}`;
    })
    .join(" ");
  const last = series[series.length - 1] ?? 0;

  return (
    <Bezel innerClassName="p-7">
      <div className="flex items-center justify-between mb-4">
        <Eyebrow>Lap delta</Eyebrow>
        <span className="font-mono tabular text-2xl text-ink">
          {series.length === 0 ? "-" : `${last >= 0 ? "+" : ""}${last.toFixed(2)}s`}
        </span>
      </div>
      <div className="relative h-32">
        <svg viewBox="0 0 100 100" className="absolute inset-0 h-full w-full" preserveAspectRatio="none">
          <line x1="0" x2="100" y1="50" y2="50" stroke="rgba(242,235,224,0.10)" strokeWidth="0.5" />
          {series.length > 1 && (
            <polyline
              points={pts}
              fill="none"
              stroke="#E26C45"
              strokeWidth="1.5"
              strokeLinejoin="round"
              strokeLinecap="round"
              vectorEffect="non-scaling-stroke"
            />
          )}
        </svg>
      </div>
      <div className="mt-4 flex justify-between font-mono text-[10px] uppercase tracking-[0.28em] text-ink-mute">
        <span>{(-max).toFixed(2)}s</span>
        <span>vs running best lap</span>
        <span>+{max.toFixed(2)}s</span>
      </div>
    </Bezel>
  );
}
