"""
Lines of Action computer client
Extends SuperClient

Starbuck Beagley
"""
import random
from SuperClient import SuperClient

ROWS = 8
COLS = 8
ORD_A = 65


class ClientBadC(SuperClient):
    def __init__(self, num):
        """
        Constructor
        :param num: player number
        """
        SuperClient.__init__(self, num)

    def next_move(self):
        """
        Gets move from player
        :return: player move as list
        """
        return get_computer_move(self.player, self.move)


def get_computer_move(player, move):
    """
    Gets a random, legal move for computer player
    :param player: which player computer represents, for move legality
    :param move: Move object, checks move legality
    :return: computer's move if random move is legal, recursive call otherwise
    """
    r1 = random.randint(0, (ROWS - 1))
    c1 = random.randint(0, (COLS - 1))
    r2 = random.randint(0, (ROWS - 1))
    c2 = random.randint(0, (COLS - 1))
    while 1:
        if move.legal_move(player, r1, c1, r2, c2) == "Legal":
            a = [r1, c1, r2, c2]
            untranslate(a)
            return a
        else:
            return get_computer_move(player, move)

def untranslate(a):
    """
    Server expects ord-char-ord-char format
    :param a: list of number-only coordinates
    :return: coordinate string where rows are letters
    """
    a[1] = str(chr(ORD_A + a[1]))
    a[3] = str(chr(ORD_A + a[3]))
