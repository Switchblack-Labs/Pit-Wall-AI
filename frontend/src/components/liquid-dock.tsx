"use client";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";
import { cn } from "@/lib/utils";
import { api } from "@/lib/api";
import { Play, Pause, RotateCcw, Flag, Flame, AlertTriangle } from "lucide-react";

type Mode = "landing" | "dashboard" | "compact" | "hidden";

function useMode(): Mode {
  const path = usePathname();
  const [scrollY, setScrollY] = useState(0);
  useEffect(() => {
    const onScroll = () => setScrollY(window.scrollY);
    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll();
    return () => window.removeEventListener("scroll", onScroll);
  }, []);
  if (path === "/") {
    
    return scrollY < 600 ? "landing" : "hidden";
  }
  if (path?.startsWith("/dashboard")) return "dashboard";
  if (path === "/about") return "hidden";
  return "compact";
}

export function LiquidDock() {
  const mode = useMode();
  const [busy, setBusy] = useState<string | null>(null);
  const run = async (key: string, fn: () => Promise<unknown>) => {
    setBusy(key);
    try { await fn(); } finally { setTimeout(() => setBusy(null), 400); }
  };

  if (mode === "hidden") return null;

  const buttons = [
    { key: "start", label: "Start demo", icon: Play, run: () => api.demoStart() },
    { key: "pause", label: "Pause", icon: Pause, run: () => api.demoStop() },
    { key: "reset", label: "Reset", icon: RotateCcw, run: () => api.demoStop() },
    
    { key: "sc",    label: "Pit now (SC)", icon: Flag,          run: () => api.simulate({ scenario_type: "pit_now", laps_until_action: 0 }) },
    { key: "wear",  label: "Pit hard",     icon: Flame,         run: () => api.simulate({ scenario_type: "pit_hard", laps_until_action: 1 }) },
    { key: "rival", label: "Stay out",     icon: AlertTriangle, run: () => api.simulate({ scenario_type: "stay_out", laps_until_action: 0 }) },
  ];

  return (
    <div
      className={cn(
        "fixed left-1/2 z-30 -translate-x-1/2 transition-all duration-700 ease-spring",
        mode === "landing" && "bottom-8 opacity-100",
        mode === "dashboard" && "bottom-6 opacity-100",
        mode === "compact" && "bottom-6 opacity-90 scale-90"
      )}
    >
      <div className="liquid-pill flex items-center gap-1 p-1.5">
        {mode !== "compact" && (
          <span className="px-3 py-1 text-[10px] uppercase tracking-[0.22em] text-ink-mute">
            Director
          </span>
        )}
        {buttons.map((b) => {
          const Icon = b.icon;
          const active = busy === b.key;
          return (
            <button
              key={b.key}
              onClick={() => run(b.key, b.run as () => Promise<unknown>)}
              title={b.label}
              className={cn(
                "group flex items-center gap-2 rounded-full px-3 py-2 text-sm transition-all duration-300 ease-spring",
                active ? "bg-coral text-white" : "text-ink-dim hover:bg-white/[0.07] hover:text-ink"
              )}
            >
              <Icon className="h-4 w-4 stroke-[1.4]" />
              {mode === "dashboard" && <span className="hidden md:inline">{b.label}</span>}
            </button>
          );
        })}
      </div>
    </div>
  );
}
