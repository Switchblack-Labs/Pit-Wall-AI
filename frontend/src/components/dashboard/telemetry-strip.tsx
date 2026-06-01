"use client";
import { useLiveTelemetry } from "@/lib/use-live";
import { Bezel, Eyebrow } from "@/components/bezel";
import { compact, fmt, pad } from "@/lib/utils";

function NumberBlock({ label, value, unit }: { label: string; value: string; unit?: string }) {
  return (
    <div className="flex min-w-0 flex-col">
      <span className="font-mono text-[10px] uppercase tracking-[0.28em] text-ink-mute mb-2">{label}</span>
      <span className="font-mono tabular text-[clamp(30px,4vw,64px)] leading-none text-ink whitespace-nowrap">
        {value}
        {unit && <span className="ml-2 text-base text-ink-mute">{unit}</span>}
      </span>
    </div>
  );
}

export function TelemetryStrip() {
  const { data, status } = useLiveTelemetry(100);

  const speed = data ? Math.round(data.speed) : 0;
  const rpm = data ? data.rpm : 0;
  const gear = data ? data.gear : 0;
  const throttle = data ? Math.round(data.throttle * 100) : 0;
  const brake = data ? Math.round(data.brake * 100) : 0;
  const lap = data ? data.lap : 1;

  return (
    <Bezel innerClassName="p-8 lg:p-10">
      <div className="flex items-start justify-between mb-8">
        <div>
          <Eyebrow>Telemetry - 60Hz</Eyebrow>
          <div className="mt-3 font-sans text-3xl font-medium tracking-tight text-ink">
            Lap {pad(lap)}
          </div>
        </div>
        <div className="font-mono text-[10px] uppercase tracking-[0.28em] text-ink-mute">
          socket {status}
        </div>
      </div>

      <div className="grid grid-cols-2 xl:grid-cols-4 gap-x-10 gap-y-8">
        <NumberBlock label="SPEED" value={fmt(speed)} unit="KM/H" />
        <NumberBlock label="RPM" value={compact(rpm)} />
        <NumberBlock label="GEAR" value={String(gear)} />
        <NumberBlock label="FUEL" value={data ? fmt(data.fuel, 1) : "-"} unit="KG" />
      </div>

      {}
      <div className="mt-10 space-y-4">
        <div className="flex items-center gap-4">
          <span className="font-mono text-[10px] uppercase tracking-[0.28em] text-ink-mute w-20">THR</span>
          <div className="h-1.5 flex-1 overflow-hidden rounded-full bg-white/[0.05] ring-1 ring-white/[0.05]">
            <div
              className="h-full rounded-full bg-signal-ok transition-all duration-200 ease-out"
              style={{ width: `${throttle}%` }}
            />
          </div>
          <span className="font-mono tabular text-sm w-12 text-right text-ink">{throttle}</span>
        </div>
        <div className="flex items-center gap-4">
          <span className="font-mono text-[10px] uppercase tracking-[0.28em] text-ink-mute w-20">BRK</span>
          <div className="h-1.5 flex-1 overflow-hidden rounded-full bg-white/[0.05] ring-1 ring-white/[0.05]">
            <div
              className="h-full rounded-full bg-signal-danger transition-all duration-200 ease-out"
              style={{ width: `${brake}%` }}
            />
          </div>
          <span className="font-mono tabular text-sm w-12 text-right text-ink">{brake}</span>
        </div>
      </div>
    </Bezel>
  );
}
