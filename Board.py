"""
Lines of Action Board class
Starbuck Beagley
"""


class Board:
    def __init__(self, r, c, p1, p2):
        """
        Constructor
        :param r: total rows
        :param c: total columns
        :param p1: player 1's piece
        :param p2: player 2's piece
        """
        self.rows = r
        self.cols = c
        if p1.get_number() == 1:
            self.piece1 = p1.get_piece()
            self.piece2 = p2.get_piece()
        else:
            self.piece1 = p2.get_piece()
            self.piece2 = p1.get_piece()
        self.grid = [[' ' for x in range(self.cols)] for y in range(self.rows)]

    def reset_board(self):
        """ Sets board to initial state """
        for r in range(0, self.rows):
            for c in range(0, self.cols):
                self.grid[r].append(' ')
        for rr in range(1, self.rows - 1):
            self.grid[rr][0] = self.piece1
            self.grid[rr][self.cols - 1] = self.piece1
        for cc in range(1, self.cols - 1):
            self.grid[0][cc] = self.piece2
            self.grid[self.rows - 1][cc] = self.piece2

    def get_grid(self):
        """
        Gets grid
        :return: grid
        """
        return self.grid

    def get_cell(self, r, c):
        """
        Gets piece occupying cell, if any
        :param r: row position
        :param c: column position
        :return: piece at grid[r][c]
        """
        return self.grid[r][c]

    def get_rows(self):
        """
        Gets total rows in grid
        :return: total rows
        """
        return self.rows

    def get_cols(self):
        """
        Gets total columns in grid
        :return: total columns
        """
        return self.cols

    def change_cell(self, r, c, p):
        """
        Changes piece occupying particular cell
        :param r: row position
        :param c: column position
        :param p: new piece
        """
        self.grid[r][c] = p
