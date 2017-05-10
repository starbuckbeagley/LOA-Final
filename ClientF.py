"""
Lines of Action forgiving human client
Extends SuperClient
Warns player about invalid moves

Starbuck Beagley
"""
from SuperClient import SuperClient

ORD_A_LOWER = 97
COLS = 8


class ClientF(SuperClient):

    def __init__(self, num):
        """
        Constructor
        :param num: player number
        """
        SuperClient.__init__(self, num)

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
            elif not translate(l, a, COLS):
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
    for j in range(ORD_A_LOWER, ORD_A_LOWER + c):
        if l[1].lower() == chr(j):
            a.append(j - ORD_A_LOWER)
            break
        elif j == (ORD_A_LOWER + c - 1):
            return False
    try:
        i = int(l[2])
        a.append(i)
    except ValueError:
        return False
    for j in range(ORD_A_LOWER, ORD_A_LOWER + c):
        if l[3].lower() == chr(j):
            a.append(j - ORD_A_LOWER)
            break
        elif j == (ORD_A_LOWER + c - 1):
            return False
    return True
