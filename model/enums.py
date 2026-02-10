from enum import Enum

class Color(Enum):
    WHITE = 1
    BLACK = -1

class PieceType(Enum):
    KING = "K"
    QUEEN = "Q"
    ROOK = "R"
    BISHOP = "B"
    KNIGHT = "N"
    PAWN = "P"

class MoveType(Enum):
    ORDINARY = 1
    CASTLING = 2
    ENPASSANT = 3
    PROMOTION = 4
