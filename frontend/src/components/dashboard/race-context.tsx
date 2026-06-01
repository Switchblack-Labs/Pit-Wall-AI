"use client";
import { createContext, useContext, useEffect, useMemo, useState } from "react";
import type { ReactNode } from "react";
import { Bezel, Eyebrow } from "@/components/bezel";
import { api } from "@/lib/api";
import { cn } from "@/lib/utils";

type Ctx = {
  circuit: string;
  position: number;
  totalLaps: number;
  compound: "SOFT" | "MEDIUM" | "HARD";
  pitLossS: number;
};

const defaultCtx: Ctx = {
  circuit: "bahrain",
  position: 4,
  totalLaps: 57,
  compound: "MEDIUM",
  pitLossS: 22.3,
};

const RaceCtx = createContext<Ctx>(defaultCtx);
export const useRaceContext = () => useContext(RaceCtx);

type SampleState = {
  circuit?: string;
  total_laps?: number;
  position?: number;
  compound?: string;
  pit_loss_s?: number;
};

export function RaceContextProvider({ children }: { children: ReactNode }) {
  const [ctx, setCtx] = useState<Ctx>(defaultCtx);

  
  useEffect(() => {
    api.sampleState().then((s: SampleState | null) => {
      if (!s) return;
      setCtx({
        circuit: s.circuit ?? defaultCtx.circuit,
        position: s.position ?? defaultCtx.position,
        totalLaps: s.total_laps ?? defaultCtx.totalLaps,
        compound: (s.compound as Ctx["compound"]) ?? defaultCtx.compound,
        pitLossS: s.pit_loss_s ?? defaultCtx.pitLossS,
      });
    });
  }, []);

  const value = useMemo(() => ctx, [ctx]);

  return (
    <RaceCtx.Provider value={value}>
      <Bezel innerClassName="p-5">
        <div className="flex flex-wrap items-center gap-x-6 gap-y-3">
          <Eyebrow>Race context</Eyebrow>
          <Field
            label="circuit"
            value={ctx.circuit}
            kind="select"
            options={["bahrain", "monaco", "silverstone", "monza", "spa", "hungaroring", "marina_bay", "zandvoort", "catalunya", "imola", "suzuka"]}
            onChange={(v) => setCtx((c) => ({ ...c, circuit: v as string }))}
          />
          <Field
            label="position"
            value={ctx.position}
            kind="number"
            min={1}
            max={20}
            onChange={(v) => setCtx((c) => ({ ...c, position: Number(v) }))}
          />
          <Field
            label="total laps"
            value={ctx.totalLaps}
            kind="number"
            min={5}
            max={80}
            onChange={(v) => setCtx((c) => ({ ...c, totalLaps: Number(v) }))}
          />
          <Field
            label="compound"
            value={ctx.compound}
            kind="select"
            options={["SOFT", "MEDIUM", "HARD"]}
            onChange={(v) => setCtx((c) => ({ ...c, compound: v as Ctx["compound"] }))}
          />
        </div>
      </Bezel>
      {children}
    </RaceCtx.Provider>
  );
}

function Field({
  label,
  value,
  kind,
  options,
  onChange,
  min,
  max,
}: {
  label: string;
  value: string | number;
  kind: "select" | "number";
  options?: string[];
  onChange: (v: string | number) => void;
  min?: number;
  max?: number;
}) {
  return (
    <label className="flex items-center gap-2 text-xs">
      <span className="font-mono text-[10px] uppercase tracking-[0.28em] text-ink-mute">{label}</span>
      {kind === "select" ? (
        <select
          value={String(value)}
          onChange={(e) => onChange(e.target.value)}
          className={cn("bg-bg-1 ring-1 ring-white/[0.10] rounded-full px-3 py-1 text-xs text-ink")}
        >
          {options?.map((o) => (
            <option key={o} value={o}>{o}</option>
          ))}
        </select>
      ) : (
        <input
          type="number"
          min={min}
          max={max}
          value={value}
          onChange={(e) => onChange(Number(e.target.value))}
          className="bg-bg-1 ring-1 ring-white/[0.10] rounded-full px-3 py-1 text-xs text-ink w-20"
        />
      )}
    </label>
  );
}
