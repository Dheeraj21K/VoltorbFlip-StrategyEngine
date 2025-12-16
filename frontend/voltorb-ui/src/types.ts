export type Position = [number, number];

export interface TileState {
  value: 0 | 1 | 2 | 3 | null;
  revealed: boolean;

  // Solver overlays (UI only)
  guaranteedSafe?: boolean;
  guaranteedVoltorb?: boolean;
  pVoltorb?: number;
  bestMove?: boolean;
  // Full probability distribution for shadows {0: 0.1, 1: 0.5...}
  distribution?: Record<number, number>;
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
  distribution: Record<number, number>;
}

export interface ForcedTile {
  row: number;
  col: number;
  value: number;
}

export interface AnalyzeResponse {
  guaranteed_safe: Position[];
  guaranteed_voltorb: Position[];
  recommendations: Recommendation[];
  forced_values: ForcedTile[];
  quit_recommended: boolean;
  explanation: string;
  mode: "level" | "profit";
  // NEW: Game State for Win/Loss detection
  game_state: "active" | "won" | "lost";
}