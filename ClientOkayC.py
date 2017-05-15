"""
Lines of Action computer client
Extends SuperClient

Starbuck Beagley
"""
import random
from SuperClient import SuperClient

ROWS = 8
COLS = 8
MID1 = 3
MID2 = 4
ORD_A = 65


class ClientOkayC(SuperClient):
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
    Tries moving a piece closer to the center of the board, tries random moves if this strategy fails
    :param player: which player computer represents, for move legality
    :param move: Move object, checks move legality
    :return: computer's move
    """
    row_list = []
    col_list = []
    for i in range(0, int((ROWS / 2))):
        r = [i, (ROWS - i)]
        random.shuffle(r)
        for j in range(0, 2):
            row_list.append(r[j])
        random.shuffle(r)
        for j in range(0, 2):
            col_list.append(r[j])
    for r1 in row_list:
        for c1 in col_list:
            for r2 in range(MID1, MID2 + 1):
                for c2 in range(MID1, MID2 + 1):
                    if move.legal_move(player, r1, c1, r2, c2) == "Legal":
                        a = [r1, c1, r2, c2]
                        untranslate(a)
                        return a
            for r2 in range(MID1 - 1, MID2 + 2, 3):
                for c2 in range(MID1 - 1, MID2 + 2, 3):
                    if move.legal_move(player, r1, c1, r2, c2) == "Legal":
                        a = [r1, c1, r2, c2]
                        untranslate(a)
                        return a
            for r2 in range(MID1 - 2, MID2 + 3, 5):
                for c2 in range(MID1 - 2, MID2 + 3, 5):
                    if move.legal_move(player, r1, c1, r2, c2) == "Legal":
                        a = [r1, c1, r2, c2]
                        untranslate(a)
                        return a
    while 1:
        r1 = random.randint(0, (ROWS - 1))
        c1 = random.randint(0, (COLS - 1))
        r2 = random.randint(0, (ROWS - 1))
        c2 = random.randint(0, (COLS - 1))
        if move.legal_move(player, r1, c1, r2, c2) == "Legal":
            a = [r1, c1, r2, c2]
            untranslate(a)
            return a


def untranslate(a):
    """
    Server expects ord-char-ord-char format
    :param a: list of number-only coordinates
    :return: coordinate string where rows are letters
    """
    a[1] = str(chr(ORD_A + a[1]))
    a[3] = str(chr(ORD_A + a[3]))
