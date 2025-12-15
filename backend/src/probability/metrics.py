from typing import Dict, Tuple

from src.core.board import Position
from src.core.constraints import CellValue


class ProbabilityMetrics:
    """
    Computes interpretable metrics from Monte Carlo distributions.
    """

    # Default risk thresholds (can be tuned by policies)
    LOW_RISK = 0.15
    MEDIUM_RISK = 0.35

    @staticmethod
    def voltorb_probability(
        distribution: Dict[CellValue, float]
    ) -> float:
        """
        Returns probability that the tile is a Voltorb.
        """
        return distribution.get(0, 0.0)

    @staticmethod
    def expected_value(
        distribution: Dict[CellValue, float]
    ) -> float:
        """
        Computes expected multiplier value (ignores Voltorb).
        """
        ev = 0.0
        for value, prob in distribution.items():
            if value > 0:
                ev += value * prob
        return ev

    @classmethod
    def risk_tier(cls, voltorb_prob: float) -> str:
        """
        Classifies risk level based on Voltorb probability.
        """
        if voltorb_prob == 0.0:
            return "GUARANTEED_SAFE"
        if voltorb_prob <= cls.LOW_RISK:
            return "LOW_RISK"
        if voltorb_prob <= cls.MEDIUM_RISK:
            return "MEDIUM_RISK"
        return "HIGH_RISK"

    @classmethod
    def summarize(
        cls,
        distributions: Dict[Position, Dict[CellValue, float]]
    ) -> Dict[Position, Dict[str, float | str]]:
        """
        Produces summary metrics per position.
        """
        summary = {}

        for pos, dist in distributions.items():
            p_voltorb = cls.voltorb_probability(dist)
            ev = cls.expected_value(dist)
            tier = cls.risk_tier(p_voltorb)

            summary[pos] = {
                "p_voltorb": p_voltorb,
                "expected_value": ev,
                "risk_tier": tier
            }

        return summary
