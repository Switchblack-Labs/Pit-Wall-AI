"use client";
import { cn } from "@/lib/utils";

export function Marquee({
  items,
  speed = 40,
  className,
}: {
  items: string[];
  speed?: number;
  className?: string;
}) {
  const repeated = [...items, ...items, ...items];
  return (
    <div className={cn("relative overflow-hidden", className)}>
      <div
        className="flex gap-12 whitespace-nowrap will-change-transform"
        style={{ animation: `marquee ${speed}s linear infinite` }}
      >
        {repeated.map((item, i) => (
          <span
            key={i}
            className="font-mono text-xs uppercase tracking-[0.28em] text-ink-mute"
          >
            <span className="mr-12 text-coral">●</span>
            {item}
          </span>
        ))}
      </div>
      <style jsx>{`
        @keyframes marquee {
          from { transform: translate3d(0,0,0); }
          to { transform: translate3d(-33.333%,0,0); }
        }
      `}</style>
    </div>
  );
}
