import pytest
from api.models import SolveRequest, LineConstraint
from api.utils import validate_constraints


def test_valid_constraints():
    """Normal valid board should pass"""
    request = SolveRequest(
        mode="level",
        rows=[
            LineConstraint(sum=5, voltorbs=0),
            LineConstraint(sum=6, voltorbs=1),
            LineConstraint(sum=7, voltorbs=0),
            LineConstraint(sum=4, voltorbs=1),
            LineConstraint(sum=8, voltorbs=1),
        ],
        cols=[
            LineConstraint(sum=6, voltorbs=0),
            LineConstraint(sum=5, voltorbs=1),
            LineConstraint(sum=7, voltorbs=1),
            LineConstraint(sum=6, voltorbs=1),
            LineConstraint(sum=6, voltorbs=0),
        ],
        revealed=[]
    )
    
    # Should not raise
    validate_constraints(request)


def test_impossible_row_sum_too_low():
    """Sum too low for voltorb count"""
    request = SolveRequest(
        mode="level",
        rows=[
            LineConstraint(sum=2, voltorbs=4),  # Impossible: need at least 1 for remaining tile
            LineConstraint(sum=5, voltorbs=0),
            LineConstraint(sum=5, voltorbs=0),
            LineConstraint(sum=5, voltorbs=0),
            LineConstraint(sum=5, voltorbs=0),
        ],
        cols=[
            LineConstraint(sum=4, voltorbs=0),
            LineConstraint(sum=4, voltorbs=0),
            LineConstraint(sum=4, voltorbs=1),
            LineConstraint(sum=4, voltorbs=1),
            LineConstraint(sum=6, voltorbs=2),
        ],
        revealed=[]
    )
    
    with pytest.raises(ValueError, match="too low"):
        validate_constraints(request)


def test_impossible_row_sum_too_high():
    """Sum too high for voltorb count"""
    request = SolveRequest(
        mode="level",
        rows=[
            LineConstraint(sum=13, voltorbs=3),  # Impossible: max is 6 (two 3s)
            LineConstraint(sum=5, voltorbs=0),
            LineConstraint(sum=5, voltorbs=0),
            LineConstraint(sum=5, voltorbs=0),
            LineConstraint(sum=5, voltorbs=0),
        ],
        cols=[
            LineConstraint(sum=6, voltorbs=0),
            LineConstraint(sum=6, voltorbs=0),
            LineConstraint(sum=6, voltorbs=1),
            LineConstraint(sum=6, voltorbs=1),
            LineConstraint(sum=9, voltorbs=1),
        ],
        revealed=[]
    )
    
    with pytest.raises(ValueError, match="too high"):
        validate_constraints(request)


def test_global_sum_mismatch():
    """Total row sums != total column sums"""
    request = SolveRequest(
        mode="level",
        rows=[
            LineConstraint(sum=5, voltorbs=0),
            LineConstraint(sum=5, voltorbs=0),
            LineConstraint(sum=5, voltorbs=0),
            LineConstraint(sum=5, voltorbs=0),
            LineConstraint(sum=5, voltorbs=0),
        ],
        cols=[
            LineConstraint(sum=6, voltorbs=0),  # Total = 30, but rows = 25
            LineConstraint(sum=6, voltorbs=0),
            LineConstraint(sum=6, voltorbs=0),
            LineConstraint(sum=6, voltorbs=0),
            LineConstraint(sum=6, voltorbs=0),
        ],
        revealed=[]
    )
    
    with pytest.raises(ValueError, match="Sum of all row sums"):
        validate_constraints(request)


def test_global_voltorb_mismatch():
    """Total row voltorbs != total column voltorbs"""
    request = SolveRequest(
        mode="level",
        rows=[
            LineConstraint(sum=5, voltorbs=1),
            LineConstraint(sum=5, voltorbs=1),
            LineConstraint(sum=5, voltorbs=0),
            LineConstraint(sum=5, voltorbs=0),
            LineConstraint(sum=5, voltorbs=0),
        ],
        cols=[
            LineConstraint(sum=5, voltorbs=1),  # Total = 3, but rows = 2
            LineConstraint(sum=5, voltorbs=1),
            LineConstraint(sum=5, voltorbs=1),
            LineConstraint(sum=5, voltorbs=0),
            LineConstraint(sum=5, voltorbs=0),
        ],
        revealed=[]
    )
    
    with pytest.raises(ValueError, match="Total voltorbs counted by rows"):
        validate_constraints(request)


def test_negative_values():
    """Negative sums or voltorbs"""
    request = SolveRequest(
        mode="level",
        rows=[
            LineConstraint(sum=-5, voltorbs=0),
            LineConstraint(sum=5, voltorbs=0),
            LineConstraint(sum=5, voltorbs=0),
            LineConstraint(sum=5, voltorbs=0),
            LineConstraint(sum=5, voltorbs=0),
        ],
        cols=[
            LineConstraint(sum=3, voltorbs=0),
            LineConstraint(sum=3, voltorbs=0),
            LineConstraint(sum=3, voltorbs=0),
            LineConstraint(sum=3, voltorbs=0),
            LineConstraint(sum=3, voltorbs=0),
        ],
        revealed=[]
    )
    
    with pytest.raises(ValueError, match="cannot be negative"):
        validate_constraints(request)


def test_voltorb_out_of_range():
    """More than 5 voltorbs in a line"""
    request = SolveRequest(
        mode="level",
        rows=[
            LineConstraint(sum=0, voltorbs=6),  # Impossible
            LineConstraint(sum=5, voltorbs=0),
            LineConstraint(sum=5, voltorbs=0),
            LineConstraint(sum=5, voltorbs=0),
            LineConstraint(sum=5, voltorbs=0),
        ],
        cols=[
            LineConstraint(sum=4, voltorbs=1),
            LineConstraint(sum=4, voltorbs=1),
            LineConstraint(sum=4, voltorbs=1),
            LineConstraint(sum=4, voltorbs=1),
            LineConstraint(sum=4, voltorbs=2),
        ],
        revealed=[]
    )
    
    with pytest.raises(ValueError, match="must be between 0 and 5"):
        validate_constraints(request)