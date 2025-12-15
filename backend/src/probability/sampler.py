import random
import time
from typing import Dict
from collections import defaultdict

from src.core.board import Board, Position
from src.core.solver import CSPSolver
from src.core.constraints import CellValue, ConstraintEngine


class MonteCarloSampler:
    """
    CSP-aware Monte Carlo sampler for Voltorb Flip.

    Strategy:
    - Sample ROW-consistent assignments using CSP row constraints
    - Reject samples that violate column constraints
    - Run within a fixed time budget for real-time responsiveness
    """

    def __init__(self, board: Board):
        self.board = board
        self.solver = CSPSolver(board)

    # --------------------------------------------------
    # Public API
    # --------------------------------------------------

    def sample(
        self,
        time_budget_ms: int = 75
    ) -> Dict[Position, Dict[CellValue, float]]:
        """
        Runs time-bounded Monte Carlo sampling.

        Args:
            time_budget_ms: Maximum time to spend sampling (milliseconds)

        Returns:
            Dict[position][cell_value] = probability
        """
        start_time = time.time()
        time_budget = time_budget_ms / 1000.0

        domains = self.solver.solve()

        counts: Dict[Position, Dict[CellValue, int]] = {
            pos: defaultdict(int) for pos in domains
        }

        valid_samples = 0

        while True:
            if time.time() - start_time >= time_budget:
                break

            assignment = self._random_assignment(domains)

            if self._is_valid_assignment(assignment):
                valid_samples += 1
                for pos, value in assignment.items():
                    counts[pos][value] += 1

        if valid_samples == 0:
            raise ValueError(
                "The given row/column constraints are inconsistent. "
                "No valid Voltorb Flip board exists for this configuration."
            )

        return self._normalize(counts, valid_samples)

    # --------------------------------------------------
    # Sampling Helpers
    # --------------------------------------------------

    def _random_assignment(
        self,
        domains: Dict[Position, set]
    ) -> Dict[Position, CellValue]:
        """
        Generates a random assignment that satisfies ALL ROW constraints.
        Column constraints are checked later via rejection.
        """
        engine = ConstraintEngine(self.board)
        assignment: Dict[Position, CellValue] = {}

        for r in range(self.board.size):
            positions = [(r, c) for c in range(self.board.size)]
            constraint = self.board.row_constraints.get(r)

            if constraint is None:
                raise ValueError(f"Missing constraint for row {r}")

            valid_rows = engine._valid_line_configurations(
                positions,
                constraint,
                domains
            )

            if not valid_rows:
                raise ValueError(
                    f"No valid row configurations for row {r}"
                )

            chosen_row = random.choice(valid_rows)

            for pos, value in zip(positions, chosen_row):
                assignment[pos] = value

        return assignment

    def _is_valid_assignment(
        self,
        assignment: Dict[Position, CellValue]
    ) -> bool:
        """
        Validates assignment against FULL CSP constraints
        (rows + columns).
        """
        test_board = self._board_from_assignment(assignment)

        try:
            CSPSolver(test_board).solve()
            return True
        except ValueError:
            return False

    def _board_from_assignment(
        self,
        assignment: Dict[Position, CellValue]
    ) -> Board:
        """
        Constructs a Board instance from a full assignment.
        """
        test_board = Board(size=self.board.size)
        test_board.row_constraints = self.board.row_constraints
        test_board.col_constraints = self.board.col_constraints

        for (r, c), value in assignment.items():
            test_board.reveal_tile(r, c, value)

        return test_board

    @staticmethod
    def _normalize(
        counts: Dict[Position, Dict[CellValue, int]],
        total: int
    ) -> Dict[Position, Dict[CellValue, float]]:
        """
        Converts raw sample counts into probabilities.
        """
        probabilities: Dict[Position, Dict[CellValue, float]] = {}

        for pos, value_counts in counts.items():
            probabilities[pos] = {
                value: count / total
                for value, count in value_counts.items()
            }

        return probabilities
