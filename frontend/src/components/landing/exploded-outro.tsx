"use client";
import Link from "next/link";
import { ArrowUpRight } from "lucide-react";

export function ExplodedOutro() {
  return (
    <section
      id="exploded-outro"
      className="relative min-h-[320vh] w-full transition-colors duration-300"
      style={{
        background:
          "linear-gradient(180deg, #F0EEE6 0%, #F6F4ED 25%, #FBFAF6 55%, #FFFFFF 85%, #FFFFFF 100%)",
      }}
    >
      <div className="sticky top-0 h-screen w-full overflow-hidden">
        <div className="relative z-10 flex h-full flex-col items-center justify-between px-[6vw] py-20 text-black">
          <div className="text-center max-w-4xl">
            <div className="flex items-center justify-center gap-3 font-mono text-[10px] uppercase tracking-[0.32em] text-black/50">
              <span>04 / 04</span>
              <span className="h-px w-8 bg-black/20" />
              <span>The whole pit wall, in pieces</span>
            </div>
            <h2
              className="mt-7 font-sans tracking-[-0.04em] leading-[0.9]"
              style={{ fontSize: "clamp(56px, 9vw, 168px)", fontWeight: 500 }}
            >
              Every part is<br />
              <span className="text-coral">a backend service.</span>
            </h2>
          </div>

          <div className="flex flex-col items-center gap-6 pb-8">
            <p className="max-w-xl text-center text-base md:text-lg text-black/55">
              Pulled apart, it's just APIs. Put it back together, it's a race
              engineer that explains every call.
            </p>
            <div className="flex flex-wrap items-center justify-center gap-4">
              <Link href="/dashboard" className="btn-coral">
                Open Dashboard
                <span className="btn-coral-icon">
                  <ArrowUpRight className="h-4 w-4 stroke-[1.6]" />
                </span>
              </Link>
              <Link
                href="/fia"
                className="inline-flex items-center gap-2 rounded-full px-5 py-2 ring-1 ring-black/15 bg-black/[0.03] text-black transition-all duration-500 ease-spring hover:bg-black/[0.06] active:scale-[0.98]"
              >
                Ask the rulebook
              </Link>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
