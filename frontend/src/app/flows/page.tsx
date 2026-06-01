"use client";
import { useEffect, useState } from "react";
import { Bezel, Eyebrow } from "@/components/bezel";
import { api } from "@/lib/api";
import { cn } from "@/lib/utils";
import { ArrowRight } from "lucide-react";

type Flow = {
  id: string;
  name: string;
  description: string;
  steps: string[];
  langflow_enabled: boolean;
  endpoint: string;
};

export default function FlowsPage() {
  const [flows, setFlows] = useState<Flow[] | null>(null);
  const [running, setRunning] = useState<string | null>(null);
  const [output, setOutput] = useState<Record<string, any>>({});

  useEffect(() => {
    api.flows().then((d) => setFlows((d ?? []) as Flow[]));
  }, []);

  const runFlow = async (flow: Flow) => {
    setRunning(flow.id);
    let res: any = null;
    if (flow.id === "fia_workflow") {
      res = await api.rag("Can drivers pit during a safety car deployment");
    } else if (flow.id === "explainability_workflow") {
      
      
      await api.recommend();
      res = await api.explain();
    }
    setOutput((o) => ({ ...o, [flow.id]: res }));
    setRunning(null);
  };

  return (
    <main className="px-[6vw] pt-32 pb-40 space-y-12">
      <header className="grid grid-cols-12 gap-10 items-end">
        <div className="col-span-12 lg:col-span-8">
          <Eyebrow>05 - Orchestration</Eyebrow>
          <h1
            className="mt-7 font-sans tracking-[-0.04em] text-ink leading-[0.9]"
            style={{ fontSize: "clamp(56px, 7vw, 128px)", fontWeight: 500 }}
          >
            Workflows.<br />
            <span className="text-coral">LangFlow-ready.</span>
          </h1>
        </div>
        <div className="col-span-12 lg:col-span-4">
          <p className="text-base lg:text-lg text-ink-dim leading-relaxed">
            Each pipeline runs in-process for low latency and can drop into a
            LangFlow server one env var away. Click <em>Run</em> to fire the
            live endpoint and inspect the result.
          </p>
        </div>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {flows?.map((f) => (
          <Bezel key={f.id} innerClassName="p-7 h-full flex flex-col">
            <div className="flex items-center justify-between mb-3">
              <Eyebrow>{f.id}</Eyebrow>
              <span className={cn(
                "rounded-full px-2 py-0.5 text-[10px] uppercase tracking-[0.18em] ring-1",
                f.langflow_enabled
                  ? "bg-signal-ok/15 text-signal-ok ring-signal-ok/30"
                  : "bg-white/[0.04] text-ink-mute ring-white/[0.08]"
              )}>
                {f.langflow_enabled ? "LangFlow live" : "in-process"}
              </span>
            </div>
            <h3 className="font-sans text-2xl tracking-tight text-ink mb-2" style={{ fontWeight: 500 }}>
              {f.name}
            </h3>
            <p className="text-sm text-ink-dim leading-relaxed">{f.description}</p>

            <div className="mt-6 flex flex-wrap items-center gap-2">
              {f.steps.map((s, i) => (
                <span key={i} className="flex items-center gap-2">
                  <span className="rounded-bezel-sm bg-white/[0.04] px-2.5 py-1 text-[10px] uppercase tracking-[0.18em] text-ink-dim ring-1 ring-white/[0.05]">
                    {s}
                  </span>
                  {i < f.steps.length - 1 && (
                    <ArrowRight className="h-3 w-3 text-ink-mute" />
                  )}
                </span>
              ))}
            </div>

            <div className="mt-6 flex items-center justify-between font-mono text-[10px] uppercase tracking-[0.22em] text-ink-mute">
              <span>endpoint</span>
              <code className="text-coral">{f.endpoint}</code>
            </div>

            <div className="mt-auto pt-6">
              <button
                onClick={() => runFlow(f)}
                disabled={running === f.id}
                className="btn-ghost w-full justify-between disabled:opacity-50"
              >
                <span>{running === f.id ? "Running..." : "Run flow"}</span>
                <span className="font-mono text-[10px] tracking-[0.28em] text-ink-mute">EXEC ↗</span>
              </button>
              {output[f.id] && (
                <pre className="mt-4 font-mono text-[10px] leading-relaxed text-ink-dim whitespace-pre-wrap break-words max-h-48 overflow-auto">
                  {JSON.stringify(output[f.id], null, 2)}
                </pre>
              )}
            </div>
          </Bezel>
        ))}
        {flows && flows.length === 0 && (
          <div className="col-span-2 text-center text-ink-mute font-mono text-sm">
            /api/orchestration/flows returned no workflows.
          </div>
        )}
      </div>
    </main>
  );
}
