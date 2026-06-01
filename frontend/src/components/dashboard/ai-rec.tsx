"use client";
import { useEffect, useState } from "react";
import { Bezel, Eyebrow } from "@/components/bezel";
import { api } from "@/lib/api";
import { useLiveTelemetry } from "@/lib/use-live";
import { useRaceContext } from "@/components/dashboard/race-context";
import type { FullRecommendation } from "@/lib/api";

export function AiRecommendation() {
  const { data: tel } = useLiveTelemetry();
  const ctx = useRaceContext();
  const [rec, setRec] = useState<FullRecommendation | null>(null);
  const [open, setOpen] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const lap = tel?.lap ?? 0;
  const tyreLife = tel ? Math.max(1, Math.round((tel.tire_wear ?? 0) * 40)) : 1;
  const lapsRemaining = Math.max(1, ctx.totalLaps - lap);

  useEffect(() => {
    let killed = false;
    const fetchRec = async () => {
      const live = await api.recommendFull({
        circuit: ctx.circuit,
        compound: ctx.compound,
        tyre_life: tyreLife,
        laps_remaining: lapsRemaining,
        total_laps: ctx.totalLaps,
        position: ctx.position,
        pit_loss_s: ctx.pitLossS,
      });
      if (killed) return;
      if (live) { setRec(live); setError(null); }
      else setError("backend unreachable");
    };
    fetchRec();
    return () => { killed = true; };
  }, [lap, tyreLife, lapsRemaining, ctx.circuit, ctx.compound, ctx.totalLaps, ctx.position, ctx.pitLossS]);

  if (error) {
    return (
      <Bezel className="h-full" innerClassName="p-7 h-full flex flex-col">
        <Eyebrow>Granite recommendation</Eyebrow>
        <div className="mt-auto pt-10 text-center text-signal-danger text-xs font-mono uppercase tracking-[0.22em]">
          {error}
        </div>
      </Bezel>
    );
  }

  if (!rec) {
    return (
      <Bezel className="h-full" innerClassName="p-7 h-full flex flex-col">
        <Eyebrow>Granite recommendation</Eyebrow>
        <div className="mt-auto pt-10 text-center text-ink-mute text-xs">loading</div>
      </Bezel>
    );
  }

  const confPct = Math.round(rec.confidence * 100);
  const risk = rec.risk_level.toLowerCase();
  const riskMark =
    risk === "low" ? "bg-white/35" :
    risk === "high" ? "bg-coral" : "bg-white/55";

  return (
    <Bezel className="h-full" innerClassName="p-7 h-full flex flex-col">
      <div className="flex items-center justify-between">
        <Eyebrow>Granite recommendation</Eyebrow>
        <span className="inline-flex items-center gap-2 font-mono text-[10px] uppercase tracking-[0.22em] text-ink-mute">
          <span className={`h-1.5 w-1.5 rounded-full ${riskMark}`} />
          risk {risk}
        </span>
      </div>

      <h3 className="display-serif text-3xl lg:text-4xl mt-6 leading-tight text-ink">
        {rec.recommended_action}
      </h3>

      <div className="mt-8">
        <div className="flex items-end justify-between mb-2">
          <span className="font-mono text-[10px] uppercase tracking-[0.28em] text-ink-mute">Confidence</span>
          <span className="font-mono tabular text-2xl text-ink">{confPct}%</span>
        </div>
        <div className="h-1 overflow-hidden rounded-full bg-white/[0.05]">
          <div
            className="h-full rounded-full bg-coral transition-all duration-700 ease-spring"
            style={{ width: `${confPct}%` }}
          />
        </div>
      </div>

      <div className="mt-4 grid grid-cols-3 gap-3 font-mono tabular text-xs">
        <Mini label="lap" value={String(lap || "?")} />
        <Mini label="tyre" value={`${tyreLife}L`} />
        <Mini label="to go" value={`${lapsRemaining}L`} />
      </div>

      <ul className="mt-5 space-y-2">
        {rec.reason_codes.map((r, i) => (
          <li key={i} className="flex items-start gap-2 text-sm text-ink-dim">
            <span className="mt-1.5 h-1 w-1 rounded-full bg-coral shrink-0" />
            <span>{r.replace(/_/g, " ").toLowerCase()}</span>
          </li>
        ))}
      </ul>

      <div className="mt-auto pt-6">
        <button
          onClick={() => setOpen((o) => !o)}
          className="btn-ghost w-full justify-between"
        >
          <span>{open ? "hide rationale" : "why this call"}</span>
          <span className="font-mono text-[10px] tracking-[0.28em] text-ink-mute">granite</span>
        </button>
        {open && (
          <p className="mt-4 text-sm leading-relaxed text-ink-dim">{rec.explanation}</p>
        )}
      </div>
    </Bezel>
  );
}

function Mini({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-bezel-sm bg-white/[0.03] px-3 py-2">
      <div className="text-[10px] uppercase tracking-[0.22em] text-ink-mute">{label}</div>
      <div className="text-ink mt-0.5">{value}</div>
    </div>
  );
}
