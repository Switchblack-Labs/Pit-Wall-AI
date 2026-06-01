"use client";
import { useEffect, useState } from "react";
import { cn } from "@/lib/utils";














export function F1Lights({ onDone }: { onDone?: () => void }) {
  const [step, setStep] = useState(0); 
  const [out, setOut] = useState(false);
  const [closing, setClosing] = useState(false);
  const [hidden, setHidden] = useState(false);
  const [skipped, setSkipped] = useState(false);

  useEffect(() => {
    if (typeof window === "undefined") return;
    if (sessionStorage.getItem("rm:intro") === "1") {
      setHidden(true);
      onDone?.();
      return;
    }

    const timers: ReturnType<typeof setTimeout>[] = [];
    [1, 2, 3, 4, 5].forEach((n) => {
      timers.push(setTimeout(() => setStep(n), 300 + n * 400));
    });
    timers.push(setTimeout(() => setOut(true), 2700));
    timers.push(setTimeout(() => setClosing(true), 3300));
    timers.push(setTimeout(() => {
      sessionStorage.setItem("rm:intro", "1");
      setHidden(true);
      onDone?.();
    }, 3700));
    return () => timers.forEach(clearTimeout);
  }, [onDone]);

  const skip = () => {
    if (skipped) return;
    setSkipped(true);
    sessionStorage.setItem("rm:intro", "1");
    setClosing(true);
    setTimeout(() => { setHidden(true); onDone?.(); }, 350);
  };

  if (hidden) return null;

  return (
    <div
      className={cn(
        "fixed inset-0 z-[80] flex flex-col items-center justify-between bg-[#08070a]",
        "transition-all duration-700 ease-spring",
        closing && "-translate-y-full"
      )}
      role="dialog"
      aria-label="Race start sequence"
    >
      {}
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute inset-0 bg-[radial-gradient(60%_50%_at_50%_15%,rgba(255,255,255,0.05),transparent_70%)]" />
        <div className="absolute inset-0 bg-[radial-gradient(80%_60%_at_50%_120%,rgba(226,108,69,0.06),transparent_60%)]" />
      </div>

      {}
      <div className="relative z-10 pt-[18vh] flex flex-col items-center">
        <div className="font-mono text-[10px] uppercase tracking-[0.38em] text-white/30 mb-10">
          Start procedure - {out ? "GO" : `${step}/5`}
        </div>
        <Gantry step={step} out={out} />
        {out && (
          <div className="mt-12 font-sans font-medium tracking-[-0.04em] text-[clamp(40px,8vw,120px)] text-white leading-none">
            Lights out.
          </div>
        )}
      </div>

      <div className="relative z-10 pb-10 flex w-full justify-between px-8 text-[10px] uppercase tracking-[0.32em] text-white/40">
        <span>PitWall - 2026</span>
        <button onClick={skip} className="hover:text-white/80 transition-colors">
          Skip intro &gt;
        </button>
      </div>
    </div>
  );
}

function Gantry({ step, out }: { step: number; out: boolean }) {
  
  return (
    <div className="flex items-end gap-3 md:gap-4">
      {[1, 2, 3, 4, 5].map((n) => {
        const lit = !out && step >= n;
        return (
          <div
            key={n}
            className={cn(
              "rounded-xl px-3 pt-3 pb-2 ring-1 ring-white/10 bg-black/50 backdrop-blur",
              "transition-all duration-300 ease-spring",
              "shadow-[inset_0_1px_0_rgba(255,255,255,0.08)]"
            )}
          >
            <div className="flex flex-col gap-2">
              <Bulb lit={lit} />
              <Bulb lit={lit} />
            </div>
          </div>
        );
      })}
    </div>
  );
}

function Bulb({ lit }: { lit: boolean }) {
  return (
    <div className="relative h-10 w-10 md:h-14 md:w-14">
      <div
        className={cn(
          "absolute inset-0 rounded-full transition-all duration-200 ease-spring",
          lit
            ? "bg-[#FF1C1C] shadow-[0_0_28px_rgba(255,28,28,0.85),inset_0_2px_0_rgba(255,255,255,0.55)]"
            : "bg-black/60 ring-1 ring-white/10"
        )}
      />
      {}
      {lit && (
        <div className="absolute left-1/2 top-1.5 h-1.5 w-3 -translate-x-1/2 rounded-full bg-white/80 blur-[1px]" />
      )}
    </div>
  );
}
