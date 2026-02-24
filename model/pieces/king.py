from model.enums import PieceType, Color

class King():
    point_value = 0
    def __init__(self, color: Color):
        self.type = PieceType.KING
        self.color = color
        self.moved = False

    def moves(self, board, row: int, col: int) -> list[tuple[int, int]]:
        """
        Zwraca listę pseudo-legalnych ruchów + .
        Uwzględnia zasady poruszania się figury i przeszkody,
        ale NIE sprawdza, czy ruch pozostawia króla pod szachem.
        Ruch specjalny: roszada (ruch krolem o dwa pola)
        """
        Moves = []
        opp_color = Color.BLACK if self.color == Color.WHITE else Color.WHITE

        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1), (-1, 0), (1, 0), (0, -1), (0, 1)]
        for dr, dc in directions:
            next_row = row + dr
            next_col = col + dc

            if board.is_empty(next_row, next_col):
                Moves.append((next_row, next_col))
            elif board.get_piece_color(next_row, next_col) == opp_color:
                Moves.append((next_row, next_col))

        # Roszada
        if not self.moved and not board.is_tile_in_check(row, col, opp_color):

            # Krotka roszada
            if board.get_piece_type(row, 0) == PieceType.ROOK and not board.grid[row][0].moved:
                if board.is_empty(row, 1) and board.is_empty(row, 2):
                    if not board.is_tile_in_check(row, 1, opp_color) and not board.is_tile_in_check(row, 2, opp_color):
                        Moves.append((row, 1))

            # Dluga roszada

            if board.get_piece_type(row, 7) == PieceType.ROOK and not board.grid[row][7].moved:
                if board.is_empty(row, 4) and board.is_empty(row, 5) and board.is_empty(row, 6):
                    if not board.is_tile_in_check(row, 4, opp_color) and not board.is_tile_in_check(row, 5, opp_color):
                        Moves.append((row, 5))

        return Moves
