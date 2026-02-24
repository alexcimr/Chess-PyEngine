from model.enums import PieceType, Color

class Bishop():
    point_value = 3
    def __init__(self, color: Color):
        self.type = PieceType.BISHOP
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
        directions = [(-1, -1), (1, -1), (-1, 1), (1, 1)]

        for dr, dc in directions:
            k = 1
            while True:
                next_row = row + dr * k
                next_col = col + dc * k
                if board.is_empty(next_row, next_col):
                    Moves.append((next_row, next_col))
                elif board.get_piece_color(next_row, next_col) == opp_color:
                    Moves.append((next_row, next_col))
                    break
                else:
                    break
                k += 1

        return Moves

