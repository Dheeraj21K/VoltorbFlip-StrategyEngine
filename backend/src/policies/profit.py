from typing import Dict, List, Tuple

from src.core.board import Position


class ProfitMaximizationPolicy:
    """
    Reward-first policy.
    Recommends moves with highest risk-adjusted expected value.
    """

    def __init__(self, risk_penalty: float = 1.0):
        self.risk_penalty = risk_penalty

    def score(self, data: Dict[str, float | str]) -> float:
        """
        Computes risk-adjusted expected value.
        """
        ev = data["expected_value"]
        p = data["p_voltorb"]
        return ev - self.risk_penalty * p

    def recommend(
        self,
        metrics: Dict[Position, Dict[str, float | str]],
        top_k: int = 3
    ) -> List[Tuple[Position, Dict]]:
        """
        Returns top-k profit-maximizing moves.
        """
        scored = [
            (pos, data, self.score(data))
            for pos, data in metrics.items()
        ]

        scored.sort(key=lambda x: x[2], reverse=True)

        return [(pos, data) for pos, data, _ in scored[:top_k]]
