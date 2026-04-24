from model.enums import PieceType, Color

class Rook():
    point_value = 5
    def __init__(self, color: Color):
        self.type = PieceType.ROOK
        self.color = color
        self.moved = False

    def moves(self, board, row: int, col: int) -> list[tuple[int, int]]:
        """
        Returns a list of pseudo-legal destination squares.

        Slides along ranks and files until it hits the board edge,
        a friendly piece (excluded) or an enemy piece (included – capture).
        Does NOT verify that the resulting position leaves the king out of check.
        """
        moves = []
        opp_color = Color.BLACK if self.color == Color.WHITE else Color.WHITE
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        for dr, dc in directions:
            k = 1
            while True:
                next_row = row + dr * k
                next_col = col + dc * k
                if board.is_empty(next_row, next_col):
                    moves.append((next_row, next_col))
                elif board.get_piece_color(next_row, next_col) == opp_color:
                    moves.append((next_row, next_col))
                    break
                else:
                    break
                k += 1

        return moves
