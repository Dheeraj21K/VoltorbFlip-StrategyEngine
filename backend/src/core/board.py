from dataclasses import dataclass, field
from typing import Dict, Tuple, Set, Optional, List

Position = Tuple[int, int]  # (row, col), 0-indexed


@dataclass
class Tile:
    """
    Represents a single tile on the board.
    """
    value: Optional[int] = None  # None = unknown, else {0,1,2,3}
    revealed: bool = False

    def is_unknown(self) -> bool:
        return self.value is None

    def is_voltorb(self) -> bool:
        return self.value == 0

    def is_safe(self) -> bool:
        return self.value is not None and self.value > 0


@dataclass
class LineConstraint:
    """
    Represents constraints for a row or column.
    """
    total_sum: int
    voltorb_count: int


@dataclass
class Board:
    """
    Represents the full Voltorb Flip board state.

    This class stores:
    - Tile states
    - Row constraints
    - Column constraints

    It does NOT perform solving or inference.
    """

    size: int = 5
    grid: Dict[Position, Tile] = field(default_factory=dict)
    row_constraints: Dict[int, LineConstraint] = field(default_factory=dict)
    col_constraints: Dict[int, LineConstraint] = field(default_factory=dict)

    def __post_init__(self):
        # Initialize empty grid if not provided
        if not self.grid:
            for r in range(self.size):
                for c in range(self.size):
                    self.grid[(r, c)] = Tile()

    # ------------------
    # Constraint Setup
    # ------------------

    def set_row_constraint(self, row: int, total_sum: int, voltorbs: int):
        self._validate_index(row)
        self.row_constraints[row] = LineConstraint(total_sum, voltorbs)

    def set_col_constraint(self, col: int, total_sum: int, voltorbs: int):
        self._validate_index(col)
        self.col_constraints[col] = LineConstraint(total_sum, voltorbs)

    # ------------------
    # Tile Operations
    # ------------------

    def reveal_tile(self, row: int, col: int, value: int):
        """
        Reveals a tile with a known value.
        """
        self._validate_index(row)
        self._validate_index(col)
        self._validate_value(value)

        tile = self.grid[(row, col)]

        if tile.revealed:
            raise ValueError(f"Tile ({row},{col}) is already revealed.")

        tile.value = value
        tile.revealed = True

    def mark_voltorb(self, row: int, col: int):
        """
        Marks a tile as a Voltorb (value = 0).
        """
        self.reveal_tile(row, col, 0)

    # ------------------
    # Queries
    # ------------------

    def get_tile(self, row: int, col: int) -> Tile:
        self._validate_index(row)
        self._validate_index(col)
        return self.grid[(row, col)]

    def unknown_positions(self) -> List[Position]:
        return [
            pos for pos, tile in self.grid.items()
            if tile.is_unknown()
        ]

    def revealed_positions(self) -> List[Position]:
        return [
            pos for pos, tile in self.grid.items()
            if tile.revealed
        ]

    # 🔹 ADDITION (ENGINE COMPATIBILITY)
    def unrevealed_positions(self) -> List[Position]:
        """
        Alias for solver/probability engine.
        Returns all positions that are not revealed yet.
        """
        return [
            pos for pos, tile in self.grid.items()
            if not tile.revealed
        ]


    # ------------------
    # Validation Helpers
    # ------------------

    def _validate_index(self, idx: int):
        if not (0 <= idx < self.size):
            raise IndexError(f"Index {idx} out of bounds.")

    def _validate_value(self, value: int):
        if value not in {0, 1, 2, 3}:
            raise ValueError("Tile value must be one of {0,1,2,3}.")

    # ------------------
    # Debug / Display
    # ------------------

    def __str__(self) -> str:
        """
        Simple string representation for debugging / CLI.
        """
        rows = []
        for r in range(self.size):
            row = []
            for c in range(self.size):
                tile = self.grid[(r, c)]
                if tile.is_unknown():
                    row.append(" ? ")
                else:
                    row.append(f" {tile.value} ")
            rows.append("|".join(row))
        return "\n".join(rows)
