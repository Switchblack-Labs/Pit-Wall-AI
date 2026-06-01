import { TelemetryStrip } from "@/components/dashboard/telemetry-strip";
import { TrackMap } from "@/components/dashboard/track-map";
import { AiRecommendation } from "@/components/dashboard/ai-rec";
import { TyreGauges } from "@/components/dashboard/tyre-gauges";
import { LapDelta } from "@/components/dashboard/lap-delta";
import { Sectors } from "@/components/dashboard/sectors";
import { Timeline } from "@/components/dashboard/timeline";
import { CompetitorsTable } from "@/components/dashboard/competitors-table";
import { F1Live } from "@/components/dashboard/f1-live";
import { AutoDemo } from "@/components/dashboard/auto-demo";
import { RaceContextProvider } from "@/components/dashboard/race-context";

export default function DashboardPage() {
  return (
    <main className="px-[4vw] pt-32 pb-40 space-y-16">
      <AutoDemo />
      <header>
        <div className="font-mono text-[10px] uppercase tracking-[0.32em] text-ink-mute">
          Pit Wall, live
        </div>
        <h1
          className="mt-4 font-sans text-ink tracking-[-0.04em] leading-[0.9]"
          style={{ fontSize: "clamp(56px, 8vw, 140px)", fontWeight: 500 }}
        >
          Dashboard
        </h1>
      </header>

      <RaceContextProvider>
        <section className="mt-8 space-y-6">
          <div className="font-mono text-[10px] uppercase tracking-[0.32em] text-ink-mute">
            Section A, live race state
          </div>
          <div className="grid grid-cols-12 gap-5 lg:gap-6">
            <div className="col-span-12 lg:col-span-8 lg:row-span-2">
              <TrackMap />
            </div>
            <div className="col-span-12 lg:col-span-4 lg:row-span-2">
              <AiRecommendation />
            </div>

            <div className="col-span-12 lg:col-span-8">
              <TelemetryStrip />
            </div>
            <div className="col-span-12 lg:col-span-4">
              <TyreGauges />
            </div>

            <div className="col-span-12 lg:col-span-4">
              <LapDelta />
            </div>
            <div className="col-span-12 lg:col-span-4">
              <Sectors />
            </div>
            <div className="col-span-12 lg:col-span-4">
              <CompetitorsTable />
            </div>

            <div className="col-span-12">
              <Timeline />
            </div>
          </div>
        </section>
      </RaceContextProvider>

      <section>
        <div className="flex items-end justify-between mb-6">
          <div>
            <div className="font-mono text-[10px] uppercase tracking-[0.32em] text-ink-mute">
              Section B, every call the engine ever made
            </div>
            <h2
              className="mt-3 font-sans text-ink tracking-[-0.035em] leading-[0.95]"
              style={{ fontSize: "clamp(32px, 4vw, 64px)", fontWeight: 500 }}
            >
              Pick a race, pick a driver, see the call.
            </h2>
          </div>
        </div>
        <F1Live />
      </section>
    </main>
  );
}
