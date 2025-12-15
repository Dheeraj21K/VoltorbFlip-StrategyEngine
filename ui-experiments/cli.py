from src.core.board import Board
from src.engine import SolverEngine


def read_int(prompt: str, min_val: int = None, max_val: int = None) -> int:
    while True:
        try:
            value = int(input(prompt))
            if min_val is not None and value < min_val:
                raise ValueError
            if max_val is not None and value > max_val:
                raise ValueError
            return value
        except ValueError:
            print("Invalid input. Try again.")


def setup_board() -> Board:
    board = Board()

    print("\n--- Enter ROW constraints ---")
    for r in range(5):
        s = read_int(f"Row {r} total sum: ", 0)
        v = read_int(f"Row {r} voltorbs: ", 0, 5)
        board.set_row_constraint(r, s, v)

    print("\n--- Enter COLUMN constraints ---")
    for c in range(5):
        s = read_int(f"Column {c} total sum: ", 0)
        v = read_int(f"Column {c} voltorbs: ", 0, 5)
        board.set_col_constraint(c, s, v)

    print("\n--- Reveal known tiles (optional) ---")
    while True:
        ans = input("Reveal a tile? (y/n): ").lower()
        if ans != "y":
            break

        r = read_int("Row (0-4): ", 0, 4)
        c = read_int("Col (0-4): ", 0, 4)
        val = read_int("Value (0-3): ", 0, 3)

        board.reveal_tile(r, c, val)
        print("\nCurrent board:")
        print(board)

    return board


def print_result(result: dict):
    print("\n=== Solver Output ===")

    if result.get("guaranteed_safe"):
        print("\nGuaranteed safe tiles:")
        for pos in result["guaranteed_safe"]:
            print(f"  - {pos}")

    if result.get("guaranteed_voltorb"):
        print("\nGuaranteed voltorbs:")
        for pos in result["guaranteed_voltorb"]:
            print(f"  - {pos}")

    print("\nRecommendations:")
    for rec in result.get("recommendations", []):
        print(
            f"  Tile {rec['position']} | "
            f"P(Voltorb): {rec.get('p_voltorb', 0):.2f} | "
            f"EV: {rec.get('expected_value', 0):.2f} | "
            f"Risk: {rec.get('risk_tier', 'N/A')}"
        )

    if result.get("quit_recommended"):
        print("\n⚠️  Solver recommends quitting at this point.")

    print("\nExplanation:")
    print(result.get("explanation", ""))


def main():
    print("=== Voltorb Flip Solver CLI ===")

    board = setup_board()

    mode = input("\nChoose mode (level / profit): ").strip().lower()
    if mode not in {"level", "profit"}:
        print("Invalid mode, defaulting to level.")
        mode = "level"

    engine = SolverEngine(board, mode=mode)
    result = engine.analyze()

    print_result(result)


if __name__ == "__main__":
    main()
