"use client";
import { Bezel, Eyebrow } from "@/components/bezel";
import { useRaceHistory } from "@/lib/use-race-history";
import { cn } from "@/lib/utils";

const ICON: Record<string, string> = {
  start: "▶",
  tyre_warning: "▲",
  competitor_pit: "◆",
  ai_rec: "★",
  sim: "◇",
  sc: "■",
  vsc: "■",
  pit: "◆",
  yellow: "▲",
};

export function Timeline() {
  const { events } = useRaceHistory();
  const ordered = [...events].sort((a, b) => a.lap - b.lap);

  return (
    <Bezel innerClassName="p-7">
      <div className="flex items-center justify-between mb-6">
        <Eyebrow>Race events</Eyebrow>
        <span className="font-mono text-[10px] uppercase tracking-[0.28em] text-ink-mute">
          live from telemetry
        </span>
      </div>
      {ordered.length === 0 ? (
        <div className="py-10 text-center text-ink-mute text-xs">
          no events yet
        </div>
      ) : (
        <ol className="relative space-y-5">
          <span className="absolute left-[7px] top-2 bottom-2 w-px bg-gradient-to-b from-coral/50 via-white/10 to-transparent" />
          {ordered.map((e, i) => (
            <li key={`${e.lap}-${e.kind}-${i}`} className="relative flex items-start gap-4 pl-6">
              <span
                className={cn(
                  "absolute left-0 top-1.5 h-3.5 w-3.5 rounded-full flex items-center justify-center font-mono text-[8px] ring-1 ring-white/[0.12]",
                  e.kind === "ai_rec" ? "bg-coral text-white" : "bg-bg-2 text-ink-dim"
                )}
              >
                {ICON[e.kind] ?? "-"}
              </span>
              <div className="flex-1">
                <div className="font-mono text-[10px] uppercase tracking-[0.28em] text-ink-mute">
                  Lap {String(e.lap).padStart(2, "0")}
                </div>
                <div className="text-sm text-ink mt-0.5">{e.label}</div>
              </div>
            </li>
          ))}
        </ol>
      )}
    </Bezel>
  );
}
