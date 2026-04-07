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
    NORMAL = 1
    CASTLING = 2
    EN_PASSANT = 3
    PROMOTION_QUEEN = 4
    PROMOTION_ROOK = 5
    PROMOTION_BISHOP = 6
    PROMOTION_KNIGHT = 7

class GameStatus(Enum):
    NORMAL = 1
    CHECKMATE = 2
    STALEMATE = 3

class Zorbist(Enum):
    EXACT = 1
    UPPERBOUND = 2
    LOWERBOUND = 3