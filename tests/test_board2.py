import unittest
from model.board import Board
from model.enums import Color, MoveType, PieceType
from model.pieces import Pawn, King, Rook, Queen, Bishop, Knight


class TestBoardComprehensive(unittest.TestCase):

    def setUp(self):
        self.board = Board()
        self.board.clear_board()

    def test_01_simple_pawn_move_and_undo(self):
        pawn = Pawn(Color.WHITE)
        self.board.grid[1][0] = pawn
        start, end = (1, 0), (2, 0)

        cap, moved, ep = self.board.make_move(start, end, MoveType.NORMAL)
        self.assertIsNone(self.board.grid[1][0])
        self.assertEqual(self.board.grid[2][0], pawn)

        self.board.undo_move(start, end, cap, moved, ep, MoveType.NORMAL)
        self.assertEqual(self.board.grid[1][0], pawn)
        self.assertIsNone(self.board.grid[2][0])

    def test_02_capture_piece_and_undo(self):
        rook = Rook(Color.WHITE)
        enemy_pawn = Pawn(Color.BLACK)
        self.board.grid[0][0] = rook
        self.board.grid[5][0] = enemy_pawn
        start, end = (0, 0), (5, 0)

        cap, moved, ep = self.board.make_move(start, end, MoveType.NORMAL)
        self.assertEqual(cap, enemy_pawn)
        self.assertEqual(self.board.grid[5][0], rook)

        self.board.undo_move(start, end, cap, moved, ep, MoveType.NORMAL)
        self.assertEqual(self.board.grid[0][0], rook)
        self.assertEqual(self.board.grid[5][0], enemy_pawn)

    def test_03_knight_jump_undo(self):
        knight = Knight(Color.WHITE)
        self.board.grid[4][4] = knight
        pawn = Pawn(Color.WHITE)
        self.board.grid[5][4] = pawn

        start, end = (4, 4), (6, 5)
        cap, moved, ep = self.board.make_move(start, end, MoveType.NORMAL)

        self.assertEqual(self.board.grid[6][5], knight)
        self.board.undo_move(start, end, cap, moved, ep, MoveType.NORMAL)
        self.assertEqual(self.board.grid[4][4], knight)

    def test_04_en_passant_flag_set(self):
        pawn = Pawn(Color.WHITE)
        self.board.grid[1][0] = pawn

        self.board.make_move((1, 0), (3, 0), MoveType.NORMAL)
        self.assertTrue(pawn.enpassant_available)

    def test_05_en_passant_execution(self):
        white_pawn = Pawn(Color.WHITE)
        black_pawn = Pawn(Color.BLACK)

        self.board.grid[3][0] = white_pawn
        self.board.grid[3][1] = black_pawn
        white_pawn.enpassant_available = True

        start, end = (3, 1), (2, 0)
        cap, moved, ep = self.board.make_move(start, end, MoveType.EN_PASSANT)

        self.assertIsNone(self.board.grid[3][0])
        self.assertEqual(self.board.grid[2][0], black_pawn)
        self.assertEqual(cap, white_pawn)

    def test_06_en_passant_undo(self):
        white_pawn = Pawn(Color.WHITE)
        black_pawn = Pawn(Color.BLACK)
        self.board.grid[3][0] = white_pawn
        self.board.grid[3][1] = black_pawn
        white_pawn.enpassant_available = True

        start, end = (3, 1), (2, 0)
        cap, moved, ep = self.board.make_move(start, end, MoveType.EN_PASSANT)

        self.board.undo_move(start, end, cap, moved, ep, MoveType.EN_PASSANT)

        self.assertEqual(self.board.grid[3][0], white_pawn)
        self.assertEqual(self.board.grid[3][1], black_pawn)
        self.assertIsNone(self.board.grid[2][0])

    def test_07_short_castling_white(self):
        king = King(Color.WHITE)
        rook = Rook(Color.WHITE)
        self.board.grid[0][3] = king
        self.board.grid[0][0] = rook

        start, end = (0, 3), (0, 1)
        cap, moved, ep = self.board.make_move(start, end, MoveType.CASTLING)

        self.assertEqual(self.board.grid[0][1], king)
        self.assertEqual(self.board.grid[0][2], rook)
        self.assertTrue(king.moved)
        self.assertTrue(rook.moved)

    def test_08_long_castling_white(self):
        king = King(Color.WHITE)
        rook = Rook(Color.WHITE)
        self.board.grid[0][3] = king
        self.board.grid[0][7] = rook

        start, end = (0, 3), (0, 5)
        cap, moved, ep = self.board.make_move(start, end, MoveType.CASTLING)

        self.assertEqual(self.board.grid[0][5], king)
        self.assertEqual(self.board.grid[0][4], rook)

    def test_09_castling_undo(self):
        king = King(Color.WHITE)
        rook = Rook(Color.WHITE)
        self.board.grid[0][3] = king
        self.board.grid[0][0] = rook

        start, end = (0, 3), (0, 1)
        cap, moved, ep = self.board.make_move(start, end, MoveType.CASTLING)

        self.board.undo_move(start, end, cap, moved, ep, MoveType.CASTLING)

        self.assertEqual(self.board.grid[0][3], king)
        self.assertEqual(self.board.grid[0][0], rook)
        self.assertIsNone(self.board.grid[0][1])
        self.assertFalse(king.moved)
        self.assertFalse(rook.moved)

    def test_10_promotion_to_queen(self):
        pawn = Pawn(Color.WHITE)
        self.board.grid[6][0] = pawn
        start, end = (6, 0), (7, 0)

        cap, moved, ep = self.board.make_move(start, end, MoveType.PROMOTION_QUEEN)

        self.assertEqual(self.board.grid[7][0].type, PieceType.QUEEN)
        self.assertEqual(self.board.grid[7][0].color, Color.WHITE)

    def test_11_promotion_undo(self):
        pawn = Pawn(Color.WHITE)
        self.board.grid[6][0] = pawn
        start, end = (6, 0), (7, 0)

        cap, moved, ep = self.board.make_move(start, end, MoveType.PROMOTION_QUEEN)
        self.board.undo_move(start, end, cap, moved, ep, MoveType.PROMOTION_QUEEN)

        result_piece = self.board.grid[6][0]
        self.assertIsNotNone(result_piece)
        self.assertEqual(result_piece.type, PieceType.PAWN)
        self.assertEqual(result_piece.color, Color.WHITE)
        self.assertIsNone(self.board.grid[7][0])

    def test_12_promotion_capture_undo(self):
        pawn = Pawn(Color.WHITE)
        enemy_rook = Rook(Color.BLACK)
        self.board.grid[6][1] = pawn
        self.board.grid[7][0] = enemy_rook

        start, end = (6, 1), (7, 0)
        cap, moved, ep = self.board.make_move(start, end, MoveType.PROMOTION_KNIGHT)

        self.assertEqual(self.board.grid[7][0].type, PieceType.KNIGHT)
        self.assertEqual(cap, enemy_rook)

        self.board.undo_move(start, end, cap, moved, ep, MoveType.PROMOTION_KNIGHT)

        result_piece = self.board.grid[6][1]
        self.assertEqual(result_piece.type, PieceType.PAWN)
        self.assertEqual(self.board.grid[7][0], enemy_rook)

    def test_13_absolute_pin_orthogonal(self):
        king = King(Color.WHITE)
        rook = Rook(Color.WHITE)
        enemy_rook = Rook(Color.BLACK)

        self.board.grid[0][0] = king
        self.board.grid[0][2] = rook
        self.board.grid[0][7] = enemy_rook

        moves = self.board.get_legal_moves(0, 2)

        expected_moves = [(0, 1), (0, 3), (0, 4), (0, 5), (0, 6), (0, 7)]
        self.assertEqual(sorted(moves), sorted(expected_moves))

    def test_14_absolute_pin_diagonal(self):
        king = King(Color.WHITE)
        bishop = Bishop(Color.WHITE)
        enemy_queen = Queen(Color.BLACK)

        self.board.grid[0][0] = king
        self.board.grid[1][1] = bishop
        self.board.grid[3][3] = enemy_queen

        moves = self.board.get_legal_moves(1, 1)

        self.assertIn((2, 2), moves)
        self.assertIn((3, 3), moves)
        self.assertNotIn((0, 2), moves)

    def test_15_king_cannot_move_into_check(self):
        king = King(Color.WHITE)
        enemy_rook = Rook(Color.BLACK)
        self.board.grid[0][0] = king
        self.board.grid[2][1] = enemy_rook

        moves = self.board.get_legal_moves(0, 0)

        self.assertNotIn((0, 1), moves)
        self.assertNotIn((1, 1), moves)
        self.assertIn((1, 0), moves)

    def test_16_must_capture_or_block_check(self):
        king = King(Color.WHITE)
        rook = Rook(Color.WHITE)
        enemy_rook = Rook(Color.BLACK)

        self.board.grid[0][0] = king
        self.board.grid[7][0] = enemy_rook

        self.board.grid[7][5] = rook

        moves = self.board.get_legal_moves(7, 5)

        self.assertIn((7, 0), moves)
        self.assertNotIn((6, 5), moves)

    def test_17_pawn_cannot_move_pinned(self):
        king = King(Color.WHITE)
        pawn = Pawn(Color.WHITE)
        enemy_bishop = Bishop(Color.BLACK)

        self.board.grid[0][0] = king
        self.board.grid[1][1] = pawn
        self.board.grid[3][3] = enemy_bishop

        moves = self.board.get_legal_moves(1, 1)

        self.assertEqual(moves, [])

    def test_18_king_moves_out_of_check(self):
        king = King(Color.WHITE)
        enemy_rook = Rook(Color.BLACK)

        self.board.grid[0][0] = king
        self.board.grid[0][7] = enemy_rook

        moves = self.board.get_legal_moves(0, 0)

        self.assertNotIn((0, 1), moves)
        self.assertIn((1, 0), moves)
        self.assertIn((1, 1), moves)

    def test_19_cant_castle_through_check(self):
        king = King(Color.WHITE)
        rook = Rook(Color.WHITE)
        enemy_rook = Rook(Color.BLACK)

        self.board.grid[0][3] = king
        self.board.grid[0][0] = rook
        self.board.grid[1][1] = enemy_rook

        moves = self.board.get_legal_moves(0, 3)
        self.assertNotIn((0, 1), moves)

    def test_20_undo_restores_moved_flag(self):
        king = King(Color.WHITE)
        self.board.grid[0][0] = king
        self.assertFalse(king.moved)

        start, end = (0, 0), (1, 0)
        cap, moved, ep = self.board.make_move(start, end, MoveType.NORMAL)
        self.assertTrue(king.moved)

        self.board.undo_move(start, end, cap, moved, ep, MoveType.NORMAL)
        self.assertFalse(king.moved)

    def test_21_complex_sequence_en_passant_discovered_check_undo(self):
        king = King(Color.WHITE)
        white_pawn = Pawn(Color.WHITE)
        black_pawn = Pawn(Color.BLACK)
        enemy_rook = Rook(Color.BLACK)

        self.board.grid[0][4] = king
        self.board.grid[1][3] = white_pawn
        self.board.grid[3][4] = black_pawn
        self.board.grid[7][4] = enemy_rook

        start1, end1 = (1, 3), (3, 3)
        cap1, moved1, ep1 = self.board.make_move(start1, end1, MoveType.NORMAL)

        self.assertTrue(white_pawn.enpassant_available)
        self.assertFalse(self.board.is_tile_in_check(0, 4, Color.BLACK))

        start2, end2 = (3, 4), (2, 3)
        cap2, moved2, ep2 = self.board.make_move(start2, end2, MoveType.EN_PASSANT)

        self.assertIsNone(self.board.grid[3][4])
        self.assertIsNone(self.board.grid[3][3])
        self.assertEqual(self.board.grid[2][3], black_pawn)
        self.assertEqual(cap2, white_pawn)

        self.assertTrue(self.board.is_tile_in_check(0, 4, Color.BLACK))

        start3, end3 = (0, 4), (0, 5)
        cap3, moved3, ep3 = self.board.make_move(start3, end3, MoveType.NORMAL)
        self.assertFalse(self.board.is_tile_in_check(0, 5, Color.BLACK))

        self.board.undo_move(start3, end3, cap3, moved3, ep3, MoveType.NORMAL)
        self.assertEqual(self.board.grid[0][4], king)
        self.assertTrue(self.board.is_tile_in_check(0, 4, Color.BLACK))

        self.board.undo_move(start2, end2, cap2, moved2, ep2, MoveType.EN_PASSANT)

        self.assertEqual(self.board.grid[3][4], black_pawn)
        self.assertEqual(self.board.grid[3][3], white_pawn)
        self.assertIsNone(self.board.grid[2][3])

        self.assertFalse(self.board.is_tile_in_check(0, 4, Color.BLACK))
        self.assertTrue(white_pawn.enpassant_available)

        self.board.undo_move(start1, end1, cap1, moved1, ep1, MoveType.NORMAL)

        self.assertEqual(self.board.grid[1][3], white_pawn)
        self.assertIsNone(self.board.grid[3][3])
        self.assertFalse(white_pawn.enpassant_available)

if __name__ == '__main__':
    unittest.main()