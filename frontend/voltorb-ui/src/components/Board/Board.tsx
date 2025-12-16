import { useState, useRef, useEffect, useCallback } from "react";
import Tile from "./Tile";
import { analyzeBoard } from "../../api/solver";
import type { TileState, LineConstraint } from "../../types";
import "./Board.css";

const SIZE = 5;

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
  
  // Track if we need to run a "Chain Solve" (auto-solve after auto-flip)
  const [needsChainSolve, setNeedsChainSolve] = useState(false);

  const inputRefs = useRef<(HTMLInputElement | null)[]>([]);

  // --- History Management ---
  const saveToHistory = () => {
    setHistory(prev => [
      ...prev.slice(-15), // Keep last 15 moves
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
    setNeedsChainSolve(false); // Stop any chains
  };

  // --- Handlers ---

  const handleTileClick = (r: number, c: number) => {
    if (grid[r][c].revealed) return;
    setInputTile(inputTile && inputTile[0] === r && inputTile[1] === c ? null : [r, c]);
  };

  const handleTileInput = (r: number, c: number, val: 0 | 1 | 2 | 3) => {
    saveToHistory();
    
    // Update Grid
    const newGrid = [...grid];
    newGrid[r] = [...newGrid[r]];
    newGrid[r][c] = {
      ...newGrid[r][c],
      value: val,
      revealed: true,
      distribution: undefined 
    };
    setGrid(newGrid);
    setInputTile(null);
    setError(null);

    // LIVE UPDATE: Trigger solve immediately after input
    // We use a timeout to let the state settle, or pass newGrid directly.
    // Setting a flag to trigger the effect is cleanest.
    setNeedsChainSolve(true); 
  };

  const updateConstraint = (
    idx: number, 
    type: 'sum' | 'voltorbs', 
    val: string, 
    isRow: boolean
  ) => {
    const num = parseInt(val);
    const cleanNum = isNaN(num) ? 0 : num;
    const setter = isRow ? setRowConstraints : setColConstraints;
    setter(prev => {
      const next = [...prev];
      next[idx] = { ...next[idx], [type]: cleanNum };
      return next;
    });
    setError(null);
    // Note: We don't auto-solve on constraint typing to avoid spamming while user types "1...2"
  };

  // --- Solver Logic ---
  
  const runSolver = useCallback(async (currentGrid = grid) => {
    setLoading(true);
    setError(null);
    
    try {
      // Build request
      const revealedTiles = [];
      for(let r=0; r<SIZE; r++) {
        for(let c=0; c<SIZE; c++) {
          if(currentGrid[r][c].revealed && currentGrid[r][c].value !== null) {
            revealedTiles.push({ position: [r,c], value: currentGrid[r][c].value! });
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

      if (res.game_state === 'won') {
        setLoading(false);
        setNeedsChainSolve(false);
        return; 
      }

      // Map forced values
      const forcedMap = new Map<string, number>();
      if (res.forced_values) {
        res.forced_values.forEach(fv => {
          forcedMap.set(`${fv.row},${fv.col}`, fv.value);
        });
      }

      let didAutoFlip = false;

      setGrid(prev => prev.map((row, r) => row.map((tile, c) => {
        // 1. Auto-Flip Forced Values
        const forcedVal = forcedMap.get(`${r},${c}`);
        if (forcedVal !== undefined && !tile.revealed) {
          didAutoFlip = true;
          return {
            ...tile,
            value: forcedVal as 0 | 1 | 2 | 3,
            revealed: true,
            guaranteedSafe: forcedVal > 0,
            guaranteedVoltorb: forcedVal === 0,
            distribution: undefined,
            bestMove: false 
          };
        }

        // 2. Keep Revealed
        if(tile.revealed) return tile;

        // 3. Update Shadows/Recs
        const rec = res.recommendations.find(re => re.position[0] === r && re.position[1] === c);
        
        return {
          ...tile,
          pVoltorb: rec?.pVoltorb,
          distribution: rec?.distribution || undefined, 
          bestMove: res.recommendations[0]?.position[0] === r && res.recommendations[0]?.position[1] === c,
          guaranteedSafe: res.guaranteed_safe.some(([gr, gc]) => gr === r && gc === c),
          guaranteedVoltorb: res.guaranteed_voltorb.some(([gr, gc]) => gr === r && gc === c),
        };
      })));

      // CHAIN REACTION: If we auto-flipped something, solve again!
      if (didAutoFlip) {
        setNeedsChainSolve(true);
      } else {
        setNeedsChainSolve(false);
      }

    } catch (e) {
      console.error(e);
      setError(e instanceof Error ? e.message : "Solver error occurred");
      setNeedsChainSolve(false); // Stop chain on error
    } finally {
      setLoading(false);
    }
  }, [grid, mode, rowConstraints, colConstraints]);

  // --- Chain Reaction Effect ---
  // This watches the "needsChainSolve" flag. 
  // If true, it waits a tiny bit (for visuals) then runs solver.
  useEffect(() => {
    if (needsChainSolve) {
      const timer = setTimeout(() => {
        runSolver(); 
      }, 400); // 400ms delay to let user see the flip happen
      return () => clearTimeout(timer);
    }
  }, [needsChainSolve, runSolver]);


  const softReset = () => {
    saveToHistory();
    setGrid(createEmptyBoard());
    setGameState("active");
    setExplanation(null);
    setNeedsChainSolve(false);
  };

  const hardReset = () => {
    saveToHistory();
    setGrid(createEmptyBoard());
    setRowConstraints(Array.from({ length: SIZE }, () => ({ sum: 0, voltorbs: 0 })));
    setColConstraints(Array.from({ length: SIZE }, () => ({ sum: 0, voltorbs: 0 })));
    setGameState("active");
    setExplanation(null);
    setNeedsChainSolve(false);
  };

  // --- Keyboard ---
  const handleKeyDown = (e: React.KeyboardEvent, index: number) => {
    if (e.key === "z" && (e.ctrlKey || e.metaKey)) {
        e.preventDefault();
        undo();
        return;
    }
    if (e.key.startsWith("Arrow")) {
      e.preventDefault(); 
      let nextIndex = index;
      if (e.key === "ArrowDown") nextIndex = index < 10 ? Math.min(index + 2, 9) : index; 
      else if (e.key === "ArrowUp") nextIndex = index < 10 ? Math.max(index - 2, 0) : index - 10; 
      else if (e.key === "ArrowRight") nextIndex = Math.min(index + 1, 19);
      else if (e.key === "ArrowLeft") nextIndex = Math.max(index - 1, 0);
      inputRefs.current[nextIndex]?.focus();
    }
  };

  return (
    <div className="board-wrapper" onKeyDown={(e) => {
        if (e.key === "z" && (e.ctrlKey || e.metaKey)) undo();
    }}>
      {/* Game State Banner */}
      {gameState === 'won' && (
        <div className="quit-banner" style={{background: '#4caf50', color: 'white', border: 'none'}}>
            <strong>🎉 GAME CLEARED!</strong><br/>
            All high-value cards have been identified.
        </div>
      )}

      <div className="board-main-area">
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
        
        {/* Row Constraints */}
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

      <div style={{display: 'flex', gap: '10px', marginTop: '10px', width: '100%', justifyContent: 'center'}}>
         <button 
           onClick={() => { setMode('level'); setNeedsChainSolve(true); }} 
           style={{
             background: mode === 'level' ? 'var(--color-gold)' : 'var(--bg-tile-hidden)',
             color: mode === 'level' ? 'black' : 'white',
             padding: '8px 16px', border: 'none', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold'
           }}
         >
           Level Mode
         </button>
         <button 
           onClick={() => { setMode('profit'); setNeedsChainSolve(true); }} 
           style={{
             background: mode === 'profit' ? 'var(--color-gold)' : 'var(--bg-tile-hidden)',
             color: mode === 'profit' ? 'black' : 'white',
             padding: '8px 16px', border: 'none', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold'
           }}
         >
           Profit Mode
         </button>
      </div>

      {explanation && gameState !== 'won' && (
        <div className="solver-explanation">
          {explanation}
        </div>
      )}

      {error && <div className="error-banner">{error}</div>}

      <div className="action-bar">
        <button className="btn-analyze" onClick={() => runSolver()} disabled={loading}>
          {loading ? "CALCULATING..." : "SOLVE / UPDATE"}
        </button>
        <button className="btn-reset" onClick={softReset} disabled={loading} style={{background: '#ffa726'}}>
          RESET BOARD
        </button>
        <button className="btn-reset" onClick={hardReset} disabled={loading}>
          CLEAR ALL
        </button>
        {history.length > 0 && (
             <button className="btn-reset" onClick={undo} disabled={loading} style={{background: '#78909c'}}>
                UNDO
             </button>
        )}
      </div>
    </div>
  );
}