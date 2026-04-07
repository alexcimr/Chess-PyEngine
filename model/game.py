from model.board import Board
from model.bot_pst import Bot
from model.enums import Color, PieceType, GameStatus
import time


def print_board(board):
    """Rysuje szachownicę zgodnie z Twoim układem H-A i 1-8."""
    # Słownik do ładnego wypisywania figur, jeśli nie masz ich przypisanych jako stringi
    piece_chars = {
        (PieceType.PAWN, Color.WHITE): 'P', (PieceType.PAWN, Color.BLACK): 'p',
        (PieceType.ROOK, Color.WHITE): 'R', (PieceType.ROOK, Color.BLACK): 'r',
        (PieceType.KNIGHT, Color.WHITE): 'N', (PieceType.KNIGHT, Color.BLACK): 'n',
        (PieceType.BISHOP, Color.WHITE): 'B', (PieceType.BISHOP, Color.BLACK): 'b',
        (PieceType.QUEEN, Color.WHITE): 'Q', (PieceType.QUEEN, Color.BLACK): 'q',
        (PieceType.KING, Color.WHITE): 'K', (PieceType.KING, Color.BLACK): 'k',
    }

    print("\n  | H G F E D C B A")
    print("  | ----------------|")
    for row_index, row in enumerate(board.grid):
        print(f"{row_index + 1} |", end=" ")
        for col_index in range(8):
            piece = board.grid[row_index][col_index]
            if piece is None:
                symbol = "."
            else:
                # Zamienia Enum na literkę ze słownika
                symbol = piece_chars.get((piece.type, piece.color), "?")
            print(f"{symbol} ", end="")
        print("|")
    print("  | ----------------|\n")


def parse_move(move_str):
    """
    Tłumaczy szachowe 'e2 e4' na indeksy Twojej tablicy.
    Dla Twojego układu:
    - Rzędy: '1' to indeks 0, '8' to indeks 7.
    - Kolumny: 'h' to indeks 0, 'a' to indeks 7.
    """
    try:
        start, end = move_str.lower().split()

        # Kolumna: 7 - (kod_ascii_litery - kod_ascii_'a')
        start_col = 7 - (ord(start[0]) - ord('a'))
        # Rząd: Cyfra - 1
        start_row = int(start[1]) - 1

        end_col = 7 - (ord(end[0]) - ord('a'))
        end_row = int(end[1]) - 1

        return (start_row, start_col), (end_row, end_col)
    except Exception:
        return None, None


def format_move(row, col):
    """Tłumaczy indeksy planszy bota z powrotem na 'e2', 'a4' itd."""
    col_str = chr(ord('a') + (7 - col))
    row_str = str(row + 1)
    return f"{col_str}{row_str}"


def play_game():
    board = Board()
    board.setup_start_position()
    bot = Bot(board)

    DEPTH = 5  # Głębokość myślenia bota. Ustaw na 3 lub 4.

    print("=== SZACHY KONSOLOWE vs TWOJ BOT ===")
    print("Grasz Białymi (Wielkie litery). Bot gra Czarnymi (Małe litery).")
    print("Wpisuj ruchy podając literę i cyfrę skąd-dokąd, np.: 'e2 e4' lub 'g1 f3'")

    while True:
        print_board(board)

        # 1. Sprawdź czy gra się nie skończyła (Białe)
        status = board.game_status(Color.WHITE)
        if status == GameStatus.CHECKMATE:
            print("SZACH MAT! Czarny bot wygrywa!")
            break
        elif status == GameStatus.STALEMATE:
            print("PAT! Remis.")
            break

        # 2. Twój ruch (Białe)
        legal_moves = board.all_legal_moves(Color.WHITE)
        if not legal_moves:
            print("Brak legalnych ruchów, koniec gry!")
            break

        valid_input = False
        while not valid_input:
            user_input = input("Twój ruch (np. e2 e4) lub wpisz 'q' by wyjść: ")
            if user_input.lower() == 'q':
                return

            start_pos, end_pos = parse_move(user_input)
            if start_pos is None:
                print("Niepoprawny format. Użyj formatu 'e2 e4'.")
                continue

            # Znajdź Twój ruch wśród legalnych ruchów planszy
            chosen_move_data = None
            for move_data, score in legal_moves:
                m_start, m_end, m_type = move_data
                if m_start == start_pos and m_end == end_pos:
                    # Domyślnie bierzemy pierwszy pasujący (jeśli to promocja, weźmie Hetmana)
                    chosen_move_data = move_data
                    break

            if chosen_move_data:
                valid_input = True
                board.make_move(chosen_move_data[0], chosen_move_data[1], chosen_move_data[2])
                board.update_king_positions()
                board.update_zobrist_hash()
            else:
                print("Ten ruch jest nielegalny lub naraza krola na szach! Spróbuj ponownie.")

        print_board(board)

        # 3. Sprawdź czy wygrałeś (Czarne)
        status = board.game_status(Color.BLACK)
        if status == GameStatus.CHECKMATE:
            print("SZACH MAT! WYGRAŁEŚ!")
            break
        elif status == GameStatus.STALEMATE:
            print("PAT! Remis.")
            break

        # 4. Ruch Bota (Czarne)
        print("Bot myśli...")
        start_time = time.time()

        best_move_tuple = bot.best_move(DEPTH, Color.BLACK)

        end_time = time.time()

        if best_move_tuple:
            m_start, m_end, m_type = best_move_tuple
            board.make_move(m_start, m_end, m_type)
            board.update_king_positions()
            board.update_zobrist_hash()

            start_algebraic = format_move(m_start[0], m_start[1])
            end_algebraic = format_move(m_end[0], m_end[1])
            print(
                f"\n---> Bot zagrał: {start_algebraic} {end_algebraic} (Czas myślenia: {round(end_time - start_time, 2)}s) <---")
        else:
            print("Bot nie ma ruchów. Poddaje się!")
            break


if __name__ == "__main__":
    play_game()