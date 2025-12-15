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
            
        Raises:
            ValueError: If board constraints are impossible or contradictory
        """
        start_time = time.time()
        time_budget = time_budget_ms / 1000.0

        # First, validate that the board is solvable
        try:
            domains = self.solver.solve()
        except ValueError as e:
            raise ValueError(
                f"Invalid board configuration detected during constraint propagation: {str(e)}. "
                "Please verify that:\n"
                "  - Row and column sums are achievable with the given voltorb counts\n"
                "  - Revealed tiles don't contradict the constraints\n"
                "  - Each row/column has valid combinations"
            )

        counts: Dict[Position, Dict[CellValue, int]] = {
            pos: defaultdict(int) for pos in domains
        }

        valid_samples = 0
        total_attempts = 0
        max_attempts = 10000  # Safety limit to prevent infinite loops

        while True:
            # Check time budget
            if time.time() - start_time >= time_budget:
                break
            
            # Check attempt limit
            total_attempts += 1
            if total_attempts >= max_attempts:
                if valid_samples == 0:
                    raise ValueError(
                        f"Could not find any valid board configurations after {max_attempts} attempts. "
                        "The given constraints appear to be impossible to satisfy together. "
                        "\n\nCommon issues:"
                        "\n  - Row sum + column sum mismatch"
                        "\n  - Voltorb counts impossible with given sums"
                        "\n  - Revealed tiles conflict with constraints"
                        "\n\nSuggestion: Double-check constraint values and revealed tiles."
                    )
                # If we have at least some samples, use them
                break

            try:
                assignment = self._random_assignment(domains)
            except (ValueError, KeyError) as e:
                # This can happen if row configurations are temporarily exhausted
                # Just skip and try again
                continue

            if self._is_valid_assignment(assignment):
                valid_samples += 1
                for pos, value in assignment.items():
                    counts[pos][value] += 1

        if valid_samples == 0:
            raise ValueError(
                "The given row/column constraints are inconsistent. "
                "No valid Voltorb Flip board exists for this configuration.\n"
                f"Total attempts: {total_attempts}, Valid samples: 0\n"
                "\nPlease verify:"
                "\n  - Sum of all row sums = sum of all column sums"
                "\n  - Voltorb counts are consistent across rows/columns"
                "\n  - No mathematical impossibilities (e.g., sum=15 with 5 voltorbs)"
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
                    f"No valid row configurations for row {r}. "
                    f"This usually means the constraint (sum={constraint.total_sum}, "
                    f"voltorbs={constraint.voltorb_count}) is impossible to satisfy."
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