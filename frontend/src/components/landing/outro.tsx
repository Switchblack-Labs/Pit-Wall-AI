"use client";
import Link from "next/link";
import { ArrowUpRight } from "lucide-react";
import { Eyebrow } from "@/components/bezel";
import { Marquee } from "@/components/marquee";

export function Outro() {
  return (
    <section className="relative px-[6vw] py-32 lg:py-40">
      <div className="mx-auto max-w-7xl">
        <Eyebrow>Final lap</Eyebrow>
        <h2 className="display-serif text-hero text-ink mt-6">
          The chequered flag<br />
          is just <span className="text-coral">the start</span>.
        </h2>
        <p className="mt-10 max-w-2xl text-lg text-ink-dim leading-relaxed">
          Open the live dashboard or ask the regulations assistant a question.
          Demo mode runs a full race in 90 seconds. No simulator required.
        </p>

        <div className="mt-14 flex flex-wrap gap-4">
          <Link href="/dashboard" className="btn-coral">
            Open Dashboard
            <span className="btn-coral-icon">
              <ArrowUpRight className="h-4 w-4 stroke-[1.6]" />
            </span>
          </Link>
          <Link href="/simulator" className="btn-ghost">
            Try the Strategy Simulator
          </Link>
          <Link href="/fia" className="btn-ghost">
            Ask the rulebook
          </Link>
        </div>
      </div>

      <div className="mt-32">
        <Marquee
          items={[
            "FastAPI - WebSockets - IBM Granite",
            "RAG - ChromaDB - Docling",
            "Counterfactual simulation engine",
            "FIA 2026 Sporting & Technical regulations",
            "Built in 72 hours - IBM Hackathon 2026",
          ]}
          speed={45}
        />
      </div>

      <div className="mt-24 flex items-center justify-between text-[10px] uppercase tracking-[0.28em] text-ink-mute">
        <span>(c) 2026 PitWall AI</span>
        <span>v0.1 - Hackathon build</span>
      </div>
    </section>
  );
}
