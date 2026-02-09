from model.enums import PieceType, Color
from model.board import Board

class Bishop():
    def __init__(self, color: Color):
        self.type = PieceType.BISHOP
        self.color = color
