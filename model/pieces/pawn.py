from model.enums import PieceType, Color
from model.utils import is_on_board

class Pawn():
    point_value = 1
    def __init__(self, color: Color):
        self.type = PieceType.PAWN
        self.color = color
        self.moved = False

    def moves(self, board, row: int, col: int) -> list[tuple[int, int]]:
        """
        Zwraca listę pseudo-legalnych ruchów.
        Uwzględnia zasady poruszania się figury i przeszkody,
        ale NIE sprawdza, czy ruch pozostawia króla pod szachem.
        Ruch specjalny: en passant (bicie w przelocie)
        """
        Moves = []
        move_value = self.color.value # -1 (czarne) or 1 (białe)
        opp_color = Color.BLACK if self.color == Color.WHITE else Color.WHITE

        # Bicie w prawo (z uwzglednieniem en passant)
        if is_on_board(row + move_value, col + 1):
            target_row = row + move_value
            target_col = col + 1
            tile = board.get_piece_color(target_row, target_col)
            if tile == opp_color:
                Moves.append((target_row, target_col))
            elif tile == None and board.enpassant_tile == (target_row, target_col):
                if board.get_piece_type(row, col + 1) == PieceType.PAWN and board.get_piece_color(row, col + 1) == opp_color:
                    Moves.append((target_row, target_col))
        # Bicie w lewo (z uwzglednieniem en passant)
        if is_on_board(row + move_value, col - 1):
            target_row = row + move_value
            target_col = col - 1
            tile = board.get_piece_color(target_row, target_col)
            if tile == opp_color:
                Moves.append((target_row, target_col))
            elif tile == None and board.enpassant_tile == (target_row, target_col):
                if board.get_piece_type(row, col - 1) == PieceType.PAWN and board.get_piece_color(row, col - 1) == opp_color:
                    Moves.append((target_row, target_col))

        # Pchanie
        if board.is_empty(row + move_value, col):
            Moves.append((row + move_value, col))

            if self.color == Color.WHITE and row == 1 and board.is_empty(row + 2, col):
                Moves.append((row + 2, col))

            if self.color == Color.BLACK and row == 6 and board.is_empty(row - 2, col):
                Moves.append((row - 2, col))

        return Moves
