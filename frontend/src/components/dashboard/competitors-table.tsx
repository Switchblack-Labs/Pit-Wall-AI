"use client";
import { useEffect, useState } from "react";
import { Bezel, Eyebrow } from "@/components/bezel";
import { api } from "@/lib/api";
import type { Competitor } from "@/lib/types";
import { cn } from "@/lib/utils";

export function CompetitorsTable() {
  const [rows, setRows] = useState<Competitor[] | null>(null);

  useEffect(() => {
    let killed = false;
    const tick = async () => {
      const live = await api.competitors();
      if (!killed) setRows(live ?? []);
    };
    tick();
    const id = setInterval(tick, 4000);
    return () => { killed = true; clearInterval(id); };
  }, []);

  return (
    <Bezel innerClassName="p-7">
      <div className="flex items-center justify-between mb-4">
        <Eyebrow>Field</Eyebrow>
        <span className="font-mono text-[10px] uppercase tracking-[0.28em] text-ink-mute">
          from /api/competitors
        </span>
      </div>
      {rows === null && (
        <div className="py-8 text-center text-ink-mute text-xs">loading</div>
      )}
      {rows && rows.length === 0 && (
        <div className="py-8 text-center text-ink-mute text-xs">
          no competitors posted yet
        </div>
      )}
      {rows && rows.length > 0 && (
        <table className="w-full font-mono text-sm tabular">
          <thead>
            <tr className="text-[10px] uppercase tracking-[0.22em] text-ink-mute">
              <th className="text-left py-2 font-normal">POS</th>
              <th className="text-left py-2 font-normal">CAR</th>
              <th className="text-right py-2 font-normal">GAP</th>
              <th className="text-right py-2 font-normal">PACE</th>
              <th className="text-right py-2 font-normal">WEAR</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((c) => (
              <tr key={c.car_id} className="border-t border-line">
                <td className="py-2.5 text-ink-dim">P{c.position}</td>
                <td className="py-2.5 text-ink">
                  <span className="inline-flex items-center gap-2">
                    {c.car_id}
                    {c.pit_status && (
                      <span className="rounded-full bg-coral/20 px-2 py-0.5 text-[9px] uppercase tracking-[0.18em] text-coral-hi ring-1 ring-coral/30">
                        PIT
                      </span>
                    )}
                  </span>
                </td>
                <td className="py-2.5 text-right text-ink">{c.gap === 0 ? "-" : `+${c.gap.toFixed(1)}s`}</td>
                <td className={cn(
                  "py-2.5 text-right",
                  c.pace_delta < 0 ? "text-signal-ok" : c.pace_delta > 0 ? "text-signal-danger" : "text-ink"
                )}>
                  {c.pace_delta >= 0 ? "+" : ""}{c.pace_delta.toFixed(2)}s
                </td>
                <td className="py-2.5 text-right text-ink-dim">{Math.round(c.tire_wear * 100)}%</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </Bezel>
  );
}
