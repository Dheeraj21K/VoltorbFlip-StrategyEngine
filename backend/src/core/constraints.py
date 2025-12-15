from itertools import product
from typing import Dict, List, Set, Tuple

from src.core.board import Board, Position


CellValue = int  # {0,1,2,3}


class ConstraintEngine:
    """
    Constraint Satisfaction Engine for Voltorb Flip.

    Responsible for:
    - Enumerating valid row/column configurations
    - Pruning impossible cell values
    - Detecting contradictions

    Does NOT perform probability estimation or decision-making.
    """

    def __init__(self, board: Board):
        self.board = board

    # --------------------------------------------------
    # Public API
    # --------------------------------------------------

    def compute_domains(self) -> Dict[Position, Set[CellValue]]:
        """
        Computes the allowed domain for each cell based on
        row and column constraints.

        Returns:
            Dict mapping cell position -> allowed values
        Raises:
            ValueError if a contradiction is detected
        """
        # Initialize domains
        domains: Dict[Position, Set[CellValue]] = {
            pos: self._initial_domain(pos)
            for pos in self.board.grid
        }

        changed = True
        while changed:
            changed = False

            # Row propagation
            for row in range(self.board.size):
                changed |= self._propagate_line(
                    line_type="row",
                    index=row,
                    domains=domains
                )

            # Column propagation
            for col in range(self.board.size):
                changed |= self._propagate_line(
                    line_type="col",
                    index=col,
                    domains=domains
                )

        return domains

    # --------------------------------------------------
    # Propagation Logic
    # --------------------------------------------------

    def _propagate_line(
        self,
        line_type: str,
        index: int,
        domains: Dict[Position, Set[CellValue]]
    ) -> bool:
        """
        Propagates constraints for a single row or column.

        Returns True if any domain was reduced.
        """
        positions = self._line_positions(line_type, index)
        constraint = self._get_constraint(line_type, index)

        # If no constraint exists, nothing to propagate
        if constraint is None:
            return False

        valid_configs = self._valid_line_configurations(
            positions,
            constraint,
            domains
        )

        if not valid_configs:
            raise ValueError(
                f"Contradiction detected in {line_type} {index}"
            )

        changed = False

        # For each cell, keep only values that appear in at least one config
        for idx, pos in enumerate(positions):
            allowed_values = {config[idx] for config in valid_configs}
            current_domain = domains[pos]

            new_domain = current_domain & allowed_values

            if not new_domain:
                raise ValueError(
                    f"Domain wiped out at position {pos}"
                )

            if new_domain != current_domain:
                domains[pos] = new_domain
                changed = True

        return changed

    # --------------------------------------------------
    # Line Configuration Enumeration
    # --------------------------------------------------

    def _valid_line_configurations(
        self,
        positions: List[Position],
        constraint,
        domains: Dict[Position, Set[CellValue]]
    ) -> List[Tuple[CellValue, ...]]:
        """
        Generates all valid value assignments for a row or column.
        """
        candidate_domains = [
            domains[pos] for pos in positions
        ]

        valid_configs = []

        for values in product(*candidate_domains):
            if self._satisfies_constraint(values, constraint):
                valid_configs.append(values)

        return valid_configs

    @staticmethod
    def _satisfies_constraint(
        values: Tuple[CellValue, ...],
        constraint
    ) -> bool:
        """
        Checks whether a value assignment satisfies sum and Voltorb count.
        """
        total_sum = sum(values)
        voltorbs = values.count(0)

        return (
            total_sum == constraint.total_sum and
            voltorbs == constraint.voltorb_count
        )

    # --------------------------------------------------
    # Helpers
    # --------------------------------------------------

    def _initial_domain(self, pos: Position) -> Set[CellValue]:
        """
        Returns initial domain based on revealed tile.
        """
        tile = self.board.grid[pos]
        if tile.revealed:
            return {tile.value}
        return {0, 1, 2, 3}

    def _line_positions(
        self,
        line_type: str,
        index: int
    ) -> List[Position]:
        """
        Returns ordered positions for a row or column.
        """
        if line_type == "row":
            return [(index, c) for c in range(self.board.size)]
        elif line_type == "col":
            return [(r, index) for r in range(self.board.size)]
        else:
            raise ValueError("line_type must be 'row' or 'col'")

    def _get_constraint(self, line_type: str, index: int):
        if line_type == "row":
            return self.board.row_constraints.get(index)
        if line_type == "col":
            return self.board.col_constraints.get(index)
        return None
