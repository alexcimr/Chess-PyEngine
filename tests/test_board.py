import unittest
from model.board import Board
from model.enums import Color
from model.pieces import King, Rook, Pawn, Knight, Bishop

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
    def test_all_legals(self):
        self.board.grid[0][1] = King(Color.WHITE)
        self.board.grid[1][0] = Pawn(Color.WHITE)
        self.board.grid[1][1] = Pawn(Color.WHITE)
        self.board.grid[1][2] = Pawn(Color.WHITE)
        self.board.grid[4][1] = Knight(Color.WHITE)
        self.board.grid[3][6] = Rook(Color.WHITE)

        self.board.grid[6][0] = Pawn(Color.BLACK)
        self.board.grid[6][1] = Pawn(Color.BLACK)
        self.board.grid[6][2] = Pawn(Color.BLACK)
        self.board.grid[6][3] = Bishop(Color.BLACK)
        self.board.grid[7][1] = King(Color.BLACK)
        self.board.grid[7][2] = Rook(Color.BLACK)
        self.board.update_king_positions()

        print(self.board.all_legal_moves(Color.BLACK))

    def test_M3(self):
        self.board.grid[4][4] = King(Color.BLACK)
if __name__ == '__main__':
    unittest.main()