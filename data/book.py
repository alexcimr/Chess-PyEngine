import json
import chess.pgn
from model.board import Board
from model.enums import MoveType

# Settings
PGN_FILE = "lichess_elite_2025-11.pgn"  # https://database.nikonoel.fr/
MAX_GAMES_TO_READ = 500000
MOVES_PER_GAME = 20
MIN_MOVES_PLAYED = 3

def print_book_stats(filtered_book: dict, games_read: int) -> None:
    """Prints a summary of the generated opening book."""
    stats = {
        "games read": games_read,
        "book size": len(filtered_book['white']) + len(filtered_book['black']),
        "max moves per game": MOVES_PER_GAME,
        "min times played": MIN_MOVES_PLAYED,
    }
    print("book.json created!")
    print("-" * 30)
    for key, val in stats.items():
        print(f"{key:<18} {val}")

def uci_to_board_move(board: Board, uci: str) -> tuple:
    """
    Converts a UCI string into an internal board move tuple.

    Returns None if the square is empty or the move is not legal.
    """
    # Convertion from UCI to board's
    start_col = ord('h') - ord(uci[0].lower())
    start_row = int(uci[1]) - 1
    end_col = ord('h') - ord(uci[2].lower())
    end_row = int(uci[3]) - 1

    start_pos = (start_row, start_col)
    end_pos = (end_row, end_col)

    # Gets the MoveType
    promo_char = uci[4] if len(uci) == 5 else None
    if promo_char:
        promos = {'q': MoveType.PROMOTION_QUEEN, 'r': MoveType.PROMOTION_ROOK,
                  'b': MoveType.PROMOTION_BISHOP, 'n': MoveType.PROMOTION_KNIGHT}
        return start_pos, end_pos, promos[promo_char]

    legal_moves = board.get_legal_moves(start_row, start_col)
    for move_end, move_type in legal_moves:
        if move_end == end_pos:
            return start_pos, end_pos, move_type

def build_book() -> None:
    """
    Reads PGN games and builds a weighted opening book saved as book.json.

    Each position is identified by its Zobrist hash. For every hash the book
    stores a dict of move_string -> count, where count is how many times that
    move was played in the dataset. Moves played fewer than MIN_MOVES_PLAYED
    times are filtered out to remove noise.
    """
    book = {"white": {}, "black": {}}
    board = Board()

    with open(PGN_FILE, "r", encoding="utf-8") as pgn:
        games_read = 0
        while games_read < MAX_GAMES_TO_READ:
            game = chess.pgn.read_game(pgn)
            if game is None: 
                break

            board.setup_start_position()
            moves_count = 0
            for move in game.mainline_moves():
                if moves_count >= MOVES_PER_GAME: 
                    break

                side = "white" if moves_count % 2 == 0 else "black"
                zhash = str(board.current_hash)
                b_move = uci_to_board_move(board, move.uci())

                # Encode the move as a 5-digit string: start_row, start_col, end_row, end_col, move_type.value
                sr, sc = b_move[0]
                er, ec = b_move[1]
                move_type_val = b_move[2].value
                move_str = f"{sr}{sc}{er}{ec}{move_type_val}"

                if zhash not in book[side]:
                    book[side][zhash] = {}

                if move_str not in book[side][zhash]:
                    book[side][zhash][move_str] = 0

                book[side][zhash][move_str] += 1

                board.make_move(*b_move)
                moves_count += 1

            games_read += 1
            if games_read % 10000 == 0:
                print(f"{games_read}/{MAX_GAMES_TO_READ} games processed")

    # Filter out rare moves to keep the book clean
    filtered_book = {"white": {}, "black": {}}
    for side in ["white", "black"]:
        for h, moves in book[side].items():
            good_moves = {m: count for m, count in moves.items() if count >= MIN_MOVES_PLAYED}
            if good_moves:
                filtered_book[side][h] = good_moves

    with open("book.json", "w") as f:
        json.dump(filtered_book, f)

    print_book_stats(filtered_book, games_read)

if __name__ == "__main__":
    build_book()