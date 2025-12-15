from typing import Dict, List, Tuple

from src.core.board import Position
from src.probability.metrics import ProbabilityMetrics


class LevelMaximizationPolicy:
    """
    Survival-first policy.
    Recommends lowest-risk moves to retain level.
    """

    def __init__(
        self,
        required_safe_moves: int,
        risk_threshold: float = 0.25
    ):
        self.required_safe_moves = required_safe_moves
        self.risk_threshold = risk_threshold

    def recommend(
        self,
        metrics: Dict[Position, Dict[str, float | str]]
    ) -> List[Tuple[Position, Dict]]:
        """
        Returns ranked move recommendations.
        """
        candidates = []

        for pos, data in metrics.items():
            p = data["p_voltorb"]

            if p <= self.risk_threshold:
                candidates.append((pos, data))

        # Sort by lowest risk first
        candidates.sort(key=lambda x: x[1]["p_voltorb"])

        return candidates[: self.required_safe_moves]

    def survival_probability(
        self,
        selected_moves: List[Tuple[Position, Dict]]
    ) -> float:
        """
        Computes compounded survival probability.
        """
        prob = 1.0
        for _, data in selected_moves:
            prob *= (1.0 - data["p_voltorb"])
        return prob
