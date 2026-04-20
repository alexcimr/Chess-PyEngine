from model.board import Board
from model.enums import PieceType, Color, MoveType, GameStatus, Zorbist


class Bot():
    def __init__(self, board: Board):
        self.board = board
        # Zorbist
        self.tt_white = {}
        self.tt_black = {}

    def eval_position(self):
        res = 0
        for row in range(8):
            for col in range(8):
                piece = self.board.grid[row][col]
                if piece is not None:
                    res += piece.point_value * piece.color.value  # 1 or -1
        return res

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
                curr_eval = pos_eval + score
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
                curr_eval = pos_eval - score
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
        pos_eval = self.eval_position()
        self.board.update_zobrist_hash()
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
                curr_eval = pos_eval + score
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
                curr_eval = pos_eval - score
                undo_data = self.board.make_move(*move)

                eval = self.minimax(depth - 1, curr_eval, Color.WHITE, alfa, beta)

                if eval < minEval:
                    minEval = eval
                    best_move = move

                self.board.undo_move(move[0], move[1], undo_data, move[2])

                beta = min(beta, eval)

        return best_move