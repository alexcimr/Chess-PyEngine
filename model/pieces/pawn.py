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
        Returns a list of pseudo-legal destination squares.

        Covers forward pushes (one or two squares from the starting rank),
        diagonal captures, and en-passant captures.
        Does NOT verify that the resulting position leaves the king out of check.
        """
        moves = []
        move_value = self.color.value  # color.value is +1 for White and -1 for Black
        opp_color = Color.BLACK if self.color == Color.WHITE else Color.WHITE

        # Diagonal captures (including en passant)
        for dc in (-1, 1):
            target_row = row + move_value
            target_col = col + dc
            if not is_on_board(target_row, target_col):
                continue

            if board.get_piece_color(target_row, target_col) == opp_color:
                # Normal capture
                moves.append((target_row, target_col))
            elif (board.enpassant_tile == (target_row, target_col)
                  and board.get_piece_type(row, target_col) == PieceType.PAWN
                  and board.get_piece_color(row, target_col) == opp_color):
                # En passant: the captured pawn sits beside us on the same rank
                moves.append((target_row, target_col))

        # Forward push
        if board.is_empty(row + move_value, col):
            moves.append((row + move_value, col))

            # Double push from the starting rank
            if self.color == Color.WHITE and row == 1 and board.is_empty(row + 2, col):
                moves.append((row + 2, col))

            if self.color == Color.BLACK and row == 6 and board.is_empty(row - 2, col):
                moves.append((row - 2, col))

        return moves
