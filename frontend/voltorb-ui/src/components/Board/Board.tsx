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

/* ---------------- Component ---------------- */

export default function Board() {
  const [grid, setGrid] = useState<TileState[][]>(createEmptyBoard);
  const [cursor, setCursor] = useState({ row: 0, col: 0 });
  const [loading, setLoading] = useState(false);

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
    }
  });

  /* ---------------- Solver ---------------- */

  async function runSolver() {
    try {
      setLoading(true);
      setQuitRecommended(false);
      setSolverExplanation(null);

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
      console.error(e);
      alert("Solver error: check constraints.");
    } finally {
      setLoading(false);
    }
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
                value={rc.sum || ""}
                onChange={(e) =>
                  updateConstraint(i, "sum", e.target.value, true)
                }
              />
              <div className="input-group">
                <span>💣</span>
                <input
                  className="c-input input-bomb"
                  value={rc.voltorbs || ""}
                  onChange={(e) =>
                    updateConstraint(i, "voltorbs", e.target.value, true)
                  }
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
              value={cc.sum || ""}
              onChange={(e) =>
                updateConstraint(i, "sum", e.target.value, false)
              }
            />
            <div className="input-group">
              <span>💣</span>
              <input
                className="c-input input-bomb"
                value={cc.voltorbs || ""}
                onChange={(e) =>
                  updateConstraint(i, "voltorbs", e.target.value, false)
                }
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
{/* Quit Recommendation (inline, non-blocking) */}
{quitRecommended && (
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
{solverExplanation && (
  <div className="solver-explanation">
    {solverExplanation}
  </div>
)}

{/* Action bar */}
<div className="action-bar">
  <button className="btn-analyze" onClick={runSolver} disabled={loading}>
    {loading ? "Calculating…" : "ANALYZE BOARD"}
  </button>
</div>

    </div>
  );
}