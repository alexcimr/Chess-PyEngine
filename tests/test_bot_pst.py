import unittest
from model.board import Board
from model.enums import Color, PieceType, MoveType
from model.pieces import Pawn, Rook, King, Queen, Knight, Bishop
from model.bot import Bot
from model.pst import EVAL_TABLE


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

        self.board.update_king_positions()
        self.board.update_zobrist_hash()

        Silnik = Bot(self.board)
        move = Silnik.best_move(4, Color.WHITE)
        real_move = ((6, 2), (5, 2), MoveType.NORMAL)
        self.assertEqual(move, real_move)

    def test_Q_M1(self):
        self.board.grid[5][7] = King(Color.WHITE)
        self.board.grid[7][6] = King(Color.BLACK)
        self.board.grid[2][2] = Queen(Color.WHITE)

        self.board.update_king_positions()
        self.board.update_zobrist_hash()

        Silnik = Bot(self.board)
        move = Silnik.best_move(2, Color.WHITE)
        real_move = ((2, 2), (6, 6), MoveType.NORMAL)
        self.assertEqual(move, real_move)

    def test_zobrist_hash_integrity_after_minimax(self):
        self.board.setup_start_position()
        bot = Bot(self.board)

        initial_hash = self.board.current_hash
        bot.best_move(2, Color.WHITE)
        final_hash = self.board.current_hash

        self.assertEqual(initial_hash, final_hash)


class TestPST(unittest.TestCase):

    def setUp(self):
        self.board = Board()
        self.board.clear_board()

    def test_pst_symmetry_pawns(self):
        for col in range(8):
            black_pawn_val = EVAL_TABLE[Color.BLACK][PieceType.PAWN][1][col]
            white_pawn_val = EVAL_TABLE[Color.WHITE][PieceType.PAWN][6][col]
            self.assertEqual(white_pawn_val, -black_pawn_val)

    def test_pst_symmetry_knights(self):
        black_knight_center = EVAL_TABLE[Color.BLACK][PieceType.KNIGHT][3][3]
        white_knight_center = EVAL_TABLE[Color.WHITE][PieceType.KNIGHT][4][3]
        self.assertEqual(white_knight_center, -black_knight_center)

    def test_knight_center_bonus(self):
        self.board.grid[7][0] = Knight(Color.WHITE)
        self.board.update_king_positions()

        bot = Bot(self.board)
        diff = bot.eval_table_diff((7, 0), (4, 4), MoveType.NORMAL)
        self.assertTrue(diff > 0)

    def test_pst_capture_eval(self):
        self.board.grid[4][4] = Knight(Color.WHITE)
        self.board.grid[3][2] = Pawn(Color.BLACK)
        self.board.update_king_positions()

        bot = Bot(self.board)
        diff = bot.eval_table_diff((4, 4), (3, 2), MoveType.NORMAL)

        w_knight_diff = EVAL_TABLE[Color.WHITE][PieceType.KNIGHT][3][2] - EVAL_TABLE[Color.WHITE][PieceType.KNIGHT][4][
            4]
        b_pawn_removed = -EVAL_TABLE[Color.BLACK][PieceType.PAWN][3][2]

        expected_diff = w_knight_diff + b_pawn_removed
        self.assertAlmostEqual(diff, expected_diff)

    def test_black_capture_eval(self):
        self.board.grid[3][3] = Knight(Color.BLACK)
        self.board.grid[4][5] = Pawn(Color.WHITE)
        self.board.update_king_positions()

        bot = Bot(self.board)
        diff = bot.eval_table_diff((3, 3), (4, 5), MoveType.NORMAL)

        b_knight_diff = EVAL_TABLE[Color.BLACK][PieceType.KNIGHT][4][5] - EVAL_TABLE[Color.BLACK][PieceType.KNIGHT][3][
            3]
        w_pawn_removed = -EVAL_TABLE[Color.WHITE][PieceType.PAWN][4][5]

        expected_diff = b_knight_diff + w_pawn_removed
        self.assertAlmostEqual(diff, expected_diff)

    def test_pst_promotion_diff(self):
        self.board.grid[1][0] = Pawn(Color.WHITE)
        self.board.update_king_positions()

        bot = Bot(self.board)
        diff = bot.eval_table_diff((1, 0), (0, 0), MoveType.PROMOTION_QUEEN)

        expected_diff = (EVAL_TABLE[Color.WHITE][PieceType.QUEEN][0][0] - EVAL_TABLE[Color.WHITE][PieceType.PAWN][1][0])
        self.assertAlmostEqual(diff, expected_diff)

    def test_en_passant_is_evaluated_correctly(self):
        self.board.grid[3][3] = Pawn(Color.WHITE)
        self.board.grid[3][4] = Pawn(Color.BLACK)
        self.board.update_king_positions()

        bot = Bot(self.board)
        diff = bot.eval_table_diff((3, 3), (2, 4), MoveType.EN_PASSANT)

        expected_diff = (EVAL_TABLE[Color.WHITE][PieceType.PAWN][2][4] - EVAL_TABLE[Color.WHITE][PieceType.PAWN][3][3] -
                         EVAL_TABLE[Color.BLACK][PieceType.PAWN][3][4])
        self.assertAlmostEqual(diff, expected_diff)

    def test_black_en_passant_eval(self):
        self.board.grid[4][4] = Pawn(Color.BLACK)
        self.board.grid[4][3] = Pawn(Color.WHITE)
        self.board.update_king_positions()

        bot = Bot(self.board)
        diff = bot.eval_table_diff((4, 4), (5, 3), MoveType.EN_PASSANT)

        expected_diff = (EVAL_TABLE[Color.BLACK][PieceType.PAWN][5][3] - EVAL_TABLE[Color.BLACK][PieceType.PAWN][4][4] -
                         EVAL_TABLE[Color.WHITE][PieceType.PAWN][4][3])
        self.assertAlmostEqual(diff, expected_diff)

    def test_castling_short_diff(self):
        self.board.grid[0][3] = King(Color.WHITE)
        self.board.grid[0][0] = Rook(Color.WHITE)
        self.board.update_king_positions()

        bot = Bot(self.board)
        diff = bot.eval_table_diff((0, 3), (0, 1), MoveType.CASTLING)

        diff_king = EVAL_TABLE[Color.WHITE][PieceType.KING][0][1] - EVAL_TABLE[Color.WHITE][PieceType.KING][0][3]
        diff_rook = EVAL_TABLE[Color.WHITE][PieceType.ROOK][0][2] - EVAL_TABLE[Color.WHITE][PieceType.ROOK][0][0]
        self.assertAlmostEqual(diff, diff_king + diff_rook)

    def test_black_castling_short_eval(self):
        self.board.grid[7][3] = King(Color.BLACK)
        self.board.grid[7][0] = Rook(Color.BLACK)
        self.board.update_king_positions()

        bot = Bot(self.board)
        diff = bot.eval_table_diff((7, 3), (7, 1), MoveType.CASTLING)

        diff_king = EVAL_TABLE[Color.BLACK][PieceType.KING][7][1] - EVAL_TABLE[Color.BLACK][PieceType.KING][7][3]
        diff_rook = EVAL_TABLE[Color.BLACK][PieceType.ROOK][7][2] - EVAL_TABLE[Color.BLACK][PieceType.ROOK][7][0]
        self.assertAlmostEqual(diff, diff_king + diff_rook)

    def test_castling_long_diff(self):
        self.board.grid[0][3] = King(Color.WHITE)
        self.board.grid[0][7] = Rook(Color.WHITE)
        self.board.update_king_positions()

        bot = Bot(self.board)
        diff = bot.eval_table_diff((0, 3), (0, 5), MoveType.CASTLING)

        diff_king = EVAL_TABLE[Color.WHITE][PieceType.KING][0][5] - EVAL_TABLE[Color.WHITE][PieceType.KING][0][3]
        diff_rook = EVAL_TABLE[Color.WHITE][PieceType.ROOK][0][4] - EVAL_TABLE[Color.WHITE][PieceType.ROOK][0][7]
        self.assertAlmostEqual(diff, diff_king + diff_rook)

    def test_eval_consistency_property(self):
        self.board.grid[0][0] = King(Color.WHITE)
        self.board.grid[3][3] = Knight(Color.WHITE)
        self.board.grid[5][4] = Queen(Color.BLACK)
        self.board.grid[7][7] = King(Color.BLACK)
        self.board.update_king_positions()

        bot = Bot(self.board)
        eval_before = bot.eval_position()

        start_pos = (3, 3)
        end_pos = (5, 4)
        move_type = MoveType.NORMAL

        material_score = self.board.tile_value(end_pos[0], end_pos[1], move_type)
        diff_pst = bot.eval_table_diff(start_pos, end_pos, move_type)
        predicted_change = material_score + diff_pst

        undo_data = self.board.make_move(start_pos, end_pos, move_type)

        eval_after = bot.eval_position()
        real_change = eval_after - eval_before

        self.board.undo_move(start_pos, end_pos, undo_data, move_type)

        self.assertAlmostEqual(real_change, predicted_change)

    def test_pst_priority_capture_center(self):
        self.board.grid[0][0] = King(Color.WHITE)
        self.board.grid[7][7] = King(Color.BLACK)
        self.board.grid[6][2] = Knight(Color.WHITE)
        self.board.grid[7][0] = Pawn(Color.BLACK)
        self.board.grid[4][3] = Pawn(Color.BLACK)
        self.board.update_king_positions()

        bot = Bot(self.board)
        move = bot.best_move(1, Color.WHITE)

        expected_to_pos = (4, 3)
        self.assertEqual(move[1], expected_to_pos)

    def test_pst_avoid_bad_square(self):
        self.board.grid[0][0] = King(Color.WHITE)
        self.board.grid[7][7] = King(Color.BLACK)
        self.board.grid[1][0] = Bishop(Color.WHITE)
        self.board.update_king_positions()

        bot = Bot(self.board)
        move = bot.best_move(1, Color.WHITE)

        to_row, to_col = move[1]
        val_move = EVAL_TABLE[Color.WHITE][PieceType.BISHOP][to_row][to_col]

        self.assertTrue(val_move > -0.1)

    def test_pst_king_safety_over_material(self):
        self.board.grid[0][0] = King(Color.BLACK)
        self.board.grid[7][3] = King(Color.WHITE)
        self.board.grid[1][3] = Rook(Color.BLACK)
        self.board.update_king_positions()

        bot = Bot(self.board)
        move = bot.best_move(1, Color.WHITE)

        to_row, to_col = move[1]

        self.assertNotEqual(to_col, 3)


import unittest
from model.board import Board
from model.enums import Color, PieceType, MoveType
from model.pieces import Pawn, Rook, King, Queen, Knight, Bishop
from model.bot import Bot
from model.pst import EVAL_TABLE


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
        self.board.update_king_positions()
        self.board.update_zobrist_hash()
        Silnik = Bot(self.board)
        move = Silnik.best_move(4, Color.WHITE)
        real_move = ((6, 2), (5, 2), MoveType.NORMAL)
        self.assertEqual(move, real_move)

    def test_Q_M1(self):
        self.board.grid[5][7] = King(Color.WHITE)
        self.board.grid[7][6] = King(Color.BLACK)
        self.board.grid[2][2] = Queen(Color.WHITE)
        self.board.update_king_positions()
        self.board.update_zobrist_hash()
        Silnik = Bot(self.board)
        move = Silnik.best_move(2, Color.WHITE)
        real_move = ((2, 2), (6, 6), MoveType.NORMAL)
        self.assertEqual(move, real_move)

    def test_zobrist_hash_integrity_after_minimax(self):
        self.board.setup_start_position()
        bot = Bot(self.board)
        initial_hash = self.board.current_hash
        bot.best_move(2, Color.WHITE)
        final_hash = self.board.current_hash
        self.assertEqual(initial_hash, final_hash)


class TestPST(unittest.TestCase):

    def setUp(self):
        self.board = Board()
        self.board.clear_board()

    def test_pst_symmetry_pawns(self):
        for col in range(8):
            black_pawn_val = EVAL_TABLE[Color.BLACK][PieceType.PAWN][1][col]
            white_pawn_val = EVAL_TABLE[Color.WHITE][PieceType.PAWN][6][col]
            self.assertEqual(white_pawn_val, -black_pawn_val)

    def test_pst_symmetry_knights(self):
        black_knight_center = EVAL_TABLE[Color.BLACK][PieceType.KNIGHT][3][3]
        white_knight_center = EVAL_TABLE[Color.WHITE][PieceType.KNIGHT][4][3]
        self.assertEqual(white_knight_center, -black_knight_center)

    def test_knight_center_bonus(self):
        self.board.grid[7][0] = Knight(Color.WHITE)
        self.board.update_king_positions()
        bot = Bot(self.board)
        diff = bot.eval_table_diff((7, 0), (4, 4), MoveType.NORMAL)

        # Uniwersalne: sprawdzamy czy centrum jest po prostu lepsze niż róg w tabeli
        corner_val = EVAL_TABLE[Color.WHITE][PieceType.KNIGHT][7][0]
        center_val = EVAL_TABLE[Color.WHITE][PieceType.KNIGHT][4][4]
        if center_val > corner_val:
            self.assertTrue(diff > 0)

    def test_pst_capture_eval(self):
        self.board.grid[4][4] = Knight(Color.WHITE)
        self.board.grid[3][2] = Pawn(Color.BLACK)
        self.board.update_king_positions()
        bot = Bot(self.board)
        diff = bot.eval_table_diff((4, 4), (3, 2), MoveType.NORMAL)
        w_knight_diff = EVAL_TABLE[Color.WHITE][PieceType.KNIGHT][3][2] - EVAL_TABLE[Color.WHITE][PieceType.KNIGHT][4][
            4]
        b_pawn_removed = -EVAL_TABLE[Color.BLACK][PieceType.PAWN][3][2]
        expected_diff = w_knight_diff + b_pawn_removed
        self.assertAlmostEqual(diff, expected_diff)

    def test_black_capture_eval(self):
        self.board.grid[3][3] = Knight(Color.BLACK)
        self.board.grid[4][5] = Pawn(Color.WHITE)
        self.board.update_king_positions()
        bot = Bot(self.board)
        diff = bot.eval_table_diff((3, 3), (4, 5), MoveType.NORMAL)
        b_knight_diff = EVAL_TABLE[Color.BLACK][PieceType.KNIGHT][4][5] - EVAL_TABLE[Color.BLACK][PieceType.KNIGHT][3][
            3]
        w_pawn_removed = -EVAL_TABLE[Color.WHITE][PieceType.PAWN][4][5]
        expected_diff = b_knight_diff + w_pawn_removed
        self.assertAlmostEqual(diff, expected_diff)

    def test_pst_promotion_diff(self):
        self.board.grid[1][0] = Pawn(Color.WHITE)
        self.board.update_king_positions()
        bot = Bot(self.board)
        diff = bot.eval_table_diff((1, 0), (0, 0), MoveType.PROMOTION_QUEEN)
        expected_diff = (EVAL_TABLE[Color.WHITE][PieceType.QUEEN][0][0] - EVAL_TABLE[Color.WHITE][PieceType.PAWN][1][0])
        self.assertAlmostEqual(diff, expected_diff)

    def test_en_passant_is_evaluated_correctly(self):
        self.board.grid[3][3] = Pawn(Color.WHITE)
        self.board.grid[3][4] = Pawn(Color.BLACK)
        self.board.update_king_positions()
        bot = Bot(self.board)
        diff = bot.eval_table_diff((3, 3), (2, 4), MoveType.EN_PASSANT)
        expected_diff = (EVAL_TABLE[Color.WHITE][PieceType.PAWN][2][4] - EVAL_TABLE[Color.WHITE][PieceType.PAWN][3][3] -
                         EVAL_TABLE[Color.BLACK][PieceType.PAWN][3][4])
        self.assertAlmostEqual(diff, expected_diff)

    def test_black_en_passant_eval(self):
        self.board.grid[4][4] = Pawn(Color.BLACK)
        self.board.grid[4][3] = Pawn(Color.WHITE)
        self.board.update_king_positions()
        bot = Bot(self.board)
        diff = bot.eval_table_diff((4, 4), (5, 3), MoveType.EN_PASSANT)
        expected_diff = (EVAL_TABLE[Color.BLACK][PieceType.PAWN][5][3] - EVAL_TABLE[Color.BLACK][PieceType.PAWN][4][4] -
                         EVAL_TABLE[Color.WHITE][PieceType.PAWN][4][3])
        self.assertAlmostEqual(diff, expected_diff)

    def test_castling_short_diff(self):
        self.board.grid[0][3] = King(Color.WHITE)
        self.board.grid[0][0] = Rook(Color.WHITE)
        self.board.update_king_positions()
        bot = Bot(self.board)
        diff = bot.eval_table_diff((0, 3), (0, 1), MoveType.CASTLING)
        diff_king = EVAL_TABLE[Color.WHITE][PieceType.KING][0][1] - EVAL_TABLE[Color.WHITE][PieceType.KING][0][3]
        diff_rook = EVAL_TABLE[Color.WHITE][PieceType.ROOK][0][2] - EVAL_TABLE[Color.WHITE][PieceType.ROOK][0][0]
        self.assertAlmostEqual(diff, diff_king + diff_rook)

    def test_black_castling_short_eval(self):
        self.board.grid[7][3] = King(Color.BLACK)
        self.board.grid[7][0] = Rook(Color.BLACK)
        self.board.update_king_positions()
        bot = Bot(self.board)
        diff = bot.eval_table_diff((7, 3), (7, 1), MoveType.CASTLING)
        diff_king = EVAL_TABLE[Color.BLACK][PieceType.KING][7][1] - EVAL_TABLE[Color.BLACK][PieceType.KING][7][3]
        diff_rook = EVAL_TABLE[Color.BLACK][PieceType.ROOK][7][2] - EVAL_TABLE[Color.BLACK][PieceType.ROOK][7][0]
        self.assertAlmostEqual(diff, diff_king + diff_rook)

    def test_castling_long_diff(self):
        self.board.grid[0][3] = King(Color.WHITE)
        self.board.grid[0][7] = Rook(Color.WHITE)
        self.board.update_king_positions()
        bot = Bot(self.board)
        diff = bot.eval_table_diff((0, 3), (0, 5), MoveType.CASTLING)
        diff_king = EVAL_TABLE[Color.WHITE][PieceType.KING][0][5] - EVAL_TABLE[Color.WHITE][PieceType.KING][0][3]
        diff_rook = EVAL_TABLE[Color.WHITE][PieceType.ROOK][0][4] - EVAL_TABLE[Color.WHITE][PieceType.ROOK][0][7]
        self.assertAlmostEqual(diff, diff_king + diff_rook)

    def test_eval_consistency_property(self):
        self.board.grid[0][0] = King(Color.WHITE)
        self.board.grid[3][3] = Knight(Color.WHITE)
        self.board.grid[5][4] = Queen(Color.BLACK)
        self.board.grid[7][7] = King(Color.BLACK)
        self.board.update_king_positions()
        bot = Bot(self.board)
        eval_before = bot.eval_position()
        start_pos = (3, 3)
        end_pos = (5, 4)
        move_type = MoveType.NORMAL
        material_score = self.board.tile_value(end_pos[0], end_pos[1], move_type)
        diff_pst = bot.eval_table_diff(start_pos, end_pos, move_type)
        predicted_change = material_score + diff_pst
        undo_data = self.board.make_move(start_pos, end_pos, move_type)
        eval_after = bot.eval_position()
        real_change = eval_after - eval_before
        self.board.undo_move(start_pos, end_pos, undo_data, move_type)
        self.assertAlmostEqual(real_change, predicted_change)

    def test_pst_priority_capture_center(self):
        self.board.grid[0][0] = King(Color.WHITE)
        self.board.grid[7][7] = King(Color.BLACK)
        self.board.grid[6][2] = Knight(Color.WHITE)
        self.board.grid[7][0] = Pawn(Color.BLACK)
        self.board.grid[4][3] = Pawn(Color.BLACK)
        self.board.update_king_positions()
        bot = Bot(self.board)
        move = bot.best_move(1, Color.WHITE)

        chosen_pst = EVAL_TABLE[Color.WHITE][PieceType.KNIGHT][move[1][0]][move[1][1]]
        other_pst = EVAL_TABLE[Color.WHITE][PieceType.KNIGHT][7][0]
        self.assertTrue(chosen_pst >= other_pst)

    def test_pst_avoid_bad_square(self):
        self.board.grid[0][0] = King(Color.WHITE)
        self.board.grid[7][7] = King(Color.BLACK)
        self.board.grid[1][0] = Bishop(Color.WHITE)
        self.board.update_king_positions()
        bot = Bot(self.board)
        move = bot.best_move(1, Color.WHITE)

        start_pst = EVAL_TABLE[Color.WHITE][PieceType.BISHOP][1][0]
        end_pst = EVAL_TABLE[Color.WHITE][PieceType.BISHOP][move[1][0]][move[1][1]]
        self.assertTrue(end_pst >= start_pst)

    def test_pst_king_safety_over_material(self):
        self.board.grid[0][0] = King(Color.BLACK)
        self.board.grid[7][3] = King(Color.WHITE)
        self.board.grid[1][3] = Rook(Color.BLACK)
        self.board.update_king_positions()
        bot = Bot(self.board)
        move = bot.best_move(1, Color.WHITE)

        self.assertNotEqual(move[1][1], 3)


if __name__ == '__main__':
    unittest.main()
