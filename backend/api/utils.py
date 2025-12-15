from src.core.board import Board
from api.models import SolveRequest


def build_board(request: SolveRequest) -> Board:
    board = Board()

    for i, row in enumerate(request.rows):
        board.set_row_constraint(i, row.sum, row.voltorbs)

    for j, col in enumerate(request.cols):
        board.set_col_constraint(j, col.sum, col.voltorbs)

    for tile in request.revealed:
        board.reveal_tile(tile.row, tile.col, tile.value)

    return board
