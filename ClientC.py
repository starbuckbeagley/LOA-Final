"""
Lines of Action computer client
Starbuck Beagley

"""

import Player
import Board
import Move
import random


class ClientC:

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

    def next_move(self):
        return get_computer_move(self.player, self.move)

    def move_was(self, p, move):
        if p == self.player.get_number():
            a_move = self.move.make_move(self.player, move[0], move[1], move[2], move[3])
        else:
            a_move = self.move.make_move(self.opponent, move[0], move[1], move[2], move[3])
        if a_move[0] == 0:
            pass
            # print(a_move[1])
            # print("Illegal move approved by server. This message should never happen!")


def get_computer_move(player, move):
    """
    Gets a random, legal move for computer player
    :param player: which player computer represents, for move legality
    :param move: Move object, checks move legality
    :return: computer's move if random move is legal, recursive call otherwise
    """
    r1 = random.randint(0, 7)
    c1 = random.randint(0, 7)
    r2 = random.randint(0, 7)
    c2 = random.randint(0, 7)
    while 1:
        if move.legal_move(player, r1, c1, r2, c2) == "Legal":
            a = [r1, c1, r2, c2]
            return a
        else:
            return get_computer_move(player, move)
