"use client";
import { useEffect, useMemo, useState } from "react";
import { ArrowUpRight } from "lucide-react";
import { Bezel } from "@/components/bezel";
import { CircuitPicker, CircuitHeadline } from "@/components/circuit-picker";
import { CIRCUITS, getCircuit } from "@/lib/circuits";
import { api } from "@/lib/api";
import { cn, fmt } from "@/lib/utils";

type FerrariDisaster = {
  name: string;
  race_id: string;
  driver: string;
  lap: number;
  description: string;
  correct_action: string;
  what_ferrari_did: string;
  positions_lost: number;
};
const SCENARIO_PRESETS = [
  { id: "pit_now",   label: "Pit now",       scenario_type: "pit_now",   laps_until_action: 1 },
  { id: "pit_hard",  label: "Pit (Hard)",    scenario_type: "pit_hard",  laps_until_action: 1 },
  { id: "pit_soft",  label: "Pit (Soft)",    scenario_type: "pit_soft",  laps_until_action: 1 },
  { id: "stay_out",  label: "Stay out",      scenario_type: "stay_out",  laps_until_action: 1 },
] as const;

const COMPOUNDS = [
  { id: "S" as const, label: "Soft",   color: "#E0492E" },
  { id: "M" as const, label: "Medium", color: "#E2A33B" },
  { id: "H" as const, label: "Hard",   color: "#F2EBE0" },
];

type ScenarioId = "pit_now" | "pit_soft" | "pit_medium" | "pit_hard" | "stay_out";

type ScenarioProjection = {
  id: ScenarioId;
  label: string;
  color: string;
  points: { lap_offset: number; gap_s: number }[];
  net_gain_s: number;
  projected_position: number;
  risk: "low" | "medium" | "high";
  confidence: number;
  notes: string[];
};

export default function SimulatorPage() {
  
  
  const [circuitId, setCircuitId] = useState<string>("imola");
  useEffect(() => {
    const saved = localStorage.getItem("rm:circuit");
    if (saved) setCircuitId(saved);
  }, []);
  useEffect(() => { localStorage.setItem("rm:circuit", circuitId); }, [circuitId]);

  const circuit = getCircuit(circuitId);

  const [currentLap, setCurrentLap] = useState(14);
  const [basePosition, setBasePosition] = useState(3);
  const [baseGap, setBaseGap] = useState(2.4);
  const [tyreAge, setTyreAge] = useState(13);
  const [compound, setCompound] = useState<"S" | "M" | "H">("M");
  const [granite, setGranite] = useState<string | null>(null);
  const [graniteBusy, setGraniteBusy] = useState(false);
  const [activeDisaster, setActiveDisaster] = useState<FerrariDisaster | null>(null);
  const [disasters, setDisasters] = useState<FerrariDisaster[]>([]);
  const [backendCall, setBackendCall] = useState<{
    label: string;
    risk: string;
    projected_position: number;
    projected_gap: number;
    explanation?: string;
  } | null>(null);
  const [backendBusy, setBackendBusy] = useState(false);

  
  
  useEffect(() => {
    let killed = false;
    api.disasters().then((list) => {
      if (!killed && list) setDisasters(list as FerrariDisaster[]);
    });
    return () => { killed = true; };
  }, []);

  
  
  const disasterCircuitId = (race_id: string): string => {
    const stem = race_id.replace(/^(\d{4})_/, "").replace(/_r$/, "");
    return stem === "marina_bay" ? "marina-bay" : stem.replace(/_/g, "-");
  };

  const applyDisaster = (d: FerrariDisaster) => {
    setActiveDisaster(d);
    setCircuitId(disasterCircuitId(d.race_id));
    setCurrentLap(d.lap);
    setBackendCall(null);
  };

  
  
  const runScenario = async (scenario_type: string, laps_until_action: number) => {
    setBackendBusy(true);
    const sim = await api.simulate({
      scenario_type,
      laps_until_action,
      context: {
        circuit: circuit.shortName.toLowerCase().replace(/\s+/g, "_"),
        lap: currentLap,
        total_laps: circuit.laps,
        position: basePosition,
        gap_s: baseGap,
        tyre_age_laps: tyreAge,
        compound,
        pit_loss_s: circuit.pit_loss_s,
      },
    });
    
    const fullRec = await api.recommendFull({
      circuit: circuit.shortName.toLowerCase().replace(/\s+/g, "_"),
      compound: compound === "S" ? "SOFT" : compound === "M" ? "MEDIUM" : "HARD",
      tyre_life: tyreAge,
      laps_remaining: Math.max(1, circuit.laps - currentLap),
      total_laps: circuit.laps,
      position: basePosition,
      pit_loss_s: circuit.pit_loss_s,
    });
    if (sim) {
      setBackendCall({
        label: scenario_type.replace(/_/g, " ").toUpperCase(),
        risk: sim.projected_risk,
        projected_position: sim.projected_position,
        projected_gap: sim.projected_gap,
        explanation: fullRec?.explanation,
      });
    }
    setBackendBusy(false);
  };

  const DECISION_META: Record<string, { id: ScenarioId; label: string; color: string }> = {
    STAY_OUT:   { id: "stay_out",   label: "Stay out",          color: "#7AB7C7" },
    PIT_NOW:    { id: "pit_now",    label: "Pit now",           color: "#E26C45" },
    PIT_SOFT:   { id: "pit_soft",   label: "Pit, fit soft",     color: "#E0492E" },
    PIT_MEDIUM: { id: "pit_medium", label: "Pit, fit medium",   color: "#E2A33B" },
    PIT_HARD:   { id: "pit_hard",   label: "Pit, fit hard",     color: "#F2EBE0" },
  };

  const [scenarios, setScenarios] = useState<ScenarioProjection[]>([]);
  const [scenariosBusy, setScenariosBusy] = useState(false);
  const [scenariosError, setScenariosError] = useState<string | null>(null);

  useEffect(() => {
    let killed = false;
    const fetchScenarios = async () => {
      setScenariosBusy(true);
      const result = await api.scenarios({
        circuit: circuit.shortName.toLowerCase().replace(/\s+/g, "_"),
        lap: currentLap,
        total_laps: circuit.laps,
        position: basePosition,
        gap_s: baseGap,
        tyre_age_laps: tyreAge,
        compound,
        pit_loss_s: circuit.pit_loss_s,
      });
      if (killed) return;
      if (!result) {
        setScenariosError("backend unreachable");
        setScenariosBusy(false);
        return;
      }
      setScenariosError(null);
      const mapped: ScenarioProjection[] = result.map((s) => {
        const meta = DECISION_META[s.decision] ?? { id: "stay_out", label: s.decision, color: "#999" };
        const riskPos = s.projected_position;
        const risk = riskPos <= 3 ? "low" : riskPos <= 6 ? "medium" : "high";
        return {
          id: meta.id,
          label: meta.label,
          color: meta.color,
          points: s.points,
          net_gain_s: s.net_gain_s,
          projected_position: s.projected_position,
          risk,
          confidence: 0.6 + Math.min(0.35, Math.max(0, s.net_gain_s / 10) * 0.05),
          notes: [`avg pace ${s.avg_pace.toFixed(2)}s`, `total race ${s.projected_total_time.toFixed(1)}s`],
        };
      });
      setScenarios(mapped);
      setScenariosBusy(false);
    };
    fetchScenarios();
    return () => { killed = true; };
  }, [circuit.shortName, circuit.laps, circuit.pit_loss_s, currentLap, basePosition, baseGap, tyreAge, compound]);

  const recommendedId = useMemo<ScenarioId>(() => {
    if (scenarios.length === 0) return "stay_out";
    return scenarios.reduce((best, s) => (s.net_gain_s > best.net_gain_s ? s : best), scenarios[0]).id;
  }, [scenarios]);
  const recommended = scenarios.find((s) => s.id === recommendedId);

  const [highlightedId, setHighlightedId] = useState<ScenarioId>(recommendedId);
  useEffect(() => { setHighlightedId(recommendedId); }, [recommendedId]);

  const explain = async () => {
    setGraniteBusy(true);
    
    
    const full = await api.recommendFull({
      circuit: circuit.shortName.toLowerCase().replace(/\s+/g, "_"),
      compound: compound === "S" ? "SOFT" : compound === "M" ? "MEDIUM" : "HARD",
      tyre_life: tyreAge,
      laps_remaining: Math.max(1, circuit.laps - currentLap),
      total_laps: circuit.laps,
      position: basePosition,
      pit_loss_s: circuit.pit_loss_s,
    });
    setGranite(full?.explanation ?? "backend unreachable");
    setGraniteBusy(false);
  };

  return (
    <main className="px-[6vw] pt-32 pb-44">
      {}
      <header className="grid grid-cols-12 gap-10 items-end mb-14">
        <div className="col-span-12 lg:col-span-7">
          <div className="flex items-center gap-3 font-mono text-[10px] uppercase tracking-[0.32em] text-ink-mute">
            <span>02 - Strategy</span>
            <span className="h-px w-8 bg-white/15" />
            <span>Counterfactual simulator</span>
          </div>
          <h1
            className="mt-7 font-sans tracking-[-0.04em] text-ink leading-[0.9]"
            style={{ fontSize: "clamp(56px, 8vw, 144px)", fontWeight: 500 }}
          >
            Branch the<br />race <span className="text-coral">forward.</span>
          </h1>
        </div>
        <div className="col-span-12 lg:col-span-5">
          <p className="text-base lg:text-lg text-ink-dim leading-relaxed max-w-md">
            Pick a circuit, set the race state, and watch all five strategic
            branches project ten laps forward. Real circuit data: length,
            pit loss, tyre degradation, sectors.
          </p>
        </div>
      </header>

      {}
      <div className="mb-6">
        <CircuitPicker value={circuitId} onChange={setCircuitId} />
      </div>
      <div className="mb-12">
        <CircuitHeadline circuit={circuit} />
      </div>

      {}
      <div className="mb-10 grid grid-cols-12 gap-6">
        <Bezel innerClassName="p-5" className="col-span-12 lg:col-span-7">
          <div className="flex items-center justify-between mb-3">
            <div className="font-mono text-[10px] uppercase tracking-[0.28em] text-coral-hi">
              Replay a Ferrari disaster
            </div>
            {activeDisaster && (
              <button
                onClick={() => setActiveDisaster(null)}
                className="font-mono text-[10px] uppercase tracking-[0.22em] text-ink-mute hover:text-ink"
              >
                clear x
              </button>
            )}
          </div>
          <div className="flex flex-wrap gap-2">
            {disasters.map((d) => (
              <button
                key={d.race_id}
                onClick={() => applyDisaster(d)}
                className={cn(
                  "rounded-bezel-sm px-3 py-2 text-xs ring-1 transition-all duration-300 ease-spring",
                  activeDisaster?.race_id === d.race_id
                    ? "bg-coral/15 text-coral-hi ring-coral/40"
                    : "bg-white/[0.02] text-ink-dim ring-white/[0.06] hover:bg-white/[0.05] hover:text-ink"
                )}
              >
                {d.name.split(" - ")[0]}
              </button>
            ))}
            {disasters.length === 0 && (
              <span className="text-xs text-ink-mute">Loading from /api/v1/disasters...</span>
            )}
          </div>
          {activeDisaster && (
            <div className="mt-4 text-sm text-ink-dim leading-relaxed">
              <span className="text-ink">{activeDisaster.name}.</span> {activeDisaster.description}
              <div className="mt-3 grid grid-cols-3 gap-3 text-xs font-mono">
                <div>
                  <div className="text-ink-mute uppercase tracking-[0.2em]">Correct</div>
                  <div className="text-signal-ok mt-1">{activeDisaster.correct_action}</div>
                </div>
                <div>
                  <div className="text-ink-mute uppercase tracking-[0.2em]">Ferrari did</div>
                  <div className="text-signal-danger mt-1">{activeDisaster.what_ferrari_did}</div>
                </div>
                <div>
                  <div className="text-ink-mute uppercase tracking-[0.2em]">Lost</div>
                  <div className="text-ink mt-1">{activeDisaster.positions_lost} pos</div>
                </div>
              </div>
            </div>
          )}
        </Bezel>

        <Bezel innerClassName="p-5" className="col-span-12 lg:col-span-5">
          <div className="font-mono text-[10px] uppercase tracking-[0.28em] text-coral-hi mb-3">
            One-click scenarios - real engine
          </div>
          <div className="flex flex-wrap gap-2">
            {SCENARIO_PRESETS.map((p) => (
              <button
                key={p.id}
                onClick={() => runScenario(p.scenario_type, p.laps_until_action)}
                disabled={backendBusy}
                className="rounded-bezel-sm px-3 py-2 text-xs ring-1 ring-white/[0.06] bg-white/[0.02] text-ink-dim hover:text-ink hover:bg-white/[0.05] transition-all duration-300 ease-spring disabled:opacity-40"
              >
                {p.label}
              </button>
            ))}
          </div>
          {backendCall && (
            <div className="mt-4 rounded-bezel-sm bg-white/[0.03] p-3 text-xs font-mono">
              <div className="flex items-center justify-between text-ink">
                <span className="text-coral-hi">{backendCall.label}</span>
                <span className="text-ink-mute">
                  P{backendCall.projected_position} - {backendCall.risk}
                </span>
              </div>
              {backendCall.explanation && (
                <p className="mt-2 font-sans text-ink-dim leading-relaxed">
                  {backendCall.explanation}
                </p>
              )}
            </div>
          )}
        </Bezel>
      </div>

      {}
      <div className="grid grid-cols-12 gap-6 lg:gap-8 items-start">
        {}
        <div className="col-span-12 lg:col-span-8 space-y-6">
          <Bezel innerClassName="p-8">
            <div className="flex items-end justify-between mb-2">
              <div>
                <div className="font-mono text-[10px] uppercase tracking-[0.28em] text-ink-mute">
                  net seconds vs stay out, end of race
                </div>
                <div className="mt-2 text-ink font-mono tabular text-3xl">
                  {recommended ? (
                    <>
                      {recommended.net_gain_s >= 0 ? "+" : ""}{recommended.net_gain_s.toFixed(1)}s
                      <span className="text-ink-mute text-sm ml-3">{recommended.label.toLowerCase()}</span>
                    </>
                  ) : (
                    <span className="text-ink-mute">{scenariosError ?? (scenariosBusy ? "computing" : "no data")}</span>
                  )}
                </div>
              </div>
              <div className="text-right">
                <div className="font-mono text-[10px] uppercase tracking-[0.28em] text-ink-mute">projected finish</div>
                <div className="mt-2 text-ink font-mono tabular text-3xl">
                  {recommended ? `P${recommended.projected_position}` : "-"}
                </div>
              </div>
            </div>
            {scenarios.length > 0 ? (
              <Chart scenarios={scenarios} highlightedId={highlightedId} />
            ) : (
              <div className="h-64 flex items-center justify-center text-ink-mute text-xs">
                {scenariosError ?? "computing on backend"}
              </div>
            )}
            <div className="mt-3 flex items-center gap-4 text-[10px] uppercase tracking-[0.24em] text-ink-mute">
              <span>now, lap {currentLap}</span>
              <span className="hair flex-1" />
              <span>lap {currentLap + Math.max(1, circuit.laps - currentLap)}</span>
            </div>
          </Bezel>

          {}
          <Bezel innerClassName="p-0">
            <table className="w-full font-mono text-sm tabular">
              <thead>
                <tr className="text-[10px] uppercase tracking-[0.22em] text-ink-mute">
                  <th className="text-left py-4 pl-7 font-normal w-12"></th>
                  <th className="text-left py-4 font-normal">Scenario</th>
                  <th className="text-right py-4 font-normal">Δ vs leader</th>
                  <th className="text-right py-4 font-normal">Pos</th>
                  <th className="text-right py-4 font-normal">Risk</th>
                  <th className="text-right py-4 pr-7 font-normal">Confidence</th>
                </tr>
              </thead>
              <tbody>
                {scenarios.map((s) => (
                  <tr
                    key={s.id}
                    onClick={() => setHighlightedId(s.id)}
                    onMouseEnter={() => setHighlightedId(s.id)}
                    className={cn(
                      "border-t border-line cursor-pointer transition-colors",
                      highlightedId === s.id ? "bg-white/[0.03]" : "hover:bg-white/[0.02]"
                    )}
                  >
                    <td className="py-3 pl-7">
                      <span className="inline-block h-2 w-4 rounded-full" style={{ background: s.color }} />
                    </td>
                    <td className="py-3 text-ink">
                      <div className="flex items-center gap-2">
                        {s.label}
                        {s.id === recommendedId && (
                          <span className="rounded-full bg-coral/15 text-coral-hi ring-1 ring-coral/30 px-2 py-0.5 text-[9px] uppercase tracking-[0.18em]">
                            recommended
                          </span>
                        )}
                      </div>
                    </td>
                    <td className={cn(
                      "py-3 text-right",
                      s.net_gain_s > 0 ? "text-signal-ok" : s.net_gain_s < 0 ? "text-signal-danger" : "text-ink"
                    )}>
                      {s.net_gain_s >= 0 ? "+" : ""}{s.net_gain_s.toFixed(1)}s
                    </td>
                    <td className="py-3 text-right text-ink">P{s.projected_position}</td>
                    <td className="py-3 text-right">
                      <span className="inline-flex items-center justify-end gap-2 font-mono text-[10px] uppercase tracking-[0.18em] text-ink-mute">
                        <span className={cn(
                          "h-1.5 w-1.5 rounded-full",
                          s.risk === "low" && "bg-white/35",
                          s.risk === "medium" && "bg-white/55",
                          s.risk === "high" && "bg-coral"
                        )} />
                        {s.risk}
                      </span>
                    </td>
                    <td className="py-3 pr-7 text-right text-ink-dim">{Math.round(s.confidence * 100)}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </Bezel>

        </div>

        {}
        <div className="col-span-12 lg:col-span-4 space-y-6">
          {}
          <Bezel innerClassName="p-7">
            <div className="font-mono text-[10px] uppercase tracking-[0.28em] text-ink-mute">Race state</div>
            <h3 className="mt-3 font-sans text-ink text-xl tracking-tight" style={{ fontWeight: 500 }}>Now</h3>

            <div className="mt-6 space-y-6">
              <Slider label="Current lap" v={currentLap} min={1} max={circuit.laps} onChange={setCurrentLap} />
              <Slider label="Position" v={basePosition} min={1} max={20} onChange={setBasePosition} />
              <Slider label="Gap to leader (s)" v={baseGap} min={-30} max={30} step={0.1} onChange={setBaseGap} />
              <Slider label="Tyre age (laps)" v={tyreAge} min={0} max={40} onChange={setTyreAge} />
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="font-mono text-[10px] uppercase tracking-[0.22em] text-ink-mute">Current compound</span>
                </div>
                <div className="flex gap-2">
                  {COMPOUNDS.map((c) => (
                    <button
                      key={c.id}
                      onClick={() => setCompound(c.id)}
                      className={cn(
                        "flex-1 rounded-bezel-sm px-3 py-3 text-xs ring-1 transition-all duration-300 ease-spring",
                        compound === c.id
                          ? "bg-white/[0.08] text-ink ring-white/[0.16]"
                          : "bg-white/[0.02] text-ink-dim ring-white/[0.06] hover:bg-white/[0.05]"
                      )}
                    >
                      <span className="inline-block h-1.5 w-1.5 rounded-full mr-2" style={{ background: c.color }} />
                      {c.label}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </Bezel>

          {}
          <Bezel innerClassName="p-7">
            <div className="font-mono text-[10px] uppercase tracking-[0.28em] text-coral-hi">
              recommendation
            </div>
            {recommended ? (
              <>
                <h3 className="mt-3 font-sans text-ink text-2xl tracking-tight leading-tight" style={{ fontWeight: 500 }}>
                  {recommended.label}
                </h3>
                <div className="mt-4 flex items-center gap-3">
                  <span className="font-mono text-[10px] uppercase tracking-[0.22em] text-ink-mute">net</span>
                  <span className="font-mono tabular text-sm text-ink">
                    {recommended.net_gain_s >= 0 ? "+" : ""}{recommended.net_gain_s.toFixed(1)}s
                  </span>
                  <span className="font-mono text-[10px] uppercase tracking-[0.22em] text-ink-mute ml-3">finish</span>
                  <span className="font-mono tabular text-sm text-ink">P{recommended.projected_position}</span>
                </div>
                <ul className="mt-4 space-y-1.5">
                  {recommended.notes.map((n, i) => (
                    <li key={i} className="text-sm text-ink-dim">{n}</li>
                  ))}
                </ul>
              </>
            ) : (
              <p className="mt-3 text-ink-mute text-sm">
                {scenariosError ?? (scenariosBusy ? "computing" : "no data")}
              </p>
            )}

            <button onClick={explain} disabled={graniteBusy || !recommended} className="mt-6 btn-ghost w-full justify-between disabled:opacity-40">
              <span>{graniteBusy ? "asking granite" : granite ? "hide rationale" : "why this call"}</span>
              <span className="font-mono text-[10px] tracking-[0.28em] text-ink-mute">granite</span>
            </button>
            {granite && (
              <p className="mt-4 text-sm leading-relaxed text-ink-dim">{granite}</p>
            )}
          </Bezel>
        </div>
      </div>

      {}
      <div className="mt-16">
        <div className="flex items-center gap-3 font-mono text-[10px] uppercase tracking-[0.32em] text-ink-mute mb-6">
          <span>backend</span>
          <span className="h-px w-8 bg-white/15" />
          <span>how this screen calls fastapi</span>
        </div>
        <BackendStrip
          circuit={circuit.shortName}
          currentLap={currentLap}
          basePosition={basePosition}
          baseGap={baseGap}
          tyreAge={tyreAge}
          compound={compound}
          recommended={recommended}
        />
      </div>
    </main>
  );
}



function Slider({
  label,
  v,
  min,
  max,
  step = 1,
  onChange,
}: {
  label: string;
  v: number;
  min: number;
  max: number;
  step?: number;
  onChange: (n: number) => void;
}) {
  return (
    <div>
      <div className="flex items-center justify-between mb-2">
        <span className="font-mono text-[10px] uppercase tracking-[0.22em] text-ink-mute">{label}</span>
        <span className="font-mono tabular text-sm text-ink">{step < 1 ? v.toFixed(1) : v}</span>
      </div>
      <input
        type="range"
        min={min} max={max} step={step}
        value={v}
        onChange={(e) => onChange(Number(e.target.value))}
        className="w-full accent-coral"
      />
    </div>
  );
}

function Chart({
  scenarios,
  highlightedId,
}: {
  scenarios: ScenarioProjection[];
  highlightedId: string;
}) {
  const allPts = scenarios.flatMap((s) => s.points.map((p) => p.gap_s));
  const min = Math.min(...allPts, 0);
  const max = Math.max(...allPts, 0);
  const w = 100, h = 100;
  const toPath = (pts: { lap_offset: number; gap_s: number }[]) =>
    pts.map((pt, i) => {
      const x = (pt.lap_offset / 10) * w;
      const y = h - ((pt.gap_s - min) / Math.max(0.001, max - min)) * h;
      return `${i === 0 ? "M" : "L"}${x.toFixed(2)},${y.toFixed(2)}`;
    }).join(" ");

  
  const zeroY = h - ((0 - min) / Math.max(0.001, max - min)) * h;

  return (
    <div className="relative h-64 mt-4">
      <svg viewBox="0 0 100 100" className="absolute inset-0 h-full w-full" preserveAspectRatio="none">
        <line x1="0" x2="100" y1={zeroY} y2={zeroY} stroke="rgba(242,235,224,0.10)" strokeWidth="0.4" />
        {}
        {[2, 4, 6, 8].map((n) => (
          <line key={n} x1={n * 10} x2={n * 10} y1="0" y2="100" stroke="rgba(242,235,224,0.04)" strokeWidth="0.3" />
        ))}
        {scenarios.map((s) => (
          <path
            key={s.id}
            d={toPath(s.points)}
            fill="none"
            stroke={s.color}
            strokeWidth={highlightedId === s.id ? 2.2 : 1}
            strokeOpacity={highlightedId === s.id ? 1 : 0.45}
            strokeLinejoin="round"
            vectorEffect="non-scaling-stroke"
          />
        ))}
      </svg>
    </div>
  );
}



function BackendStrip({
  circuit,
  currentLap,
  basePosition,
  baseGap,
  tyreAge,
  compound,
  recommended,
}: {
  circuit: string;
  currentLap: number;
  basePosition: number;
  baseGap: number;
  tyreAge: number;
  compound: string;
  recommended: ScenarioProjection | undefined;
}) {
  const reqBody = {
    context: {
      circuit,
      lap: currentLap,
      total_laps: undefined,
      position: basePosition,
      gap_s: baseGap,
      tyre_age_laps: tyreAge,
      compound,
    },
  };
  const resBody = recommended ? {
    projected_position: recommended.projected_position,
    net_gain_s: recommended.net_gain_s,
    risk: recommended.risk,
  } : { status: "waiting on backend" };
  return (
    <div className="mb-10 rounded-[28px] ring-1 ring-white/[0.06] bg-bg-1/40 overflow-hidden">
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-0 divide-x divide-line">
        {}
        <div className="lg:col-span-3 p-6">
          <div className="font-mono text-[10px] uppercase tracking-[0.28em] text-ink-mute">endpoint</div>
          <div className="mt-3 font-mono text-sm text-coral">POST /api/v1/scenarios</div>
          <div className="mt-1 font-mono text-[11px] text-ink-mute">ml_engine.projector.project for every decision</div>
          <div className="mt-3 text-xs text-ink-dim leading-relaxed">
            returns the full per-lap forward projection for stay out, pit soft, pit medium and pit hard, all from the trained ml engine
          </div>
        </div>

        {}
        <div className="lg:col-span-4 p-6">
          <div className="font-mono text-[10px] uppercase tracking-[0.28em] text-ink-mute">request body</div>
          <pre className="mt-3 font-mono text-[11px] leading-relaxed text-ink-dim whitespace-pre-wrap break-words">
{JSON.stringify(reqBody, null, 2)}
          </pre>
        </div>

        {}
        <div className="lg:col-span-3 p-6">
          <div className="font-mono text-[10px] uppercase tracking-[0.28em] text-ink-mute">response, recommended row</div>
          <pre className="mt-3 font-mono text-[11px] leading-relaxed text-ink whitespace-pre-wrap break-words">
{JSON.stringify(resBody, null, 2)}
          </pre>
        </div>

        {}
        <div className="lg:col-span-2 p-6">
          <div className="font-mono text-[10px] uppercase tracking-[0.28em] text-ink-mute">pipeline</div>
          <ul className="mt-3 space-y-1.5 font-mono text-[11px] text-ink-dim">
            <li>/api/v1/scenarios</li>
            <li>/api/v1/recommend</li>
            <li>/api/explain, granite</li>
            <li>/ws/live broadcast</li>
          </ul>
        </div>
      </div>

      {}
      <div className="border-t border-line px-6 py-3 flex flex-wrap items-center justify-between gap-3 font-mono text-[10px] uppercase tracking-[0.22em] text-ink-mute">
        <span>every number on this page is from the trained ml engine, no client side math</span>
        <span className="text-ink-dim">fastapi, port 8000</span>
      </div>
    </div>
  );
}
