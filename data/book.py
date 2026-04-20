import json
import chess.pgn
from model.board import Board
from model.enums import MoveType

# Ustawienia
PGN_FILE = "lichess_elite_2025-11.pgn" #https://database.nikonoel.fr/
MAX_GAMES_TO_READ = 200000
MOVES_PER_GAME = 20
MIN_MOVES_PLAYED = 4


def uci_to_board_move(board: Board, uci: str):
    start_col = ord('h') - ord(uci[0].lower())
    start_row = int(uci[1]) - 1
    end_col = ord('h') - ord(uci[2].lower())
    end_row = int(uci[3]) - 1

    start_pos = (start_row, start_col)
    end_pos = (end_row, end_col)

    promo_char = uci[4] if len(uci) == 5 else None
    if promo_char:
        promos = {'q': MoveType.PROMOTION_QUEEN, 'r': MoveType.PROMOTION_ROOK,
                  'b': MoveType.PROMOTION_BISHOP, 'n': MoveType.PROMOTION_KNIGHT}
        return start_pos, end_pos, promos[promo_char]

    if board.grid[start_row][start_col] is None:
        return None

    legal_moves = board.get_legal_moves(start_row, start_col)
    for move_end, move_type in legal_moves:
        if move_end == end_pos:
            return start_pos, end_pos, move_type
    return None


def build_book():
    book = {"white": {}, "black": {}}
    board = Board()

    with open(PGN_FILE, "r", encoding="utf-8") as pgn:
        games_read = 0
        while games_read < MAX_GAMES_TO_READ:
            game = chess.pgn.read_game(pgn)
            if game is None: break

            board.setup_start_position()
            ply_count = 0
            for move in game.mainline_moves():
                if ply_count >= MOVES_PER_GAME: break

                side = "white" if ply_count % 2 == 0 else "black"
                zhash = str(board.current_hash)
                b_move = uci_to_board_move(board, move.uci())


                sr, sc = b_move[0]
                er, ec = b_move[1]
                move_type_val = b_move[2].value
                my_move_str = f"{sr}{sc}{er}{ec}{move_type_val}"

                if zhash not in book[side]:
                    book[side][zhash] = {}

                if my_move_str not in book[side][zhash]:
                    book[side][zhash][my_move_str] = 0

                book[side][zhash][my_move_str] += 1

                board.make_move(*b_move)
                ply_count += 1
            games_read += 1

    # Filtrowanie
    filtered_book = {"white": {}, "black": {}}
    for side in ["white", "black"]:
        for h, moves in book[side].items():
            good_moves = {m: count for m, count in moves.items() if count >= MIN_MOVES_PLAYED}
            if good_moves:
                filtered_book[side][h] = good_moves

    with open("book.json", "w") as f:
        json.dump(filtered_book, f)

    print("=============================")
    print("book.json created with:")
    print(f"games read: {games_read}")
    print(f"book size: {len(filtered_book['white']) + len(filtered_book['black'])}")
    print(f"max moves per game: {MOVES_PER_GAME}")
    print(f"min games played: {MIN_MOVES_PLAYED}")
    print("=============================")


if __name__ == "__main__":
    build_book()