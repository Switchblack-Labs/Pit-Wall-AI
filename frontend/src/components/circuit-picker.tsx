"use client";
import { CIRCUITS, type Circuit } from "@/lib/circuits";
import { cn } from "@/lib/utils";

export function CircuitPicker({
  value,
  onChange,
  className,
}: {
  value: string;
  onChange: (id: string) => void;
  className?: string;
}) {
  return (
    <div className={cn("flex items-center gap-2 overflow-x-auto", className)}>
      {CIRCUITS.map((c) => {
        const active = value === c.id;
        return (
          <button
            key={c.id}
            onClick={() => onChange(c.id)}
            className={cn(
              "shrink-0 rounded-full px-3.5 py-1.5 text-xs ring-1 transition-all duration-300 ease-spring",
              active
                ? "bg-coral text-white ring-coral"
                : "bg-white/[0.03] text-ink-dim ring-white/[0.10] hover:text-ink hover:bg-white/[0.06]"
            )}
          >
            <span className="font-medium">{c.shortName}</span>
            <span className="ml-2 font-mono text-[10px] tracking-[0.18em] opacity-70">{c.flag}</span>
          </button>
        );
      })}
    </div>
  );
}

export function CircuitHeadline({ circuit }: { circuit: Circuit }) {
  return (
    <div className="flex flex-wrap items-end gap-x-8 gap-y-3 font-mono text-[10px] uppercase tracking-[0.22em] text-ink-mute">
      <span><span className="text-ink-dim">Length</span> - {circuit.length_km.toFixed(3)} km</span>
      <span><span className="text-ink-dim">Laps</span> - {circuit.laps}</span>
      <span><span className="text-ink-dim">Corners</span> - {circuit.corners}</span>
      <span><span className="text-ink-dim">Pit loss</span> - {circuit.pit_loss_s}s</span>
      <span><span className="text-ink-dim">DRS</span> - {circuit.drs_zones} zone{circuit.drs_zones > 1 ? "s" : ""}</span>
    </div>
  );
}
