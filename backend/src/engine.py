from typing import Dict, List

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
    """

    def __init__(self, board: Board, mode: str = "level"):
        self.board = board
        self.mode = mode

        self.csp_solver = CSPSolver(board)
        self.quit_policy = QuitPolicy()

    def analyze(self) -> Dict:
        """
        Main solver entry point.
        """
        result = {
            "mode": self.mode,
            "guaranteed_safe": [],
            "guaranteed_voltorb": [],
            "recommendations": [],
            "forced_values": [],
            "quit_recommended": False,
            "explanation": "",
            "game_state": "active"
        }

        # ------------------------------
        # Step 1: CSP analysis
        # ------------------------------
        try:
            domains = self.csp_solver.solve()
            
            # --- WIN CONDITION ---
            can_win_points = False
            for pos, domain in domains.items():
                if not self.board.grid[pos].revealed:
                    if 2 in domain or 3 in domain:
                        can_win_points = True
                        break
            
            if not can_win_points:
                result["game_state"] = "won"
                result["explanation"] = "🎉 GAME CLEARED! All 2s and 3s have been found."
                return result

            # --- STANDARD LOGIC ---
            guaranteed_safe = self.csp_solver.guaranteed_safe()
            guaranteed_voltorb = self.csp_solver.guaranteed_voltorbs()
            forced_map = self.csp_solver.forced_assignments()
            
            # --- SMART AUTO-FLIP ---
            final_forced_values = []
            for (r, c), val in forced_map.items():
                if self.board.grid[(r, c)].revealed:
                    continue
                
                # In PROFIT mode, we hide 1s (val=1). 
                # But we MUST show Voltorbs (val=0) and high cards (val=2,3).
                if self.mode == "profit" and val == 1:
                    continue
                
                final_forced_values.append({"row": r, "col": c, "value": val})

            result["guaranteed_safe"] = guaranteed_safe
            result["guaranteed_voltorb"] = guaranteed_voltorb
            result["forced_values"] = final_forced_values

        except Exception as e:
            result["quit_recommended"] = True
            result["explanation"] = f"Invalid board: {str(e)}"
            return result

        # ------------------------------
        # Step 2: Monte Carlo
        # ------------------------------
        sampler = MonteCarloSampler(self.board)
        unrevealed_count = len(self.board.unrevealed_positions())
        
        if unrevealed_count > 20: time_budget = 40
        elif unrevealed_count > 10: time_budget = 75
        else: time_budget = 120

        try:
            distributions = sampler.sample(time_budget_ms=time_budget)
            metrics = ProbabilityMetrics.summarize(distributions)
        except ValueError:
            metrics = {}

        # ------------------------------
        # Step 3: Policy
        # ------------------------------
        if self.mode == "level":
            return self._level_mode(metrics, result)
        else:
            return self._profit_mode(metrics, result)

    def _level_mode(self, metrics, base_result):
        policy = LevelMaximizationPolicy(required_safe_moves=1)
        recommendations = policy.recommend(metrics)
        
        surv_prob = 0.0
        if recommendations:
            surv_prob = policy.survival_probability(recommendations)

        base_result.update({
            "recommendations": [self._fmt_rec(p, d) for p, d in recommendations],
            "quit_recommended": self.quit_policy.should_quit_level_mode(surv_prob),
            "explanation": "Level Mode: Showing safest moves."
        })
        return base_result

    def _profit_mode(self, metrics, base_result):
        policy = ProfitMaximizationPolicy()
        recommendations = policy.recommend(metrics)

        # Fallback: If profit policy returns nothing (e.g. too risky),
        # but we are NOT quitting yet, grab the least risky move from Level policy
        # so the user has *something* to click.
        if not recommendations and not base_result["forced_values"]:
            fallback_policy = LevelMaximizationPolicy(required_safe_moves=1)
            recommendations = fallback_policy.recommend(metrics)
            base_result["explanation"] = "Profit Mode: High risk! Showing safest fallback."
        else:
            base_result["explanation"] = "Profit Mode: Targeting 2s and 3s."

        quit_now = False
        if not recommendations and not base_result["forced_values"]:
            quit_now = True
        elif recommendations:
            best_ev = float(recommendations[0][1]["expected_value"])
            quit_now = self.quit_policy.should_quit_profit_mode(best_ev)

        base_result.update({
            "recommendations": [self._fmt_rec(p, d) for p, d in recommendations],
            "quit_recommended": quit_now
        })
        return base_result

    def _fmt_rec(self, pos, data):
        return {
            "position": pos,
            "p_voltorb": data["p_voltorb"],
            "risk_tier": data["risk_tier"],
            "expected_value": data["expected_value"],
            "distribution": data.get("distribution", {})
        }