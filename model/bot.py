from model.board import Board
from model.enums import PieceType, Color, MoveType, GameStatus

class Bot():
    def __init__(self, board: Board):
        self.board = board

    def eval_position(self):
        res = 0
        for row in range(8):
            for col in range(8):
                piece = self.board.grid[row][col]
                color = self.board.get_piece_color(row, col)
                if color is not None:
                    res += piece.point_value * piece.color.value # 1 or -1
        return res

    def tile_value(self, row, col, move_type: MoveType):
        points = 0
        if self.board.grid[row][col] is not None:
            points += self.board.grid[row][col].point_value

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

    def minimax(self, depth, pos_eval, maximazing_color, alfa, beta):
        if depth == 0:
            return pos_eval

        moves = self.board.all_legal_moves(maximazing_color)

        if not moves:
            king_row, king_col = self.board.king_finder(maximazing_color)
            incheck = self.board.is_tile_in_check(king_row, king_col, Color.WHITE if maximazing_color == Color.BLACK else Color.BLACK)
            if incheck:
                return - (10000 + depth)* maximazing_color.value
            else:
                return 0

        if maximazing_color == Color.WHITE:
            maxEval = -float('inf')
            for move in moves:
                next_eval = pos_eval + self.tile_value(*move[1], move[2])
                captured, moved, passant = self.board.make_move(*move)

                eval = self.minimax(depth - 1, next_eval, Color.BLACK, alfa, beta)
                maxEval = max(maxEval, eval)

                self.board.undo_move(move[0], move[1], captured, moved, passant, move[2])

                # alfa-beta
                alfa = max(alfa, eval)
                if beta <= alfa:
                    break

            return maxEval

        elif maximazing_color == Color.BLACK:
            minEval = float('inf')
            for move in moves:
                next_eval = pos_eval - self.tile_value(*move[1], move[2])
                captured, moved, passant = self.board.make_move(*move)

                eval = self.minimax(depth - 1, next_eval, Color.WHITE, alfa, beta)
                minEval = min(minEval, eval)

                self.board.undo_move(move[0], move[1], captured, moved, passant, move[2])

                # alfa-beta
                beta = min(beta, eval)
                if beta <= alfa:
                    break

            return minEval


    def best_move(self, depth, maximazing_color):

        #TODO sortowanie moves po next_eval albo biciu albo cso co przyspiszy kod i w minimaxie
        pos_eval = self.eval_position()
        alfa = -float('inf')
        beta = float('inf')
        moves = self.board.all_legal_moves(maximazing_color)
        if not moves:
            return None



        best_move = moves[0]
        if maximazing_color == Color.WHITE:
            maxEval = -float('inf')
            for move in moves:
                next_eval = pos_eval + self.tile_value(*move[1], move[2])
                captured, moved, passant = self.board.make_move(*move)

                eval = self.minimax(depth - 1, next_eval, Color.BLACK, alfa, beta)

                if eval > maxEval:
                    maxEval = eval
                    best_move = move

                self.board.undo_move(move[0], move[1], captured, moved, passant, move[2])

                alfa = max(alfa, eval)


        elif maximazing_color == Color.BLACK:
            minEval = float('inf')
            for move in moves:
                next_eval = pos_eval - self.tile_value(*move[1], move[2])
                captured, moved, passant = self.board.make_move(*move)

                eval = self.minimax(depth - 1, next_eval, Color.WHITE, alfa, beta)

                if eval < minEval:
                    minEval = eval
                    best_move = move

                self.board.undo_move(move[0], move[1], captured, moved, passant, move[2])

                beta = min(beta, eval)

        return best_move

