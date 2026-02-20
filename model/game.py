from model.board import Board
from model.enums import Color, MoveType, GameStatus
from model.utils import is_on_board



class Game:
    def __init__(self):
        self.board = Board()
        self.turn: Color = Color.WHITE
        self.status: GameStatus = GameStatus.NORMAL

    def new_game(self):
        self.board.clear_board()
        self.board.setup_start_position()
        self.turn = Color.WHITE
        self.status = GameStatus.NORMAL

    def make_move(self, start_pos: tuple[int, int], end_pos: tuple[int, int], pawn_promotion: MoveType | None):
        # TODO do poprawy tutaj
        if self.board.get_piece_type() is None or self.board.get_piece_type() != self.turn:
            return False

        Legal_moves = self.board.get_legal_moves(start_pos[0], start_pos[1])
        for coords, move_type in Legal_moves:
            if coords == end_pos and (pawn_promotion == None or pawn_promotion == move_type):
                self.board.make_move(start_pos, end_pos, move_type)
                self.turn = Color.BLACK
                return True

        return False

    def start_game_2_players(self):
        # TODO do poprawy tutaji dokonczenia tutaj
        self.new_game()

        while self.status == GameStatus.NORMAL:

            color_on_move = "Biały" if self.turn == Color.WHITE else "Czarny"

            self.board_print()
            print()
            print(f"Ruch: {color_on_move} ")
            print()
            while self.status == GameStatus.NORMAL:
                while not self.make_move(input(...)...):
                    self.turn = Color.WHITE if self.turn == Color.BLACK else Color.BLACK

            print(self.status)

    def board_print(self):
        print("  | H G F E D C B A")
        print("  | ----------------|")
        for row_index, row in enumerate(self.board.grid):
            print(f"{row_index + 1} |", end=" ")
            for col_index in range(8):
                if self.board.is_empty(row_index, col_index):
                    symbol = "."
                else:
                    symbol = self.board.get_piece_type(row_index,col_index).value
                    color = self.board.get_piece_color(row_index,col_index)
                    if color == Color.BLACK:
                        symbol = symbol.lower()
                print(f"{symbol} ", end="")
            print("|")