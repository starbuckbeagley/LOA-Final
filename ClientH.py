"""
Lines of Action human client
Starbuck Beagley

"""

import Player
import Board
import Move


class ClientH:

    def __init__(self, num):
        self.rows = 8
        self.cols = 8
        self.player = Player.Player(num)
        if num == 1:
            self.opponent = Player.Player(2)
        else:
            self.opponent = Player.Player(1)
        self.board = Board.Board(self.rows, self.cols, self.player, self.opponent)
        self.move = Move.Move(self.board, self.player, self.opponent)

    def initialize(self):
        self.board.reset_board()

    def get_num(self):
        return self.player.get_number()

    @staticmethod
    def next_move():
        return list("".join(input().split()))

    def move_was(self, p, move):
        if p == self.player.get_number():
            a_move = self.move.make_move(self.player, move[0], move[1], move[2], move[3])
        else:
            a_move = self.move.make_move(self.opponent, move[0], move[1], move[2], move[3])
        if a_move[0] == 0:
            pass
            # print(a_move[1])
            # print("Illegal move approved by server. This message should never happen!")
