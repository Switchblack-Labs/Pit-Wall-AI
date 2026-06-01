"use client";
import { useEffect, useState } from "react";
import { useLiveTelemetry } from "@/lib/use-live";
import { Bezel } from "@/components/bezel";
import { CircuitPicker } from "@/components/circuit-picker";
import { CIRCUITS, getCircuit } from "@/lib/circuits";

export function TrackMap() {
  const { data } = useLiveTelemetry(120);
  const phase = data?.track_position ?? 0;

  const [circuitId, setCircuitId] = useState<string>(() => {
    if (typeof window !== "undefined") return localStorage.getItem("rm:circuit") ?? "imola";
    return "imola";
  });
  useEffect(() => { localStorage.setItem("rm:circuit", circuitId); }, [circuitId]);

  const circuit = getCircuit(circuitId);

  return (
    <Bezel className="h-full" innerClassName="p-6 h-full flex flex-col">
      <div className="flex items-start justify-between mb-4 gap-4">
        <div>
          <div className="font-mono text-[10px] uppercase tracking-[0.28em] text-ink-mute">
            Circuit
          </div>
          <h3 className="mt-1.5 font-sans text-ink text-lg tracking-tight" style={{ fontWeight: 500 }}>
            {circuit.shortName}
            <span className="ml-2 font-mono text-[10px] text-ink-mute uppercase tracking-[0.22em]">
              {circuit.country}
            </span>
          </h3>
        </div>
        <div className="font-mono text-[10px] uppercase tracking-[0.22em] text-ink-mute text-right leading-relaxed">
          {circuit.length_km.toFixed(3)} km<br />
          {circuit.laps} laps - pit −{circuit.pit_loss_s}s
        </div>
      </div>

      <div className="mb-4">
        <CircuitPicker value={circuitId} onChange={setCircuitId} />
      </div>

      <div className="relative flex-1 min-h-[320px]">
        <svg viewBox="0 0 660 560" className="absolute inset-0 h-full w-full">
          <defs>
            <filter id="trk-glow">
              <feGaussianBlur stdDeviation="4" />
            </filter>
          </defs>
          {}
          <path
            d={circuit.svgPath}
            fill="none"
            stroke="rgba(242,235,224,0.10)"
            strokeWidth="22"
            strokeLinejoin="round"
          />
          {}
          <path
            d={circuit.svgPath}
            fill="none"
            stroke="rgba(242,235,224,0.04)"
            strokeWidth="14"
            strokeLinejoin="round"
          />
          {}
          <path
            d={circuit.svgPath}
            fill="none"
            stroke="#E26C45"
            strokeWidth="1.8"
            strokeOpacity="0.7"
            strokeLinejoin="round"
            strokeDasharray="6 12"
            className="animate-pulse"
          />
          {}
          <CarDot path={circuit.svgPath} phase={phase} />
          {}
          {[circuit.sectors[0], circuit.sectors[0] + circuit.sectors[1]].map((s, i) => (
            <SectorMarker key={i} path={circuit.svgPath} phase={s} />
          ))}
        </svg>
      </div>

      <div className="mt-3 flex items-center justify-between text-[10px] uppercase tracking-[0.22em] font-mono text-ink-mute">
        <span>S1 - {(circuit.sectors[0] * 100).toFixed(0)}%</span>
        <span>S2 - {(circuit.sectors[1] * 100).toFixed(0)}%</span>
        <span>S3 - {(circuit.sectors[2] * 100).toFixed(0)}%</span>
      </div>
    </Bezel>
  );
}

function pointAtPhase(path: string, phase: number) {
  if (typeof document === "undefined") return { x: 80, y: 220 };
  const tmp = document.createElementNS("http://www.w3.org/2000/svg", "path");
  tmp.setAttribute("d", path);
  const len = (tmp as SVGPathElement).getTotalLength?.() ?? 0;
  if (!len) return { x: 80, y: 220 };
  const p = (tmp as SVGPathElement).getPointAtLength(len * phase);
  return { x: p.x, y: p.y };
}

function CarDot({ path, phase }: { path: string; phase: number }) {
  const pos = pointAtPhase(path, phase);
  return (
    <g>
      <circle cx={pos.x} cy={pos.y} r={9} fill="#E26C45" filter="url(#trk-glow)" />
      <circle cx={pos.x} cy={pos.y} r={4} fill="#fff" />
    </g>
  );
}

function SectorMarker({ path, phase }: { path: string; phase: number }) {
  const pos = pointAtPhase(path, phase);
  return <circle cx={pos.x} cy={pos.y} r={3} fill="rgba(242,235,224,0.4)" />;
}
