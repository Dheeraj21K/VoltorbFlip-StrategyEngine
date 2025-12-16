import { useState, useRef } from "react";
import Tile from "./Tile";
import { analyzeBoard } from "../../api/solver";
import type { TileState, LineConstraint } from "../../types";
import "./Board.css";

const SIZE = 5;

// Helper to create empty board
function createEmptyBoard(): TileState[][] {
  return Array.from({ length: SIZE }, () =>
    Array.from({ length: SIZE }, () => ({
      value: null,
      revealed: false,
      distribution: undefined,
    }))
  );
}

// History Snapshot Type for Undo
type HistoryState = {
  grid: TileState[][];
  rowConstraints: LineConstraint[];
  colConstraints: LineConstraint[];
};

export default function Board() {
  const [grid, setGrid] = useState<TileState[][]>(createEmptyBoard);
  const [rowConstraints, setRowConstraints] = useState<LineConstraint[]>(
    Array.from({ length: SIZE }, () => ({ sum: 0, voltorbs: 0 }))
  );
  const [colConstraints, setColConstraints] = useState<LineConstraint[]>(
    Array.from({ length: SIZE }, () => ({ sum: 0, voltorbs: 0 }))
  );
  
  // History Stack
  const [history, setHistory] = useState<HistoryState[]>([]);

  // Interaction State
  const [inputTile, setInputTile] = useState<[number, number] | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [mode, setMode] = useState<"level" | "profit">("level");
  const [gameState, setGameState] = useState<"active" | "won" | "lost">("active");
  const [explanation, setExplanation] = useState<string | null>(null);

  // Refs for Keyboard Navigation [R0S, R0V, R1S, R1V... C0S, C0V...]
  const inputRefs = useRef<(HTMLInputElement | null)[]>([]);

  // --- History Management ---
  const saveToHistory = () => {
    setHistory(prev => [
      ...prev.slice(-10), // Keep last 10 moves
      {
        grid: JSON.parse(JSON.stringify(grid)),
        rowConstraints: JSON.parse(JSON.stringify(rowConstraints)),
        colConstraints: JSON.parse(JSON.stringify(colConstraints))
      }
    ]);
  };

  const undo = () => {
    if (history.length === 0) return;
    const prev = history[history.length - 1];
    setGrid(prev.grid);
    setRowConstraints(prev.rowConstraints);
    setColConstraints(prev.colConstraints);
    setHistory(h => h.slice(0, -1));
    setExplanation(null);
    setGameState("active");
  };

  // --- Handlers ---

  const handleTileClick = (r: number, c: number) => {
    // If tile is already revealed (either manually or by auto-solve), ignore click
    if (grid[r][c].revealed) return;
    setInputTile(inputTile && inputTile[0] === r && inputTile[1] === c ? null : [r, c]);
  };

  const handleTileInput = (r: number, c: number, val: 0 | 1 | 2 | 3) => {
    saveToHistory(); // Save before mutating
    
    const newGrid = [...grid];
    newGrid[r] = [...newGrid[r]];
    newGrid[r][c] = {
      ...newGrid[r][c],
      value: val,
      revealed: true,
      distribution: undefined // Clear prediction once known
    };
    setGrid(newGrid);
    setInputTile(null);
    setError(null);
  };

  const updateConstraint = (
    idx: number, 
    type: 'sum' | 'voltorbs', 
    val: string, 
    isRow: boolean
  ) => {
    const num = parseInt(val);
    // Allow empty string for clearing input, else default to 0 for logic
    const cleanNum = isNaN(num) ? 0 : num;
    
    const setter = isRow ? setRowConstraints : setColConstraints;
    setter(prev => {
      const next = [...prev];
      next[idx] = { ...next[idx], [type]: cleanNum };
      return next;
    });
    setError(null);
  };

  // --- Solver Integration ---
  
  const runSolver = async () => {
    if(loading) return;
    saveToHistory(); // Save state before solver might auto-reveal stuff
    
    setLoading(true);
    setError(null);
    setExplanation(null);
    
    try {
      // Build request payload
      const revealedTiles = [];
      for(let r=0; r<SIZE; r++) {
        for(let c=0; c<SIZE; c++) {
          if(grid[r][c].revealed && grid[r][c].value !== null) {
            revealedTiles.push({ position: [r,c] as [number, number], value: grid[r][c].value! });
          }
        }
      }

      const res = await analyzeBoard({
        mode,
        rows: rowConstraints,
        cols: colConstraints,
        revealed: revealedTiles
      });

      setExplanation(res.explanation);
      setGameState(res.game_state);

      // If Game Won, stop processing moves
      if (res.game_state === 'won') {
        setLoading(false);
        return; 
      }

      // Create a map of auto-solved tiles for easy lookup
      const forcedMap = new Map<string, number>();
      if (res.forced_values) {
        res.forced_values.forEach(fv => {
          forcedMap.set(`${fv.row},${fv.col}`, fv.value);
        });
      }

      setGrid(prev => prev.map((row, r) => row.map((tile, c) => {
        // 1. Check if this tile was just Auto-Solved (Forced)
        const forcedVal = forcedMap.get(`${r},${c}`);
        if (forcedVal !== undefined && !tile.revealed) {
          return {
            ...tile,
            value: forcedVal as 0 | 1 | 2 | 3,
            revealed: true,
            guaranteedSafe: forcedVal > 0,
            guaranteedVoltorb: forcedVal === 0,
            distribution: undefined, // No need for shadows if revealed
            bestMove: false 
          };
        }

        // 2. If already revealed, keep state
        if(tile.revealed) return tile;

        // 3. Otherwise update solver data (Shadows/Probabilities)
        const rec = res.recommendations.find(re => re.position[0] === r && re.position[1] === c);
        
        return {
          ...tile,
          pVoltorb: rec?.pVoltorb,
          // Use the full distribution from backend for shadows
          distribution: rec?.distribution || undefined, 
          bestMove: res.recommendations[0]?.position[0] === r && res.recommendations[0]?.position[1] === c,
          // Update guarantee flags
          guaranteedSafe: res.guaranteed_safe.some(([gr, gc]) => gr === r && gc === c),
          guaranteedVoltorb: res.guaranteed_voltorb.some(([gr, gc]) => gr === r && gc === c),
        };
      })));

    } catch (e) {
      console.error(e);
      setError(e instanceof Error ? e.message : "Solver error occurred");
    } finally {
      setLoading(false);
    }
  };

  const softReset = () => {
    saveToHistory();
    setGrid(createEmptyBoard());
    setGameState("active");
    setExplanation(null);
    setError(null);
  };

  const hardReset = () => {
    saveToHistory();
    setGrid(createEmptyBoard());
    setRowConstraints(Array.from({ length: SIZE }, () => ({ sum: 0, voltorbs: 0 })));
    setColConstraints(Array.from({ length: SIZE }, () => ({ sum: 0, voltorbs: 0 })));
    setGameState("active");
    setExplanation(null);
    setError(null);
  };

  // --- Keyboard Navigation Logic ---
  const handleKeyDown = (e: React.KeyboardEvent, index: number) => {
    // Undo Shortcut
    if (e.key === "z" && (e.ctrlKey || e.metaKey)) {
        e.preventDefault();
        undo();
        return;
    }

    if (e.key.startsWith("Arrow")) {
      e.preventDefault(); 
      
      let nextIndex = index;
      
      // Map: 0-9 are Rows (Sum, V, Sum, V...), 10-19 are Cols
      
      if (e.key === "ArrowDown") {
        if (index < 10) nextIndex = Math.min(index + 2, 9); 
        else nextIndex = index; 
      } 
      else if (e.key === "ArrowUp") {
        if (index < 10) nextIndex = Math.max(index - 2, 0);
        else nextIndex = index - 10; 
      }
      else if (e.key === "ArrowRight") nextIndex = Math.min(index + 1, 19);
      else if (e.key === "ArrowLeft") nextIndex = Math.max(index - 1, 0);

      inputRefs.current[nextIndex]?.focus();
    }
  };

  return (
    <div className="board-wrapper" onKeyDown={(e) => {
        // Global Undo listener if needed, though inputs handle it mostly
        if (e.key === "z" && (e.ctrlKey || e.metaKey)) undo();
    }}>
      
      {/* Game State Banner (Win) */}
      {gameState === 'won' && (
        <div className="quit-banner" style={{background: '#4caf50', color: 'white', border: 'none'}}>
            <strong>🎉 GAME CLEARED!</strong><br/>
            All high-value cards have been identified.
        </div>
      )}

      <div className="board-main-area">
        {/* The 5x5 Grid */}
        <div className="board-grid">
          {grid.map((row, r) => row.map((tile, c) => (
            <Tile 
              key={`${r}-${c}`}
              tile={tile}
              isActive={false} 
              onClick={() => handleTileClick(r, c)}
              showInput={inputTile?.[0] === r && inputTile?.[1] === c}
              onInput={(v) => handleTileInput(r, c, v)}
            />
          )))}
        </div>

        {/* Row Constraints (Right Side) */}
        <div className="constraints-row">
          {rowConstraints.map((rc, i) => (
            <div key={`row-${i}`} className={`constraint-card c-idx-${i}`}>
              <input 
                ref={el => { inputRefs.current[i*2] = el; }}
                className="c-input sum"
                type="number" 
                value={rc.sum || ''} 
                placeholder="0"
                onChange={e => updateConstraint(i, 'sum', e.target.value, true)}
                onKeyDown={e => handleKeyDown(e, i*2)}
              />
              <div style={{display:'flex', alignItems:'center'}}>
                <span style={{fontSize:'12px'}}>💣</span>
                <input 
                  ref={el => { inputRefs.current[i*2+1] = el; }}
                  className="c-input bomb"
                  type="number" 
                  value={rc.voltorbs || ''} 
                  placeholder="0"
                  onChange={e => updateConstraint(i, 'voltorbs', e.target.value, true)}
                  onKeyDown={e => handleKeyDown(e, i*2+1)}
                />
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Column Constraints (Bottom) */}
      <div className="constraints-col">
        {colConstraints.map((cc, i) => (
          <div key={`col-${i}`} className={`constraint-card c-idx-${i}`}>
             <input 
                ref={el => { inputRefs.current[10 + i*2] = el; }}
                className="c-input sum"
                type="number" 
                value={cc.sum || ''} 
                placeholder="0"
                onChange={e => updateConstraint(i, 'sum', e.target.value, false)}
                onKeyDown={e => handleKeyDown(e, 10 + i*2)}
              />
              <div style={{display:'flex', alignItems:'center'}}>
                <span style={{fontSize:'12px'}}>💣</span>
                <input 
                  ref={el => { inputRefs.current[10 + i*2 + 1] = el; }}
                  className="c-input bomb"
                  type="number" 
                  value={cc.voltorbs || ''} 
                  placeholder="0"
                  onChange={e => updateConstraint(i, 'voltorbs', e.target.value, false)}
                  onKeyDown={e => handleKeyDown(e, 10 + i*2 + 1)}
                />
              </div>
          </div>
        ))}
      </div>

      {/* Mode Controls */}
      <div style={{display: 'flex', gap: '10px', marginTop: '10px', width: '100%', justifyContent: 'center'}}>
         <button 
           onClick={() => setMode('level')} 
           style={{
             background: mode === 'level' ? 'var(--color-gold)' : 'var(--bg-tile-hidden)',
             color: mode === 'level' ? 'black' : 'white',
             padding: '8px 16px', border: 'none', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold'
           }}
         >
           Level Mode
         </button>
         <button 
           onClick={() => setMode('profit')} 
           style={{
             background: mode === 'profit' ? 'var(--color-gold)' : 'var(--bg-tile-hidden)',
             color: mode === 'profit' ? 'black' : 'white',
             padding: '8px 16px', border: 'none', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold'
           }}
         >
           Profit Mode
         </button>
      </div>

      {/* Explanation Banner */}
      {explanation && gameState !== 'won' && (
        <div className="solver-explanation">
          {explanation}
        </div>
      )}

      {error && (
        <div className="error-banner">
          <strong>Error</strong><br/>
          {error}
        </div>
      )}

      {/* Action Bar */}
      <div className="action-bar">
        <button className="btn-analyze" onClick={runSolver} disabled={loading}>
          {loading ? "CALCULATING..." : "SOLVE BOARD"}
        </button>
        
        {/* Soft Reset (Keeps Numbers) */}
        <button className="btn-reset" onClick={softReset} disabled={loading} style={{background: '#ffa726'}}>
          RESET BOARD
        </button>
        
        {/* Hard Reset (Clears Everything) */}
        <button className="btn-reset" onClick={hardReset} disabled={loading}>
          CLEAR ALL
        </button>

        {/* Undo Button */}
        {history.length > 0 && (
             <button className="btn-reset" onClick={undo} disabled={loading} style={{background: '#78909c'}}>
                UNDO
             </button>
        )}
      </div>
    </div>
  );
}