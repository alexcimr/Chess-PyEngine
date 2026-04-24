import pytest

from model.board import Board
from model.enums import Color, GameStatus, MoveType, PieceType
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


def test_setup_start_position(board):
    board.setup_start_position()

    assert board.white_king_pos == (0, 3)
    assert board.black_king_pos == (7, 3)
    assert board.grid[0][3].type == PieceType.KING
    assert board.grid[7][4].type == PieceType.QUEEN
    assert sum(piece is not None for row in board.grid for piece in row) == 32
    assert board.material_on_board() == 78


def test_square_helpers(board):
    board.grid[2][5] = Pawn(Color.BLACK)

    assert board.is_empty(2, 4) is True
    assert board.is_empty(2, 5) is False
    assert board.is_empty(8, 8) is False
    assert board.get_piece_type(2, 5) == PieceType.PAWN
    assert board.get_piece_color(2, 5) == Color.BLACK
    assert board.get_piece_type(4, 4) is None
    assert board.get_piece_color(4, 4) is None
    assert board.get_piece_type(-1, 0) is None
    assert board.get_piece_color(-1, 0) is None


def test_update_king_positions_and_eval_position(board):
    board.grid[1][1] = King(Color.WHITE)
    board.grid[6][6] = King(Color.BLACK)
    board.grid[4][4] = Queen(Color.WHITE)
    board.grid[5][5] = Rook(Color.BLACK)

    board.update_king_positions()

    assert board.white_king_pos == (1, 1)
    assert board.black_king_pos == (6, 6)
    assert board.eval_position() == 4


def test_is_tile_in_check(board):
    board.grid[4][4] = King(Color.WHITE)
    board.grid[7][7] = King(Color.BLACK)
    board.grid[4][0] = Rook(Color.BLACK)

    assert board.is_tile_in_check(4, 4, Color.BLACK) is True

    board.grid[4][2] = Pawn(Color.WHITE)
    assert board.is_tile_in_check(4, 4, Color.BLACK) is False

    board.grid[4][2] = None
    board.grid[2][3] = Knight(Color.BLACK)
    assert board.is_tile_in_check(4, 4, Color.BLACK) is True

    board.grid[2][3] = None
    board.grid[3][3] = Pawn(Color.BLACK)
    assert board.is_tile_in_check(4, 4, Color.BLACK) is True

    board.grid[3][3] = None
    board.grid[2][2] = Bishop(Color.BLACK)
    assert board.is_tile_in_check(4, 4, Color.BLACK) is True


def test_make_move_and_undo_restore_state(board):
    set_kings(board)
    pawn = Pawn(Color.WHITE)
    board.grid[1][4] = pawn
    board.update_zobrist_hash()
    start_hash = board.current_hash

    undo_data = board.make_move((1, 4), (3, 4))

    assert board.grid[3][4] is pawn
    assert board.grid[1][4] is None
    assert pawn.moved is True
    assert board.enpassant_tile == (2, 4)

    board.undo_move((1, 4), (3, 4), undo_data)

    assert board.grid[1][4] is pawn
    assert board.grid[3][4] is None
    assert pawn.moved is False
    assert board.enpassant_tile is None
    assert board.current_hash == start_hash


def test_en_passant_move_and_undo(board):
    set_kings(board)
    white_pawn = Pawn(Color.WHITE)
    black_pawn = Pawn(Color.BLACK)
    board.grid[4][3] = white_pawn
    board.grid[6][4] = black_pawn
    board.update_zobrist_hash()

    board.make_move((6, 4), (4, 4))
    undo_data = board.make_move((4, 3), (5, 4), MoveType.EN_PASSANT)

    assert board.grid[5][4] is white_pawn
    assert board.grid[4][4] is None
    assert board.grid[4][3] is None

    board.undo_move((4, 3), (5, 4), undo_data, MoveType.EN_PASSANT)

    assert board.grid[4][3] is white_pawn
    assert board.grid[4][4] is black_pawn
    assert board.grid[5][4] is None


def test_castling_move_and_undo(board):
    board.grid[0][3] = King(Color.WHITE)
    board.grid[0][0] = Rook(Color.WHITE)
    board.grid[7][3] = King(Color.BLACK)
    board.update_king_positions()
    board.update_zobrist_hash()
    white_king = board.grid[0][3]
    white_rook = board.grid[0][0]

    undo_data = board.make_move((0, 3), (0, 1), MoveType.CASTLING)

    assert board.grid[0][1] is white_king
    assert board.grid[0][2] is white_rook
    assert white_king.moved is True
    assert white_rook.moved is True

    board.undo_move((0, 3), (0, 1), undo_data, MoveType.CASTLING)

    assert board.grid[0][3] is white_king
    assert board.grid[0][0] is white_rook
    assert board.grid[0][1] is None
    assert board.grid[0][2] is None
    assert white_king.moved is False
    assert white_rook.moved is False


def test_promotion_and_undo(board):
    set_kings(board)
    pawn = Pawn(Color.WHITE)
    board.grid[6][0] = pawn
    board.update_zobrist_hash()

    undo_data = board.make_move((6, 0), (7, 0), MoveType.PROMOTION_QUEEN)

    assert board.grid[7][0].type == PieceType.QUEEN
    assert board.grid[7][0].color == Color.WHITE

    board.undo_move((6, 0), (7, 0), undo_data, MoveType.PROMOTION_QUEEN)

    assert board.grid[6][0].type == PieceType.PAWN
    assert board.grid[6][0].color == Color.WHITE
    assert board.grid[7][0] is None


def test_game_status_checkmate(board):
    board.grid[0][0] = King(Color.WHITE)
    board.grid[1][1] = Queen(Color.BLACK)
    board.grid[2][2] = King(Color.BLACK)
    board.update_king_positions()

    assert board.game_status(Color.WHITE) == GameStatus.CHECKMATE


def test_game_status_stalemate(board):
    board.grid[0][0] = King(Color.WHITE)
    board.grid[1][2] = Queen(Color.BLACK)
    board.grid[2][1] = King(Color.BLACK)
    board.update_king_positions()

    assert board.game_status(Color.WHITE) == GameStatus.STALEMATE


def test_all_legal_moves_prioritizes_capture(board):
    set_kings(board)
    board.grid[3][3] = Rook(Color.WHITE)
    board.grid[3][6] = Queen(Color.BLACK)

    moves = board.all_legal_moves(Color.WHITE)

    assert moves[0][0] == ((3, 3), (3, 6), MoveType.NORMAL)
    assert moves[0][1] == 9


def test_tile_value_counts_capture_and_special_move(board):
    board.grid[3][3] = Queen(Color.BLACK)

    assert board.tile_value(3, 3, MoveType.NORMAL) == 9

    board.grid[3][3] = None

    assert board.tile_value(3, 3, MoveType.PROMOTION_QUEEN) == 8
    assert board.tile_value(3, 3, MoveType.EN_PASSANT) == 1


def test_update_zobrist_hash_changes_with_position(board):
    set_kings(board)
    board.update_zobrist_hash()
    start_hash = board.current_hash
    board.grid[3][3] = Rook(Color.WHITE)

    board.update_zobrist_hash()

    assert board.current_hash != 0
    assert board.current_hash != start_hash
