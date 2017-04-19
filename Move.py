"""
Lines of Action Move class
Starbuck Beagley
"""


class Move:
    def __init__(self, b, p1, p2):
        """
        Constructor
        :param b: board
        :param p1: player 1
        :param p2: player 2
        """
        self.board = b
        self.player1 = p1
        self.player2 = p2
        self.rows = self.board.get_rows()
        self.cols = self.board.get_cols()

    def make_move(self, p, r1, c1, r2, c2):
        """
        Attempts to perform requested move
        :param p: current player
        :param r1: row coordinate of piece
        :param c1: column coordinate of piece
        :param r2: row coordinate of target
        :param c2: column coordinate of target
        :return: confirmation message if move is legal, error message otherwise
        """
        r1 = int(r1)
        c1 = int(c1)
        r2 = int(r2)
        c2 = int(c2)
        message = self.legal_move(p, r1, c1, r2, c2)
        player_piece = p.get_piece()
        if message != "Legal":
            tup = (0, message)
            return tup
        else:
            lost_piece = ""
            if p == self.player1 and self.board.get_grid()[r2][c2] == self.player2.get_piece():
                self.player2.lose_piece()
                lost_piece = ", taking opponent's piece"
            elif p == self.player2 and self.board.get_grid()[r2][c2] == self.player1.get_piece():
                self.player1.lose_piece()
                lost_piece = ", taking opponent's piece"
            self.board.get_grid()[r1][c1] = ' '
            self.board.get_grid()[r2][c2] = player_piece
            m = "Moved " + str(p) + "'s piece from " + str(r1) + self.num_to_let(c1) \
                + " to " + str(r2) + self.num_to_let(c2) + lost_piece
            tup = (1, m)
            return tup

    @staticmethod
    def num_to_let(num):
        """
        Translates number to letter for output string
        :param num: number to translate
        :return: translated letter
        """
        return chr(65 + num)

    def check_for_win(self, player):
        """
        Checks for winning arrangement
        :param player: current player
        :return: true if current player has won
        """
        if player.get_pieces_left() == 1:
            return True
        piece = player.get_piece()
        start = self.get_first_piece(piece)
        if not start:
            return False
        visited = [start]
        self.win_recur(start, visited, piece)
        return player.get_pieces_left() == len(visited)

    def get_first_piece(self, piece):
        for r in range(0, self.rows):
            for c in range(0, self.cols):
                if self.board.get_grid()[r][c] == piece:
                    tup = (r, c)
                    return tup
        return False

    def win_recur(self, tup, visited, piece):
        """
        Recursively checks if a player's pieces are all adjacent
        :param tup: tuple containing the current coordinate
        :param visited: list of visited coordinates
        :param piece: player's piece to check
        :return: true if all pieces are adjacent
        """
        row = tup[0]
        col = tup[1]
        if row - 1 > -1:
            tup_n = (row - 1, col)
            if self.board.get_grid()[row - 1][col] == piece and not tup_n in visited:
                visited.append(tup_n)
                self.win_recur(tup_n, visited, piece)
            if col - 1 > -1:
                tup_nw = (row - 1, col - 1)
                if self.board.get_grid()[row - 1][col - 1] == piece and not tup_nw in visited:
                    visited.append(tup_nw)
                    self.win_recur(tup_nw, visited, piece)
            if col + 1 < self.cols:
                tup_ne = (row - 1, col + 1)
                if self.board.get_grid()[row - 1][col + 1] == piece and not tup_ne in visited:
                    visited.append(tup_ne)
                    self.win_recur(tup_ne, visited, piece)
        if row + 1 < self.rows:
            tup_s = (row + 1, col)
            if self.board.get_grid()[row + 1][col] == piece and not tup_s in visited:
                visited.append(tup_s)
                self.win_recur(tup_s, visited, piece)
            if col - 1 > -1:
                tup_sw = (row + 1, col - 1)
                if self.board.get_grid()[row + 1][col - 1] == piece and not tup_sw in visited:
                    visited.append(tup_sw)
                    self.win_recur(tup_sw, visited, piece)
            if col + 1 < self.cols:
                tup_se = (row + 1, col + 1)
                if self.board.get_grid()[row + 1][col + 1] == piece and not tup_se in visited:
                    visited.append(tup_se)
                    self.win_recur(tup_se, visited, piece)
        if col - 1 > -1:
            tup_w = (row, col - 1)
            if self.board.get_grid()[row][col - 1] == piece and not tup_w in visited:
                visited.append(tup_w)
                self.win_recur(tup_w, visited, piece)
        if col + 1 < self.cols:
            tup_e = (row, col + 1)
            if self.board.get_grid()[row][col + 1] == piece and not tup_e in visited:
                visited.append(tup_e)
                self.win_recur(tup_e, visited, piece)
        return visited

    def legal_move(self, p, r1, c1, r2, c2):
        """
        Checks legality of proposed move
        :param p: current player
        :param r1: row coordinate of piece
        :param c1: column coordinate of piece
        :param r2: row coordinate of target
        :param c2: column coordinate of target
        :return: "Legal" if legal, error message otherwise
        """
        player_piece = p.get_piece()
        if p.get_number() == 1:
            opp_piece = self.player2.get_piece()
        else:
            opp_piece = self.player1.get_piece()
        if r1 == r2 and c1 == c2:
            return "Piece and destination coordinates must be different."
        elif not self.legal_coords(r1, c1, r2, c2):
            return "Coordinates outside board boundaries."
        elif self.board.get_grid()[r1][c1] != p.get_piece():
            return str(p) + "'s piece not at location " + str(r1) + self.num_to_let(c1) + "."
        elif not self.legal_distance(r1, c1, r2, c2):
            return "Can't move that many spaces from " + str(r1) + self.num_to_let(c1) + "."
        elif not self.legal_direction(r1, c1, r2, c2):
            return "Illegal direction."
        elif self.check_opp_piece(r1, c1, r2, c2, opp_piece):
            return "Cannot jump opponent's piece."
        elif self.board.get_grid()[r2][c2] == player_piece:
            return "Cannot move to space occupied by own piece."
        else:
            return "Legal"

    def legal_coords(self, r1, c1, r2, c2):
        """
        Checks all move coordinates for legality
        :param r1: row position of piece
        :param c1: column position of piece
        :param r2: row position of target
        :param c2: column position of target
        :return: true if coordinates are legal
        """
        if r1 < 0 or r1 >= self.rows or \
                c1 < 0 or c1 >= self.cols or \
                r2 < 0 or r2 >= self.rows or \
                c2 < 0 or c2 >= self.cols:
            return False
        return True

    @staticmethod
    def legal_direction(r1, c1, r2, c2):
        """
        Checks if move direction is legal
        :param r1: row position of piece
        :param c1: column position of piece
        :param r2: row position of target
        :param c2: column position of target
        :return: true if direction is legal
        """
        if r1 == r2:
            return True
        elif c1 == c2:
            return True
        if abs(r1 - r2) == abs(c1 - c2):
            return True
        else:
            return False

    def legal_distance(self, r1, c1, r2, c2):
        if r1 == r2:
            d = abs(c1 - c2)
        else:
            d = abs(r1 - r2)
        return d == self.piece_line_count(r1, c1, r2, c2)

    def piece_line_count(self, r1, c1, r2, c2):
        """
        Gets number of pieces in a specific row, column or diagonal
        :param r1: row position of piece
        :param c1: column position of piece
        :param r2: row position of target
        :param c2: column position of target
        :return: piece count
        """
        count = 0

        if r1 == r2:
            for c in range(0, self.cols):
                if self.board.get_grid()[r1][c] != ' ':
                    count += 1
        elif c1 == c2:
            for r in range(0, self.rows):
                if self.board.get_grid()[r][c1] != ' ':
                    count += 1
        else:
            slope = (r1 - r2) // (c1 - c2)
            if slope > 0:
                r_check = r1
                c_check = c1
                while r_check < self.rows and c_check < self.cols:
                    if self.board.get_grid()[r_check][c_check] != ' ':
                        count += 1
                    r_check += 1
                    c_check += 1
                r_check = r1 - 1
                c_check = c1 - 1
                while r_check > -1 and c_check > -1:
                    if self.board.get_grid()[r_check][c_check] != ' ':
                        count += 1
                    r_check -= 1
                    c_check -= 1
            else:
                r_check = r1
                c_check = c1
                while r_check > -1 and c_check < self.cols:
                    if self.board.get_grid()[r_check][c_check] != ' ':
                        count += 1
                    r_check -= 1
                    c_check += 1
                r_check = r1 + 1
                c_check = c1 - 1
                while r_check < self.rows and c_check > -1:
                    if self.board.get_grid()[r_check][c_check] != ' ':
                        count += 1
                    r_check += 1
                    c_check -= 1
        return count

    def check_opp_piece(self, r1, c1, r2, c2, piece):
        """
        Checks for opponent piece
        :param r1: row position of piece
        :param c1: column position of piece
        :param r2: row position of target
        :param c2: column position of target
        :param piece: opponent piece type
        :return: true if opponent piece found
        """
        if r1 == r2:
            if c1 > c2:
                c_start = c2 + 1
                c_end = c1
            else:
                c_start = c1 + 1
                c_end = c2
            for c in range(c_start, c_end):
                if self.board.get_grid()[r1][c] == piece:
                    return True
        elif c1 == c2:
            if r1 > r2:
                r_start = r2 + 1
                r_end = r1
            else:
                r_start = r1 + 1
                r_end = r2
            for r in range(r_start, r_end):
                if self.board.get_grid()[r][c1] == piece:
                    return True
        else:
            slope = (r1 - r2) // (c1 - c2)
            if slope > 0:
                if r1 > r2:
                    r_start = r2 + 1
                    c_start = c2 + 1
                    r_end = r1 - 1
                    c_end = c1 - 1
                else:
                    r_start = r1 + 1
                    c_start = c1 + 1
                    r_end = r2 - 1
                    c_end = c2 - 1
                r = r_start
                c = c_start
                while r <= r_end and c <= c_end:
                    if self.board.get_grid()[r][c] == piece:
                        return True
                    r += 1
                    c += 1
            else:
                if r1 > r2:
                    r_start = r1 - 1
                    c_start = c1 + 1
                    r_end = r2 + 1
                    c_end = c2 - 1
                else:
                    r_start = r2 - 1
                    c_start = c2 + 1
                    r_end = r1 + 1
                    c_end = c1 - 1
                r = r_start
                c = c_start
                while r >= r_end and c <= c_end:
                    if self.board.get_grid()[r][c] == piece:
                        return True
                    r -= 1
                    c += 1
        return False
