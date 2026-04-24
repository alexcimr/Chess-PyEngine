import pytest

from model.board import Board
from model.enums import Color, MoveType
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


def test_pawn_moves_from_start(board):
    set_kings(board)
    board.grid[1][3] = Pawn(Color.WHITE)

    moves = board.get_legal_moves(1, 3)

    assert {end for end, _ in moves} == {(2, 3), (3, 3)}
    assert all(move_type == MoveType.NORMAL for _, move_type in moves)


def test_pawn_blocked(board):
    board.grid[1][3] = Pawn(Color.WHITE)
    board.grid[2][3] = Pawn(Color.BLACK)

    moves = board.grid[1][3].moves(board, 1, 3)

    assert moves == []


def test_pawn_captures_diagonally(board):
    board.grid[1][3] = Pawn(Color.WHITE)
    board.grid[2][4] = Pawn(Color.BLACK)

    moves = board.grid[1][3].moves(board, 1, 3)

    assert (2, 4) in moves


def test_pawn_en_passant(board):
    set_kings(board)
    board.grid[4][3] = Pawn(Color.WHITE)
    board.grid[6][4] = Pawn(Color.BLACK)

    board.make_move((6, 4), (4, 4))
    moves = board.get_legal_moves(4, 3)

    assert ((5, 4), MoveType.EN_PASSANT) in moves


def test_rook_stops_before_friendly_piece(board):
    board.grid[3][3] = Rook(Color.WHITE)
    board.grid[3][5] = Pawn(Color.WHITE)

    moves = board.grid[3][3].moves(board, 3, 3)

    assert (3, 4) in moves
    assert (3, 5) not in moves
    assert (3, 6) not in moves


def test_rook_captures_enemy_and_stops(board):
    board.grid[3][3] = Rook(Color.WHITE)
    board.grid[3][5] = Pawn(Color.BLACK)

    moves = board.grid[3][3].moves(board, 3, 3)

    assert (3, 5) in moves
    assert (3, 6) not in moves


def test_knight_jumps_over_pieces(board):
    board.grid[3][3] = Knight(Color.WHITE)
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr or dc:
                board.grid[3 + dr][3 + dc] = Pawn(Color.WHITE)

    moves = board.grid[3][3].moves(board, 3, 3)

    assert set(moves) == {
        (1, 2), (1, 4),
        (2, 1), (2, 5),
        (4, 1), (4, 5),
        (5, 2), (5, 4),
    }


def test_bishop_captures_on_diagonal(board):
    board.grid[3][3] = Bishop(Color.WHITE)
    board.grid[5][5] = Pawn(Color.BLACK)

    moves = board.grid[3][3].moves(board, 3, 3)

    assert (4, 4) in moves
    assert (5, 5) in moves
    assert (6, 6) not in moves


def test_queen_combines_straight_and_diagonal_moves(board):
    board.grid[3][3] = Queen(Color.WHITE)

    moves = board.grid[3][3].moves(board, 3, 3)

    assert len(moves) == 27
    assert (3, 0) in moves
    assert (0, 3) in moves
    assert (0, 0) in moves
    assert (7, 7) in moves


def test_king_cannot_move_into_check(board):
    board.grid[3][3] = King(Color.WHITE)
    board.grid[7][7] = King(Color.BLACK)
    board.grid[3][0] = Rook(Color.BLACK)
    board.update_king_positions()

    moves = board.get_legal_moves(3, 3)
    destinations = {end for end, _ in moves}

    assert (3, 2) not in destinations
    assert (3, 4) not in destinations
    assert (2, 2) in destinations


def test_king_can_castle_on_clear_side(board):
    board.grid[0][3] = King(Color.WHITE)
    board.grid[0][0] = Rook(Color.WHITE)
    board.grid[7][3] = King(Color.BLACK)
    board.update_king_positions()

    moves = board.get_legal_moves(0, 3)

    assert ((0, 1), MoveType.CASTLING) in moves
