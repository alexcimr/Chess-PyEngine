import unittest
from model.board import Board
from model.enums import Color
from model.pieces import King, Rook, Knight, Pawn


class TestKingCastling(unittest.TestCase):

    def setUp(self):
        self.board = Board()
        self.board.clear_board()

    def test_castling_available_both_sides(self):
        king = King(Color.WHITE)
        self.board.grid[0][3] = king
        self.board.grid[0][0] = Rook(Color.WHITE)
        self.board.grid[0][7] = Rook(Color.WHITE)

        moves = king.moves(self.board, 0, 3)

        self.assertIn((0, 1), moves)
        self.assertIn((0, 5), moves)

    def test_castling_blocked_by_piece(self):
        king = King(Color.WHITE)
        self.board.grid[0][3] = king
        self.board.grid[0][0] = Rook(Color.WHITE)
        self.board.grid[0][1] = Knight(Color.WHITE)

        moves = king.moves(self.board, 0, 3)

        self.assertNotIn((0, 1), moves)

    def test_castling_forbidden_during_check(self):
        king = King(Color.WHITE)
        self.board.grid[0][3] = king
        self.board.grid[0][0] = Rook(Color.WHITE)
        self.board.grid[7][3] = Rook(Color.BLACK)

        moves = king.moves(self.board, 0, 3)

        self.assertNotIn((0, 1), moves)

    def test_castling_forbidden_path_attacked(self):
        king = King(Color.WHITE)
        self.board.grid[0][3] = king
        self.board.grid[0][0] = Rook(Color.WHITE)
        self.board.grid[7][2] = Rook(Color.BLACK)

        moves = king.moves(self.board, 0, 3)

        self.assertNotIn((0, 1), moves)

    def test_castling_rook_already_moved(self):
        king = King(Color.WHITE)
        self.board.grid[0][3] = king
        rook = Rook(Color.WHITE)
        rook.moved = True
        self.board.grid[0][0] = rook

        moves = king.moves(self.board, 0, 3)

        self.assertNotIn((0, 1), moves)


if __name__ == '__main__':
    unittest.main()