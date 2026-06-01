

export type RaceEventFrame = {
  lap: number;
  kind: string;
  label: string;
  at?: string;
};

export type Telemetry = {
  speed: number;
  rpm: number;
  gear: number;
  throttle: number;
  brake: number;
  steering_angle: number;
  track_position: number;
  lap: number;
  fuel: number;
  tire_wear: number;
  timestamp: string;
  
  cur_lap_time?: number;
  last_lap_time?: number | null;
  sector_times?: number[];
  race_events?: RaceEventFrame[];
};

export type Competitor = {
  car_id: string;
  position: number;
  gap: number;
  pit_status: boolean;
  pace_delta: number;
  tire_wear: number;
};

export type StrategyRecommendation = {
  recommended_action: string;
  confidence: number;
  risk_level: "low" | "medium" | "high" | string;
  reason_codes: string[];
};

export type SimulationContext = {
  circuit?: string;
  lap?: number;
  total_laps?: number;
  position?: number;
  gap_s?: number;
  gap_ahead_s?: number;
  gap_behind_s?: number;
  tyre_age_laps?: number;
  compound?: string;
  pit_loss_s?: number;
  track_temp?: number;
  track_status?: string;
  stops_made?: number;
  compounds_used?: string;
};

export type SimulationRequest = {
  scenario_type: string;
  laps_until_action: number;
  context?: SimulationContext;
};

export type SimulationResult = {
  projected_position: number;
  projected_gap: number;
  projected_risk: "low" | "medium" | "high" | string;
};

export type Citation = {
  source: string;
  snippet: string;
};

export type RagResponse = {
  question: string;
  answer: string;
  citations?: Citation[];
  grounded?: boolean;
};

export type RaceEvent = {
  lap: number;
  kind: "start" | "tyre_warning" | "competitor_pit" | "ai_rec" | "sim" | "sc" | string;
  label: string;
  at?: string;
};
