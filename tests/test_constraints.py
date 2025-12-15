import pytest

from src.core.board import Board
from src.core.constraints import ConstraintEngine


def test_row_constraint_domain_reduction():
    """
    Row sum = 1, voltorbs = 4
    Only one cell can be 1, rest must be 0
    """
    board = Board()
    board.set_row_constraint(0, total_sum=1, voltorbs=4)

    engine = ConstraintEngine(board)
    domains = engine.compute_domains()

    row_positions = [(0, c) for c in range(5)]

    for pos in row_positions:
        assert domains[pos].issubset({0, 1})


def test_column_all_safe():
    """
    Column with 0 voltorbs → all values must be > 0
    """
    board = Board()
    board.set_col_constraint(2, total_sum=10, voltorbs=0)

    engine = ConstraintEngine(board)
    domains = engine.compute_domains()

    for r in range(5):
        assert 0 not in domains[(r, 2)]


def test_contradiction_detection():
    """
    Impossible constraint should raise ValueError
    """
    board = Board()
    board.set_row_constraint(0, total_sum=0, voltorbs=0)  # impossible

    engine = ConstraintEngine(board)

    with pytest.raises(ValueError):
        engine.compute_domains()
