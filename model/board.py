from model.enums import PieceType, Color, MoveType, GameStatus
from model.pieces import Pawn, Rook, Knight, Bishop, Queen, King
from model.utils import is_on_board


class Board():
    def __init__(self):
        self.grid = [[None for _ in range(8)] for _ in range(8)]
        self.enpassant_tile = None # Puste pole ktore można zbić pionkim

    def clear_board(self):
        self.grid = [[None for _ in range(8)] for _ in range(8)]
        self.enpassant_tile = None

    def setup_start_position(self):
        """Ustawia figury na pozycjach startowych dla nowej gry."""
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

    def is_empty(self, row, col):
        """Zwraca True, jeśli pole jest na planszy i jest puste."""
        if not is_on_board(row, col):
            return False

        return self.grid[row][col] == None

    def get_piece_type(self, row, col):
        """Zwraca typ figury lub None, jeśli pole puste."""
        if not is_on_board(row, col):
            return None

        piece = self.grid[row][col]
        if piece == None:
            return None
        return piece.type

    def get_piece_color(self, row, col):
        """Zwraca kolor figury lub None, jeśli pole puste."""
        if not is_on_board(row, col):
            return None

        piece = self.grid[row][col]
        if piece == None:
            return None
        return piece.color

    def is_tile_in_check(self, row, col, attacking_color: Color):
        """Sprawdza, czy pole (row, col) jest atakowane przez dany kolor. Zwraca True lub False."""
        # Sprawdzamy cala plansze w poszukiwaniu ataków
        for r in range(8):
            for c in range(8):
                piece = self.grid[r][c]
                if self.get_piece_color(r, c) == attacking_color:
                    # Problem z rekurencja króla (wywoływanie king.moves())
                    if self.get_piece_type(r, c) == PieceType.KING:
                        if abs(c - col) <= 1 and abs(r - row) <= 1:
                            return True
                    # Problem z pionem jak tylko pchamy go
                    elif self.get_piece_type(r, c) == PieceType.PAWN:
                        pawn_attack = attacking_color.value
                        if r + pawn_attack == row and abs(c - col) == 1:
                            return True
                    # Reszta figur, logika -> .moves()
                    else:
                        pseudo_moves = piece.moves(self, r, c)
                        if (row, col) in pseudo_moves:
                            return True
        return False

    def make_move(self, start_pos, end_pos, move_type=MoveType.NORMAL):
        """Robi ruch na planszy i zwraca stare wartosci potrzebne do undo."""
        sr, sc = start_pos
        er, ec = end_pos

        # Pobieramy figure i zapisujemy stany do cofniecia
        piece = self.grid[sr][sc]
        captured_piece = self.grid[er][ec]
        old_moved_status = piece.moved
        old_enpassant_status = self.enpassant_tile

        # Ustawiamy enpassant jesli pion skacze o 2 pola
        if piece.type == PieceType.PAWN and abs(sr - er) == 2:
            self.enpassant_tile = ((sr + er) // 2, sc) # Pole za pionkiem
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
            elif ec == 5:
                self.grid[sr][4] = self.grid[sr][7]
                self.grid[sr][7] = None
                self.grid[sr][4].moved = True
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

        # Dane do undo
        return captured_piece, old_moved_status, old_enpassant_status

    def undo_move(self, start_pos, end_pos, captured_piece, old_moved_status, old_enpassant_status,
                  move_type=MoveType.NORMAL):
        """Cofa ruch, przywracając zbitą figurę i flagi (moved, enpassant)."""
        sr, sc = start_pos
        er, ec = end_pos

        # Cofamy figure na pole startowe
        piece = self.grid[er][ec]
        piece.moved = old_moved_status
        self.grid[sr][sc] = piece

        # Przywracamy flage enpassant
        self.enpassant_tile = old_enpassant_status

        # Przywracamy figure na pole docelowe
        if move_type == MoveType.NORMAL:
            self.grid[er][ec] = captured_piece

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
            self.grid[sr][sc].moved = old_moved_status
            self.grid[er][ec] = captured_piece

        elif move_type == MoveType.EN_PASSANT:
            # Oddajemy piona na pole obok
            self.grid[sr][ec] = captured_piece
            self.grid[er][ec] = None

    def get_legal_moves(self, row, col):
        """Zwraca listę legalnych ruchów (takich, które nie narażają króla na szach) i typ ruchu."""
        Legal_moves = []
        piece = self.grid[row][col]
        pseudo_moves = piece.moves(self, row, col)
        start_pos = (row, col)
        piece_color = piece.color
        opp_color = Color.WHITE if piece_color == Color.BLACK else Color.BLACK

        Promotes = [
            MoveType.PROMOTION_QUEEN, MoveType.PROMOTION_ROOK,
            MoveType.PROMOTION_BISHOP, MoveType.PROMOTION_KNIGHT
        ]

        # Funkcja pomocnicza: Zrob ruch -> Sprawdz krola czy nie w szachu -> Cofnij
        def is_safe(start_pos, end_pos, move_type):
            captured_piece, old_moved_status, old_enpassant_status = self.make_move(start_pos, end_pos, move_type)
            king_row, king_col = self.king_finder(piece_color)
            res = not self.is_tile_in_check(king_row, king_col, opp_color)
            self.undo_move(start_pos, end_pos, captured_piece, old_moved_status, old_enpassant_status, move_type)
            return res

        for end_row, end_col in pseudo_moves:
            end_pos = (end_row, end_col)

            # Logika dla Piona (promocje i en passant)
            if piece.type == PieceType.PAWN:
                if end_row == 0 or end_row == 7:
                    for promoted in Promotes:
                        if is_safe(start_pos, end_pos, promoted):
                            Legal_moves.append((end_pos, promoted))
                elif self.grid[end_row][end_col] == None and col != end_col:  # czy zrobil en passant?
                    if is_safe(start_pos, end_pos, MoveType.EN_PASSANT):
                        Legal_moves.append((end_pos, MoveType.EN_PASSANT))
                else:
                    if is_safe(start_pos, end_pos, MoveType.NORMAL):
                        Legal_moves.append((end_pos, MoveType.NORMAL))

            # Logika dla Krola (roszady)
            elif piece.type == PieceType.KING:
                if abs(col - end_col) == 2:
                    if is_safe(start_pos, end_pos, MoveType.CASTLING):
                        Legal_moves.append((end_pos, MoveType.CASTLING))
                else:
                    if is_safe(start_pos, end_pos, MoveType.NORMAL):
                        Legal_moves.append((end_pos, MoveType.NORMAL))
            # Logika dla reszty
            else:
                if is_safe(start_pos, end_pos, MoveType.NORMAL):
                    Legal_moves.append((end_pos, MoveType.NORMAL))

        return Legal_moves

    def king_finder(self, color: Color):
        """Znajduje pozycję (row, col) króla danego koloru."""
        for row in range(8):
            for col in range(8):
                if self.get_piece_type(row, col) == PieceType.KING and self.get_piece_color(row, col) == color:
                    return (row, col)

    def game_status(self, king_color: Color):
        """Zwraca status gry dla danego koloru: normalnie, mat albo pat."""
        opp_color = Color.WHITE if king_color == Color.BLACK else Color.BLACK

        for row in range(8):
            for col in range(8):
                if self.get_piece_color(row, col) == king_color and self.get_legal_moves(row, col):
                    return GameStatus.NORMAL

        king_row, king_col = self.king_finder(king_color)
        if self.is_tile_in_check(king_row, king_col, opp_color):
            return GameStatus.CHECKMATE
        return GameStatus.STALEMATE







