"use client";
import { Bezel, Eyebrow } from "@/components/bezel";
import { useRaceHistory } from "@/lib/use-race-history";
import { cn } from "@/lib/utils";

function fmt(v?: number) {
  if (v == null) return "-";
  const m = Math.floor(v / 60);
  const s = (v - m * 60).toFixed(3);
  return m ? `${m}:${s.padStart(6, "0")}` : s;
}

export function Sectors() {
  const { lapRows } = useRaceHistory();
  const recent = lapRows.slice(0, 5);

  
  let pbLap: number | null = null;
  let flLap: number | null = null;
  let pbTotal = Infinity;
  for (const r of lapRows) {
    if (r.total != null && r.total < pbTotal) {
      pbTotal = r.total;
      pbLap = r.lap;
      flLap = r.lap;
    }
  }

  return (
    <Bezel innerClassName="p-7">
      <div className="flex items-center justify-between mb-4">
        <Eyebrow>Sector times</Eyebrow>
        <span className="font-mono text-[10px] uppercase tracking-[0.28em] text-ink-mute">
          live from telemetry
        </span>
      </div>
      <table className="w-full font-mono text-sm tabular">
        <thead>
          <tr className="text-[10px] uppercase tracking-[0.22em] text-ink-mute">
            <th className="text-left py-2 font-normal">LAP</th>
            <th className="text-right py-2 font-normal">S1</th>
            <th className="text-right py-2 font-normal">S2</th>
            <th className="text-right py-2 font-normal">S3</th>
            <th className="text-right py-2 font-normal w-12"></th>
          </tr>
        </thead>
        <tbody>
          {recent.length === 0 && (
            <tr className="border-t border-line">
              <td colSpan={5} className="py-6 text-center text-ink-mute text-xs">
                waiting for first completed lap
              </td>
            </tr>
          )}
          {recent.map((r) => {
            const isFL = r.lap === flLap;
            const isPB = r.lap === pbLap && !isFL;
            return (
              <tr key={r.lap} className="border-t border-line">
                <td className="py-2.5 text-ink-dim">{String(r.lap).padStart(2, "0")}</td>
                <td className="py-2.5 text-right text-ink">{fmt(r.s1)}</td>
                <td className="py-2.5 text-right text-ink">{fmt(r.s2)}</td>
                <td className="py-2.5 text-right text-ink">{fmt(r.s3)}</td>
                <td className="py-2.5 text-right">
                  {(isFL || isPB) && (
                    <span className={cn(
                      "rounded-full px-2 py-0.5 text-[10px] uppercase tracking-[0.18em]",
                      isFL ? "bg-coral text-white" : "bg-white/[0.06] text-ink-dim ring-1 ring-white/[0.08]"
                    )}>{isFL ? "FL" : "PB"}</span>
                  )}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </Bezel>
  );
}
