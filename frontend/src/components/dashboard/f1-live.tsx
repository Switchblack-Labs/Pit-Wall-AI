"use client";
import { useEffect, useMemo, useState } from "react";
import { Bezel, Eyebrow } from "@/components/bezel";
import { api } from "@/lib/api";
import { cn } from "@/lib/utils";

type BacktestRow = {
  race_id: string;
  circuit: string;
  lap: number;
  driver: string;
  position: number;
  actual_decision: string;
  recommended_action: string;
  confidence: number;
  agrees: boolean;
  actual_outcome: string;
  model_was_right: boolean;
  reason_codes: string[];
  reasoning: string;
  positions_delta_5: number;
  positions_delta_10: number;
};

type ByCircuit = {
  circuit: string;
  total: number;
  right: number;
  agree: number;
  drivers: Set<string>;
};

export function F1Live() {
  const [years, setYears] = useState<string[]>([]);
  const [year, setYear] = useState<string | null>(null);
  const [rows, setRows] = useState<BacktestRow[] | null>(null);
  const [circuit, setCircuit] = useState<string | null>(null);
  const [driver, setDriver] = useState<string | null>(null);

  useEffect(() => {
    api.backtests().then((d) => {
      if (!d) return;
      const ys = Object.keys(d).sort();
      setYears(ys);
      if (ys.length) setYear(ys[ys.length - 1]);
    });
  }, []);

  useEffect(() => {
    if (!year) return;
    setRows(null);
    api.backtestYear(year).then((r) => setRows(r ?? []));
  }, [year]);

  const byCircuit = useMemo(() => {
    if (!rows) return [] as ByCircuit[];
    const m = new Map<string, ByCircuit>();
    for (const r of rows) {
      const cur = m.get(r.circuit) ?? { circuit: r.circuit, total: 0, right: 0, agree: 0, drivers: new Set<string>() };
      cur.total++;
      if (r.model_was_right) cur.right++;
      if (r.agrees) cur.agree++;
      cur.drivers.add(r.driver);
      m.set(r.circuit, cur);
    }
    return Array.from(m.values()).sort((a, b) => a.circuit.localeCompare(b.circuit));
  }, [rows]);

  const drivers = useMemo(() => {
    if (!rows || !circuit) return [] as string[];
    const set = new Set<string>();
    for (const r of rows) if (r.circuit === circuit) set.add(r.driver);
    return Array.from(set).sort();
  }, [rows, circuit]);

  const driverRows = useMemo(() => {
    if (!rows || !circuit || !driver) return [] as BacktestRow[];
    return rows
      .filter((r) => r.circuit === circuit && r.driver === driver)
      .sort((a, b) => a.lap - b.lap);
  }, [rows, circuit, driver]);

  
  useEffect(() => {
    if (!circuit && byCircuit.length) setCircuit(byCircuit[0].circuit);
  }, [byCircuit, circuit]);
  useEffect(() => {
    if (drivers.length && (!driver || !drivers.includes(driver))) setDriver(drivers[0]);
  }, [drivers, driver]);

  return (
    <div className="space-y-6">
      <Bezel innerClassName="p-6">
        <div className="flex flex-wrap items-center gap-x-6 gap-y-3">
          <div>
            <div className="font-mono text-[10px] uppercase tracking-[0.28em] text-ink-mute">Source</div>
            <h3 className="mt-1.5 font-sans text-ink text-xl tracking-tight" style={{ fontWeight: 500 }}>
              Backtest dataset
            </h3>
          </div>
          <div className="hidden md:block h-8 w-px bg-line" />
          <div className="flex items-center gap-2 text-xs">
            <span className="font-mono text-[10px] uppercase tracking-[0.28em] text-ink-mute">Season</span>
            {years.map((y) => (
              <button
                key={y}
                onClick={() => { setYear(y); setCircuit(null); setDriver(null); }}
                className={cn(
                  "rounded-full px-3 py-1 ring-1 transition-all duration-300",
                  year === y ? "bg-coral text-white ring-coral"
                             : "bg-white/[0.03] text-ink-dim ring-white/[0.10] hover:text-ink"
                )}
              >
                {y}
              </button>
            ))}
          </div>
          <div className="hidden md:block h-8 w-px bg-line" />
          <div className="flex items-center gap-2 flex-1 min-w-[260px]">
            <span className="font-mono text-[10px] uppercase tracking-[0.28em] text-ink-mute shrink-0">Round</span>
            <select
              value={circuit ?? ""}
              onChange={(e) => { setCircuit(e.target.value || null); setDriver(null); }}
              className="flex-1 bg-bg-1 ring-1 ring-white/[0.10] rounded-full px-3 py-1.5 text-xs text-ink"
            >
              <option value="">choose circuit</option>
              {byCircuit.map((c) => (
                <option key={c.circuit} value={c.circuit}>
                  {c.circuit} ({c.total} calls)
                </option>
              ))}
            </select>
            <span className="font-mono text-[10px] uppercase tracking-[0.28em] text-ink-mute shrink-0">Driver</span>
            <select
              value={driver ?? ""}
              onChange={(e) => setDriver(e.target.value || null)}
              className="bg-bg-1 ring-1 ring-white/[0.10] rounded-full px-3 py-1.5 text-xs text-ink"
            >
              {drivers.map((d) => (
                <option key={d} value={d}>{d}</option>
              ))}
            </select>
          </div>
        </div>
      </Bezel>

      {!rows && (
        <Bezel innerClassName="p-10 text-center text-ink-mute text-xs">loading backtest dataset</Bezel>
      )}

      {rows && byCircuit.length === 0 && (
        <Bezel innerClassName="p-10 text-center text-ink-mute text-xs">backend returned no rows for this season</Bezel>
      )}

      {circuit && driver && (
        <div className="grid grid-cols-12 gap-5 lg:gap-6">
          <div className="col-span-12 lg:col-span-7">
            <Bezel innerClassName="p-0">
              <div className="px-6 py-5 flex items-end justify-between">
                <div>
                  <div className="font-mono text-[10px] uppercase tracking-[0.28em] text-ink-mute">
                    Lap-by-lap calls
                  </div>
                  <h3 className="mt-1.5 font-sans text-ink text-lg tracking-tight" style={{ fontWeight: 500 }}>
                    {driver} at {circuit}
                  </h3>
                </div>
                <div className="font-mono text-[10px] uppercase tracking-[0.22em] text-ink-mute text-right">
                  {driverRows.length} laps
                </div>
              </div>
              <div className="max-h-[420px] overflow-auto">
                <table className="w-full font-mono text-xs tabular">
                  <thead className="sticky top-0 bg-bg-1/95 backdrop-blur">
                    <tr className="text-[10px] uppercase tracking-[0.22em] text-ink-mute">
                      <th className="text-left py-2 pl-6 font-normal">LAP</th>
                      <th className="text-left py-2 font-normal">ACTUAL</th>
                      <th className="text-left py-2 font-normal">MODEL</th>
                      <th className="text-right py-2 font-normal">CONF</th>
                      <th className="text-right py-2 pr-6 font-normal">RIGHT</th>
                    </tr>
                  </thead>
                  <tbody>
                    {driverRows.map((r, i) => (
                      <tr key={i} className="border-t border-line">
                        <td className="py-2 pl-6 text-ink-dim">{r.lap}</td>
                        <td className="py-2 text-ink">{r.actual_decision}</td>
                        <td className={cn(
                          "py-2",
                          r.agrees ? "text-signal-ok" : "text-coral-hi"
                        )}>
                          {r.recommended_action}
                        </td>
                        <td className="py-2 text-right text-ink-dim">{Math.round(r.confidence * 100)}%</td>
                        <td className="py-2 pr-6 text-right">
                          <span className={cn(
                            "rounded-full px-2 py-0.5 text-[10px] uppercase tracking-[0.18em] ring-1",
                            r.model_was_right
                              ? "bg-signal-ok/15 text-signal-ok ring-signal-ok/30"
                              : "bg-signal-danger/15 text-signal-danger ring-signal-danger/30"
                          )}>
                            {r.model_was_right ? "yes" : "no"}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </Bezel>
          </div>

          <div className="col-span-12 lg:col-span-5">
            <DriverScore rows={driverRows} circuit={circuit} driver={driver} />
          </div>
        </div>
      )}
    </div>
  );
}

function DriverScore({ rows, circuit, driver }: { rows: BacktestRow[]; circuit: string; driver: string }) {
  const right = rows.filter((r) => r.model_was_right).length;
  const agree = rows.filter((r) => r.agrees).length;
  const pct = (n: number) => (rows.length ? Math.round((n / rows.length) * 100) : 0);

  
  const wins = rows
    .filter((r) => !r.agrees && r.model_was_right)
    .slice(0, 3);

  return (
    <Bezel innerClassName="p-7 h-full flex flex-col">
      <Eyebrow>Stint score</Eyebrow>
      <h3 className="mt-3 font-sans text-ink text-3xl tracking-tight" style={{ fontWeight: 500 }}>
        <span className="text-coral">{driver}</span> at {circuit}
      </h3>

      <div className="mt-6 grid grid-cols-3 gap-4 font-mono tabular">
        <div>
          <div className="font-mono text-[10px] uppercase tracking-[0.22em] text-ink-mute">calls</div>
          <div className="mt-1.5 text-3xl text-ink">{rows.length}</div>
        </div>
        <div>
          <div className="font-mono text-[10px] uppercase tracking-[0.22em] text-ink-mute">agreed</div>
          <div className="mt-1.5 text-3xl text-ink">{pct(agree)}%</div>
        </div>
        <div>
          <div className="font-mono text-[10px] uppercase tracking-[0.22em] text-ink-mute">correct</div>
          <div className="mt-1.5 text-3xl text-signal-ok">{pct(right)}%</div>
        </div>
      </div>

      {wins.length > 0 && (
        <div className="mt-6">
          <div className="font-mono text-[10px] uppercase tracking-[0.22em] text-ink-mute mb-2">
            standout calls
          </div>
          <ul className="space-y-2">
            {wins.map((w, i) => (
              <li key={i} className="text-sm text-ink-dim">
                <span className="text-coral-hi font-mono text-xs">L{w.lap}</span>
                {" "}team did <span className="text-ink">{w.actual_decision}</span>, model said{" "}
                <span className="text-ink">{w.recommended_action}</span>
                {w.reasoning && <span className="block text-xs text-ink-mute mt-0.5">{w.reasoning}</span>}
              </li>
            ))}
          </ul>
        </div>
      )}

      <div className="mt-auto pt-6 font-mono text-[10px] uppercase tracking-[0.22em] text-ink-mute">
        from /api/v1/backtests
      </div>
    </Bezel>
  );
}
