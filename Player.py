"""
Lines of Action Player class
Starbuck Beagley
"""


class Player:

    def __init__(self, num):
        """
        Constructor
        :param num: player number
        :param p: player piece
        """
        self.number = num
        if num == 1:
            self.piece = 'x'
        else:
            self.piece = 'o'
        self.pieces_left = 12

    def get_number(self):
        """
        Gets player number
        :return: player number
        """
        return self.number

    def get_piece(self):
        """
        Gets player piece
        :return: player piece
        """
        return self.piece

    def lose_piece(self):
        """
        Decreases pieces_left by 1
        """
        self.pieces_left -= 1

    def get_pieces_left(self):
        """
        Gets pieces_left
        :return: pieces_left
        """
        return self.pieces_left

    def __str__(self):
        """
        ToString override
        :return: player 'name'
        """
        return "Player " + str(self.number)
