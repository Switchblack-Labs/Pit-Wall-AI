"use client";
import { useEffect, useRef } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";

if (typeof window !== "undefined") {
  gsap.registerPlugin(ScrollTrigger);
}

type Panel = {
  index: string;
  kicker: string;
  title: string;
  caption: string;
  numeral: string;
  numeralCaption: string;
};

const PANELS: Panel[] = [
  {
    index: "01",
    kicker: "Lights out",
    title: "Telemetry, the moment it happens.",
    caption:
      "Every brake, throttle and steering input streams from the simulator to the pit wall at 60 Hz over WebSocket.",
    numeral: "60Hz",
    numeralCaption: "stream rate",
  },
  {
    index: "02",
    kicker: "The apex",
    title: "Every call carries a reason.",
    caption:
      "IBM Granite turns model output into plain language. Tyre wear, gap, weather, cited line by line.",
    numeral: "0.71",
    numeralCaption: "confidence",
  },
  {
    index: "03",
    kicker: "Pit window",
    title: "Branch the race in one click.",
    caption:
      "Counterfactual sim compares stay-out, undercut and overcut. Projected position and risk land before the lollipop drops.",
    numeral: "+4.2s",
    numeralCaption: "undercut net gain",
  },
  {
    index: "04",
    kicker: "The rulebook",
    title: "Ask the FIA regulations directly.",
    caption:
      "RAG over the 2026 Sporting and Technical regulations. Cited answers in under a second. No scrolling 400-page PDFs at race pace.",
    numeral: "Art. 26",
    numeralCaption: "safety car",
  },
];

export function HorizontalReel() {
  const wrapRef = useRef<HTMLDivElement>(null);
  const trackRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!wrapRef.current || !trackRef.current) return;
    const track = trackRef.current;
    const panels = track.children.length;
    const distance = () => -((panels - 1) * window.innerWidth);

    const ctx = gsap.context(() => {
      const tween = gsap.to(track, {
        x: distance,
        ease: "none",
        scrollTrigger: {
          trigger: wrapRef.current,
          start: "top top",
          end: () => `+=${(panels - 1) * window.innerHeight * 1.45}`,
          pin: true,
          scrub: 1.4,
          invalidateOnRefresh: true,
        },
      });
      const sections = track.querySelectorAll<HTMLElement>("[data-panel]");
      sections.forEach((sec) => {
        gsap.from(sec.querySelectorAll<HTMLElement>("[data-reveal]"), {
          y: 50,
          opacity: 0,
          filter: "blur(8px)",
          duration: 1,
          ease: "power3.out",
          stagger: 0.09,
          scrollTrigger: {
            trigger: sec,
            containerAnimation: tween,
            start: "left center",
          },
        });
      });
    }, wrapRef);

    return () => ctx.revert();
  }, []);

  return (
    <section id="reel" ref={wrapRef} className="relative h-screen w-full overflow-hidden bg-bg">
      <div className="pointer-events-none absolute inset-x-0 top-0 z-[25] h-40 bg-gradient-to-b from-bg to-transparent" />
      <div className="pointer-events-none absolute inset-x-0 bottom-0 z-10 h-32 bg-gradient-to-t from-[#1a1714] to-transparent" />

      <div className="pointer-events-none absolute left-8 top-1/2 -translate-y-1/2 z-20 flex flex-col gap-3 font-mono text-[10px] tracking-[0.32em] text-ink-mute">
        {PANELS.map((p, i) => (
          <span key={p.index} className={i === 0 ? "text-ink" : ""}>
            {p.index}
          </span>
        ))}
      </div>

      <div ref={trackRef} className="flex h-full w-fit" style={{ willChange: "transform" }}>
        {PANELS.map((p) => (
          <article
            key={p.index}
            data-panel
            className="relative flex h-screen w-screen shrink-0 items-center px-[10vw]"
          >
            <div className="pointer-events-none absolute inset-x-[6vw] inset-y-[14vh] rounded-[40px] bg-white/[0.015] ring-1 ring-white/[0.04] backdrop-blur-[2px] z-[5]" />
            <div className="relative z-[30] grid w-full grid-cols-12 items-center gap-10">
              <div className="col-span-12 lg:col-span-7 flex flex-col gap-7">
                <div data-reveal className="flex items-center gap-3 font-mono text-[10px] uppercase tracking-[0.32em] text-ink-mute">
                  <span>{p.index} / 04</span>
                  <span className="h-px w-8 bg-white/15" />
                  <span>{p.kicker}</span>
                </div>

                <h2
                  data-reveal
                  className="font-sans text-ink tracking-[-0.04em] leading-[0.92]"
                  style={{ fontSize: "clamp(40px, 5.5vw, 96px)", fontWeight: 500 }}
                >
                  {p.title}
                </h2>

                <p
                  data-reveal
                  className="max-w-xl text-base lg:text-lg leading-relaxed text-ink-dim"
                >
                  {p.caption}
                </p>
              </div>

              <div className="col-span-12 lg:col-span-5 flex flex-col items-end gap-3">
                <div data-reveal className="font-mono text-[10px] uppercase tracking-[0.28em] text-ink-mute">
                  {p.numeralCaption}
                </div>
                <div
                  data-reveal
                  className="font-sans tabular text-ink tracking-[-0.06em] leading-[0.9]"
                  style={{ fontSize: "clamp(80px, 12vw, 240px)", fontWeight: 400 }}
                >
                  {p.numeral}
                </div>
                <div data-reveal className="flex items-center gap-2 font-mono text-[10px] uppercase tracking-[0.28em] text-ink-mute">
                  <span className="h-1.5 w-1.5 rounded-full bg-coral animate-pulse" />
                  Live
                </div>
              </div>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}
