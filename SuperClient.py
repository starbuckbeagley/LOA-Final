"""
Client superclass for Lines of Action

Starbuck Beagley
"""

import Player
import Board
import Move

ROWS = 8
COLS = 8


class SuperClient:
    def __init__(self, num):
        """
        Constructor
        :param num: player number
        """
        self.player = Player.Player(num)
        if num == 1:
            self.opponent = Player.Player(2)
            self.board = Board.Board(ROWS, COLS, self.player, self.opponent)
            self.move = Move.Move(self.board, self.player, self.opponent)
        else:
            self.opponent = Player.Player(1)
            self.board = Board.Board(ROWS, COLS, self.opponent, self.player)
            self.move = Move.Move(self.board, self.opponent, self.player)

    def initialize(self):
        """
        Initializes client
        """
        self.board.reset_board()

    def get_num(self):
        """
        Gets player number
        :return: player number
        """
        return self.player.get_number()

    def next_move(self):
        """
        Gets move from player
        :return: player move as list
        """
        pass

    def move_was(self, p, move):
        """
        Applies last move to local board object
        :param p: player who moved
        :param move: player's move
        """
        if p == self.player.get_number():
            self.move.make_move(self.player, move[0], move[1], move[2], move[3])
        else:
            self.move.make_move(self.opponent, move[0], move[1], move[2], move[3])
