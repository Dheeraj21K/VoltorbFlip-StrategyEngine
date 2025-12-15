import type { TileState } from "../../types";
import VoltorbIcon from "./VoltorbIcon";
import "./Board.css";

type Props = {
  tile: TileState;
  isActive: boolean;
  onClick: () => void;
};

export default function Tile({ tile, isActive, onClick }: Props) {
  // Determine display content
  let content: React.ReactNode = null;
  
  if (tile.value !== null) {
    // If user has manually set a value
    content = tile.value === 0 ? <VoltorbIcon /> : tile.value;
  }

  // Determine CSS classes
  const classes = [
    "tile",
    isActive ? "active" : "",
    tile.guaranteedSafe ? "safe" : "",
    tile.guaranteedVoltorb ? "voltorb" : "",
    tile.bestMove ? "best-move" : "",
    // Only show risk shadows if tile is hidden (value is null)
    (tile.value === null && tile.pVoltorb !== undefined) ? riskClass(tile.pVoltorb) : "",
  ].join(" ");

  return (
    <div className={classes} onClick={onClick} data-value={tile.value}>
      {content}
      
      {/* Probability Badge (Only if hidden and calculated) */}
      {tile.value === null && tile.pVoltorb !== undefined && (
        <div className="prob-badge">
          {Math.round((1 - tile.pVoltorb) * 100)}%
        </div>
      )}
    </div>
  );
}

function riskClass(p?: number) {
  if (p === undefined) return "";
  if (p === 0) return "risk-safe";
  if (p < 0.20) return "risk-low";
  if (p < 0.50) return "risk-mid";
  return "risk-high";
}