from model.enums import PieceType, Color
from model.board import Board

class Knight():
    def __init__(self, color: Color):
        self.type = PieceType.KNIGHT
        self.color = color
