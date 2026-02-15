from model.enums import PieceType, Color

class Knight():
    def __init__(self, color: Color):
        self.type = PieceType.KNIGHT
        self.color = color
        self.moved = False

    def moves(self, board, row: int, col: int) -> list[tuple[int, int]]:
        """
        Zwraca listę pseudo-legalnych ruchów.
        Uwzględnia zasady poruszania się figury i przeszkody,
        ale NIE sprawdza, czy ruch pozostawia króla pod szachem.
        """
        Moves = []
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
                Moves.append((next_row, next_col))
            elif board.get_piece_color(next_row, next_col) == opp_color:
                Moves.append((next_row, next_col))

        return Moves