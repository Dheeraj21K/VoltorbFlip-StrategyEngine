from src.core.board import Board
from api.models import SolveRequest


def validate_constraints(request: SolveRequest) -> None:
    """
    Validates that the request contains mathematically possible constraints.
    
    Raises:
        ValueError: If constraints are impossible or contradictory
    """
    # Validate row constraints
    for i, row in enumerate(request.rows):
        if row.voltorbs < 0 or row.voltorbs > 5:
            raise ValueError(f"Row {i}: Voltorb count must be between 0 and 5 (got {row.voltorbs})")
        
        if row.sum < 0:
            raise ValueError(f"Row {i}: Sum cannot be negative (got {row.sum})")
        
        # With v voltorbs, minimum sum is (5-v) since remaining tiles must be at least 1
        min_possible_sum = 5 - row.voltorbs
        
        # With v voltorbs, maximum sum is (5-v)*3 since remaining tiles can be at most 3
        max_possible_sum = (5 - row.voltorbs) * 3
        
        if row.sum < min_possible_sum:
            raise ValueError(
                f"Row {i}: Sum {row.sum} is too low for {row.voltorbs} voltorbs. "
                f"Minimum possible sum is {min_possible_sum} "
                f"(remaining {5-row.voltorbs} tiles must be at least 1 each)."
            )
        
        if row.sum > max_possible_sum:
            raise ValueError(
                f"Row {i}: Sum {row.sum} is too high for {row.voltorbs} voltorbs. "
                f"Maximum possible sum is {max_possible_sum} "
                f"(remaining {5-row.voltorbs} tiles can be at most 3 each)."
            )
    
    # Validate column constraints
    for i, col in enumerate(request.cols):
        if col.voltorbs < 0 or col.voltorbs > 5:
            raise ValueError(f"Column {i}: Voltorb count must be between 0 and 5 (got {col.voltorbs})")
        
        if col.sum < 0:
            raise ValueError(f"Column {i}: Sum cannot be negative (got {col.sum})")
        
        min_possible_sum = 5 - col.voltorbs
        max_possible_sum = (5 - col.voltorbs) * 3
        
        if col.sum < min_possible_sum:
            raise ValueError(
                f"Column {i}: Sum {col.sum} is too low for {col.voltorbs} voltorbs. "
                f"Minimum possible sum is {min_possible_sum}."
            )
        
        if col.sum > max_possible_sum:
            raise ValueError(
                f"Column {i}: Sum {col.sum} is too high for {col.voltorbs} voltorbs. "
                f"Maximum possible sum is {max_possible_sum}."
            )
    
    # Validate global consistency: sum of row sums = sum of column sums
    total_row_sum = sum(r.sum for r in request.rows)
    total_col_sum = sum(c.sum for c in request.cols)
    
    if total_row_sum != total_col_sum:
        raise ValueError(
            f"Global constraint violation: Sum of all row sums ({total_row_sum}) "
            f"must equal sum of all column sums ({total_col_sum}). "
            f"These represent the same 5x5 grid."
        )
    
    # Validate global voltorb consistency
    total_row_voltorbs = sum(r.voltorbs for r in request.rows)
    total_col_voltorbs = sum(c.voltorbs for c in request.cols)
    
    if total_row_voltorbs != total_col_voltorbs:
        raise ValueError(
            f"Global constraint violation: Total voltorbs counted by rows ({total_row_voltorbs}) "
            f"must equal total voltorbs counted by columns ({total_col_voltorbs})."
        )
    
    # Validate revealed tiles
    for tile in request.revealed:
        row, col = tile.position
        
        if not (0 <= row < 5 and 0 <= col < 5):
            raise ValueError(f"Revealed tile position {tile.position} is out of bounds (must be 0-4)")
        
        if tile.value not in {0, 1, 2, 3}:
            raise ValueError(f"Revealed tile value must be 0, 1, 2, or 3 (got {tile.value})")


def build_board(request: SolveRequest) -> Board:
    """
    Builds a Board instance from a validated SolveRequest.
    
    Args:
        request: The solve request (should be pre-validated)
        
    Returns:
        Configured Board instance
        
    Raises:
        ValueError: If board construction fails
    """
    # First validate the request
    validate_constraints(request)
    
    board = Board()

    # Set row constraints
    for i, row in enumerate(request.rows):
        board.set_row_constraint(i, row.sum, row.voltorbs)

    # Set column constraints
    for j, col in enumerate(request.cols):
        board.set_col_constraint(j, col.sum, col.voltorbs)

    # Reveal known tiles
    for tile in request.revealed:
        try:
            board.reveal_tile(tile.position[0], tile.position[1], tile.value)
        except Exception as e:
            raise ValueError(
                f"Failed to reveal tile at {tile.position} with value {tile.value}: {str(e)}"
            )

    return board