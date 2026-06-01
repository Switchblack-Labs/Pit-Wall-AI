"use client";
import { useEffect, useMemo, useState } from "react";
import { Bezel, Eyebrow } from "@/components/bezel";
import { api } from "@/lib/api";
import { cn } from "@/lib/utils";

type Row = {
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

export default function BacktestsPage() {
  const [data, setData] = useState<Record<string, Row[]> | null>(null);
  const [year, setYear] = useState<string | null>(null);
  const [circuit, setCircuit] = useState<string | null>(null);
  const [ferrari, setFerrari] = useState<any | null>(null);

  useEffect(() => {
    api.backtests().then((d) => {
      if (!d) return;
      setData(d);
      const years = Object.keys(d).sort();
      setYear(years[years.length - 1] ?? null);
    });
    api.ferrariResults().then(setFerrari);
  }, []);

  const rows = useMemo<Row[]>(() => {
    if (!data || !year) return [];
    return data[year] ?? [];
  }, [data, year]);

  const circuits = useMemo(() => {
    const seen = new Set<string>();
    for (const r of rows) seen.add(r.circuit);
    return Array.from(seen).sort();
  }, [rows]);

  const filteredRows = useMemo(
    () => (circuit ? rows.filter((r) => r.circuit === circuit) : rows),
    [rows, circuit]
  );

  const accuracy = useMemo(() => {
    if (!filteredRows.length) return { agree: 0, right: 0, total: 0 };
    const agree = filteredRows.filter((r) => r.agrees).length;
    const right = filteredRows.filter((r) => r.model_was_right).length;
    return { agree, right, total: filteredRows.length };
  }, [filteredRows]);

  return (
    <main className="px-[6vw] pt-32 pb-40 space-y-12">
      <header className="grid grid-cols-12 gap-10 items-end">
        <div className="col-span-12 lg:col-span-8">
          <Eyebrow>04 - Validation</Eyebrow>
          <h1
            className="mt-7 font-sans tracking-[-0.04em] text-ink leading-[0.9]"
            style={{ fontSize: "clamp(56px, 7vw, 128px)", fontWeight: 500 }}
          >
            Backtests &<br />
            <span className="text-coral">ground truth.</span>
          </h1>
        </div>
        <div className="col-span-12 lg:col-span-4">
          <p className="text-base lg:text-lg text-ink-dim leading-relaxed">
            Every recommendation the engine made replayed against the actual race
            that followed. Sourced from <code className="font-mono text-coral">ml_engine/results/</code>.
          </p>
        </div>
      </header>

      {}
      {ferrari && (
        <Bezel innerClassName="p-7">
          <div className="flex items-center justify-between mb-4">
            <Eyebrow>Ferrari disaster suite</Eyebrow>
            <span className="font-mono text-sm text-ink-mute">
              {ferrari.passed}/{ferrari.passed + ferrari.failed + ferrari.skipped} passed
            </span>
          </div>
          <div className="grid grid-cols-4 gap-4 font-mono tabular text-2xl">
            <div>
              <div className="text-[10px] uppercase tracking-[0.22em] text-ink-mute">PASS</div>
              <div className="mt-1 text-signal-ok">{ferrari.passed}</div>
            </div>
            <div>
              <div className="text-[10px] uppercase tracking-[0.22em] text-ink-mute">FAIL</div>
              <div className="mt-1 text-signal-danger">{ferrari.failed}</div>
            </div>
            <div>
              <div className="text-[10px] uppercase tracking-[0.22em] text-ink-mute">SKIP</div>
              <div className="mt-1 text-ink">{ferrari.skipped}</div>
            </div>
            <div>
              <div className="text-[10px] uppercase tracking-[0.22em] text-ink-mute">RATE</div>
              <div className="mt-1 text-coral-hi">
                {Math.round((ferrari.pass_rate ?? 0) * 100)}%
              </div>
            </div>
          </div>
        </Bezel>
      )}

      {}
      <div className="flex flex-wrap items-center gap-3">
        <span className="font-mono text-[10px] uppercase tracking-[0.28em] text-ink-mute">Season</span>
        {data &&
          Object.keys(data).sort().map((y) => (
            <button
              key={y}
              onClick={() => { setYear(y); setCircuit(null); }}
              className={cn(
                "rounded-full px-4 py-1.5 ring-1 transition-all duration-300",
                year === y ? "bg-coral text-white ring-coral"
                           : "bg-white/[0.03] text-ink-dim ring-white/[0.10] hover:text-ink"
              )}
            >
              {y}
            </button>
          ))}

        <span className="hidden md:inline h-6 w-px bg-line ml-3 mr-1" />

        <span className="font-mono text-[10px] uppercase tracking-[0.28em] text-ink-mute">Circuit</span>
        <select
          value={circuit ?? ""}
          onChange={(e) => setCircuit(e.target.value || null)}
          className="bg-bg-1 ring-1 ring-white/[0.10] rounded-full px-3 py-1.5 text-xs text-ink"
        >
          <option value="">All ({rows.length})</option>
          {circuits.map((c) => (
            <option key={c} value={c}>{c}</option>
          ))}
        </select>
      </div>

      {}
      <div className="grid grid-cols-3 gap-4">
        <Bezel innerClassName="p-6">
          <div className="text-[10px] uppercase tracking-[0.22em] text-ink-mute">Calls</div>
          <div className="mt-2 font-mono tabular text-4xl text-ink">{accuracy.total}</div>
        </Bezel>
        <Bezel innerClassName="p-6">
          <div className="text-[10px] uppercase tracking-[0.22em] text-ink-mute">Agreed with team</div>
          <div className="mt-2 font-mono tabular text-4xl text-ink">
            {accuracy.total ? Math.round((accuracy.agree / accuracy.total) * 100) : 0}%
          </div>
        </Bezel>
        <Bezel innerClassName="p-6">
          <div className="text-[10px] uppercase tracking-[0.22em] text-ink-mute">Model right (outcome)</div>
          <div className="mt-2 font-mono tabular text-4xl text-signal-ok">
            {accuracy.total ? Math.round((accuracy.right / accuracy.total) * 100) : 0}%
          </div>
        </Bezel>
      </div>

      {}
      <Bezel innerClassName="p-0">
        <div className="max-h-[600px] overflow-auto">
          <table className="w-full font-mono text-xs tabular">
            <thead className="sticky top-0 bg-bg-1/95 backdrop-blur">
              <tr className="text-[10px] uppercase tracking-[0.22em] text-ink-mute">
                <th className="text-left py-3 pl-6 font-normal">Race</th>
                <th className="text-left py-3 font-normal">Driver</th>
                <th className="text-right py-3 font-normal">Lap</th>
                <th className="text-right py-3 font-normal">Pos</th>
                <th className="text-left py-3 pl-6 font-normal">Actual</th>
                <th className="text-left py-3 font-normal">Model</th>
                <th className="text-right py-3 font-normal">Conf</th>
                <th className="text-right py-3 pr-6 font-normal">Verdict</th>
              </tr>
            </thead>
            <tbody>
              {filteredRows.slice(0, 500).map((r, i) => (
                <tr key={i} className="border-t border-line">
                  <td className="py-2 pl-6 text-ink-dim">{r.circuit}</td>
                  <td className="py-2 text-ink">{r.driver}</td>
                  <td className="py-2 text-right text-ink-dim">{r.lap}</td>
                  <td className="py-2 text-right text-ink">P{r.position}</td>
                  <td className="py-2 pl-6 text-ink">{r.actual_decision}</td>
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
                      {r.model_was_right ? "right" : "wrong"}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {filteredRows.length > 500 && (
            <div className="border-t border-line py-3 text-center text-[10px] uppercase tracking-[0.22em] text-ink-mute">
              Showing first 500 of {filteredRows.length} rows
            </div>
          )}
        </div>
      </Bezel>
    </main>
  );
}
