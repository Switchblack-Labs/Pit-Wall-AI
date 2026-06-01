import { Bezel, Eyebrow } from "@/components/bezel";

const STACK = [
  { kind: "Backend", items: ["FastAPI", "Pydantic", "WebSockets", "Docker"] },
  { kind: "AI", items: ["IBM Granite", "Groq", "Docling", "ChromaDB"] },
  { kind: "Data", items: ["FIA 2026 Sporting", "FIA 2026 Technical", "Telemetry adapters", "Mock generator"] },
  { kind: "Frontend", items: ["Next.js", "React", "GSAP + Lenis", "Tailwind"] },
];

const TEAM = [
  "Mayank",
  "Ghoda",
  "Sparsh",
  "Aaryan",
  "Devansh",
];

export default function AboutPage() {
  return (
    <main className="px-[6vw] pt-32 pb-40">
      <header className="max-w-4xl">
        <Eyebrow>Architecture - About</Eyebrow>
        <h1 className="display-serif text-hero text-ink mt-6 leading-[0.92]">
          One car.<br /><span className="text-coral">Six brains.</span>
        </h1>
        <p className="mt-10 max-w-2xl text-lg text-ink-dim leading-relaxed">
          PitWall AI is a real-time, explainable race engineering platform.
          Telemetry streams over WebSocket, a decision engine ranks strategies,
          a counterfactual simulator branches the race, IBM Granite explains
          every call, and a RAG pipeline grounds answers in the FIA 2026
          regulations. Built for the IBM Skills Build Hackathon for May 2026.
        </p>
      </header>

      {}
      <section className="mt-20">
        <Eyebrow>System</Eyebrow>
        <div className="mt-6 bezel-shell">
          <div className="bezel-core p-8">
            <ArchitectureDiagram />
          </div>
        </div>
      </section>

      {}
      <section className="mt-24">
        <Eyebrow>Stack</Eyebrow>
        <div className="mt-8 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
          {STACK.map((s) => (
            <Bezel key={s.kind} innerClassName="p-6">
              <div className="font-mono text-[10px] uppercase tracking-[0.28em] text-coral-hi">
                {s.kind}
              </div>
              <ul className="mt-4 space-y-2">
                {s.items.map((i) => (
                  <li key={i} className="text-ink text-base">{i}</li>
                ))}
              </ul>
            </Bezel>
          ))}
        </div>
      </section>

      {}
      <section className="mt-24">
        <Eyebrow>Team</Eyebrow>
        <div className="mt-8 grid grid-cols-2 md:grid-cols-5 gap-5">
          {TEAM.map((name) => (
            <Bezel key={name} innerClassName="p-6 text-center">
              <div className="font-sans text-2xl font-medium tracking-tight text-ink">{name}</div>
            </Bezel>
          ))}
        </div>
      </section>
    </main>
  );
}

function ArchitectureDiagram() {
  
  
  const Node = (x: number, y: number, w: number, h: number, title: string, sub: string, accent = false) => (
    <g key={title} transform={`translate(${x}, ${y})`}>
      <rect
        width={w} height={h} rx={14}
        fill={accent ? "rgba(226,108,69,0.10)" : "rgba(255,255,255,0.025)"}
        stroke={accent ? "rgba(226,108,69,0.5)" : "rgba(242,235,224,0.12)"}
      />
      <text x={16} y={26} fill="#F2EBE0" fontSize="13" fontFamily="ui-sans-serif">
        {title}
      </text>
      <text x={16} y={46} fill="#BDB3A4" fontSize="10" letterSpacing="2" fontFamily="ui-monospace">
        {sub.toUpperCase()}
      </text>
    </g>
  );
  const Line = (x1: number, y1: number, x2: number, y2: number, dashed = false) => (
    <path
      d={`M${x1} ${y1} L${x2} ${y2}`}
      stroke="rgba(242,235,224,0.18)"
      strokeWidth="1"
      strokeDasharray={dashed ? "3 5" : undefined}
      fill="none"
    />
  );

  return (
    <svg viewBox="0 0 1100 460" className="w-full h-auto">
      {}
      {Node(20, 30, 200, 70, "OpenF1 API", "live + historical f1 data")}
      {Node(240, 30, 200, 70, "Demo generator", "mock telemetry")}
      {Node(460, 30, 200, 70, "FIA 2026 PDFs", "rulebook")}

      {}
      {Node(20, 160, 420, 80, "FastAPI - Race state", "ingest - websockets - state")}
      {Node(460, 160, 200, 80, "Chroma", "rag pipeline")}
      {Node(680, 160, 200, 80, "Strategy + Sim engine", "decision engine", true)}
      {Node(900, 160, 180, 80, "IBM Granite", "explanation", true)}

      {}
      {Node(20, 320, 200, 80, "Dashboard", "live telemetry UI")}
      {Node(240, 320, 200, 80, "Simulator", "counterfactual")}
      {Node(460, 320, 200, 80, "FIA Assistant", "rag chat")}
      {Node(680, 320, 200, 80, "Landing - 3D", "scroll narrative")}
      {Node(900, 320, 180, 80, "Demo Director", "live controls")}

      {}
      {Line(120, 100, 120, 160)}
      {Line(340, 100, 230, 160)}
      {Line(560, 100, 560, 160)}
      {Line(230, 240, 120, 320)}
      {Line(230, 240, 340, 320, true)}
      {Line(560, 240, 560, 320)}
      {Line(780, 240, 780, 320, true)}
      {Line(990, 240, 990, 320)}
      {Line(880, 200, 900, 200, true)}
    </svg>
  );
}
