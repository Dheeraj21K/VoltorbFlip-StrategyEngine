from copy import deepcopy
from typing import Dict, Set, Tuple, List

from src.core.board import Board, Position
from src.core.constraints import ConstraintEngine, CellValue


class CSPSolver:
    """
    High-level CSP solver that:
    - Runs constraint propagation
    - Extracts deterministic conclusions
    - Performs hypothetical consistency checks

    This class provides logical guarantees.
    """

    def __init__(self, board: Board):
        self.board = board
        self.engine = ConstraintEngine(board)

    # --------------------------------------------------
    # Core Solve
    # --------------------------------------------------

    def solve(self) -> Dict[Position, Set[CellValue]]:
        """
        Runs CSP propagation to a fixed point.

        Returns:
            Final domains for all positions
        Raises:
            ValueError if contradiction detected
        """
        return self.engine.compute_domains()

    # --------------------------------------------------
    # Deterministic Deductions
    # --------------------------------------------------

    def guaranteed_safe(self) -> List[Position]:
        """
        Returns positions that are guaranteed NOT to be Voltorbs.
        """
        domains = self.solve()
        return [
            pos for pos, d in domains.items()
            if 0 not in d
        ]

    def guaranteed_voltorbs(self) -> List[Position]:
        """
        Returns positions that must be Voltorbs.
        """
        domains = self.solve()
        return [
            pos for pos, d in domains.items()
            if d == {0}
        ]

    # --------------------------------------------------
    # Hypothetical Reasoning
    # --------------------------------------------------

    def is_consistent_assignment(
        self,
        pos: Position,
        value: CellValue
    ) -> bool:
        """
        Tests whether assigning (pos = value) leads to contradiction.

        Used for fail-proof reasoning.
        """
        test_board = deepcopy(self.board)

        try:
            test_board.reveal_tile(pos[0], pos[1], value)
            ConstraintEngine(test_board).compute_domains()
            return True
        except ValueError:
            return False

    def must_be_value(
        self,
        pos: Position,
        value: CellValue
    ) -> bool:
        """
        Returns True if the cell must take this value
        (all other values lead to contradiction).
        """
        for v in {0, 1, 2, 3} - {value}:
            if self.is_consistent_assignment(pos, v):
                return False
        return True

    # --------------------------------------------------
    # Advanced Deductions
    # --------------------------------------------------

    def forced_assignments(self) -> Dict[Position, CellValue]:
        """
        Returns assignments that are logically forced
        via hypothetical reasoning.
        """
        domains = self.solve()
        forced = {}

        for pos, domain in domains.items():
            if len(domain) == 1:
                forced[pos] = next(iter(domain))
                continue

            for v in domain:
                if self.must_be_value(pos, v):
                    forced[pos] = v
                    break

        return forced
