import json
import chess.pgn
from model.board import Board
from model.enums import MoveType, PieceType, Color, Phase
from book import uci_to_board_move

# Settings
PGN_FILE = "lichess_elite_2025-11.pgn"  # https://database.nikonoel.fr/
MAX_GAMES_TO_READ = 100
# Artificialy low for better piece placement
OPENING_THRESHOLD = 50
MIDGAME_THRESHOLD = 12


def material_count(board: Board, row: int, col: int, move_type: MoveType) -> int:
    """
    Calculates the change in total material caused by a move.
    Returns a negative value when a piece is captured (material decreases).
    """
    points = 0
    piece = board.grid[row][col]
    if piece is not None:
        points -= piece.point_value  # Value of the captured piece

    if move_type.value >= 3:
        if move_type == MoveType.PROMOTION_QUEEN:
            points += 8
        elif move_type == MoveType.PROMOTION_ROOK:
            points += 4
        elif move_type == MoveType.PROMOTION_BISHOP:
            points += 2
        elif move_type == MoveType.PROMOTION_KNIGHT:
            points += 2
        elif move_type == MoveType.EN_PASSANT:
            points -= 1

    return points

def get_phase(material: int) -> Phase:
    """Returns the current game phase based on total material on the board."""
    if material >= OPENING_THRESHOLD:
        return Phase.OPENING
    elif material >= MIDGAME_THRESHOLD:
        return Phase.MIDGAME
    return Phase.ENDGAME

def add_position_to_pst(board: Board, pst: dict, phase: Phase) -> None:
    """
    Adds the current board position to the PST counters.
    Pieces that have not moved yet receive a smaller weight to avoid
    inflating the value of starting squares.
    """
    for row in range(8):
        for col in range(8):
            piece = board.grid[row][col]
            if piece is None:
                continue

            weight = 1.0 if piece.moved or phase != Phase.OPENING else 0.25

            pst[phase.value][piece.color.value][piece.type.value][row][col] += weight

def print_pst(pst: dict) -> None:
    """Prints the learned PST tables in a readable format."""
    for phase in pst:
        print(f"\n=== {phase.upper()} ===")
        for color in pst[phase]:
            for piece in pst[phase][color]:
                print(f"\n{Color(int(color))} {PieceType(piece)}:")
                for row in pst[phase][color][piece]:
                    print("  " + "  ".join(f"{v:.2f}" for v in row))

def build_pst() -> None:
    """
    Reads PGN games and builds Piece-Square Tables saved as learned_pst.json.

    Each square value represents how often pieces stand there in master games,
    split into opening, midgame and endgame based on material on the board.
    Values are normalized to 0.0 - 0.1.
    """

    # Maps each piece type
    pieces = [
        PieceType.PAWN,
        PieceType.KNIGHT,
        PieceType.BISHOP,
        PieceType.ROOK,
        PieceType.QUEEN,
        PieceType.KING
    ]

    # Initialize counters
    pst = {Phase.OPENING.value: {}, Phase.MIDGAME.value: {}, Phase.ENDGAME.value: {}}
    for phase in pst.keys():
        for color in [Color.WHITE, Color.BLACK]:
            pst[phase][color.value] = {}
            for piece in pieces:
                pst[phase][color.value][piece.value] = [[0.0 for _ in range(8)] for _ in range(8)]

    board = Board()
    board.setup_start_position()
    START_MATERIAL = board.material_on_board()

    with open(PGN_FILE, "r", encoding="utf-8") as pgn:
        games_read = 0
        while games_read < MAX_GAMES_TO_READ:
            game = chess.pgn.read_game(pgn)
            if game is None:
                break

            board.setup_start_position()
            material_points = START_MATERIAL
            for move in game.mainline_moves():
                b_move = uci_to_board_move(board, move.uci())

                end_row = int(b_move[1][0])
                end_col = int(b_move[1][1])
                move_type = b_move[2]
                material_points += material_count(board, end_row, end_col, move_type)

                board.make_move(*b_move)
                phase = get_phase(material_points)
                add_position_to_pst(board, pst, phase)
            games_read += 1
            if games_read % 10000 == 0:
                print(f"{games_read}/{MAX_GAMES_TO_READ} games processed")

    # Normalize each table's values to range 0.0 - 0.1
    for phase in pst:
        for color in pst[phase]:
            for piece in pst[phase][color]:
                table = pst[phase][color][piece]
                max_val = max(table[r][c] for r in range(8) for c in range(8))
                if max_val > 0:
                    for r in range(8):
                        for c in range(8):
                            table[r][c] /= (max_val * 10)

    with open("pst.json", "w") as f:
        json.dump(pst, f)

    print("pst.json created!")
    print_pst(pst)


if __name__ == "__main__":
    build_pst()