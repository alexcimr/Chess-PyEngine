from model.enums import PieceType, Color
from model.board import Board

class King():
    def __init__(self, color: Color):
        self.type = PieceType.KING
        self.color = color
        self.moved = False
