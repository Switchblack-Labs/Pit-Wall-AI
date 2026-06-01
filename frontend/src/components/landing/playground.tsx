"use client";
import { useEffect, useRef, useState } from "react";
import { api } from "@/lib/api";
import { cn, fmt } from "@/lib/utils";
import type { StrategyRecommendation, Telemetry, SimulationResult } from "@/lib/types";
import {
  RoughFilter,
  DoodleTelemetry,
  DoodleStrategy,
  DoodleSim,
  DoodleGranite,
  DoodleRag,
  DoodleDirector,
} from "@/components/excalidraw";

function Tile({
  span,
  rowSpan,
  index,
  title,
  endpoint,
  doodle,
  children,
  big,
}: {
  span: string;
  rowSpan?: string;
  index: string;
  title: string;
  endpoint: string;
  doodle: React.ReactNode;
  children: React.ReactNode;
  big?: boolean;
}) {
  return (
    <article
      className={cn(
        "relative rounded-[32px] bg-white ring-1 ring-black/[0.06] overflow-hidden",
        "shadow-[0_30px_60px_-30px_rgba(20,18,16,0.18)] flex flex-col min-h-[360px]",
        span,
        rowSpan
      )}
    >
      <div className="flex items-center justify-between p-7 pb-0 font-mono text-[10px] uppercase tracking-[0.28em] text-black/40">
        <span>{index}</span>
        <span className="opacity-60">{endpoint}</span>
      </div>

      <div className="flex-1 flex flex-col p-7 pt-5">
        <h3
          className={cn(
            "font-sans tracking-[-0.025em] text-black leading-[0.95]",
            big ? "text-[clamp(36px,3.4vw,64px)]" : "text-[clamp(26px,2.4vw,40px)]"
          )}
          style={{ fontWeight: 500 }}
        >
          {title}
        </h3>

        <div className={cn(
          "text-black/45 mt-4",
          big ? "h-24 lg:h-28" : "h-24 lg:h-28"
        )}>
          {doodle}
        </div>

        <div className="mt-auto pt-5">{children}</div>
      </div>
    </article>
  );
}

function PrimaryBtn({
  onClick,
  busy,
  children,
}: {
  onClick: () => void;
  busy?: boolean;
  children: React.ReactNode;
}) {
  return (
    <button
      onClick={onClick}
      disabled={busy}
      className="inline-flex items-center gap-2 rounded-full bg-black text-white px-5 py-2.5 text-sm font-medium transition-all duration-300 ease-spring hover:bg-black/85 active:scale-[0.98] disabled:opacity-60"
    >
      {children}
    </button>
  );
}

function Chip({ active, onClick, children }: { active?: boolean; onClick: () => void; children: React.ReactNode }) {
  return (
    <button
      onClick={onClick}
      className={cn(
        "rounded-full px-3 py-1.5 text-xs ring-1 transition-all duration-300 ease-spring",
        active ? "bg-coral text-white ring-coral" : "bg-white text-black/70 ring-black/10 hover:bg-black/[0.04]"
      )}
    >
      {children}
    </button>
  );
}

function Result({ children }: { children: React.ReactNode }) {
  return (
    <div className="rounded-2xl bg-black/[0.035] ring-1 ring-black/[0.05] p-4 mt-4 text-sm text-black/80">
      {children}
    </div>
  );
}

function TelemetryTile() {
  const [data, setData] = useState<Telemetry | null>(null);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const [streaming, setStreaming] = useState(false);
  useEffect(() => () => { if (timerRef.current) clearInterval(timerRef.current); }, []);
  const toggle = () => {
    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
      setStreaming(false);
      return;
    }
    setStreaming(true);
    const tick = async () => {
      const live = await api.mockTelemetry();
      if (live) setData(live);
    };
    tick();
    timerRef.current = setInterval(tick, 500);
  };
  return (
    <Tile
      span="col-span-12 md:col-span-6 xl:col-span-4"
      index="01"
      title="Stream a lap."
      endpoint="GET /api/mock/telemetry"
      doodle={<DoodleTelemetry className="w-full h-full" />}
    >
      <div className="flex items-center gap-3">
        <PrimaryBtn onClick={toggle}>
          {streaming ? "Stop" : "Start stream"}
        </PrimaryBtn>
        {streaming && (
          <span className="font-mono text-[10px] uppercase tracking-[0.28em] text-coral">
            streaming
          </span>
        )}
      </div>
      {data && (
        <div className="mt-5 grid grid-cols-4 gap-5 font-mono tabular">
          <Stat label="speed" v={`${Math.round(data.speed)}`} u="km/h" />
          <Stat label="rpm"   v={fmt(data.rpm)} />
          <Stat label="gear"  v={String(data.gear)} />
          <Stat label="lap"   v={String(data.lap)} />
        </div>
      )}
    </Tile>
  );
}

function Stat({ label, v, u }: { label: string; v: string; u?: string }) {
  return (
    <div className="flex flex-col">
      <span className="font-mono text-[10px] uppercase tracking-[0.22em] text-black/40">{label}</span>
      <span className="text-2xl text-black mt-1">{v}{u && <span className="text-xs text-black/40 ml-1">{u}</span>}</span>
    </div>
  );
}

function StrategyTile() {
  const [r, setR] = useState<StrategyRecommendation | null>(null);
  const [busy, setBusy] = useState(false);
  const ask = async () => {
    setBusy(true);
    const live = await api.recommend();
    if (live) setR(live);
    setBusy(false);
  };
  return (
    <Tile
      span="col-span-12 md:col-span-6 xl:col-span-4"
      index="02"
      title="Rank the next call."
      endpoint="POST /api/strategy/recommend"
      doodle={<DoodleStrategy className="w-full h-full" />}
    >
      <PrimaryBtn onClick={ask} busy={busy}>
        {busy ? "Thinking" : "Recommend action"}
      </PrimaryBtn>
      {r && (
        <Result>
          <div className="text-black font-medium">{r.recommended_action}</div>
          <div className="mt-3 flex items-center gap-3">
            <div className="h-1 flex-1 rounded-full bg-black/10 overflow-hidden">
              <div className="h-full bg-coral" style={{ width: `${Math.round(r.confidence * 100)}%` }} />
            </div>
            <span className="font-mono tabular text-xs text-black/60">{Math.round(r.confidence * 100)}%</span>
          </div>
        </Result>
      )}
    </Tile>
  );
}

function GraniteTile() {
  const [text, setText] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const explain = async () => {
    setBusy(true);
    setError(null);
    setText(null);
    try {
      const r = await api.explainStrict();
      setText(r.explanation);
    } catch {
      setError("backend did not return an explanation");
    }
    setBusy(false);
  };
  return (
    <Tile
      span="col-span-12 md:col-span-6 xl:col-span-4"
      index="03"
      title="Say it in plain English."
      endpoint="POST /api/explain"
      doodle={<DoodleGranite className="w-full h-full" />}
    >
      <PrimaryBtn onClick={explain} busy={busy}>
        {busy ? "Asking Granite" : "Why this call?"}
      </PrimaryBtn>
      {text && (
        <Result>
          <p className="leading-relaxed">{text}</p>
        </Result>
      )}
      {error && <Result>{error}</Result>}
    </Tile>
  );
}

function SimTile() {
  const SCEN = [
    { id: "pit_soft", label: "Pit soft" },
    { id: "pit_medium", label: "Pit medium" },
    { id: "pit_hard", label: "Pit hard" },
    { id: "stay_out", label: "Stay out" },
  ];
  const [scen, setScen] = useState("pit_soft");
  const [r, setR] = useState<SimulationResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const run = async () => {
    setBusy(true);
    setError(null);
    setR(null);
    try {
      setR(await api.simulateStrict({ scenario_type: scen, laps_until_action: 1 }));
    } catch {
      setError("backend did not return simulation data");
    }
    setBusy(false);
  };
  return (
    <Tile
      span="col-span-12 md:col-span-6 xl:col-span-4"
      index="04"
      title="Branch forward."
      endpoint="POST /api/simulate"
      doodle={<DoodleSim className="w-full h-full" />}
    >
      <div className="flex flex-wrap gap-2 mb-3">
        {SCEN.map((s) => (
          <Chip key={s.id} active={scen === s.id} onClick={() => setScen(s.id)}>{s.label}</Chip>
        ))}
      </div>
      <PrimaryBtn onClick={run} busy={busy}>
        {busy ? "Simulating" : "Run sim"}
      </PrimaryBtn>
      {r && (
        <Result>
          <div className="grid grid-cols-3 gap-3 font-mono tabular">
            <Stat label="pos"  v={`P${r.projected_position}`} />
            <Stat label="Δ gap"  v={`${r.projected_gap >= 0 ? "+" : ""}${r.projected_gap.toFixed(1)}s`} />
            <Stat label="risk" v={String(r.projected_risk).toUpperCase()} />
          </div>
        </Result>
      )}
      {error && <Result>{error}</Result>}
    </Tile>
  );
}

function RagTile() {
  const SUGGEST = [
    "Can we pit under safety car?",
    "When is DRS enabled?",
    "Min compounds in a dry race?",
  ];
  const [q, setQ] = useState<string | null>(null);
  const [a, setA] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const ask = async (question: string) => {
    setQ(question);
    setBusy(true);
    setA(null);
    setError(null);
    try {
      const live = await api.ragStrict(question);
      setA(live.answer);
    } catch {
      setError("backend did not return a rulebook answer");
    }
    setBusy(false);
  };
  return (
    <Tile
      span="col-span-12 xl:col-span-8"
      index="05"
      title="Ask the FIA rulebook."
      endpoint="POST /api/rag/query"
      doodle={<DoodleRag className="w-full h-full" />}
    >
      <div className="flex flex-wrap gap-2 mb-3">
        {SUGGEST.map((s) => (
          <Chip key={s} active={q === s} onClick={() => ask(s)}>{s}</Chip>
        ))}
      </div>
      {q && (
        <Result>
          <div className="font-mono text-[10px] uppercase tracking-[0.22em] text-black/40 mb-1">Q. {q}</div>
          <p className="leading-relaxed">{busy ? "" : error ?? a}</p>
        </Result>
      )}
    </Tile>
  );
}

function DirectorTile() {
  const [running, setRunning] = useState(false);
  const [busy, setBusy] = useState(false);
  const toggle = async () => {
    setBusy(true);
    if (!running) await api.demoStart(); else await api.demoStop();
    setRunning(!running);
    setBusy(false);
  };
  return (
    <Tile
      span="col-span-12"
      index="06"
      title="Run the race."
      endpoint="POST /api/demo/{start,stop}"
      doodle={<DoodleDirector className="w-full h-full" />}
    >
      <div className="flex flex-wrap items-center gap-4">
        <PrimaryBtn onClick={toggle} busy={busy}>
          {running ? "Stop demo race" : "Start demo race"}
        </PrimaryBtn>
        {running && (
          <span className="font-mono text-[10px] uppercase tracking-[0.28em] text-coral">
            broadcasting on /ws/live
          </span>
        )}
      </div>
    </Tile>
  );
}

export function Playground() {
  return (
    <section
      id="playground"
      className="relative w-full min-h-screen px-[3vw] py-32 lg:py-44 overflow-hidden"
      style={{
        background:
          "linear-gradient(180deg, #1a1714 0%, #2a241d 10%, #5a4f43 20%, #aea191 30%, #F0EEE6 40%, #F0EEE6 100%)",
        color: "#0B0908",
      }}
    >
      <RoughFilter />

      <div className="grid grid-cols-12 gap-8 items-end mb-24 pt-[22vh]">
        <div className="col-span-12 lg:col-span-7">
          <div className="flex items-center gap-3 font-mono text-[10px] uppercase tracking-[0.32em] text-ink-mute">
            <span>03</span>
            <span className="h-px w-8 bg-white/15" />
            <span>Backend playground</span>
          </div>
          <h2
            className="mt-7 font-sans tracking-[-0.04em] text-ink leading-[0.9]"
            style={{ fontSize: "clamp(56px, 8.5vw, 168px)", fontWeight: 500 }}
          >
            Every endpoint,<br />
            <span className="text-coral">in your hands.</span>
          </h2>
        </div>
        <div className="col-span-12 lg:col-span-5" />
      </div>

      <div className="grid w-full grid-cols-12 gap-5 lg:gap-6 auto-rows-[minmax(360px,auto)] items-stretch">
        <TelemetryTile />
        <StrategyTile />
        <GraniteTile />
        <SimTile />
        <RagTile />
        <DirectorTile />
      </div>
    </section>
  );
}
