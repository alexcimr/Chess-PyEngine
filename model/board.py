import random
from model.enums import PieceType, Color, MoveType, GameStatus
from model.pieces import Pawn, Rook, Knight, Bishop, Queen, King
from model.utils import is_on_board

# --- ZOBRIST HASHING ---
random.seed(42)

# 1. Figury na planszy
ZOBRIST_PIECES = {}
for pt in PieceType:
    ZOBRIST_PIECES[pt] = {}
    for c in Color:
        ZOBRIST_PIECES[pt][c] = [[random.getrandbits(64) for _ in range(8)] for _ in range(8)]

# 2. En Passant
ZOBRIST_ENPASSANT = [random.getrandbits(64) for _ in range(8)]

# 3. Prawa do roszady
ZOBRIST_CASTLING = {
    "WK": random.getrandbits(64),
    "WQ": random.getrandbits(64),
    "BK": random.getrandbits(64),
    "BQ": random.getrandbits(64)
}

class Board():
    def __init__(self):
        self.grid = [[None for _ in range(8)] for _ in range(8)]
        self.enpassant_tile = None # Puste pole ktore można zbić pionkim
        self.white_king_pos = None
        self.black_king_pos = None

        # Zorbist hash
        self.current_hash = 0

    def clear_board(self):
        self.grid = [[None for _ in range(8)] for _ in range(8)]
        self.enpassant_tile = None
        self.white_king_pos = None
        self.black_king_pos = None
        self.current_hash = 0

    def setup_start_position(self):
        """Ustawia figury na pozycjach startowych dla nowej gry."""
        self.clear_board()

        # --- BIAŁE ---
        self.grid[0][0] = Rook(Color.WHITE)
        self.grid[0][7] = Rook(Color.WHITE)
        self.grid[0][1] = Knight(Color.WHITE)
        self.grid[0][6] = Knight(Color.WHITE)
        self.grid[0][2] = Bishop(Color.WHITE)
        self.grid[0][5] = Bishop(Color.WHITE)
        self.grid[0][4] = Queen(Color.WHITE)
        self.grid[0][3] = King(Color.WHITE)
        for i in range(8):
            self.grid[1][i] = Pawn(Color.WHITE)

        # --- CZARNE ---
        self.grid[7][0] = Rook(Color.BLACK)
        self.grid[7][7] = Rook(Color.BLACK)
        self.grid[7][1] = Knight(Color.BLACK)
        self.grid[7][6] = Knight(Color.BLACK)
        self.grid[7][2] = Bishop(Color.BLACK)
        self.grid[7][5] = Bishop(Color.BLACK)
        self.grid[7][4] = Queen(Color.BLACK)
        self.grid[7][3] = King(Color.BLACK)

        for i in range(8):
            self.grid[6][i] = Pawn(Color.BLACK)

        self.update_king_positions()
        self.update_zobrist_hash()

    def is_empty(self, row: int, col: int) -> bool:
        """Zwraca True, jeśli pole jest na planszy i jest puste."""
        if not is_on_board(row, col):
            return False

        return self.grid[row][col] is None

    def get_piece_type(self, row: int, col: int) -> PieceType | None:
        """Zwraca typ figury lub None, jeśli pole puste."""
        if not is_on_board(row, col):
            return None

        piece = self.grid[row][col]
        if piece is None:
            return None
        return piece.type

    def get_piece_color(self, row: int, col: int) -> Color | None:
        """Zwraca kolor figury lub None, jeśli pole puste."""
        if not is_on_board(row, col):
            return None

        piece = self.grid[row][col]
        if piece is None:
            return None
        return piece.color


    def is_tile_in_check(self, row: int, col: int, attacking_color: Color) -> bool:
        """Sprawdza, czy pole (row, col) jest atakowane przez dany kolor. Zwraca True lub False."""

        # Pionek
        for dc in [-1, 1]:
            r = row - attacking_color.value
            c = col + dc
            if 0 <= r < 8 and 0 <= c < 8:
                piece = self.grid[r][c]
                if piece is not None and piece.color == attacking_color and piece.type == PieceType.PAWN:
                    return True

        # Skoczek
        knight_jumps = [
            (-2, -1), (-2, 1),
            (-1, -2), (-1, 2),
            (1, -2), (1, 2),
            (2, -1), (2, 1)
        ]
        for dr, dc in knight_jumps:
            r, c = row + dr, col + dc
            if 0 <= r < 8 and 0 <= c < 8:
                piece = self.grid[r][c]
                if piece is not None and piece.color == attacking_color and piece.type == PieceType.KNIGHT:
                    return True

        # Wieża + Hetman
        straight_directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for dr, dc in straight_directions:
            r, c = row + dr, col + dc
            while 0 <= r < 8 and 0 <= c < 8:
                piece = self.grid[r][c]
                if piece is not None:
                    if piece.color == attacking_color and piece.type in (PieceType.ROOK, PieceType.QUEEN):
                        return True
                    break
                r += dr
                c += dc

        # Goniec + Hetman
        diagonal_directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        for dr, dc in diagonal_directions:
            r, c = row + dr, col + dc
            while 0 <= r < 8 and 0 <= c < 8:
                piece = self.grid[r][c]
                if piece is not None:
                    if piece.color == attacking_color and piece.type in (PieceType.BISHOP, PieceType.QUEEN):
                        return True
                    break
                r += dr
                c += dc

        # Król
        king_moves = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for dr, dc in king_moves:
            r, c = row + dr, col + dc
            if 0 <= r < 8 and 0 <= c < 8:
                piece = self.grid[r][c]
                if piece is not None and piece.color == attacking_color and piece.type == PieceType.KING:
                    return True

        return False


    def make_move(self, start_pos: tuple[int, int], end_pos: tuple[int, int], move_type=MoveType.NORMAL) -> tuple:
        """Robi ruch na planszy i zwraca stare wartosci potrzebne do undo."""
        sr, sc = start_pos
        er, ec = end_pos

        # Pobieramy figure i zapisujemy stany do cofniecia
        piece = self.grid[sr][sc]
        captured_piece = self.grid[er][ec]
        old_moved_status = piece.moved
        old_enpassant_status = self.enpassant_tile
        old_hash = self.current_hash

        # Zorbist wylaczanie
        self.current_hash ^= self.get_castling_hash()  # Wyłączamy stare prawa roszady
        if self.enpassant_tile is not None:
            self.current_hash ^= ZOBRIST_ENPASSANT[self.enpassant_tile[1]]
        self.current_hash ^= ZOBRIST_PIECES[piece.type][piece.color][sr][sc]
        if captured_piece is not None:
            self.current_hash ^= ZOBRIST_PIECES[captured_piece.type][captured_piece.color][er][ec]


        # Ustawiamy enpassant jesli pion skacze o 2 pola
        if piece.type == PieceType.PAWN and abs(sr - er) == 2:
            self.enpassant_tile = ((sr + er) // 2, sc) # Pole za pionkiem
            self.current_hash ^= ZOBRIST_ENPASSANT[self.enpassant_tile[1]] # Zorbist
        else:
            self.enpassant_tile = None

        # Ruch figury
        self.grid[er][ec] = piece
        self.grid[sr][sc] = None
        piece.moved = True

        # Obsluga ruchow specjalnych
        if move_type == MoveType.PROMOTION_QUEEN:
            self.grid[er][ec] = Queen(piece.color)
            self.grid[er][ec].moved = True
        # Roszada
        elif move_type == MoveType.CASTLING:
            # Przesuwamy wieze
            if ec == 1:
                self.grid[sr][2] = self.grid[sr][0]
                self.grid[sr][0] = None
                self.grid[sr][2].moved = True
                # ZOBRIST: Przesuwamy wieżę
                self.current_hash ^= ZOBRIST_PIECES[PieceType.ROOK][piece.color][sr][0]
                self.current_hash ^= ZOBRIST_PIECES[PieceType.ROOK][piece.color][sr][2]
            elif ec == 5:
                self.grid[sr][4] = self.grid[sr][7]
                self.grid[sr][7] = None
                self.grid[sr][4].moved = True
                # ZOBRIST: Przesuwamy wieżę
                self.current_hash ^= ZOBRIST_PIECES[PieceType.ROOK][piece.color][sr][7]
                self.current_hash ^= ZOBRIST_PIECES[PieceType.ROOK][piece.color][sr][4]
        # Promocje
        elif move_type == MoveType.PROMOTION_ROOK:
            self.grid[er][ec] = Rook(piece.color)
            self.grid[er][ec].moved = True

        elif move_type == MoveType.PROMOTION_BISHOP:
            self.grid[er][ec] = Bishop(piece.color)
            self.grid[er][ec].moved = True

        elif move_type == MoveType.PROMOTION_KNIGHT:
            self.grid[er][ec] = Knight(piece.color)
            self.grid[er][ec].moved = True
        # En passant
        elif move_type == MoveType.EN_PASSANT:
            # Zbicie piona w przelocie
            captured_piece = self.grid[sr][ec]
            self.grid[sr][ec] = None
            # ZOBRIST: Dodatkowe usunięcie piona zbitego w przelocie
            self.current_hash ^= ZOBRIST_PIECES[captured_piece.type][captured_piece.color][sr][ec]

        if piece.type == PieceType.KING:
            if piece.color == Color.WHITE:
                self.white_king_pos = end_pos
            else:
                self.black_king_pos = end_pos

        # Zorbist - przenoszenie figury + promocja
        nowa_figura = self.grid[er][ec]
        self.current_hash ^= ZOBRIST_PIECES[nowa_figura.type][nowa_figura.color][er][ec]

        # Zorbist wlaczanie roszad
        self.current_hash ^= self.get_castling_hash()

        # Dane do undo
        undo_data = {
            "captured": captured_piece,
            "moved": old_moved_status,
            "passant": old_enpassant_status,
            "hash": old_hash,
        }

        return undo_data

    def undo_move(self, start_pos: tuple[int, int], end_pos: tuple[int, int], undo_data: dict, move_type=MoveType.NORMAL):
        """Cofa ruch, przywracając zbitą figurę i flagi (moved, enpassant)."""
        sr, sc = start_pos
        er, ec = end_pos

        # Zorbist hash undo
        self.current_hash = undo_data["hash"]

        # Cofamy figure na pole startowe
        piece = self.grid[er][ec]
        piece.moved = undo_data["moved"]
        self.grid[sr][sc] = piece

        # Przywracamy flage enpassant
        self.enpassant_tile = undo_data["passant"]

        # Przywracamy figure na pole docelowe
        if move_type == MoveType.NORMAL:
            self.grid[er][ec] = undo_data["captured"]

        elif move_type == MoveType.CASTLING:
            # Cofamy wieze na jej miejsce
            self.grid[er][ec] = None
            if ec == 1:
                self.grid[sr][0] = self.grid[sr][2]
                self.grid[sr][2] = None
                self.grid[sr][0].moved = False
            elif ec == 5:
                self.grid[sr][7] = self.grid[sr][4]
                self.grid[sr][4] = None
                self.grid[sr][7].moved = False

        elif move_type.value >= 4:  # Promocja
            # Zamieniamy figure z powrotem na Piona
            self.grid[sr][sc] = Pawn(piece.color)
            self.grid[sr][sc].moved = undo_data["moved"]
            self.grid[er][ec] = undo_data["captured"]

        elif move_type == MoveType.EN_PASSANT:
            # Oddajemy piona na pole obok
            self.grid[sr][ec] = undo_data["captured"]
            self.grid[er][ec] = None

        if piece.type == PieceType.KING:
            if piece.color == Color.WHITE:
                self.white_king_pos = start_pos
            else:
                self.black_king_pos = start_pos

    def get_legal_moves(self, row: int, col: int) -> list[tuple]:
        """Zwraca listę legalnych ruchów (takich, które nie narażają króla na szach) i typ ruchu."""
        legal_moves = []
        piece = self.grid[row][col]
        pseudo_moves = piece.moves(self, row, col)
        start_pos = (row, col)
        piece_color = piece.color
        opp_color = Color.WHITE if piece_color == Color.BLACK else Color.BLACK

        promotes = [
            MoveType.PROMOTION_QUEEN, MoveType.PROMOTION_ROOK,
            MoveType.PROMOTION_BISHOP, MoveType.PROMOTION_KNIGHT
        ]

        # Funkcja pomocnicza: Zrob ruch -> Sprawdz krola czy nie w szachu -> Cofnij
        def is_safe(start_pos: tuple[int, int], end_pos: tuple[int, int], move_type: MoveType):
            undo_data = self.make_move(start_pos, end_pos, move_type)

            if piece_color == Color.WHITE:
                king_row, king_col = self.white_king_pos
            else:
                king_row, king_col = self.black_king_pos

            res = not self.is_tile_in_check(king_row, king_col, opp_color)
            self.undo_move(start_pos, end_pos, undo_data, move_type)
            return res

        for end_row, end_col in pseudo_moves:
            end_pos = (end_row, end_col)

            # Logika dla Piona (promocje i en passant)
            if piece.type == PieceType.PAWN:
                if end_row == 0 or end_row == 7:
                    for promoted in promotes:
                        if is_safe(start_pos, end_pos, promoted):
                            legal_moves.append((end_pos, promoted))
                elif self.grid[end_row][end_col] is None and col != end_col:  # czy zrobil en passant?
                    if is_safe(start_pos, end_pos, MoveType.EN_PASSANT):
                        legal_moves.append((end_pos, MoveType.EN_PASSANT))
                else:
                    if is_safe(start_pos, end_pos, MoveType.NORMAL):
                        legal_moves.append((end_pos, MoveType.NORMAL))

            # Logika dla Krola (roszady)
            elif piece.type == PieceType.KING:
                if abs(col - end_col) == 2:
                    if is_safe(start_pos, end_pos, MoveType.CASTLING):
                        legal_moves.append((end_pos, MoveType.CASTLING))
                else:
                    if is_safe(start_pos, end_pos, MoveType.NORMAL):
                        legal_moves.append((end_pos, MoveType.NORMAL))
            # Logika dla reszty
            else:
                if is_safe(start_pos, end_pos, MoveType.NORMAL):
                    legal_moves.append((end_pos, MoveType.NORMAL))

        return legal_moves

    def update_king_positions(self):
        """Ustala kordy dla kroli"""
        for r in range(8):
            for c in range(8):
                piece = self.grid[r][c]
                if piece is not None and piece.type == PieceType.KING:
                    if piece.color == Color.WHITE:
                        self.white_king_pos = (r, c)
                    else:
                        self.black_king_pos = (r, c)

    def game_status(self, king_color: Color) -> GameStatus:
        """Zwraca status gry dla danego koloru: normalnie, mat albo pat."""
        opp_color = Color.WHITE if king_color == Color.BLACK else Color.BLACK

        for row in range(8):
            for col in range(8):
                piece = self.grid[row][col]
                if piece is not None and piece.color == king_color and self.get_legal_moves(row, col):
                    return GameStatus.NORMAL

        if king_color == Color.WHITE:
            king_row, king_col = self.white_king_pos
        else:
            king_row, king_col = self.black_king_pos

        if self.is_tile_in_check(king_row, king_col, opp_color):
            return GameStatus.CHECKMATE
        return GameStatus.STALEMATE

    def all_legal_moves(self, color: Color) -> list[tuple[tuple, int]]:
        high_priority = []
        quiet_moves = []

        for row in range(8):
            for col in range(8):
                piece = self.grid[row][col]
                if piece is not None and piece.color == color:
                    moves = self.get_legal_moves(row, col)
                    for end_pos, move_type in moves:
                        score = self.tile_value(end_pos[0], end_pos[1], move_type)

                        move_data = ((row, col), end_pos, move_type)

                        if score > 0:
                            high_priority.append((move_data, score))
                        else:
                            quiet_moves.append((move_data, 0))

        high_priority.sort(key=lambda x: x[1], reverse=True)
        return high_priority + quiet_moves

    def tile_value(self, row: int, col: int, move_type: MoveType) -> int:
        points = 0
        piece = self.grid[row][col]
        if piece is not None:
            points += piece.point_value

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
                points += 1

        return points

    def update_zobrist_hash(self):
        """Liczy hash Zobrista od zera dla obecnego stanu planszy."""
        self.current_hash = 0

        # 1. Figury
        for r in range(8):
            for c in range(8):
                piece = self.grid[r][c]
                if piece is not None:
                    # Dodajemy figurę do hasha (operator XOR ^= )
                    self.current_hash ^= ZOBRIST_PIECES[piece.type][piece.color][r][c]

        # 2. En Passant
        if self.enpassant_tile is not None:
            kolumna = self.enpassant_tile[1]  # Bierzemy tylko kolumnę 'c'
            self.current_hash ^= ZOBRIST_ENPASSANT[kolumna]

        # 3. Prawa do roszady
        self.current_hash ^= self.get_castling_hash()

    def get_castling_hash(self) -> int:
        """Sprawdza na planszy, kto jeszcze nie ruszył królem/wieżą i zwraca ich hash."""
        h = 0
        white_king = self.grid[0][3]
        if white_king is not None and white_king.type == PieceType.KING and not white_king.moved:
            rook_q = self.grid[0][7]
            if rook_q is not None and rook_q.type == PieceType.ROOK and not rook_q.moved:
                h ^= ZOBRIST_CASTLING["WQ"]
            rook_k = self.grid[0][0]
            if rook_k is not None and rook_k.type == PieceType.ROOK and not rook_k.moved:
                h ^= ZOBRIST_CASTLING["WK"]

        black_king = self.grid[7][3]
        if black_king is not None and black_king.type == PieceType.KING and not black_king.moved:
            rook_q = self.grid[7][7]
            if rook_q is not None and rook_q.type == PieceType.ROOK and not rook_q.moved:
                h ^= ZOBRIST_CASTLING["BQ"]
            rook_k = self.grid[7][0]
            if rook_k is not None and rook_k.type == PieceType.ROOK and not rook_k.moved:
                h ^= ZOBRIST_CASTLING["BK"]
        return h

    def eval_position(self):
        res = 0
        for row in range(8):
            for col in range(8):
                piece = self.grid[row][col]
                if piece is not None:
                    res += piece.point_value * piece.color.value
        return res

    def material_on_board(self):
        res = 0
        for row in range(8):
            for col in range(8):
                piece = self.grid[row][col]
                if piece is not None:
                    res += piece.point_value
        return res