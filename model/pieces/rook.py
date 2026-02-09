from model.enums import PieceType, Color
from model.board import Board

class Rook():
    def __init__(self, color: Color):
        self.type = PieceType.ROOK
        self.color = color
