import json
import os
import random
from model.board import Board
from model.enums import PieceType, Color, MoveType, GameStatus, Zorbist
from model.pst import EVAL_TABLE


class Bot():
    def __init__(self, board: Board):
        self.board = board
        # Zorbist
        self.tt_white = {}
        self.tt_black = {}

        self.opening_book = {}
        base_dir = os.path.dirname(os.path.dirname(__file__))
        book_path = os.path.join(base_dir, "data", "book.json")

        with open(book_path, "r") as f:
            self.opening_book = json.load(f)

    def eval_position(self):
        res = 0
        for row in range(8):
            for col in range(8):
                piece = self.board.grid[row][col]
                if piece is not None:
                    res += piece.point_value * piece.color.value  # 1 or -1
                    res += EVAL_TABLE[piece.color][piece.type][row][col]
        return res

    def eval_table_diff(self, start_pos: tuple[int, int], end_pos: tuple[int, int], move_type: MoveType) -> int:
        sr, sc = start_pos
        er, ec = end_pos
        piece = self.board.grid[sr][sc]
        color = piece.color
        opp_piece = self.board.grid[er][ec]

        if move_type == MoveType.PROMOTION_QUEEN:
            diff = EVAL_TABLE[color][PieceType.QUEEN][er][ec] - EVAL_TABLE[color][piece.type][sr][sc]
        elif move_type == MoveType.PROMOTION_ROOK:
            diff = EVAL_TABLE[color][PieceType.ROOK][er][ec] - EVAL_TABLE[color][piece.type][sr][sc]
        elif move_type == MoveType.PROMOTION_BISHOP:
            diff = EVAL_TABLE[color][PieceType.BISHOP][er][ec] - EVAL_TABLE[color][piece.type][sr][sc]
        elif move_type == MoveType.PROMOTION_KNIGHT:
            diff = EVAL_TABLE[color][PieceType.KNIGHT][er][ec] - EVAL_TABLE[color][piece.type][sr][sc]
        else:
            diff = EVAL_TABLE[color][piece.type][er][ec] - EVAL_TABLE[color][piece.type][sr][sc]

        if opp_piece is not None:
            diff -= EVAL_TABLE[opp_piece.color][opp_piece.type][er][ec]

        if move_type == MoveType.CASTLING:
            if ec == 1:
                diff += EVAL_TABLE[color][PieceType.ROOK][sr][2] - EVAL_TABLE[color][PieceType.ROOK][sr][0]
            elif ec == 5:
                diff += EVAL_TABLE[color][PieceType.ROOK][sr][4] - EVAL_TABLE[color][PieceType.ROOK][sr][7]

        elif move_type == MoveType.EN_PASSANT:
            captured_pawn = self.board.grid[sr][ec]
            diff -= EVAL_TABLE[captured_pawn.color][captured_pawn.type][sr][ec]

        return diff

    def minimax(self, depth: int, pos_eval: float, maximazing_color: Color, alfa: float, beta: float) -> float:
        if depth == 0:
            return pos_eval

        # ZORBIST
        zhash = self.board.current_hash
        tt = self.tt_white if maximazing_color == Color.WHITE else self.tt_black

        if zhash in tt:
            stored_depth, stored_eval, flag = tt[zhash]
            if stored_depth >= depth:
                if flag == Zorbist.EXACT:
                    return stored_eval
                elif flag == Zorbist.LOWERBOUND:
                    alfa = max(alfa, stored_eval)
                elif flag == Zorbist.UPPERBOUND:
                    beta = min(beta, stored_eval)

                if alfa >= beta:
                    return stored_eval

        orig_alfa = alfa
        orig_beta = beta

        moves = self.board.all_legal_moves(maximazing_color)

        if not moves:
            if maximazing_color == Color.WHITE:
                king_row, king_col = self.board.white_king_pos
            else:
                king_row, king_col = self.board.black_king_pos

            incheck = self.board.is_tile_in_check(king_row, king_col,
                    Color.WHITE if maximazing_color == Color.BLACK else Color.BLACK)
            if incheck:
                return - (10000 + depth) * maximazing_color.value
            else:
                return 0

        if maximazing_color == Color.WHITE:
            maxEval = -float('inf')
            for move, score in moves:
                curr_eval = pos_eval + score + self.eval_table_diff(*move)

                undo_data = self.board.make_move(*move)

                eval = self.minimax(depth - 1, curr_eval, Color.BLACK, alfa, beta)
                maxEval = max(maxEval, eval)

                self.board.undo_move(move[0], move[1], undo_data, move[2])

                # alfa-beta
                alfa = max(alfa, eval)
                if beta <= alfa:
                    break

            # Zorbist - zapisywanie
            if maxEval <= orig_alfa:
                tt[zhash] = (depth, maxEval, Zorbist.UPPERBOUND)
            elif maxEval >= orig_beta:
                tt[zhash] = (depth, maxEval, Zorbist.LOWERBOUND)
            else:
                tt[zhash] = (depth, maxEval, Zorbist.EXACT)

            return maxEval

        elif maximazing_color == Color.BLACK:
            minEval = float('inf')
            for move, score in moves:
                curr_eval = pos_eval - score + self.eval_table_diff(*move)
                undo_data = self.board.make_move(*move)

                eval = self.minimax(depth - 1, curr_eval, Color.WHITE, alfa, beta)
                minEval = min(minEval, eval)

                self.board.undo_move(move[0], move[1], undo_data, move[2])

                # alfa-beta
                beta = min(beta, eval)
                if beta <= alfa:
                    break

            # Zorbist - zapisywnaie
            if minEval >= orig_beta:
                tt[zhash] = (depth, minEval, Zorbist.LOWERBOUND)
            elif minEval <= orig_alfa:
                tt[zhash] = (depth, minEval, Zorbist.UPPERBOUND)
            else:
                tt[zhash] = (depth, minEval, Zorbist.EXACT)

            return minEval

    def best_move(self, depth: int, maximazing_color: Color) -> tuple:
        self.board.update_zobrist_hash()
        book_move = self.get_book_move(maximazing_color)
        if book_move:
            return book_move

        pos_eval = self.eval_position()
        alfa = -float('inf')
        beta = float('inf')
        self.board.update_king_positions()
        moves = self.board.all_legal_moves(maximazing_color)

        if not moves:
            return None

        # Zorbist
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
        side = "white" if color == Color.WHITE else "black"
        zhash_str = str(self.board.current_hash)

        book_for_side = self.opening_book[side]
        if zhash_str in book_for_side:
            moves_dict = book_for_side[zhash_str]
            possible_moves = list(moves_dict.keys())
            weights = list(moves_dict.values())

            chosen_str = random.choices(possible_moves, weights=weights, k=1)[0]
            sr, sc, er, ec, mt = (int(chosen_str[i]) for i in range(5))
            return ((sr, sc), (er, ec), MoveType(mt))

        return None