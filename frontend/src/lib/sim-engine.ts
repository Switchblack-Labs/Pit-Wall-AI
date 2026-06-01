







import type { Circuit } from "./circuits";

export type ScenarioId = "pit_now" | "stay_out" | "undercut" | "overcut" | "safety_car";

export type ScenarioProjection = {
  id: ScenarioId;
  label: string;
  color: string;
  points: { lap_offset: number; gap_s: number }[];
  net_gain_s: number;          
  projected_position: number;
  risk: "low" | "medium" | "high";
  confidence: number;          
  notes: string[];
};

type Inputs = {
  circuit: Circuit;
  currentLap: number;
  basePosition: number;        
  baseGap: number;             
  tyreAgeLaps: number;
  compound: "S" | "M" | "H";
};

const COMPOUND_DELTA: Record<"S" | "M" | "H", number> = {
  S: -0.6,   
  M: 0.0,
  H: +0.35,  
};

const COMPOUND_DEG: Record<"S" | "M" | "H", number> = {
  S: 0.085,
  M: 0.055,
  H: 0.038,
};

export function projectScenarios(input: Inputs): ScenarioProjection[] {
  const { circuit, basePosition, baseGap, tyreAgeLaps, compound } = input;
  const pitLoss = circuit.pit_loss_s;
  const lapRef = circuit.reference_lap_s;
  const degCur = COMPOUND_DEG[compound];
  const deltaCur = COMPOUND_DELTA[compound];

  
  const curve = (perLapDelta: (l: number) => number, start = baseGap) => {
    const pts: { lap_offset: number; gap_s: number }[] = [];
    let g = start;
    pts.push({ lap_offset: 0, gap_s: +g.toFixed(2) });
    for (let l = 1; l <= 10; l++) {
      g += perLapDelta(l);
      pts.push({ lap_offset: l, gap_s: +g.toFixed(2) });
    }
    return pts;
  };

  
  const pitNowPts = curve((l) => {
    if (l === 1) return -pitLoss;        
    const ageGain = (tyreAgeLaps + 6) * degCur - (l - 1) * COMPOUND_DEG.M; 
    return +ageGain.toFixed(3) - 0.08;   
  }, baseGap);

  
  const stayOutPts = curve((l) => {
    const wear = (tyreAgeLaps + l) * degCur * 0.45;
    return -0.18 - wear * 0.05;          
  }, baseGap);

  
  const undercutPts = curve((l) => {
    if (l === 1) return -0.15;           
    if (l === 2) return -pitLoss;        
    const ageGain = (tyreAgeLaps + 6) * degCur - (l - 2) * COMPOUND_DEG.M;
    return +ageGain.toFixed(3) - 0.05;
  }, baseGap);

  
  const overcutPts = curve((l) => {
    if (l <= 3) return -0.22 - (tyreAgeLaps + l) * degCur * 0.04;
    if (l === 4) return -pitLoss;
    const ageGain = (tyreAgeLaps + 9) * degCur - (l - 4) * COMPOUND_DEG.H;
    return +ageGain.toFixed(3) - 0.02;
  }, baseGap);

  
  const scPts = curve((l) => {
    if (l === 1) return -9.0;            
    const ageGain = (tyreAgeLaps + 6) * degCur - (l - 1) * COMPOUND_DEG.M;
    return +ageGain.toFixed(3) - 0.04;
  }, baseGap);

  const summarize = (
    id: ScenarioId,
    label: string,
    color: string,
    pts: { lap_offset: number; gap_s: number }[],
    risk: "low" | "medium" | "high",
    confidence: number,
    notes: string[]
  ): ScenarioProjection => {
    const final = pts[pts.length - 1].gap_s;
    const net_gain_s = +(final - baseGap).toFixed(1);
    
    const projected_position = Math.max(1, Math.round(basePosition - net_gain_s / 4));
    return { id, label, color, points: pts, net_gain_s, projected_position, risk, confidence, notes };
  };

  return [
    summarize("pit_now",   "Pit now",         "#E26C45", pitNowPts,   "medium", 0.71,
      ["Take pit loss this lap", "Fresh tyres vs leader (older rubber)", `Pit loss: ${pitLoss.toFixed(1)}s`]),
    summarize("stay_out",  "Stay out",        "#7AB7C7", stayOutPts,  "high",   0.62,
      ["No pit loss", `Tyre age: ${tyreAgeLaps + 1} laps`, "Pace bleed to fresh-tyre cars"]),
    summarize("undercut",  "Undercut +1 lap", "#F2EBE0", undercutPts, "medium", 0.66,
      ["Pit next lap, gain by being fresher", "Risk: traffic on rejoin", "One more lap on old rubber"]),
    summarize("overcut",   "Overcut +3 laps", "#E2A33B", overcutPts,  "medium", 0.58,
      ["Hold for 3 laps", "Pit on Hard for stretch", "Banking on rivals over-deg"]),
    summarize("safety_car","Pit under SC",    "#5FB079", scPts,       "low",    0.85,
      ["Pit loss roughly halved under SC", "Field bunched on restart", "Only viable if SC is out"]),
  ];
}


export function recommend(scenarios: ScenarioProjection[]): ScenarioId {
  
  const riskWeight = { low: 0.85, medium: 1.0, high: 1.25 };
  let best = scenarios[0];
  let bestScore = -Infinity;
  for (const s of scenarios) {
    const score = -s.net_gain_s * riskWeight[s.risk] * s.confidence;
    if (score > bestScore) { bestScore = score; best = s; }
  }
  return best.id;
}
