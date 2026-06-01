"use client";
import { useEffect, useRef, useState } from "react";
import { PngSequence, drawContain } from "@/lib/png-sequence";

const LOADER_FRAMES = 58; 



const CAR_SCALE = 1.0;
const Y_OFFSET = 0.06;








export function BuildLoader({ onDone }: { onDone?: () => void }) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [hide, setHide] = useState(false);
  const [hidden, setHidden] = useState(false);

  useEffect(() => {
    if (typeof window === "undefined") return;

    let raf = 0;
    let killed = false;
    const timers: ReturnType<typeof setTimeout>[] = [];
    const seq = new PngSequence(LOADER_FRAMES, "/hero/", 4);

    const duration = 2200;

    const tick = (t: number, start: number) => {
      const p = Math.min(1, (t - start) / duration);
      const eased = 1 - Math.pow(1 - p, 1.8);
      const f = Math.min(LOADER_FRAMES - 1, Math.round(eased * (LOADER_FRAMES - 1)));
      const img = seq.get(f);
      const c = canvasRef.current;
      if (img && c) drawContain(c, img, CAR_SCALE, Y_OFFSET);

      if (p < 1) {
        raf = requestAnimationFrame((tt) => tick(tt, start));
      } else {
        
        
        timers.push(setTimeout(() => {
          if (killed) return;
          onDone?.();
          setHide(true);
          timers.push(setTimeout(() => { if (!killed) setHidden(true); }, 700));
        }, 250));
      }
    };

    
    
    
    seq.load(0).then((img) => {
      if (killed || !img) return;
      const c = canvasRef.current;
      if (c) drawContain(c, img, CAR_SCALE, Y_OFFSET);
    });
    const begin = () => {
      if (killed) return;
      raf = requestAnimationFrame((t) => tick(t, performance.now()));
    };
    
    let started = false;
    const startOnce = () => { if (!started) { started = true; begin(); } };
    seq.preload(0, LOADER_FRAMES - 1, 12).then(startOnce);
    timers.push(setTimeout(startOnce, 2500));

    return () => { killed = true; cancelAnimationFrame(raf); timers.forEach(clearTimeout); };
  }, [onDone]);

  if (hidden) return null;

  return (
    <div
      aria-hidden
      className="pointer-events-none fixed inset-0 z-[90] transition-opacity duration-700 ease-out"
      style={{ opacity: hide ? 0 : 1 }}
    >
      {
}
      <canvas ref={canvasRef} className="absolute inset-0 h-full w-full" />
    </div>
  );
}
