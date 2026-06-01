import type {
  Competitor,
  RagResponse,
  SimulationRequest,
  SimulationResult,
  StrategyRecommendation,
  Telemetry,
} from "./types";

const BASE =
  process.env.NEXT_PUBLIC_BACKEND_URL?.replace(/\/$/, "") ||
  "http://127.0.0.1:8000";

async function safeJson<T>(p: Promise<Response>): Promise<T | null> {
  try {
    const r = await p;
    if (!r.ok) return null;
    return (await r.json()) as T;
  } catch {
    return null;
  }
}

export async function apiJson<T>(p: Promise<Response>): Promise<T> {
  const r = await p;
  if (!r.ok) throw new Error(`HTTP ${r.status}`);
  return (await r.json()) as T;
}


export type RaceStateInput = {
  circuit?: string;
  compound?: string;
  tyre_life?: number;
  laps_remaining?: number;
  total_laps?: number;
  position?: number;
  gap_ahead_s?: number;
  gap_behind_s?: number;
  pit_loss_s?: number;
  track_temp?: number;
  track_status?: string;
  compounds_used?: string;
  stops_made?: number;
  deg_rate?: number | null;
  competitors?: { position: number; compound: string; tyre_life: number }[] | null;
};

export type FullRecommendation = {
  recommended_action: string;
  confidence: number;
  risk_level: "low" | "medium" | "high" | string;
  reason_codes: string[];
  explanation: string;
};

export type DemoStartRequest = {
  mode?: "mock" | "replay";
  circuit?: string;
  year?: number;
  driver?: string;
  tick_seconds?: number;
};

export const api = {
  base: BASE,
  wsUrl: BASE.replace(/^http/, "ws") + "/ws/live",

  health: () => safeJson<{ healthy: boolean; service: string }>(fetch(`${BASE}/health/`)),
  mockTelemetry: () => safeJson<Telemetry>(fetch(`${BASE}/api/mock/telemetry`)),
  telemetry: () => safeJson<Telemetry>(fetch(`${BASE}/api/telemetry/`)),
  competitors: () => safeJson<Competitor[]>(fetch(`${BASE}/api/competitors/`)),

  recommend: () =>
    safeJson<StrategyRecommendation>(
      fetch(`${BASE}/api/strategy/recommend`, { method: "POST" })
    ),

  
  
  recommendFull: (state: RaceStateInput) =>
    safeJson<FullRecommendation>(
      fetch(`${BASE}/api/v1/recommend`, {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify(state),
      })
    ),

  sampleState: () => safeJson<RaceStateInput>(fetch(`${BASE}/api/v1/sample-state`)),

  simulate: (body: SimulationRequest) =>
    safeJson<SimulationResult>(
      fetch(`${BASE}/api/simulate/`, {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify(body),
      })
    ),
  simulateStrict: (body: SimulationRequest) =>
    apiJson<SimulationResult>(
      fetch(`${BASE}/api/simulate/`, {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify(body),
      })
    ),

  explain: () =>
    safeJson<{ explanation: string }>(
      fetch(`${BASE}/api/explain/`, { method: "POST" })
    ),
  explainStrict: () =>
    apiJson<{ explanation: string }>(
      fetch(`${BASE}/api/explain/`, { method: "POST" })
    ),

  rag: (question: string) =>
    safeJson<RagResponse>(
      fetch(`${BASE}/api/rag/query`, {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ question }),
      })
    ),
  ragStrict: (question: string) =>
    apiJson<RagResponse>(
      fetch(`${BASE}/api/rag/query`, {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ question }),
      })
    ),

  demoStart: () =>
    safeJson<{ status: string }>(
      fetch(`${BASE}/api/demo/start`, { method: "POST" })
    ),

  demoStop: () =>
    safeJson<{ status: string }>(fetch(`${BASE}/api/demo/stop`, { method: "POST" })),

  
  disasters: () =>
    safeJson<any[]>(fetch(`${BASE}/api/v1/disasters`)),
  backtests: () =>
    safeJson<Record<string, any[]>>(fetch(`${BASE}/api/v1/backtests`)),
  backtestYear: (year: string) =>
    safeJson<any[]>(fetch(`${BASE}/api/v1/backtests/${year}`)),
  ferrariResults: () =>
    safeJson<any>(fetch(`${BASE}/api/v1/ferrari-results`)),
  flows: () =>
    safeJson<any[]>(fetch(`${BASE}/api/orchestration/flows`)),
  scenarios: (context: import("./types").SimulationContext) =>
    safeJson<{
      decision: string;
      projected_position: number;
      projected_total_time: number;
      avg_pace: number;
      points: { lap_offset: number; gap_s: number }[];
      net_gain_s: number;
    }[]>(
      fetch(`${BASE}/api/v1/scenarios`, {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ context }),
      })
    ),

  
  torcsStart: (body: { mode?: "simulated" | "live"; total_laps?: number } = {}) =>
    safeJson<{ status: string; mode: string }>(
      fetch(`${BASE}/api/torcs/start`, {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify(body),
      })
    ),
  torcsStop: () =>
    safeJson<{ status: string }>(fetch(`${BASE}/api/torcs/stop`, { method: "POST" })),
};
