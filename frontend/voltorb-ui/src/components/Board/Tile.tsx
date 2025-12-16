import type { TileState } from "../../types";
import VoltorbIcon from "./VoltorbIcon";
import "./Board.css";

type Props = {
  tile: TileState;
  isActive: boolean;
  onClick: () => void;
  showInput: boolean;
  onInput: (val: 0 | 1 | 2 | 3) => void;
};

export default function Tile({ tile, isActive, onClick, showInput, onInput }: Props) {
  // 1. REVEALED STATE: Show the big number or Voltorb
  if (tile.revealed && tile.value !== null) {
    return (
      <div className={`tile revealed value-${tile.value}`}>
        {tile.value === 0 ? <VoltorbIcon /> : tile.value}
      </div>
    );
  }

  // 2. INPUT MODE: Show the 4 mini-buttons to select value
  if (showInput) {
    return (
      <div className="tile input-mode">
        {[0, 1, 2, 3].map((v) => (
          <button 
            key={v} 
            className={`mini-btn val-${v}`}
            onClick={(e) => {
              e.stopPropagation();
              onInput(v as 0 | 1 | 2 | 3);
            }}
          >
            {v === 0 ? "💣" : v}
          </button>
        ))}
      </div>
    );
  }

  // 3. HIDDEN STATE: Show "Shadows" based on Solver Distribution
  // We check the 'distribution' map. If a number has >0% chance, we show it faintly.
  const dist = tile.distribution;
  const showShadow = (val: number) => {
    if (!dist) return false;
    // Show shadow if probability is non-zero
    return (dist[val] || 0) > 0;
  };

  const classes = [
    "tile hidden",
    isActive ? "active" : "",
    tile.bestMove ? "best-move" : "",
    // Only apply risk colors if we actually have data
    tile.pVoltorb !== undefined ? getRiskClass(tile.pVoltorb) : ""
  ].join(" ");

  return (
    <div className={classes} onClick={onClick}>
      {/* Memo Grid: The small numbers 1,2,3,💣 in corners */}
      <div className="memo-grid">
        <span className={showShadow(1) ? "memo visible" : "memo"}>1</span>
        <span className={showShadow(2) ? "memo visible" : "memo"}>2</span>
        <span className={showShadow(3) ? "memo visible" : "memo"}>3</span>
        <span className={showShadow(0) ? "memo visible bomb" : "memo"}>💣</span>
      </div>
      
      {/* Probability Badge: "90%" Safe */}
      {tile.pVoltorb !== undefined && (
        <div className="prob-badge">
          {Math.round((1 - tile.pVoltorb) * 100)}%
        </div>
      )}
    </div>
  );
}

// Helper to color-code the risk levels
function getRiskClass(p: number) {
  if (p === 0) return "safe";     // 100% Safe (Gold/Green)
  if (p > 0.4) return "danger";   // High Risk (Red)
  return "warning";               // Moderate Risk (Yellow)
}