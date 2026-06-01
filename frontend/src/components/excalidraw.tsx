"use client";
import { cn } from "@/lib/utils";









export function RoughFilter() {
  return (
    <svg width="0" height="0" className="absolute" aria-hidden>
      <defs>
        <filter id="rough">
          <feTurbulence type="fractalNoise" baseFrequency="0.04" numOctaves="2" seed="3" />
          <feDisplacementMap in="SourceGraphic" scale="1.6" />
        </filter>
        <filter id="rough-strong">
          <feTurbulence type="fractalNoise" baseFrequency="0.06" numOctaves="3" seed="7" />
          <feDisplacementMap in="SourceGraphic" scale="3" />
        </filter>
      </defs>
    </svg>
  );
}



export function DoodleTelemetry({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 120 80" className={cn("text-current", className)} fill="none" strokeWidth="1.4" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" style={{ filter: "url(#rough)" }}>
      <path d="M 10 60 A 50 50 0 0 1 110 60" />
      <path d="M 60 60 L 92 28" />
      <circle cx="60" cy="60" r="3" />
      <path d="M 18 65 L 26 65 M 30 50 L 36 47 M 50 38 L 54 33 M 70 35 L 74 30 M 92 50 L 98 47 M 102 65 L 110 65" />
      <text x="60" y="76" textAnchor="middle" fontSize="6" fontFamily="ui-monospace" letterSpacing="1">SPEED</text>
    </svg>
  );
}

export function DoodleStrategy({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 120 80" className={cn("text-current", className)} fill="none" strokeWidth="1.4" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" style={{ filter: "url(#rough)" }}>
      <circle cx="20" cy="40" r="5" />
      <path d="M 25 40 L 55 18" />
      <path d="M 25 40 L 55 40" />
      <path d="M 25 40 L 55 62" />
      <circle cx="60" cy="18" r="4" />
      <circle cx="60" cy="40" r="5" />
      <circle cx="60" cy="62" r="4" />
      <path d="M 65 40 L 95 30" />
      <path d="M 65 40 L 95 50" />
      <path d="M 65 18 L 95 22" />
      <circle cx="100" cy="22" r="3" />
      <circle cx="100" cy="30" r="3" />
      <circle cx="100" cy="50" r="3" />
      <path d="M 60 40 L 100 30" strokeDasharray="2 3" />
    </svg>
  );
}

export function DoodleSim({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 120 80" className={cn("text-current", className)} fill="none" strokeWidth="1.4" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" style={{ filter: "url(#rough)" }}>
      <path d="M 8 65 C 30 65, 40 35, 70 35 C 95 35, 100 18, 112 18" />
      <path d="M 8 65 C 30 65, 50 55, 75 55 C 100 55, 105 50, 112 50" strokeDasharray="2 3" />
      <path d="M 8 65 C 30 65, 40 70, 70 70 C 95 70, 100 75, 112 75" strokeDasharray="2 3" />
      <path d="M 105 14 L 112 18 L 105 22" />
      <path d="M 105 46 L 112 50 L 105 54" />
      <path d="M 105 71 L 112 75 L 105 79" />
    </svg>
  );
}

export function DoodleGranite({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 120 80" className={cn("text-current", className)} fill="none" strokeWidth="1.4" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" style={{ filter: "url(#rough)" }}>
      <path d="M 14 14 L 14 56 Q 14 64, 22 64 L 60 64 L 70 74 L 70 64 L 96 64 Q 104 64, 104 56 L 104 22 Q 104 14, 96 14 Z" />
      <path d="M 22 28 L 90 28" />
      <path d="M 22 38 L 78 38" />
      <path d="M 22 48 L 60 48" />
      <circle cx="92" cy="44" r="2" />
      <path d="M 92 38 L 92 30" />
    </svg>
  );
}

export function DoodleRag({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 120 80" className={cn("text-current", className)} fill="none" strokeWidth="1.4" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" style={{ filter: "url(#rough)" }}>
      <path d="M 14 14 L 14 66 L 60 70 L 60 18 Z" />
      <path d="M 60 18 L 60 70 L 106 66 L 106 14 Z" />
      <path d="M 20 24 L 54 26" />
      <path d="M 20 34 L 50 36" />
      <path d="M 20 44 L 52 46" />
      <path d="M 20 54 L 46 56" />
      <path d="M 66 22 L 100 22" />
      <path d="M 66 32 L 100 32" />
      <path d="M 66 42 L 92 42" />
      <path d="M 66 52 L 100 52" />
    </svg>
  );
}

export function DoodleDirector({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 120 80" className={cn("text-current", className)} fill="none" strokeWidth="1.4" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" style={{ filter: "url(#rough)" }}>
      <path d="M 26 10 L 26 70" />
      <path d="M 26 14 L 80 14 L 70 26 L 80 38 L 26 38" />
      {}
      <path d="M 36 14 L 36 38 M 46 14 L 46 38 M 56 14 L 56 38 M 66 14 L 66 38" strokeOpacity="0.4" />
      <path d="M 26 14 L 80 38" strokeOpacity="0.0" />
      <circle cx="26" cy="74" r="3" />
    </svg>
  );
}
