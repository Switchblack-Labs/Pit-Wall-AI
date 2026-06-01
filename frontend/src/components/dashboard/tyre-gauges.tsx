"use client";
import { useLiveTelemetry } from "@/lib/use-live";
import { Bezel, Eyebrow } from "@/components/bezel";
import { cn } from "@/lib/utils";

export function TyreGauges() {
  const { data } = useLiveTelemetry();
  const wear = data?.tire_wear ?? 0;
  const pct = Math.round(wear * 100);
  const color =
    wear > 0.75 ? "bg-signal-danger" :
    wear > 0.55 ? "bg-signal-caution" : "bg-signal-ok";

  const fuelKg = data?.fuel;

  return (
    <Bezel innerClassName="p-7">
      <div className="flex items-center justify-between mb-6">
        <Eyebrow>Tyre wear</Eyebrow>
        <span className="font-mono text-[10px] uppercase tracking-[0.28em] text-ink-mute">
          single channel from telemetry
        </span>
      </div>

      <div className="flex items-end justify-between mb-3">
        <span className="font-mono tabular text-5xl text-ink">{data ? `${pct}%` : "-"}</span>
        {fuelKg != null && (
          <div className="text-right">
            <div className="font-mono text-[10px] uppercase tracking-[0.22em] text-ink-mute">fuel</div>
            <div className="font-mono tabular text-2xl text-ink">{fuelKg.toFixed(1)}<span className="text-sm text-ink-mute ml-1">kg</span></div>
          </div>
        )}
      </div>

      <div className="h-2 rounded-full bg-white/[0.05] overflow-hidden ring-1 ring-white/[0.05]">
        <div
          className={cn("h-full rounded-full transition-all duration-500 ease-spring", color)}
          style={{ width: `${pct}%` }}
        />
      </div>
    </Bezel>
  );
}
