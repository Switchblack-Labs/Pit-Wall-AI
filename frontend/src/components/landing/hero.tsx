"use client";
import Link from "next/link";
import { ArrowDown, ArrowUpRight } from "lucide-react";
import { cn } from "@/lib/utils";

function Pin({
  side,
  title,
  sub,
  className = "",
}: {
  side: "left" | "right";
  title: string;
  sub: string;
  className?: string;
}) {
  const dot = (
    <span className="relative h-2.5 w-2.5 rounded-full ring-1 ring-white/25 bg-white/[0.04] backdrop-blur shrink-0">
      <span className="absolute inset-[2px] rounded-full bg-coral" />
      <span className="absolute -inset-[3px] rounded-full ring-1 ring-coral/30 animate-ping" />
    </span>
  );
  const text = (
    <div className={cn(side === "right" ? "text-right" : "")}>
      <div className="text-xs text-ink leading-tight">{title}</div>
      <div className="font-mono text-[9px] uppercase tracking-[0.24em] text-ink-mute mt-0.5">
        {sub}
      </div>
    </div>
  );
  return (
    <div className={`absolute z-30 flex items-center gap-2.5 ${className}`}>
      {side === "left" ? (
        <>
          {dot}
          <span className="h-px w-8 bg-white/20" />
          {text}
        </>
      ) : (
        <>
          {text}
          <span className="h-px w-8 bg-white/20" />
          {dot}
        </>
      )}
    </div>
  );
}

export function Hero() {
  return (
    <section id="hero" className="relative h-[100dvh] w-full overflow-hidden bg-bg">
      {}
      <div className="absolute right-6 top-6 z-40 flex flex-col items-end">
        <div className="flex items-center gap-2 text-sm">
          <span className="h-4 w-4 rounded-full bg-coral" />
          <span className="font-medium tracking-tight text-ink">pitwall</span>
          <span className="text-ink-mute">/ ai</span>
        </div>

        <p className="mt-2 text-sm text-ink-mute leading-relaxed">
          real-time telemetry, counterfactual strategy, <br />and the FIA rulebook as one race engineer,<br /> powered by IBM Granite.
        </p>
      </div>

      {}
      <div className="absolute left-6 top-1/2 -translate-y-1/2 z-30 flex flex-col items-center gap-3 font-mono text-[10px] tracking-[0.32em] text-ink-mute">
        <span className="text-ink">01</span>
        <span className="h-10 w-px bg-white/20" />
        <span>02</span>
        <span>03</span>
        <span>04</span>
      </div>

      {}
      <div className="absolute z-10 top-[17vh]" style={{ left: "14vw" }}>
        <span
          className="block font-sans text-ink/80 tracking-[-0.025em] leading-none"
          style={{ fontSize: "clamp(36px, 4.5vw, 84px)", fontWeight: 300 }}
        >
          real time
        </span>
      </div>

      <div className="absolute z-10 inset-x-0 top-[27vh] text-center">
        <span
          className="font-sans tracking-[-0.04em] leading-none"
          style={{ fontSize: "clamp(64px, 9vw, 200px)" }}
        >
          <span className="text-ink" style={{ fontWeight: 600 }}>race</span>
          <span className="text-ink/30" style={{ fontWeight: 300 }}> intelligence</span>
        </span>
      </div>

      <div className="absolute z-30 top-[52vh]" style={{ left: "14vw" }}>
        <span
          className="block font-sans text-ink/55 tracking-[-0.025em] leading-none"
          style={{ fontSize: "clamp(28px, 3.5vw, 64px)", fontWeight: 700 }}
        >
          for the
        </span>
      </div>

      {}
      <div className="absolute z-10 right-[8vw] top-[63vh] text-right">
        <span
          className="block font-sans text-ink tracking-[-0.04em] leading-[0.92]"
          style={{ fontSize: "clamp(40px, 6.5vw, 110px)", fontWeight: 700 }}
        >
          modern
        </span>
      </div>

      {}
      <div className="absolute z-30 right-[8vw] top-[72vh] text-right">
        <span
          className="block font-sans text-ink/30 tracking-[-0.04em] leading-[0.92]"
          style={{ fontSize: "clamp(40px, 6.5vw, 110px)", fontWeight: 600 }}
        >
          pit wall<span className="text-coral">.</span>
        </span>
      </div>

      {
}
      <div className="pointer-events-none absolute inset-x-0 top-0 z-[25] h-24 bg-gradient-to-b from-bg to-transparent" />

      {}
      <Pin
        side="left"
        title="granite"
        sub="explainability"
        className="left-[18vw] top-[61vh]"
      />
      <Pin
        side="right"
        title="telemetry"
        sub="WS - 60Hz"
        className="right-[22vw] top-[45vh]"
      />

      {}
      <div className="absolute z-30 left-[7vw] bottom-[12vh] max-w-sm">
        <Link href="/dashboard" className="btn-coral">
          Open Dashboard
          <span className="btn-coral-icon">
            <ArrowUpRight className="h-4 w-4 stroke-[1.6]" />
          </span>
        </Link>
      </div>

      {}
      <div className="absolute z-30 right-[7vw] bottom-[12vh]">
        <span className="h-11 w-11 rounded-full ring-1 ring-white/15 bg-white/[0.03] flex items-center justify-center">
          <ArrowDown className="h-4 w-4 text-ink-dim" />
        </span>
      </div>
    </section>
  );
}
