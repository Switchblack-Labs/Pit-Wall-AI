"use client";
import { useEffect, useRef } from "react";





export function Lockup() {
  const ref = useRef<HTMLDivElement>(null);
  useEffect(() => {
    const els = ref.current?.querySelectorAll<HTMLElement>("[data-line]");
    els?.forEach((el, i) => {
      el.style.opacity = "0";
      el.style.transform = "translateY(40px)";
      el.style.filter = "blur(8px)";
      requestAnimationFrame(() => {
        el.style.transition = `opacity 900ms cubic-bezier(0.22,1,0.36,1) ${i * 110}ms, transform 1000ms cubic-bezier(0.22,1,0.36,1) ${i * 110}ms, filter 800ms ease ${i * 110}ms`;
        el.style.opacity = "1";
        el.style.transform = "translateY(0)";
        el.style.filter = "blur(0)";
      });
    });
  }, []);
  return (
    <div ref={ref} className="select-none">
      <h1
        data-line
        className="font-sans font-medium text-ink leading-[0.92] tracking-[-0.035em]"
        style={{ fontSize: "clamp(56px, 9vw, 168px)" }}
      >
        The pit wall,<br />
        <span className="text-coral">rebuilt for AI.</span>
      </h1>
    </div>
  );
}
