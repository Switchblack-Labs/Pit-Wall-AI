"use client";
import { useEffect, useRef, useState } from "react";
import { PngSequence, drawContain } from "@/lib/png-sequence";

const START_FRAME = 60;
const FALLBACK_TOTAL = 291;
const EXPLOSION_TOTAL = 241;

const HERO_SCALE = 1.0;
const HERO_YOFFSET = 0.06;
const REEL_SCALE = 1.0;
const REEL_YOFFSET = 0.1;
const EXPLOSION_SCALE = 1.35;
const EXPLOSION_END_SCALE = 1.08;
const EXPLOSION_SCALE_DOWN_START = 194;
const lerp = (a: number, b: number, t: number) => a + (b - a) * t;

export function ScrollStage({
  heroSelector = "#hero",
  reelSelector = "#reel",
  explosionSelector = "#explosion-sequence",
  bufferVh = 60,
}: {
  heroSelector?: string;
  reelSelector?: string;
  explosionSelector?: string;
  bufferVh?: number;
}) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const seqRef = useRef<PngSequence | null>(null);
  const explosionSeqRef = useRef<PngSequence | null>(null);
  const totalRef = useRef<number>(FALLBACK_TOTAL);
  const lastFrameRef = useRef<number>(-1);
  const [zone, setZone] = useState<"hero" | "reel" | "hidden">("hero");
  const [ready, setReady] = useState(false);

  useEffect(() => {
    let killed = false;

    totalRef.current = FALLBACK_TOTAL;
    const seq = new PngSequence(FALLBACK_TOTAL, "/hero/", 4);
    seqRef.current = seq;
    const explosionSeq = new PngSequence(EXPLOSION_TOTAL, "/explosion/", 4);
    explosionSeqRef.current = explosionSeq;

    seq.load(START_FRAME).then((img) => {
      if (killed || !img) return;
      const c = canvasRef.current;
      if (c) { drawContain(c, img, HERO_SCALE, HERO_YOFFSET); setReady(true); }
    });

    seq.preload(START_FRAME, FALLBACK_TOTAL - 1, 3);
    explosionSeq.preload(0, EXPLOSION_TOTAL - 1, 3);

    return () => { killed = true; };
  }, []);

  useEffect(() => {
    const original = document.body.classList.contains("landing-scrollbar-hidden");
    document.body.classList.add("landing-scrollbar-hidden");
    return () => {
      if (!original) document.body.classList.remove("landing-scrollbar-hidden");
    };
  }, []);

  useEffect(() => {
    let raf = 0;
    const onScroll = () => {
      if (raf) return;
      raf = requestAnimationFrame(() => {
        raf = 0;
        const seq = seqRef.current;
        const explosionSeq = explosionSeqRef.current;
        const c = canvasRef.current;
        if (!seq || !explosionSeq || !c) return;

        const hero = document.querySelector<HTMLElement>(heroSelector);
        const reel = document.querySelector<HTMLElement>(reelSelector);
        const explosion = document.querySelector<HTMLElement>("#exploded-outro") ?? document.querySelector<HTMLElement>(explosionSelector);
        if (!hero || !reel) return;

        const vh = window.innerHeight;
        const heroRect = hero.getBoundingClientRect();
        const heroBottom = heroRect.top + window.scrollY + hero.offsetHeight;
        const spacer =
          reel.parentElement && reel.parentElement.classList.contains("pin-spacer")
            ? reel.parentElement
            : reel;
        const reelTop = spacer.getBoundingClientRect().top + window.scrollY;
        const panelCount = reel.querySelectorAll("[data-panel]").length || 4;
        const reelScrollSpan = (panelCount - 1) * vh * 1.1;
        const reelBottom = reelTop + reelScrollSpan;

        const y = window.scrollY;
        const total = totalRef.current;
        const totalRange = total - START_FRAME - 1;
        const bufferEnd = heroBottom + (bufferVh / 100) * vh;

        let frame = START_FRAME;
        let newZone: "hero" | "reel" | "hidden" = "hidden";
        let scale = HERO_SCALE;
        let yOffset = HERO_YOFFSET;

        if (y < heroBottom) {
          const p = Math.max(0, Math.min(1, y / heroBottom));
          frame = START_FRAME + Math.round(p * totalRange * 0.18);
          newZone = "hero";
        } else if (y < bufferEnd) {
          const p = (y - heroBottom) / ((bufferVh / 100) * vh);
          frame = START_FRAME + Math.round((0.18 + p * 0.07) * totalRange);
          newZone = "hero";
          scale = lerp(HERO_SCALE, REEL_SCALE, p);
          yOffset = lerp(HERO_YOFFSET, REEL_YOFFSET, p);
        } else if (y < reelBottom) {
          const span = Math.max(1, reelBottom - bufferEnd);
          const p = Math.max(0, Math.min(1, (y - bufferEnd) / span));
          frame = START_FRAME + Math.round((0.25 + p * 0.75) * totalRange);
          newZone = "reel";
          scale = REEL_SCALE;
          yOffset = REEL_YOFFSET;
        } else if (explosion) {
          const expRect = explosion.getBoundingClientRect();
          const expTop = expRect.top + window.scrollY;
          const expBottom = expTop + explosion.offsetHeight - vh;
          if (y >= expTop && y <= expBottom) {
            const p = Math.max(0, Math.min(1, (y - expTop) / Math.max(1, expBottom - expTop)));
            const expFrame = Math.round(p * (EXPLOSION_TOTAL - 1));
            let img = explosionSeq.nearest(expFrame, 10);
            if (!img) explosionSeq.load(expFrame);
            if (img) {
              const scaleDownProgress = Math.max(0, Math.min(1, (expFrame - EXPLOSION_SCALE_DOWN_START) / Math.max(1, EXPLOSION_TOTAL - 1 - EXPLOSION_SCALE_DOWN_START)));
              setZone((z) => (z !== "reel" ? "reel" : z));
              drawContain(c, img, lerp(EXPLOSION_SCALE, EXPLOSION_END_SCALE, scaleDownProgress), 0);
              lastFrameRef.current = expFrame;
            }
            return;
          }
          frame = total - 1;
          newZone = "hidden";
          scale = REEL_SCALE;
          yOffset = REEL_YOFFSET;
        } else {
          frame = total - 1;
          newZone = "hidden";
          scale = REEL_SCALE;
          yOffset = REEL_YOFFSET;
        }

        setZone((z) => (z !== newZone ? newZone : z));

        const f = Math.min(total - 1, Math.max(START_FRAME, frame));
        let img = seq.nearest(f, 10);
        if (!img) seq.load(f);
        if (img) {
          drawContain(c, img, scale, yOffset);
          lastFrameRef.current = f;
        }
      });
    };

    window.addEventListener("scroll", onScroll, { passive: true });
    window.addEventListener("resize", onScroll);
    onScroll();
    return () => {
      cancelAnimationFrame(raf);
      window.removeEventListener("scroll", onScroll);
      window.removeEventListener("resize", onScroll);
    };
  }, [heroSelector, reelSelector, explosionSelector, bufferVh]);

  const zIndexClass =
    zone === "hero" ? "z-[20]" :
    zone === "reel" ? "z-[15]" :
    "-z-10 opacity-0";

  return (
    <canvas
      ref={canvasRef}
      aria-hidden
      className={`fixed inset-0 w-full h-full pointer-events-none transition-opacity duration-300 ${zIndexClass} ${ready ? "opacity-100" : "opacity-0"}`}
    />
  );
}
