from model.enums import PieceType, Color
from model.board import Board

class Pawn():
    def __init__(self, color: Color):
        self.type = PieceType.PAWN
        self.color = color

    def moves(self, board: Board, x: int, y: int) -> list[tuple[int, int]]:
        """
        Zwraca pseudo-ruchy, czyli wszystkie mozliwe nie
        zważając czy krol jest w szachu dla danej figury
        :param board:
        :param x: oś pozioma [0,7]
        :param y: oś pionowa [0,7]
        :return:
        """
        Moves = []
        if self.color == Color.WHITE:
            # taka fuknjce moze dodac sprawdzqja empty ze czy pole psute?
            # czy lepiej Board[x][y] == "#"? ze puste
            if y + 1 <= 7 and Board.empty(y, x):
                Moves.append((y + 1, x))
            if y == 1 and Board.empty(y + 1, x) and board.isEmpty(y + 2, x):
                Moves.append((x, y + 2))

            # tutaj cos ta wiesz chcialbym sprawdzic czy danan komorka to jest
            # czarny kolor ale jak bedzie pusta o slabo bo nie moge board[][].color = Color.Black bo moze byc puste
            if x + 1 <= 7 and y + 1 <= 7 and not board.empty(y + 1, x + 1) and Board[y + 1][x + 1].color == Color.BLACK:
        return Moves