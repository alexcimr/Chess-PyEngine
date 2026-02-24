import unittest
from model.board import Board
from model.enums import Color, PieceType, MoveType
from model.pieces import Pawn, Rook, King, king, Queen
from model.bot import Bot

class BotTest(unittest.TestCase):

    def setUp(self):
        self.board = Board()
        self.board.clear_board()

    def test_2R_M2(self):
        self.board.grid[6][2] = King(Color.WHITE)
        self.board.grid[7][6] = King(Color.BLACK)
        self.board.grid[6][0] = Rook(Color.WHITE)
        self.board.grid[5][1] = Rook(Color.WHITE)
        self.board.grid[5][3] = Pawn(Color.WHITE)
        Silnik = Bot(self.board)
        move = Silnik.best_move(4, Color.WHITE)
        real_move = ((6, 2), (5, 2), MoveType.NORMAL)
        self.assertEqual(move, real_move)

    def test_Q_M1(self):
        self.board.grid[5][7] = King(Color.WHITE)
        self.board.grid[7][6] = King(Color.BLACK)
        self.board.grid[2][2] = Queen(Color.WHITE)
        Silnik = Bot(self.board)
        move = Silnik.best_move(2, Color.WHITE)
        real_move = ((2, 2), (6, 6), MoveType.NORMAL)
        self.assertEqual(move, real_move)

    def test_Test_xd(self):
        self.board.setup_start_position()
        Silnik = Bot(self.board)
        move = Silnik.best_move(4, Color.WHITE)
        print(move)


if __name__ == '__main__':
        unittest.main()
