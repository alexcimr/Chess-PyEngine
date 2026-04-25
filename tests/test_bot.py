import pytest

from model.board import Board
from model.bot import Bot
from model.enums import Color, MoveType, Phase, PieceType
from model.pieces import Bishop, King, Knight, Pawn, Queen, Rook


@pytest.fixture
def board():
    b = Board()
    b.clear_board()
    return b


def set_kings(board: Board, white_pos=(0, 3), black_pos=(7, 3)) -> None:
    board.grid[white_pos[0]][white_pos[1]] = King(Color.WHITE)
    board.grid[black_pos[0]][black_pos[1]] = King(Color.BLACK)
    board.update_king_positions()


def test_two_rooks_mate_in_2(board):
    set_kings(board, white_pos=(6, 2), black_pos=(7, 6))
    board.grid[6][0] = Rook(Color.WHITE)
    board.grid[5][1] = Rook(Color.WHITE)
    board.grid[5][3] = Pawn(Color.WHITE)

    move = Bot(board).best_move(4, Color.WHITE)

    assert move == ((6, 2), (5, 2), MoveType.NORMAL)


def test_queen_mate_in_1(board):
    set_kings(board, white_pos=(5, 7), black_pos=(7, 6))
    board.grid[2][2] = Queen(Color.WHITE)

    move = Bot(board).best_move(2, Color.WHITE)

    assert move == ((2, 2), (6, 6), MoveType.NORMAL)


def test_complex_position_black(board):
    set_kings(board, white_pos=(0, 1), black_pos=(7, 1))
    board.grid[1][0] = Pawn(Color.WHITE)
    board.grid[1][1] = Pawn(Color.WHITE)
    board.grid[1][2] = Pawn(Color.WHITE)
    board.grid[4][1] = Knight(Color.WHITE)
    board.grid[3][6] = Rook(Color.WHITE)
    board.grid[6][0] = Pawn(Color.BLACK)
    board.grid[6][1] = Pawn(Color.BLACK)
    board.grid[6][2] = Pawn(Color.BLACK)
    board.grid[6][3] = Bishop(Color.BLACK)
    board.grid[7][2] = Rook(Color.BLACK)

    move = Bot(board).best_move(7, Color.BLACK)

    assert move == ((6, 3), (3, 6), MoveType.NORMAL)


def test_bot_captures_free_queen(board):
    set_kings(board, white_pos=(0, 0), black_pos=(7, 7))
    board.grid[4][4] = Rook(Color.WHITE)
    board.grid[4][6] = Queen(Color.BLACK)

    move = Bot(board).best_move(3, Color.WHITE)

    assert move == ((4, 4), (4, 6), MoveType.NORMAL)


def test_bot_avoids_losing_queen(board):
    set_kings(board, white_pos=(0, 0), black_pos=(7, 7))
    board.grid[4][4] = Queen(Color.WHITE)
    board.grid[5][5] = Pawn(Color.BLACK)

    move = Bot(board).best_move(4, Color.WHITE)

    assert move == ((4, 4), (5, 5), MoveType.NORMAL)

def test_bot_captures_pawn(board):
    set_kings(board, white_pos=(0, 0), black_pos=(3, 7))
    board.grid[4][4] = Queen(Color.WHITE)
    board.grid[4][3] = Pawn(Color.BLACK)

    move = Bot(board).best_move(6, Color.WHITE)

    assert move == ((4, 4), (4, 3), MoveType.NORMAL)


def test_bot_promotes_pawn(board):
    set_kings(board, white_pos=(0, 4), black_pos=(0, 7))
    board.grid[6][3] = Pawn(Color.WHITE)

    move = Bot(board).best_move(3, Color.WHITE)

    assert move[2] == MoveType.PROMOTION_QUEEN


def test_bot_returns_none_when_no_moves(board):
    set_kings(board, white_pos=(6, 2), black_pos=(7, 0))
    board.grid[5][1] = Queen(Color.WHITE)

    move = Bot(board).best_move(3, Color.BLACK)

    assert move is None


def test_eval_position_subtracts_black_pst(board):
    set_kings(board)
    board.grid[7][0] = Rook(Color.BLACK)

    bot = Bot(board)
    bot.current_pst = bot.pst[Phase.ENDGAME]

    expected = -5
    expected += bot.current_pst[Color.WHITE][PieceType.KING][0][3]
    expected -= bot.current_pst[Color.BLACK][PieceType.KING][7][3]
    expected -= bot.current_pst[Color.BLACK][PieceType.ROOK][7][0]

    assert bot.eval_position() == pytest.approx(expected)


def test_black_castling_lowers_white_eval(board):
    set_kings(board)
    board.grid[7][0] = Rook(Color.BLACK)

    bot = Bot(board)
    bot.current_pst = bot.pst[Phase.OPENING]

    assert ((7, 1), MoveType.CASTLING) in board.get_legal_moves(7, 3)

    before = bot.eval_position()
    diff = bot.eval_table_diff((7, 3), (7, 1), MoveType.CASTLING)
    undo_data = board.make_move((7, 3), (7, 1), MoveType.CASTLING)
    after = bot.eval_position()
    board.undo_move((7, 3), (7, 1), undo_data, MoveType.CASTLING)

    assert diff < 0
    assert after == pytest.approx(before + diff)


def test_mate_in_3_white(board):
    set_kings(board, white_pos=(0, 0), black_pos=(7, 6))
    board.grid[0][5] = Queen(Color.WHITE)
    board.grid[1][6] = Pawn(Color.WHITE)
    board.grid[0][7] = Rook(Color.WHITE)
    board.grid[5][6] = Pawn(Color.WHITE)
    board.grid[6][6] = Pawn(Color.BLACK)
    board.grid[6][5] = Pawn(Color.BLACK)
    board.grid[7][5] = Rook(Color.BLACK)

    move = Bot(board).best_move(7, Color.WHITE)

    assert move == ((0, 7), (7, 7), MoveType.NORMAL)
