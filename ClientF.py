"""
Lines of Action forgiving human client
Warns player about invalid moves
Starbuck Beagley

"""

import Player
import Board
import Move


class ClientF:

    def __init__(self, num):
        """
        Constructor
        :param num: player number
        """
        self.rows = 8
        self.cols = 8
        self.player = Player.Player(num)
        if num == 1:
            self.opponent = Player.Player(2)
            self.board = Board.Board(self.rows, self.cols, self.player, self.opponent)
            self.move = Move.Move(self.board, self.player, self.opponent)
        else:
            self.opponent = Player.Player(1)
            self.board = Board.Board(self.rows, self.cols, self.opponent, self.player)
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
        Requests move from player until valid move is submitted
        :return: player move as list
        """
        while 1:
            l = list("".join(input().split()))
            a = []
            if l[0].lower() == "q":
                return l
            elif not translate(l, a, 8):
                print("\nIllegal move format.\n")
                print("Player " + str(self.player.get_number()) + "'s turn (" + self.player.get_piece() + ").")
                print("Enter piece and destination coordinates, row before column, separated by a space: ")
            else:
                move_check = self.move.legal_move(self.player, a[0], a[1], a[2], a[3])
                if move_check == "Legal":
                    return l
                else:
                    print("\n" + move_check + "\n")
                    print("Player " + str(self.player.get_number()) + "'s turn (" + self.player.get_piece() + ").")
                    print("Enter piece and destination coordinates, row before column, separated by a space: ")

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


def translate(l, a, c):
    """
    Translates user input into numbers for processing
    :param l: user input
    :param a: list to put translated move into
    :param c: number of columns of board
    :return: true if user input is valid, false otherwise
    """
    try:
        i = int(l[0])
        a.append(i)
    except ValueError:
        return False
    for j in range(97, 97 + c):
        if l[1].lower() == chr(j):
            a.append(j - 97)
            break
        elif j == (96 + c):
            return False
    try:
        i = int(l[2])
        a.append(i)
    except ValueError:
        return False
    for j in range(97, 97 + c):
        if l[3].lower() == chr(j):
            a.append(j - 97)
            break
        elif j == (96 + c):
            return False
    return True
