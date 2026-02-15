from model.enums import PieceType, Color
from model.utils import is_on_board

class Pawn():
    def __init__(self, color: Color):
        self.type = PieceType.PAWN
        self.color = color
        self.moved = False
        self.enpassant_available = False

    def moves(self, board, row: int, col: int) -> list[tuple[int, int]]:
        """
        Zwraca listę pseudo-legalnych ruchówen.
        Uwzględnia zasady poruszania się figury i przeszkody,
        ale NIE sprawdza, czy ruch pozostawia króla pod szachem.
        Ruch specjalny: en passant (bicie w przelocie)
        """
        Moves = []
        move_value = self.color.value # -1 (czarne) or 1 (białe)
        opp_color = Color.BLACK if self.color == Color.WHITE else Color.WHITE

        # Pchanie
        if board.is_empty(row + move_value, col):
            Moves.append((row + move_value, col))

            if self.color == Color.WHITE and row == 1 and board.is_empty(row + 2, col):
                Moves.append((row + 2, col))

            if self.color == Color.BLACK and row == 6 and board.is_empty(row - 2, col):
                Moves.append((row - 2, col))

        # Bicie
        if is_on_board(row + move_value, col + 1):
            tile = board.get_piece_color(row + move_value, col + 1)
            if tile == opp_color:
                Moves.append((row + move_value, col + 1))
            # Enpassant
            elif tile == None and board.get_piece_type(row, col + 1) == PieceType.PAWN and board.grid[row][col + 1].enpassant_available:
                Moves.append((row + move_value, col + 1))
        # Bicie
        if is_on_board(row + move_value, col - 1):
            tile = board.get_piece_color(row + move_value, col - 1)
            if tile == opp_color:
                Moves.append((row + move_value, col - 1))
            # Enpassant
            elif tile == None and board.get_piece_type(row, col - 1) == PieceType.PAWN and board.grid[row][col - 1].enpassant_available:
                Moves.append((row + move_value, col - 1))

        return Moves