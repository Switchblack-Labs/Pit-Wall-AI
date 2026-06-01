"use client";
import { useEffect, useState } from "react";
import { Bezel, Eyebrow } from "@/components/bezel";
import { api } from "@/lib/api";
import { useLiveTelemetry } from "@/lib/use-live";
import { AiRecommendation } from "@/components/dashboard/ai-rec";
import { TelemetryStrip } from "@/components/dashboard/telemetry-strip";
import { Play, Square } from "lucide-react";

export default function TorcsPage() {
  const [totalLaps, setTotalLaps] = useState(58);
  const [running, setRunning] = useState(false);
  const [busy, setBusy] = useState(false);
  const { status } = useLiveTelemetry(200);

  
  useEffect(() => {
    return () => { if (running) api.torcsStop(); };
  }, [running]);

  const start = async () => {
    setBusy(true);
    await api.torcsStart({ mode: "simulated", total_laps: totalLaps });
    setRunning(true);
    setBusy(false);
  };

  const stop = async () => {
    setBusy(true);
    await api.torcsStop();
    setRunning(false);
    setBusy(false);
  };

  return (
    <main className="px-[6vw] pt-32 pb-40 space-y-12">
      <header className="grid grid-cols-12 gap-10 items-end">
        <div className="col-span-12 lg:col-span-8">
          <Eyebrow>06 - Driver-in-the-loop</Eyebrow>
          <h1
            className="mt-7 font-sans tracking-[-0.04em] text-ink leading-[0.9]"
            style={{ fontSize: "clamp(56px, 7vw, 128px)", fontWeight: 500 }}
          >
            TORCS.<br />
            <span className="text-coral">Live recommendations.</span>
          </h1>
        </div>
        <div className="col-span-12 lg:col-span-4">
          <p className="text-base lg:text-lg text-ink-dim leading-relaxed">
            A simulated TORCS source streams telemetry into the same race-state
            pipeline the dashboard uses. No external simulator is required.
          </p>
        </div>
      </header>

      {}
      <Bezel innerClassName="p-6">
        <div className="flex flex-wrap items-center gap-4">
          <div className="flex items-center gap-2">
            <span className="font-mono text-[10px] uppercase tracking-[0.28em] text-ink-mute">Laps</span>
            <input
              type="number"
              min={1}
              max={120}
              value={totalLaps}
              disabled={running}
              onChange={(e) => setTotalLaps(Number(e.target.value))}
              className="w-20 bg-bg-1 ring-1 ring-white/[0.10] rounded-full px-3 py-1 text-xs text-ink"
            />
          </div>

          <div className="flex-1" />

          <span className="font-mono text-[10px] uppercase tracking-[0.22em] text-ink-mute">
            socket {status}
          </span>

          {!running ? (
            <button
              onClick={start}
              disabled={busy}
              className="inline-flex items-center gap-2 rounded-full bg-ink text-bg-1 px-5 py-2 text-xs uppercase tracking-[0.22em] disabled:opacity-40 hover:bg-coral hover:text-white transition-colors duration-300"
            >
              <Play className="h-3.5 w-3.5 stroke-[2]" />
              start telemetry source
            </button>
          ) : (
            <button
              onClick={stop}
              disabled={busy}
              className="inline-flex items-center gap-2 rounded-full ring-1 ring-white/[0.15] px-5 py-2 text-xs uppercase tracking-[0.22em] text-ink-dim hover:text-ink hover:ring-white/[0.30] transition-colors duration-300 disabled:opacity-40"
            >
              <Square className="h-3.5 w-3.5 stroke-[2]" />
              stop
            </button>
          )}
        </div>
      </Bezel>

      {}
      <div className="grid grid-cols-12 gap-6">
        <div className="col-span-12 lg:col-span-8">
          <TelemetryStrip />
        </div>
        <div className="col-span-12 lg:col-span-4">
          <AiRecommendation />
        </div>
      </div>
    </main>
  );
}
