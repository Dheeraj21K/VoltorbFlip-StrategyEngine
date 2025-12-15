import { useState } from "react";
import Tile from "./Tile";
import "../../styles/theme.css";
import "./Board.css";

import { analyzeBoard } from "../../api/solver";
import { useKeyboard } from "../../hooks/useKeyboard";

import type {
  TileState,
  AnalyzeRequest,
  LineConstraint,
} from "../../types";

const SIZE = 5;

/* ---------------- Helpers ---------------- */

function createEmptyBoard(): TileState[][] {
  return Array.from({ length: SIZE }, () =>
    Array.from({ length: SIZE }, () => ({
      value: null,
      revealed: false,
    }))
  );
}

function buildAnalyzeRequest(
  grid: TileState[][],
  rows: LineConstraint[],
  cols: LineConstraint[],
  mode: "level" | "profit"
): AnalyzeRequest {
  const revealed: AnalyzeRequest["revealed"] = [];

  for (let r = 0; r < SIZE; r++) {
    for (let c = 0; c < SIZE; c++) {
      const tile = grid[r][c];
      if (tile.revealed && tile.value !== null) {
        revealed.push({
          position: [r, c],
          value: tile.value,
        });
      }
    }
  }

  return { mode, rows, cols, revealed };
}

function validateConstraint(sum: number, voltorbs: number): string | null {
  if (voltorbs < 0 || voltorbs > 5) return "0-5 voltorbs";
  if (sum < 0) return "Sum ≥ 0";
  
  const minSum = 5 - voltorbs;
  const maxSum = (5 - voltorbs) * 3;
  
  if (sum < minSum) return `Min: ${minSum}`;
  if (sum > maxSum) return `Max: ${maxSum}`;
  
  return null;
}

/* ---------------- Component ---------------- */

export default function Board() {
  const [grid, setGrid] = useState<TileState[][]>(createEmptyBoard);
  const [cursor, setCursor] = useState({ row: 0, col: 0 });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Two solver policies
  const [mode, setMode] = useState<"level" | "profit">("level");

  const [quitRecommended, setQuitRecommended] = useState(false);
  const [solverExplanation, setSolverExplanation] = useState<string | null>(null);

  // Constraints
  const [rowConstraints, setRowConstraints] = useState<LineConstraint[]>(
    Array.from({ length: SIZE }, () => ({ sum: 0, voltorbs: 0 }))
  );
  const [colConstraints, setColConstraints] = useState<LineConstraint[]>(
    Array.from({ length: SIZE }, () => ({ sum: 0, voltorbs: 0 }))
  );

  /* ---------------- Constraint Handlers ---------------- */

  function updateConstraint(
    index: number,
    field: "sum" | "voltorbs",
    value: string,
    isRow: boolean
  ) {
    let num = Number(value);
    if (!Number.isFinite(num)) num = 0;

    if (field === "sum") num = Math.max(0, Math.min(15, num));
    if (field === "voltorbs") num = Math.max(0, Math.min(5, num));

    const setter = isRow ? setRowConstraints : setColConstraints;

    setter((prev) => {
      const next = [...prev];
      next[index] = { ...next[index], [field]: num };
      return next;
    });
    
    // Clear error when user makes changes
    setError(null);
  }

  /* ---------------- Tile Interaction (Click Cycle) ---------------- */

  function handleTileClick(r: number, c: number) {
    setCursor({ row: r, col: c });

    setGrid((prev) => {
      const next = prev.map((row) => row.map((t) => ({ ...t })));
      const current = next[r][c].value;

      let value: 0 | 1 | 2 | 3 | null = null;

      if (current === null) value = 1;
      else if (current === 1) value = 2;
      else if (current === 2) value = 3;
      else if (current === 3) value = 0;
      else value = null;

      next[r][c].value = value;
      next[r][c].revealed = value !== null;

      return next;
    });
    
    // Clear solver results when board changes
    setQuitRecommended(false);
    setSolverExplanation(null);
    setError(null);
  }

  /* ---------------- Keyboard Interaction ---------------- */

  useKeyboard((key) => {
    // Navigation
    if (key.startsWith("Arrow")) {
      setCursor((prev) => {
        let { row, col } = prev;
        if (key === "ArrowUp") row = Math.max(0, row - 1);
        if (key === "ArrowDown") row = Math.min(SIZE - 1, row + 1);
        if (key === "ArrowLeft") col = Math.max(0, col - 1);
        if (key === "ArrowRight") col = Math.min(SIZE - 1, col + 1);
        return { row, col };
      });
      return;
    }

    // Value entry
    if (["0", "1", "2", "3", "Backspace", "Delete"].includes(key)) {
      setGrid((prev) => {
        const next = prev.map((row) => row.map((t) => ({ ...t })));

        let value: 0 | 1 | 2 | 3 | null = null;
        if (key === "0") value = 0;
        else if (key === "1") value = 1;
        else if (key === "2") value = 2;
        else if (key === "3") value = 3;

        next[cursor.row][cursor.col].value = value;
        next[cursor.row][cursor.col].revealed = value !== null;

        return next;
      });
      
      // Clear solver results when board changes
      setQuitRecommended(false);
      setSolverExplanation(null);
      setError(null);
    }
  });

  /* ---------------- Validation ---------------- */
  
  function validateBoard(): string | null {
    // Check individual constraints
    for (let i = 0; i < SIZE; i++) {
      const rowError = validateConstraint(rowConstraints[i].sum, rowConstraints[i].voltorbs);
      if (rowError) return `Row ${i}: ${rowError}`;
      
      const colError = validateConstraint(colConstraints[i].sum, colConstraints[i].voltorbs);
      if (colError) return `Column ${i}: ${colError}`;
    }
    
    // Check global consistency
    const totalRowSum = rowConstraints.reduce((sum, r) => sum + r.sum, 0);
    const totalColSum = colConstraints.reduce((sum, c) => sum + c.sum, 0);
    
    if (totalRowSum !== totalColSum) {
      return `Row sums (${totalRowSum}) must equal column sums (${totalColSum})`;
    }
    
    const totalRowVoltorbs = rowConstraints.reduce((sum, r) => sum + r.voltorbs, 0);
    const totalColVoltorbs = colConstraints.reduce((sum, c) => sum + c.voltorbs, 0);
    
    if (totalRowVoltorbs !== totalColVoltorbs) {
      return `Row voltorbs (${totalRowVoltorbs}) must equal column voltorbs (${totalColVoltorbs})`;
    }
    
    return null;
  }

  /* ---------------- Solver ---------------- */

  async function runSolver() {
    try {
      setLoading(true);
      setError(null);
      setQuitRecommended(false);
      setSolverExplanation(null);
      
      // Frontend validation
      const validationError = validateBoard();
      if (validationError) {
        setError(validationError);
        return;
      }

      const payload = buildAnalyzeRequest(
        grid,
        rowConstraints,
        colConstraints,
        mode
      );

      const result = await analyzeBoard(payload);
      setQuitRecommended(result.quit_recommended);
      setSolverExplanation(result.explanation ?? null);
      const best = result.recommendations[0]?.position;

      setGrid((prev) =>
        prev.map((row, r) =>
          row.map((tile, c) => {
            const rec = result.recommendations.find(
              (x) => x.position[0] === r && x.position[1] === c
            );

            return {
              ...tile,
              guaranteedSafe: result.guaranteed_safe.some(
                ([rr, cc]) => rr === r && cc === c
              ),
              guaranteedVoltorb: result.guaranteed_voltorb.some(
                ([rr, cc]) => rr === r && cc === c
              ),
              pVoltorb: rec?.pVoltorb,
              bestMove: best
                ? best[0] === r && best[1] === c
                : false,
            };
          })
        )
      );
    } catch (e) {
      console.error("Solver error:", e);
      setError(e instanceof Error ? e.message : "Unknown error occurred");
    } finally {
      setLoading(false);
    }
  }
  
  /* ---------------- Reset ---------------- */
  
  function resetBoard() {
    setGrid(createEmptyBoard());
    setRowConstraints(Array.from({ length: SIZE }, () => ({ sum: 0, voltorbs: 0 })));
    setColConstraints(Array.from({ length: SIZE }, () => ({ sum: 0, voltorbs: 0 })));
    setQuitRecommended(false);
    setSolverExplanation(null);
    setError(null);
  }

  /* ---------------- Render ---------------- */

  return (
    <div className="board-wrapper">
      <div className="board-main-area">
        {/* Grid */}
        <div className="board-grid">
          {grid.map((row, r) =>
            row.map((tile, c) => (
              <Tile
                key={`${r}-${c}`}
                tile={tile}
                isActive={cursor.row === r && cursor.col === c}
                onClick={() => handleTileClick(r, c)}
              />
            ))
          )}
        </div>

        {/* Row constraints */}
        <div className="constraints-row">
          {rowConstraints.map((rc, i) => (
            <div key={i} className="constraint-card">
              <input
                className="c-input input-sum"
                type="number"
                min="0"
                max="15"
                value={rc.sum || ""}
                onChange={(e) =>
                  updateConstraint(i, "sum", e.target.value, true)
                }
                placeholder="Sum"
              />
              <div className="input-group">
                <span>💣</span>
                <input
                  className="c-input input-bomb"
                  type="number"
                  min="0"
                  max="5"
                  value={rc.voltorbs || ""}
                  onChange={(e) =>
                    updateConstraint(i, "voltorbs", e.target.value, true)
                  }
                  placeholder="0"
                />
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Column constraints */}
      <div className="constraints-col">
        {colConstraints.map((cc, i) => (
          <div key={i} className="constraint-card">
            <input
              className="c-input input-sum"
              type="number"
              min="0"
              max="15"
              value={cc.sum || ""}
              onChange={(e) =>
                updateConstraint(i, "sum", e.target.value, false)
              }
              placeholder="Sum"
            />
            <div className="input-group">
              <span>💣</span>
              <input
                className="c-input input-bomb"
                type="number"
                min="0"
                max="5"
                value={cc.voltorbs || ""}
                onChange={(e) =>
                  updateConstraint(i, "voltorbs", e.target.value, false)
                }
                placeholder="0"
              />
            </div>
          </div>
        ))}
      </div>

      {/* Mode Toggle */}
      <div className="mode-toggle">
        <button
          className={mode === "level" ? "active" : ""}
          onClick={() => setMode("level")}
          disabled={loading}
        >
          🛡 Level
        </button>

        <button
          className={mode === "profit" ? "active" : ""}
          onClick={() => setMode("profit")}
          disabled={loading}
        >
          💰 Profit
        </button>
      </div>

      {/* Mode Explanation */}
      <div className="mode-explanation">
        {mode === "level" 
          ? "🛡 Level Mode: Prioritizes survival to retain your current level. Recommends safest moves and warns when risk is too high."
          : "💰 Profit Mode: Prioritizes expected value to maximize coins. Accepts higher risk for better rewards."}
      </div>

      {/* Error Display */}
      {error && (
        <div className="error-banner">
          <strong>⚠️ Error</strong>
          <pre>{error}</pre>
        </div>
      )}

      {/* Quit Recommendation (inline, non-blocking) */}
      {quitRecommended && !error && (
        <div className="quit-banner">
          <strong>⚠️ Consider quitting</strong>
          <p>
            {mode === "level"
              ? "Continuing now has a low survival probability. Quitting helps preserve your current level."
              : "Risk outweighs expected value. Quitting may be optimal at this point."}
          </p>
        </div>
      )}

      {/* Optional solver explanation */}
      {solverExplanation && !error && (
        <div className="solver-explanation">
          {solverExplanation}
        </div>
      )}

      {/* Action bar */}
      <div className="action-bar">
        <button className="btn-analyze" onClick={runSolver} disabled={loading}>
          {loading ? "Calculating…" : "ANALYZE BOARD"}
        </button>
        <button className="btn-reset" onClick={resetBoard} disabled={loading}>
          RESET
        </button>
      </div>
    </div>
  );
}