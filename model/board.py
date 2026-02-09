from model.enums import PieceType, Color
from model.pieces import Pawn, Rook, Knight, Bishop, Queen, King

class Board():
    def __init__(self):
        self.grid = [[None for _ in range(8)] for _ in range(8)]

    def setup_start_position(self):
        # Biale
        self.grid[0][0] = Rook(Color.WHITE)
        self.grid[0][7] = Rook(Color.WHITE)

