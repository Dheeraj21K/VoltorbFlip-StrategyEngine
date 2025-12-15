export type Position = [number, number];

export interface TileState {
  value: 0 | 1 | 2 | 3 | null;
  revealed: boolean;

  // Solver overlays (UI only)
  guaranteedSafe?: boolean;
  guaranteedVoltorb?: boolean;
  pVoltorb?: number;
  bestMove?: boolean;
}

export interface LineConstraint {
  sum: number;
  voltorbs: number;
}

export interface AnalyzeRequest {
  mode: "level" | "profit";
  rows: LineConstraint[];
  cols: LineConstraint[];
  revealed: { position: Position; value: number }[];
}

export interface Recommendation {
  position: Position;
  pVoltorb: number;
  expectedValue: number;
  riskTier: string;
}

export interface AnalyzeResponse {
  guaranteed_safe: Position[];
  guaranteed_voltorb: Position[];
  recommendations: Recommendation[];
  quit_recommended: boolean;
  explanation: string;
  mode: "level" | "profit";
}
