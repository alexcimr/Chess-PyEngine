import random
from model.enums import PieceType, Color, MoveType, GameStatus
from model.pieces import Pawn, Rook, Knight, Bishop, Queen, King
from model.utils import is_on_board


# Zobrist hashing
random.seed(42)

# One random value per (piece_type, color, row, col)
ZOBRIST_PIECES = {}
for pt in PieceType:
    ZOBRIST_PIECES[pt] = {}
    for c in Color:
        ZOBRIST_PIECES[pt][c] = [[random.getrandbits(64) for _ in range(8)] for _ in range(8)]

# One value per file (column) representing the en-passant right
ZOBRIST_ENPASSANT = [random.getrandbits(64) for _ in range(8)]

# One value per castling right
ZOBRIST_CASTLING = {
    "WK": random.getrandbits(64),   # White king-side
    "WQ": random.getrandbits(64),   # White queen-side
    "BK": random.getrandbits(64),   # Black king-side
    "BQ": random.getrandbits(64),   # Black queen-side
}

class Board():
    def __init__(self) -> None:
        self.grid = [[None for _ in range(8)] for _ in range(8)]
        self.enpassant_tile = None  # Square that can be captured via en passant
        self.white_king_pos = None
        self.black_king_pos = None

        self.current_hash = 0 # Zorbist hash

    def clear_board(self) -> None:
        self.grid = [[None for _ in range(8)] for _ in range(8)]
        self.enpassant_tile = None
        self.white_king_pos = None
        self.black_king_pos = None
        self.current_hash = 0

    def setup_start_position(self) -> None:
        """Places all pieces in their standard chess starting positions."""
        self.clear_board()

        # --- White pieces ---
        self.grid[0][0] = Rook(Color.WHITE)
        self.grid[0][7] = Rook(Color.WHITE)
        self.grid[0][1] = Knight(Color.WHITE)
        self.grid[0][6] = Knight(Color.WHITE)
        self.grid[0][2] = Bishop(Color.WHITE)
        self.grid[0][5] = Bishop(Color.WHITE)
        self.grid[0][4] = Queen(Color.WHITE)
        self.grid[0][3] = King(Color.WHITE)
        for i in range(8):
            self.grid[1][i] = Pawn(Color.WHITE)

        # --- Black pieces ---
        self.grid[7][0] = Rook(Color.BLACK)
        self.grid[7][7] = Rook(Color.BLACK)
        self.grid[7][1] = Knight(Color.BLACK)
        self.grid[7][6] = Knight(Color.BLACK)
        self.grid[7][2] = Bishop(Color.BLACK)
        self.grid[7][5] = Bishop(Color.BLACK)
        self.grid[7][4] = Queen(Color.BLACK)
        self.grid[7][3] = King(Color.BLACK)

        for i in range(8):
            self.grid[6][i] = Pawn(Color.BLACK)

        self.update_king_positions()
        self.update_zobrist_hash()

    def is_empty(self, row: int, col: int) -> bool:
        """Returns True if the square is on the board and contains no piece."""
        if not is_on_board(row, col):
            return False

        return self.grid[row][col] is None

    def get_piece_type(self, row: int, col: int) -> PieceType | None:
        """Returns the type of the piece on the square, or None if empty/off-board."""
        if not is_on_board(row, col):
            return None

        piece = self.grid[row][col]
        if piece is None:
            return None
        return piece.type

    def get_piece_color(self, row: int, col: int) -> Color | None:
        """Returns the color of the piece on the square, or None if empty/off-board."""
        if not is_on_board(row, col):
            return None

        piece = self.grid[row][col]
        if piece is None:
            return None
        return piece.color


    def is_tile_in_check(self, row: int, col: int, attacking_color: Color) -> bool:
        """
        Returns True if the square (row, col) is attacked by any piece of
        attacking_color. Used for check detection and castling validation.
        """

        # Pawns
        for dc in [-1, 1]:
            r = row - attacking_color.value
            c = col + dc
            if 0 <= r < 8 and 0 <= c < 8:
                piece = self.grid[r][c]
                if piece is not None and piece.color == attacking_color and piece.type == PieceType.PAWN:
                    return True

        # Knigts
        knight_jumps = [
            (-2, -1), (-2, 1),
            (-1, -2), (-1, 2),
            (1, -2), (1, 2),
            (2, -1), (2, 1)
        ]
        for dr, dc in knight_jumps:
            r, c = row + dr, col + dc
            if 0 <= r < 8 and 0 <= c < 8:
                piece = self.grid[r][c]
                if piece is not None and piece.color == attacking_color and piece.type == PieceType.KNIGHT:
                    return True

        # Rooks + Queens
        straight_directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for dr, dc in straight_directions:
            r, c = row + dr, col + dc
            while 0 <= r < 8 and 0 <= c < 8:
                piece = self.grid[r][c]
                if piece is not None:
                    if piece.color == attacking_color and piece.type in (PieceType.ROOK, PieceType.QUEEN):
                        return True
                    break
                r += dr
                c += dc

        # Bishops + Queens
        diagonal_directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        for dr, dc in diagonal_directions:
            r, c = row + dr, col + dc
            while 0 <= r < 8 and 0 <= c < 8:
                piece = self.grid[r][c]
                if piece is not None:
                    if piece.color == attacking_color and piece.type in (PieceType.BISHOP, PieceType.QUEEN):
                        return True
                    break
                r += dr
                c += dc

        # King
        king_moves = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for dr, dc in king_moves:
            r, c = row + dr, col + dc
            if 0 <= r < 8 and 0 <= c < 8:
                piece = self.grid[r][c]
                if piece is not None and piece.color == attacking_color and piece.type == PieceType.KING:
                    return True

        return False


    def make_move(self, start_pos: tuple[int, int], end_pos: tuple[int, int], move_type: MoveType = MoveType.NORMAL) -> dict:
        """
        Applies a move to the board and returns an undo bundle.

        The undo bundle contains everything needed to restore the board to
        its exact state before this call.
        """
        sr, sc = start_pos
        er, ec = end_pos

        piece = self.grid[sr][sc]
        captured_piece = self.grid[er][ec]
        old_moved_status = piece.moved
        old_enpassant_status = self.enpassant_tile
        old_hash = self.current_hash

        # Zobrist: remove outgoing state
        self.current_hash ^= self.get_castling_hash()   # Remove old castling rights
        if self.enpassant_tile is not None:
            self.current_hash ^= ZOBRIST_ENPASSANT[self.enpassant_tile[1]]
        self.current_hash ^= ZOBRIST_PIECES[piece.type][piece.color][sr][sc]
        if captured_piece is not None:
            self.current_hash ^= ZOBRIST_PIECES[captured_piece.type][captured_piece.color][er][ec]

        # En-passant right: set when a pawn double-pushes
        if piece.type == PieceType.PAWN and abs(sr - er) == 2:
            self.enpassant_tile = ((sr + er) // 2, sc)  # Square behind the pawn
            self.current_hash ^= ZOBRIST_ENPASSANT[self.enpassant_tile[1]]
        else:
            self.enpassant_tile = None

        # Move the piece
        self.grid[er][ec] = piece
        self.grid[sr][sc] = None
        piece.moved = True

        # Special move handling
        if move_type == MoveType.PROMOTION_QUEEN:
            self.grid[er][ec] = Queen(piece.color)
            self.grid[er][ec].moved = True

        elif move_type == MoveType.CASTLING:
            # Move the rook to its post-castling square
            if ec == 1: # King-side: rook travels from col 0 to col 2
                self.grid[sr][2] = self.grid[sr][0]
                self.grid[sr][0] = None
                self.grid[sr][2].moved = True

                self.current_hash ^= ZOBRIST_PIECES[PieceType.ROOK][piece.color][sr][0]
                self.current_hash ^= ZOBRIST_PIECES[PieceType.ROOK][piece.color][sr][2]
            elif ec == 5:   # Queen-side: rook travels from col 7 to col 4
                self.grid[sr][4] = self.grid[sr][7]
                self.grid[sr][7] = None
                self.grid[sr][4].moved = True

                self.current_hash ^= ZOBRIST_PIECES[PieceType.ROOK][piece.color][sr][7]
                self.current_hash ^= ZOBRIST_PIECES[PieceType.ROOK][piece.color][sr][4]

        elif move_type == MoveType.PROMOTION_ROOK:
            self.grid[er][ec] = Rook(piece.color)
            self.grid[er][ec].moved = True

        elif move_type == MoveType.PROMOTION_BISHOP:
            self.grid[er][ec] = Bishop(piece.color)
            self.grid[er][ec].moved = True

        elif move_type == MoveType.PROMOTION_KNIGHT:
            self.grid[er][ec] = Knight(piece.color)
            self.grid[er][ec].moved = True

        elif move_type == MoveType.EN_PASSANT:
            # The captured pawn sits beside the moving pawn, not on end_pos
            captured_piece = self.grid[sr][ec]
            self.grid[sr][ec] = None
            self.current_hash ^= ZOBRIST_PIECES[captured_piece.type][captured_piece.color][sr][ec]

        if piece.type == PieceType.KING:
            if piece.color == Color.WHITE:
                self.white_king_pos = end_pos
            else:
                self.black_king_pos = end_pos

        # Zobrist: add incoming stat
        nowa_figura = self.grid[er][ec]
        self.current_hash ^= ZOBRIST_PIECES[nowa_figura.type][nowa_figura.color][er][ec]
        self.current_hash ^= self.get_castling_hash()

        undo_data = {
            "captured": captured_piece,
            "moved": old_moved_status,
            "passant": old_enpassant_status,
            "hash": old_hash,
        }

        return undo_data

    def undo_move(self, start_pos: tuple[int, int], end_pos: tuple[int, int], undo_data: dict, move_type: MoveType = MoveType.NORMAL) -> None:
        """
        Reverts a move using the bundle returned by make_move.

        Restores the piece, captured piece, en-passant flag, moved flag,
        and Zobrist hash to their pre-move values.
        """
        sr, sc = start_pos
        er, ec = end_pos

        # Restore the hash directly
        self.current_hash = undo_data["hash"]

        piece = self.grid[er][ec]
        piece.moved = undo_data["moved"]
        self.grid[sr][sc] = piece   # Move piece back to origin
        self.enpassant_tile = undo_data["passant"]

        if move_type == MoveType.NORMAL:
            self.grid[er][ec] = undo_data["captured"]

        elif move_type == MoveType.CASTLING:
            # Return the rook to its pre-castling square
            self.grid[er][ec] = None
            if ec == 1:
                self.grid[sr][0] = self.grid[sr][2]
                self.grid[sr][2] = None
                self.grid[sr][0].moved = False
            elif ec == 5:
                self.grid[sr][7] = self.grid[sr][4]
                self.grid[sr][4] = None
                self.grid[sr][7].moved = False

        elif move_type.value >= 4:  # Promocja
            # Replace promoted piece with a pawn again
            self.grid[sr][sc] = Pawn(piece.color)
            self.grid[sr][sc].moved = undo_data["moved"]
            self.grid[er][ec] = undo_data["captured"]

        elif move_type == MoveType.EN_PASSANT:
            # Re-place the captured pawn beside the moved pawn
            self.grid[sr][ec] = undo_data["captured"]
            self.grid[er][ec] = None

        # Update king position
        if piece.type == PieceType.KING:
            if piece.color == Color.WHITE:
                self.white_king_pos = start_pos
            else:
                self.black_king_pos = start_pos

    def get_legal_moves(self, row: int, col: int) -> list[tuple]:
        """
        Returns all fully legal moves for the piece on (row, col).

        A move is legal if it is pseudo-legal AND leaves the moving side's
        king out of check. The check is done by making the move, testing
        the king's square, then undoing the move.
        """
        legal_moves = []
        piece = self.grid[row][col]
        pseudo_moves = piece.moves(self, row, col)
        start_pos = (row, col)
        piece_color = piece.color
        opp_color = Color.WHITE if piece_color == Color.BLACK else Color.BLACK

        promotes = [
            MoveType.PROMOTION_QUEEN, MoveType.PROMOTION_ROOK,
            MoveType.PROMOTION_BISHOP, MoveType.PROMOTION_KNIGHT
        ]

        def is_safe(start_pos: tuple[int, int], end_pos: tuple[int, int], move_type: MoveType) -> bool:
            """Make move -> check if our king is safe -> undo."""
            undo_data = self.make_move(start_pos, end_pos, move_type)

            if piece_color == Color.WHITE:
                king_row, king_col = self.white_king_pos
            else:
                king_row, king_col = self.black_king_pos

            res = not self.is_tile_in_check(king_row, king_col, opp_color)
            self.undo_move(start_pos, end_pos, undo_data, move_type)
            return res

        for end_row, end_col in pseudo_moves:
            end_pos = (end_row, end_col)

            if piece.type == PieceType.PAWN:
                if end_row == 0 or end_row == 7:
                    # Pawn reached the back rank – generate all four promotions
                    for promoted in promotes:
                        if is_safe(start_pos, end_pos, promoted):
                            legal_moves.append((end_pos, promoted))
                elif self.grid[end_row][end_col] is None and col != end_col:
                    # Diagonal move to an empty square -> en passant
                    if is_safe(start_pos, end_pos, MoveType.EN_PASSANT):
                        legal_moves.append((end_pos, MoveType.EN_PASSANT))
                else:
                    if is_safe(start_pos, end_pos, MoveType.NORMAL):
                        legal_moves.append((end_pos, MoveType.NORMAL))

            elif piece.type == PieceType.KING:
                # King moves two squares -> castling
                if abs(col - end_col) == 2:
                    if is_safe(start_pos, end_pos, MoveType.CASTLING):
                        legal_moves.append((end_pos, MoveType.CASTLING))
                else:
                    if is_safe(start_pos, end_pos, MoveType.NORMAL):
                        legal_moves.append((end_pos, MoveType.NORMAL))
            else:
                if is_safe(start_pos, end_pos, MoveType.NORMAL):
                    legal_moves.append((end_pos, MoveType.NORMAL))

        return legal_moves

    def update_king_positions(self) -> None:
        """Scans the board and refreshes the cached king coordinates."""
        for r in range(8):
            for c in range(8):
                piece = self.grid[r][c]
                if piece is not None and piece.type == PieceType.KING:
                    if piece.color == Color.WHITE:
                        self.white_king_pos = (r, c)
                    else:
                        self.black_king_pos = (r, c)

    def game_status(self, king_color: Color) -> GameStatus:
        """
        Returns the game status from the perspective of king_color.

        If king_color has no legal moves:
        - Checkmate if the king is currently in check.
        - Stalemate otherwise.
        """
        opp_color = Color.WHITE if king_color == Color.BLACK else Color.BLACK

        for row in range(8):
            for col in range(8):
                piece = self.grid[row][col]
                if piece is not None and piece.color == king_color and self.get_legal_moves(row, col):
                    return GameStatus.NORMAL

        if king_color == Color.WHITE:
            king_row, king_col = self.white_king_pos
        else:
            king_row, king_col = self.black_king_pos

        if self.is_tile_in_check(king_row, king_col, opp_color):
            return GameStatus.CHECKMATE
        return GameStatus.STALEMATE

    def all_legal_moves(self, color: Color) -> list[tuple[tuple, int]]:
        """
        Returns all legal moves for all pieces of the given color.

        Moves that win material (captures, promotions) are sorted first
        to improve alpha-beta pruning efficiency.
        """
        high_priority = []
        quiet_moves = []

        for row in range(8):
            for col in range(8):
                piece = self.grid[row][col]
                if piece is not None and piece.color == color:
                    moves = self.get_legal_moves(row, col)
                    for end_pos, move_type in moves:
                        score = self.tile_value(end_pos[0], end_pos[1], move_type)

                        move_data = ((row, col), end_pos, move_type)

                        if score > 0:
                            high_priority.append((move_data, score))
                        else:
                            quiet_moves.append((move_data, 0))

        high_priority.sort(key=lambda x: x[1], reverse=True)
        return high_priority + quiet_moves

    def tile_value(self, row: int, col: int, move_type: MoveType) -> int:
        """
        Heuristic score for move ordering.

        Captures and promotions receive positive scores so they are
        searched before quiet moves, improving alpha-beta pruning.
        """
        points = 0
        piece = self.grid[row][col]
        if piece is not None:
            points += piece.point_value  # Value of the captured piece

        if move_type.value >= 3:
            if move_type == MoveType.PROMOTION_QUEEN:
                points += 8
            elif move_type == MoveType.PROMOTION_ROOK:
                points += 4
            elif move_type == MoveType.PROMOTION_BISHOP:
                points += 2
            elif move_type == MoveType.PROMOTION_KNIGHT:
                points += 2
            elif move_type == MoveType.EN_PASSANT:
                points += 1

        return points

    def update_zobrist_hash(self) -> None:
        """
        Recomputes the Zobrist hash from scratch.

        Should only be called once after board setup or when loading a
        position. During play the hash is maintained incrementally in
        make_move / undo_move.
        """
        self.current_hash = 0

        for r in range(8):
            for c in range(8):
                piece = self.grid[r][c]
                if piece is not None:
                    self.current_hash ^= ZOBRIST_PIECES[piece.type][piece.color][r][c]

        if self.enpassant_tile is not None:
            kolumna = self.enpassant_tile[1]
            self.current_hash ^= ZOBRIST_ENPASSANT[kolumna]

        self.current_hash ^= self.get_castling_hash()

    def get_castling_hash(self) -> int:
        """
        Returns the XOR of Zobrist values for all currently available
        castling rights, determined by whether kings and rooks have moved.
        """
        h = 0
        white_king = self.grid[0][3]
        if white_king is not None and white_king.type == PieceType.KING and not white_king.moved:
            rook_q = self.grid[0][7]
            if rook_q is not None and rook_q.type == PieceType.ROOK and not rook_q.moved:
                h ^= ZOBRIST_CASTLING["WQ"]
            rook_k = self.grid[0][0]
            if rook_k is not None and rook_k.type == PieceType.ROOK and not rook_k.moved:
                h ^= ZOBRIST_CASTLING["WK"]

        black_king = self.grid[7][3]
        if black_king is not None and black_king.type == PieceType.KING and not black_king.moved:
            rook_q = self.grid[7][7]
            if rook_q is not None and rook_q.type == PieceType.ROOK and not rook_q.moved:
                h ^= ZOBRIST_CASTLING["BQ"]
            rook_k = self.grid[7][0]
            if rook_k is not None and rook_k.type == PieceType.ROOK and not rook_k.moved:
                h ^= ZOBRIST_CASTLING["BK"]
        return h

    def eval_position(self) -> float:
        """
        Simple material-only evaluation.
        White: +
        Black: -.
        """
        res = 0
        for row in range(8):
            for col in range(8):
                piece = self.grid[row][col]
                if piece is not None:
                    res += piece.point_value * piece.color.value
        return res

    def material_on_board(self) -> int:
        """Returns the total material (sum of point values) still on the board."""
        res = 0
        for row in range(8):
            for col in range(8):
                piece = self.grid[row][col]
                if piece is not None:
                    res += piece.point_value
        return res