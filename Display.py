"""
Lines of Action Display class
Starbuck Beagley
"""


class Display:
    def __init__(self, r, c):
        self.rows = r
        self.cols = c

    def show_board(self, grid=[]):
        i = 65
        print("  ", end="")
        for c in range(0, self.cols):
            print(str(chr(i)) + " ", end="")
            i += 1
        print("")
        for r in range(0, self.rows):
            print(str(r), end="|")
            for c in range(0, self.cols):
                print(str(grid[r][c]), end="|")
            print("")
