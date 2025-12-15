from fastapi import FastAPI, HTTPException
from api.models import SolveRequest, SolveResponse
from api.utils import build_board
from src.engine import SolverEngine

app = FastAPI(
    title="Voltorb Flip Solver API",
    description="CSP-based, explainable Voltorb Flip solver",
    version="1.0.0",
    debug=True
)


@app.post("/analyze", response_model=SolveResponse)
def analyze_board(request: SolveRequest):
    try:
        board = build_board(request)
        engine = SolverEngine(board, mode=request.mode)
        result = engine.analyze()
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
