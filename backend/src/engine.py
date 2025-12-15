from typing import Dict

from src.core.board import Board, Position
from src.core.solver import CSPSolver
from src.probability.sampler import MonteCarloSampler
from src.probability.metrics import ProbabilityMetrics
from src.policies.level import LevelMaximizationPolicy
from src.policies.profit import ProfitMaximizationPolicy
from src.policies.quit import QuitPolicy


class SolverEngine:
    """
    High-level orchestrator for the Voltorb Flip solver.

    Responsibilities:
    - Run CSP deductions first
    - Fall back to time-bounded Monte Carlo when needed
    - Apply objective-aware policies (level / profit)
    - Return explainable, UI-ready results
    """

    def __init__(self, board: Board, mode: str = "level"):
        self.board = board
        self.mode = mode

        self.csp_solver = CSPSolver(board)
        self.quit_policy = QuitPolicy()

    # --------------------------------------------------
    # Public API
    # --------------------------------------------------

    def analyze(self) -> Dict:
        """
        Main solver entry point.
        Always returns a response matching the API schema.
        """

        # Base response skeleton (schema-safe)
        result = {
            "mode": self.mode,
            "guaranteed_safe": [],
            "guaranteed_voltorb": [],
            "recommendations": [],
            "quit_recommended": False,
            "explanation": "",
        }

        # ------------------------------
        # Step 1: CSP analysis
        # ------------------------------

        try:
            self.csp_solver.solve()
        except Exception as e:
            # Graceful failure for impossible boards
            result["quit_recommended"] = True
            result["explanation"] = (
                f"Invalid or contradictory board configuration: {str(e)}"
            )
            return result

        guaranteed_safe = self.csp_solver.guaranteed_safe()
        guaranteed_voltorbs = self.csp_solver.guaranteed_voltorbs()

        result["guaranteed_safe"] = guaranteed_safe
        result["guaranteed_voltorb"] = guaranteed_voltorbs

        # If CSP found guaranteed safe moves, return immediately
        if guaranteed_safe:
            result["recommendations"] = [
                {
                    "position": pos,
                    "p_voltorb": 0.0,
                    "risk_tier": "GUARANTEED_SAFE",
                    "expected_value": 1.0,
                    "reason": "Guaranteed safe by CSP"
                }
                for pos in guaranteed_safe
            ]
            result["explanation"] = (
                "Deterministic CSP deductions found. "
                "These moves are provably safe."
            )
            return result

        # ------------------------------
        # Step 2: Time-bounded Monte Carlo
        # ------------------------------

        sampler = MonteCarloSampler(self.board)

        unrevealed = len(self.board.unrevealed_positions())

        if unrevealed > 20:
            time_budget_ms = 40      # early game
        elif unrevealed > 10:
            time_budget_ms = 75      # mid game
        else:
            time_budget_ms = 120     # late game

        distributions = sampler.sample(time_budget_ms=time_budget_ms)
        metrics = ProbabilityMetrics.summarize(distributions)

        # ------------------------------
        # Step 3: Apply policy
        # ------------------------------

        if self.mode == "level":
            return self._level_mode(metrics, result)

        if self.mode == "profit":
            return self._profit_mode(metrics, result)

        raise ValueError("Mode must be 'level' or 'profit'")

    # --------------------------------------------------
    # Policy Handlers
    # --------------------------------------------------

    def _level_mode(
        self,
        metrics: Dict[Position, Dict],
        base_result: Dict
    ) -> Dict:
        """
        Level-maximization policy:
        prioritize survival and retaining the current level.
        """
        policy = LevelMaximizationPolicy(required_safe_moves=1)

        recommendations = policy.recommend(metrics)
        survival_prob = policy.survival_probability(recommendations)

        quit_now = self.quit_policy.should_quit_level_mode(
            survival_prob
        )

        base_result.update({
            "recommendations": [
                {
                    "position": pos,
                    "p_voltorb": data["p_voltorb"],
                    "risk_tier": data["risk_tier"],
                    "expected_value": data["expected_value"],
                }
                for pos, data in recommendations
            ],
            "survival_probability": survival_prob,
            "quit_recommended": quit_now,
            "explanation": (
                "Level-maximization mode selected. "
                "Moves are ranked by lowest Voltorb risk "
                "to preserve the current level."
            ),
        })

        return base_result

    def _profit_mode(
        self,
        metrics: Dict[Position, Dict],
        base_result: Dict
    ) -> Dict:
        """
        Profit-maximization policy:
        prioritize higher expected multipliers.
        """
        policy = ProfitMaximizationPolicy()

        recommendations = policy.recommend(metrics)

        if not recommendations:
            base_result["quit_recommended"] = True
            base_result["explanation"] = (
                "No profitable moves detected. "
                "Quitting is recommended."
            )
            return base_result

        best_ev = recommendations[0][1]["expected_value"]

        quit_now = self.quit_policy.should_quit_profit_mode(
            best_ev
        )

        base_result.update({
            "recommendations": [
                {
                    "position": pos,
                    "p_voltorb": data["p_voltorb"],
                    "risk_tier": data["risk_tier"],
                    "expected_value": data["expected_value"],
                }
                for pos, data in recommendations
            ],
            "quit_recommended": quit_now,
            "explanation": (
                "Profit-maximization mode selected. "
                "Moves are ranked by expected value "
                "adjusted for Voltorb risk."
            ),
        })

        return base_result
