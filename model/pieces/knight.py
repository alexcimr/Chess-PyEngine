from model.enums import PieceType, Color

class Knight():
    point_value = 3
    def __init__(self, color: Color):
        self.type = PieceType.KNIGHT
        self.color = color
        self.moved = False

    def moves(self, board, row: int, col: int) -> list[tuple[int, int]]:
        """
        Returns a list of pseudo-legal destination squares.

        Jumps in an L-shape (±1, ±2) or (±2, ±1), ignores all pieces in
        between.  Cannot land on a friendly piece.
        Does NOT verify that the resulting position leaves the king out of check.
        """
        moves = []
        opp_color = Color.BLACK if self.color == Color.WHITE else Color.WHITE

        jumps = [
            (-2, -1), (-2, 1),
            (-1, -2), (-1, 2),
            (1, -2), (1, 2),
            (2, -1), (2, 1)
        ]
        for dr, dc in jumps:
            next_row = row + dr
            next_col = col + dc

            if board.is_empty(next_row, next_col):
                moves.append((next_row, next_col))
            elif board.get_piece_color(next_row, next_col) == opp_color:
                moves.append((next_row, next_col))

        return moves