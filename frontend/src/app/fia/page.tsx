"use client";
import { useState } from "react";
import { Bezel, Eyebrow } from "@/components/bezel";
import { api } from "@/lib/api";
import { cn } from "@/lib/utils";
import { ArrowUpRight } from "lucide-react";

const SUGGESTED = [
  "Can we pit under safety car?",
  "What's the minimum tyre compound usage rule for a dry race?",
  "When is DRS enabled?",
  "Penalty for a false start?",
];

type Turn = {
  q: string;
  a: string;
  cite: { section: string; quote: string }[];
};

export default function FiaPage() {
  const [q, setQ] = useState("");
  const [turns, setTurns] = useState<Turn[]>([]);
  const [busy, setBusy] = useState(false);

  const ask = async (question: string) => {
    if (!question.trim()) return;
    setBusy(true);
    const res = await api.rag(question);
    if (!res) {
      setBusy(false);
      return;
    }
    const cite = (res.citations ?? []).slice(0, 4).map((c) => ({
      section: c.source,
      quote: c.snippet,
    }));
    setTurns((t) => [{ q: question, a: res.answer, cite }, ...t]);
    setQ("");
    setBusy(false);
  };

  return (
    <main className="px-[6vw] pt-32 pb-40">
      <div className="mx-auto max-w-4xl">
        <div className="text-center">
          <Eyebrow>FIA 2026 - RAG</Eyebrow>
          <h1 className="display-serif text-hero text-ink mt-6 leading-[0.92]">
            Ask the<br /><span className="text-coral">rulebook</span>.
          </h1>
          <p className="mt-8 text-lg text-ink-dim max-w-xl mx-auto">
            Retrieval over the 2026 Sporting and Technical regulations.
            Powered by Docling + ChromaDB + Granite, cited line by line.
          </p>
        </div>

        {}
        <div className="mt-14 bezel-shell">
          <div className="bezel-core p-2 flex items-center gap-2">
            <input
              value={q}
              onChange={(e) => setQ(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && ask(q)}
              placeholder="e.g. Can we pit under safety car?"
              className="flex-1 bg-transparent px-5 py-4 text-lg text-ink placeholder:text-ink-mute focus:outline-none"
            />
            <button
              onClick={() => ask(q)}
              disabled={busy || !q.trim()}
              className="btn-coral disabled:opacity-50"
            >
              <span>{busy ? "Searching..." : "Ask"}</span>
              <span className="btn-coral-icon">
                <ArrowUpRight className="h-4 w-4 stroke-[1.6]" />
              </span>
            </button>
          </div>
        </div>

        {}
        {turns.length === 0 && (
          <div className="mt-6 flex flex-wrap gap-2 justify-center">
            {SUGGESTED.map((s) => (
              <button
                key={s}
                onClick={() => ask(s)}
                className="liquid-pill px-4 py-2 text-sm text-ink-dim hover:text-ink transition-all duration-300 ease-spring"
              >
                {s}
              </button>
            ))}
          </div>
        )}

        {}
        <div className="mt-16 space-y-10">
          {turns.map((t, idx) => (
            <article key={idx} className="space-y-5">
              <div className="font-mono text-[10px] uppercase tracking-[0.28em] text-ink-mute">
                Q - {String(turns.length - idx).padStart(2, "0")}
              </div>
              <h2 className="display-serif text-3xl lg:text-4xl text-ink leading-tight">
                {t.q}
              </h2>

              <Bezel innerClassName="p-7">
                <div className="flex items-center justify-between mb-4">
                  <Eyebrow>Granite - Explanation</Eyebrow>
                  <span className="font-mono text-[10px] uppercase tracking-[0.28em] text-ink-mute">cited</span>
                </div>
                <p className="text-base lg:text-lg leading-relaxed text-ink">
                  {t.a}
                </p>
              </Bezel>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {t.cite.map((c) => (
                  <div key={c.section} className={cn("bezel-shell")}>
                    <div className="bezel-core p-6">
                      <div className="flex items-center justify-between mb-3">
                        <span className="font-mono text-[10px] uppercase tracking-[0.28em] text-coral-hi">
                          {c.section}
                        </span>
                        <ArrowUpRight className="h-4 w-4 text-ink-mute" />
                      </div>
                      <blockquote className="text-sm text-ink-dim leading-relaxed border-l-2 border-coral pl-4">
                        “{c.quote}”
                      </blockquote>
                    </div>
                  </div>
                ))}
              </div>
            </article>
          ))}
        </div>
      </div>
    </main>
  );
}
