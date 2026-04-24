import json
import os
import random

from model.board import Board
from model.enums import PieceType, Color, MoveType, Zobrist, Phase

OPENING_THRESHOLD = 55
MIDGAME_THRESHOLD = 20

class Bot():
    def __init__(self, board: Board) -> None:
        self.board = board
        self.rng = random.Random()
        # Separate transposition tables
        self.tt_white = {}
        self.tt_black = {}

        self.opening_book = {}
        self.pst = {}
        self.current_pst = {}

        
        base_dir = os.path.dirname(os.path.dirname(__file__))
        book_path = os.path.join(base_dir, "data", "book.json")
        pst_path = os.path.join(base_dir, "data", "pst.json")

        with open(book_path, "r") as f:
            self.opening_book = json.load(f)

        with open(pst_path, "r") as f:
            raw = json.load(f)

        self.pst = {}
        for phase, colors in raw.items():
            self.pst[Phase(phase)] = {}
            for color, pieces in colors.items():
                self.pst[Phase(phase)][Color(int(color))] = {}
                for piece, table in pieces.items():
                    self.pst[Phase(phase)][Color(int(color))][PieceType(piece)] = table


    def eval_position(self) -> float:
        """
        Full static evaluation of the current board position.
        Combines material balance and piece-square table (PST) bonuses.
        White: +
        Black: -
        """
        res = 0
        for row in range(8):
            for col in range(8):
                piece = self.board.grid[row][col]
                if piece is not None:
                    res += piece.point_value * piece.color.value  # +1 White, -1 Black
                    res += self.current_pst[piece.color][piece.type][row][col] * piece.color.value
        return res

    def eval_table_diff(self, start_pos: tuple[int, int], end_pos: tuple[int, int], move_type: MoveType) -> int:
        """
        Returns the incremental change in piece-square evaluation caused by
        a single move. Much faster than re-evaluating the full board.
        """
        sr, sc = start_pos
        er, ec = end_pos
        piece = self.board.grid[sr][sc]
        color = piece.color
        opp_piece = self.board.grid[er][ec]

        # Determine which PST to use on the destination square
        if move_type == MoveType.PROMOTION_QUEEN:
            diff = self.current_pst[color][PieceType.QUEEN][er][ec] - self.current_pst[color][piece.type][sr][sc]
        elif move_type == MoveType.PROMOTION_ROOK:
            diff = self.current_pst[color][PieceType.ROOK][er][ec] - self.current_pst[color][piece.type][sr][sc]
        elif move_type == MoveType.PROMOTION_BISHOP:
            diff = self.current_pst[color][PieceType.BISHOP][er][ec] - self.current_pst[color][piece.type][sr][sc]
        elif move_type == MoveType.PROMOTION_KNIGHT:
            diff = self.current_pst[color][PieceType.KNIGHT][er][ec] - self.current_pst[color][piece.type][sr][sc]
        else:
            diff = self.current_pst[color][piece.type][er][ec] - self.current_pst[color][piece.type][sr][sc]

        diff *= color.value

        # Remove PST contribution of a captured piece
        if opp_piece is not None:
            diff -= self.current_pst[opp_piece.color][opp_piece.type][er][ec] * opp_piece.color.value

        if move_type == MoveType.CASTLING:
            if ec == 1:     # King-side
                diff += color.value * (self.current_pst[color][PieceType.ROOK][sr][2]- self.current_pst[color][PieceType.ROOK][sr][0])
            elif ec == 5:   # Queen-side
                diff += color.value * (self.current_pst[color][PieceType.ROOK][sr][4]- self.current_pst[color][PieceType.ROOK][sr][7])

        # En passant: the captured pawn is on a different square than end_pos
        elif move_type == MoveType.EN_PASSANT:
            captured_pawn = self.board.grid[sr][ec]
            diff -= self.current_pst[captured_pawn.color][captured_pawn.type][sr][ec] * captured_pawn.color.value

        return diff

    def minimax(self, depth: int, pos_eval: float, maximazing_color: Color, alfa: float, beta: float) -> float:
        """
        Minimax search with alpha-beta pruning and Zobrist transposition tables.

        Args:
            depth:            Remaining half-moves to search.
            pos_eval:         Incrementally maintained evaluation of current position.
            maximazing_color: The side to move.
            alfa:             Best score White can guarantee (lower bound).
            beta:             Best score Black can guarantee (upper bound).

        Returns:
            The evaluated score for the current position.
        """
        if depth == 0:
            return pos_eval

        # Transposition table lookup
        zhash = self.board.current_hash
        tt = self.tt_white if maximazing_color == Color.WHITE else self.tt_black

        if zhash in tt:
            stored_depth, stored_eval, flag = tt[zhash]
            if stored_depth >= depth:
                if flag == Zobrist.EXACT:
                    return stored_eval
                elif flag == Zobrist.LOWERBOUND:
                    alfa = max(alfa, stored_eval)
                elif flag == Zobrist.UPPERBOUND:
                    beta = min(beta, stored_eval)

                if alfa >= beta:
                    return stored_eval

        orig_alfa = alfa
        orig_beta = beta

        moves = self.board.all_legal_moves(maximazing_color)

        # Checks for checkmate or stalemate
        if not moves:
            if maximazing_color == Color.WHITE:
                king_row, king_col = self.board.white_king_pos
            else:
                king_row, king_col = self.board.black_king_pos

            incheck = self.board.is_tile_in_check(king_row, king_col,
                    Color.WHITE if maximazing_color == Color.BLACK else Color.BLACK)
            if incheck:
                # Penalise deeper mates slightly less so the engine prefers faster mates
                return - (10000 + depth) * maximazing_color.value
            else:
                return 0    # Stalemate

        if maximazing_color == Color.WHITE:
            maxEval = -float('inf')
            for move, score in moves:
                curr_eval = pos_eval + score + self.eval_table_diff(*move)

                undo_data = self.board.make_move(*move)

                eval = self.minimax(depth - 1, curr_eval, Color.BLACK, alfa, beta)
                maxEval = max(maxEval, eval)

                self.board.undo_move(move[0], move[1], undo_data, move[2])

                alfa = max(alfa, eval)
                if beta <= alfa:
                    break   # Beta cutoff

            # Store result in transposition table
            if maxEval <= orig_alfa:
                tt[zhash] = (depth, maxEval, Zobrist.UPPERBOUND)
            elif maxEval >= orig_beta:
                tt[zhash] = (depth, maxEval, Zobrist.LOWERBOUND)
            else:
                tt[zhash] = (depth, maxEval, Zobrist.EXACT)

            return maxEval

        elif maximazing_color == Color.BLACK:
            minEval = float('inf')
            for move, score in moves:
                curr_eval = pos_eval - score + self.eval_table_diff(*move)
                undo_data = self.board.make_move(*move)

                eval = self.minimax(depth - 1, curr_eval, Color.WHITE, alfa, beta)
                minEval = min(minEval, eval)

                self.board.undo_move(move[0], move[1], undo_data, move[2])

                beta = min(beta, eval)
                if beta <= alfa:
                    break   # Alpha cutoff

            # Store result in transposition table
            if minEval >= orig_beta:
                tt[zhash] = (depth, minEval, Zobrist.LOWERBOUND)
            elif minEval <= orig_alfa:
                tt[zhash] = (depth, minEval, Zobrist.UPPERBOUND)
            else:
                tt[zhash] = (depth, minEval, Zobrist.EXACT)

            return minEval

    def best_move(self, depth: int, maximazing_color: Color) -> tuple:
        """
        Returns the best move for the given side at the requested search depth.
        Checks the opening book first before running the full minimax search.
        """
        self.board.update_zobrist_hash()

        # Use opening book if the current position is known
        book_move = self.get_book_move(maximazing_color)
        if book_move:
            return book_move

        # Set PST for the current game phase
        self.current_pst = self.pst[self.get_phase()]

        alfa = -float('inf')
        beta = float('inf')
        pos_eval = self.eval_position()
        self.board.update_king_positions()
        moves = self.board.all_legal_moves(maximazing_color)

        if not moves:
            return None

        # Clear transposition tables at the start of each new search
        self.tt_white.clear()
        self.tt_black.clear()

        best_move = moves[0][0]
        if maximazing_color == Color.WHITE:
            maxEval = -float('inf')
            for move, score in moves:
                curr_eval = pos_eval + score + self.eval_table_diff(*move)
                undo_data = self.board.make_move(*move)

                eval = self.minimax(depth - 1, curr_eval, Color.BLACK, alfa, beta)

                if eval > maxEval:
                    maxEval = eval
                    best_move = move

                self.board.undo_move(move[0], move[1], undo_data, move[2])

                alfa = max(alfa, eval)

        elif maximazing_color == Color.BLACK:
            minEval = float('inf')
            for move, score in moves:
                curr_eval = pos_eval - score + self.eval_table_diff(*move)
                undo_data = self.board.make_move(*move)

                eval = self.minimax(depth - 1, curr_eval, Color.WHITE, alfa, beta)

                if eval < minEval:
                    minEval = eval
                    best_move = move

                self.board.undo_move(move[0], move[1], undo_data, move[2])

                beta = min(beta, eval)

        return best_move

    def get_book_move(self, color: Color) -> tuple | None:
        """
        Looks up the current position in the opening book and returns a
        weighted-random move, or None if the position is not in the book.
        """
        side = "white" if color == Color.WHITE else "black"
        zhash_str = str(self.board.current_hash)

        book_for_side = self.opening_book[side]
        if zhash_str in book_for_side:
            moves_dict = book_for_side[zhash_str]
            possible_moves = list(moves_dict.keys())
            weights = list(moves_dict.values())

            # Pick a move at random, weighted by how often it was played in the dataset
            chosen_str = self.rng.choices(possible_moves, weights=weights, k=1)[0]
            sr, sc, er, ec, mt = (int(chosen_str[i]) for i in range(5))
            return ((sr, sc), (er, ec), MoveType(mt))

        return None

    def get_phase(self) -> Phase:
        material = self.board.material_on_board()
        if material >= OPENING_THRESHOLD:
            return Phase.OPENING
        elif material >= MIDGAME_THRESHOLD:
            return Phase.MIDGAME
        return Phase.ENDGAME
