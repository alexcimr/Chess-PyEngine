import unittest
from model.board import Board
from model.enums import Color, PieceType
from model.pieces import Pawn, Rook


class TestPawn(unittest.TestCase):

    def setUp(self):
        self.board = Board()
        self.board.clear_board()

    def test_white_pawn_initial_move(self):
        pawn = Pawn(Color.WHITE)
        self.board.grid[1][3] = pawn
        moves = pawn.moves(self.board, 1, 3)

        self.assertIn((2, 3), moves)
        self.assertIn((3, 3), moves)
        self.assertEqual(len(moves), 2)

    def test_black_pawn_blocked(self):
        black_pawn = Pawn(Color.BLACK)
        blocking_piece = Rook(Color.WHITE)

        self.board.grid[6][3] = black_pawn
        self.board.grid[5][3] = blocking_piece

        moves = black_pawn.moves(self.board, 6, 3)
        self.assertEqual(len(moves), 0, "Pionek nie powinien móc iść do przodu, gdy jest zablokowany")

    def test_pawn_capture(self):
        white_pawn = Pawn(Color.WHITE)
        enemy = Rook(Color.BLACK)

        self.board.grid[3][3] = white_pawn
        self.board.grid[4][4] = enemy  # Wróg na skos w prawo

        moves = white_pawn.moves(self.board, 3, 3)
        self.assertIn((4, 4), moves, "Biały pionek powinien móc zbić figurę na (4,4)")
        self.assertIn((4, 3), moves, "Biały pionek powinien móc iść do przodu")

    def test_en_passant_right(self):
        white_pawn = Pawn(Color.WHITE)
        black_pawn = Pawn(Color.BLACK)
        black_pawn.enpassant_available = True

        self.board.grid[4][3] = white_pawn
        self.board.grid[4][4] = black_pawn

        moves = white_pawn.moves(self.board, 4, 3)
        self.assertIn((5, 4), moves, "Powinien być dostępny En Passant na (5, 4)")


if __name__ == '__main__':
    unittest.main()