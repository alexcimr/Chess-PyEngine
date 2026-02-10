from model.enums import PieceType, Color, MoveType
from model.pieces import Pawn, Rook, Knight, Bishop, Queen, King
from model.utils import is_on_board

class Board():
    def __init__(self):
        self.grid = [[None for _ in range(8)] for _ in range(8)]

    def clear_board(self):
        self.grid = [[None for _ in range(8)] for _ in range(8)]

    def setup_start_position(self):
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
        """Sprawdza współrzędne pola i czy jest puste"""
        if not is_on_board(row, col):
            return False

        return self.grid[row][col] == None


    def get_piece_type(self, row, col):
        """Zwraca typ figury lub None lub False"""
        if not is_on_board(row, col):
            return False

        piece = self.grid[row][col]
        if piece == None:
            return None
        return piece.type

    def get_piece_color(self, row, col):
        """Zwraca kolor figury lub None lub False"""
        if not is_on_board(row, col):
            return False

        piece = self.grid[row][col]
        if piece == None:
            return None
        return piece.color

    def is_tile_in_check(self, row, col, attacking_color):
        """Sprawdza czy dane pole jest atakowane True/False"""
        for r in range(8):
            for c in range(8):
                piece = self.grid[r][c]
                if self.get_piece_color(r, c) == attacking_color:
                    # Problem z rekurencja króla
                    if self.get_piece_type(r, c) == PieceType.KING:
                        if abs(c - col) <= 1 and abs(r - row) <= 1:
                            return True
                    # Problem z pionem jak tylko pchamy go
                    elif self.get_piece_type(r, c) == PieceType.PAWN:
                        pawn_attack = attacking_color.value
                        if r + pawn_attack == row and abs(c - col) == 1:
                            return True
                    # Reszta figur
                    else:
                        pseudo_moves = piece.moves(self, r, c)
                        if (row, col) in pseudo_moves:
                            return True
        return False

    def move_to(self, row, col, new_row, new_col):
        raise ("not implemented")
    def undo_move(self):
        raise("not implemented")
    def get_legal_moves(self, row, col):
        """Zwraca wszystkie legalne ruchy dla danej figury,
         tzn takie w ktorych krol nie bedzie w szachu"""
        piece = self.grid[row][col]
        pseudo_moves = piece.moves(self, row, col)

        raise ("not implemented")



