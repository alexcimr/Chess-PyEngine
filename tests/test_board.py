import unittest
from model.board import Board
from model.enums import Color
from model.pieces import King, Rook, Pawn, Knight

class TestBoardChecks(unittest.TestCase):

    def setUp(self):
        self.board = Board()
        self.board.clear_board()

    def test_safe_king(self):
        self.board.grid[4][4] = King(Color.BLACK)
        is_check = self.board.is_tile_in_check(4, 4, Color.WHITE)
        self.assertFalse(is_check)

    def test_rook_check_horizontal(self):
        self.board.grid[4][4] = King(Color.BLACK)
        self.board.grid[4][0] = Rook(Color.WHITE)
        is_check = self.board.is_tile_in_check(4, 4, Color.WHITE)
        self.assertTrue(is_check)

    def test_rook_blocked(self):
        self.board.grid[4][4] = King(Color.BLACK)
        self.board.grid[4][0] = Rook(Color.WHITE)
        self.board.grid[4][2] = Pawn(Color.BLACK)
        is_check = self.board.is_tile_in_check(4, 4, Color.WHITE)
        self.assertFalse(is_check)

    def test_knight_check(self):
        self.board.grid[4][4] = King(Color.BLACK)
        self.board.grid[6][5] = Knight(Color.WHITE)
        is_check = self.board.is_tile_in_check(4, 4, Color.WHITE)
        self.assertTrue(is_check)

    def test_pawn_check(self):
        self.board.grid[4][4] = King(Color.BLACK)
        self.board.grid[3][3] = Pawn(Color.WHITE)
        is_check = self.board.is_tile_in_check(4, 4, Color.WHITE)
        self.assertTrue(is_check)

    def test_pawn_no_check_forward(self):
        self.board.grid[4][4] = King(Color.BLACK)
        self.board.grid[3][4] = Pawn(Color.WHITE)
        is_check = self.board.is_tile_in_check(4, 4, Color.WHITE)
        self.assertFalse(is_check)

    def test_king_proximity(self):
        self.board.grid[4][4] = King(Color.BLACK)
        self.board.grid[4][5] = King(Color.WHITE)
        is_check = self.board.is_tile_in_check(4, 4, Color.WHITE)
        self.assertTrue(is_check)

if __name__ == '__main__':
    unittest.main()