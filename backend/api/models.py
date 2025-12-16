from typing import List, Literal, Dict
from pydantic import BaseModel


class LineConstraint(BaseModel):
    sum: int
    voltorbs: int


class RevealedTile(BaseModel):
    row: int
    col: int
    value: int


class SolveRequest(BaseModel):
    mode: Literal["level", "profit"]
    rows: List[LineConstraint]
    cols: List[LineConstraint]
    revealed: List[RevealedTile] = []


class Recommendation(BaseModel):
    position: List[int]
    p_voltorb: float | None = None
    expected_value: float | None = None
    risk_tier: str | None = None
    reason: str | None = None
    distribution: Dict[int, float] = {}


class ForcedTile(BaseModel):
    row: int
    col: int
    value: int


class SolveResponse(BaseModel):
    guaranteed_safe: List[List[int]]
    guaranteed_voltorb: List[List[int]]
    recommendations: List[Recommendation]
    forced_values: List[ForcedTile] = []
    quit_recommended: bool
    explanation: str
    mode: str
    # NEW: Status of the game logic
    game_state: Literal["active", "won", "lost"] = "active"