from typing import Dict, List, Tuple
from src.core.board import Position


class ProfitMaximizationPolicy:
    """
    Reward-first policy.
    Recommends moves with highest risk-adjusted expected value.
    """

    def __init__(self, risk_penalty: float = 0.8):
        # Lower penalty (0.8) means we tolerate slightly more risk for high rewards
        self.risk_penalty = risk_penalty

    def score(self, data: Dict[str, float | str]) -> float:
        """
        Computes risk-adjusted expected value.
        EV (Expected Value) captures the reward.
        P (Prob Voltorb) captures the risk.
        """
        ev = float(data["expected_value"])
        p = float(data["p_voltorb"])
        
        # If a tile is guaranteed safe (0% Voltorb), prioritize it massively
        # This ensures we always pick safe 2s/3s before risking anything.
        if p == 0:
            return ev + 10.0
            
        return ev - (self.risk_penalty * p)

    def recommend(
        self,
        metrics: Dict[Position, Dict[str, float | str]],
        top_k: int = 5
    ) -> List[Tuple[Position, Dict]]:
        """
        Returns top-k profit-maximizing moves.
        """
        scored = [
            (pos, data, self.score(data))
            for pos, data in metrics.items()
        ]

        # Sort by score descending (Highest score first)
        scored.sort(key=lambda x: x[2], reverse=True)

        return [(pos, data) for pos, data, _ in scored[:top_k]]