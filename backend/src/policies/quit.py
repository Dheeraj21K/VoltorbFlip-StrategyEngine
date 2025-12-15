from typing import List, Tuple

from src.core.board import Position


class QuitPolicy:
    """
    Determines whether quitting is preferable to continuing.
    """

    def __init__(
        self,
        survival_threshold: float = 0.5,
        min_expected_gain: float = 0.5
    ):
        self.survival_threshold = survival_threshold
        self.min_expected_gain = min_expected_gain

    def should_quit_level_mode(
        self,
        survival_probability: float
    ) -> bool:
        """
        Quit if survival probability is too low.
        """
        return survival_probability < self.survival_threshold

    def should_quit_profit_mode(
        self,
        best_ev: float
    ) -> bool:
        """
        Quit if expected gain is too small.
        """
        return best_ev < self.min_expected_gain
