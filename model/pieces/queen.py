from model.enums import PieceType, Color
from model.board import Board

class Queen():
    def __init__(self, color: Color):
        self.type = PieceType.QUEEN
        self.color = color
