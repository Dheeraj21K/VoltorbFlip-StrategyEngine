from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from api.models import SolveRequest, SolveResponse
from api.utils import build_board
from src.engine import SolverEngine
import traceback

app = FastAPI(
    title="Voltorb Flip Solver API",
    description="CSP-based, explainable Voltorb Flip solver",
    version="1.0.0",
    debug=True
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],  # Vite default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/analyze", response_model=SolveResponse)
def analyze_board(request: SolveRequest):
    """
    Analyzes a Voltorb Flip board and returns recommendations.
    
    Args:
        request: Board state with constraints and revealed tiles
        
    Returns:
        Analysis with guaranteed safe/voltorb tiles, recommendations, and explanations
        
    Raises:
        HTTPException: If board is invalid or analysis fails
    """
    try:
        # Build and validate board
        board = build_board(request)
        
        # Run solver engine
        engine = SolverEngine(board, mode=request.mode)
        result = engine.analyze()
        
        return result
        
    except ValueError as e:
        # These are expected validation errors - return them cleanly
        error_message = str(e)
        
        # Make error messages more user-friendly
        if "constraint violation" in error_message.lower():
            error_message = "⚠️ Invalid Board Configuration\n\n" + error_message
        elif "impossible" in error_message.lower():
            error_message = "⚠️ Impossible Constraints\n\n" + error_message
        elif "inconsistent" in error_message.lower():
            error_message = "⚠️ Inconsistent Constraints\n\n" + error_message
        
        raise HTTPException(status_code=400, detail=error_message)
        
    except Exception as e:
        # Unexpected errors - log them and return generic message
        print("Unexpected error in solver:")
        print(traceback.format_exc())
        
        raise HTTPException(
            status_code=500,
            detail=f"Internal solver error: {str(e)}\n\nPlease check server logs for details."
        )


@app.get("/")
def root():
    """Health check endpoint."""
    return {
        "status": "running",
        "service": "Voltorb Flip Solver API",
        "version": "1.0.0"
    }


@app.get("/health")
def health():
    """Detailed health check."""
    return {
        "status": "healthy",
        "api": "operational",
        "csp_engine": "ready",
        "monte_carlo": "ready"
    }