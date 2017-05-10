"""
Lines of Action Server

Creates messages for server to send to clients
    
Starbuck Beagley
"""
from AbstractServer import AbstractServer
import Player
import Board
import Move

INIT = 0
P1_MOVE_REQ = 1
P2_MOVE_REQ = 2
P1_MOVE_WAS = 3
P2_MOVE_WAS = 4
WIN_MESS = 5
ERR_MESS = 6
QUIT_MESS = 7
ROWS = 8
COLS = 8

ORD_A_LOWER = 97


class LOAServer(AbstractServer):
    def __init__(self):
        """
        Constructor
        """
        self.player1 = Player.Player(1)
        self.player2 = Player.Player(2)
        self.board = Board.Board(ROWS, COLS, self.player1, self.player2)
        self.move = Move.Move(self.board, self.player1, self.player2)
        self.current_player = self.player1
        self.board.reset_board()

    def initialize_client(self, client_id, game_id):
        """
        Generates initial message to send to client
        :param client_id: which client will receive message
        :param game_id: unique game id
        :return: initial message for client
        """
        return [INIT, client_id, game_id, client_id]

    def request_move(self, client_id):
        """
        Generates move-request message to send to client
        :param client_id: which client will receive message
        :return: move-request message for client
        """
        return [client_id, "", self.board.get_grid()]

    def evaluate_move(self, client_id, msg):
        """
        Evaluates move for server
        :param client_id: which client made the move
        :param msg: the most recent move
        :return: evaluation message for server
        """
        if len(msg[1]) == 4:
            a = []
            if translate(msg[1], a, COLS):
                if client_id == self.player1.get_number():
                    return self.move.make_move(self.player1, a[0], a[1], a[2], a[3])
                else:
                    return self.move.make_move(self.player2, a[0], a[1], a[2], a[3])
        return [ERR_MESS, "Incorrect move format."]

    def send_move(self, client_id, msg):
        """
        Generates message informing client of most recent move
        :param client_id: who moved
        :param msg: the most recent move
        :return: recent-move message for client
        """
        a = []
        translate(msg[1], a, COLS)
        if client_id == P1_MOVE_WAS:
            return [P1_MOVE_WAS, a, self.board.get_grid()]
        else:
            return [P2_MOVE_WAS, a, self.board.get_grid()]

    def send_error(self, client_id, err_type):
        """
        Generates message to send to client when an error is caused
        by an invalid move or an unexpected disconnection
        :param client_id: which player made the invalid move
        :param err_type: string containing error
        :return: error message for client
        """
        other_player = 3 - client_id
        err_str = "Player " + str(client_id) + " error: " + str(err_type) + "\nPlayer " + \
                  str(client_id) + " is disqualified. Player " + str(other_player) + " wins!"
        return [ERR_MESS, err_str, self.board.get_grid()]

    def send_quit(self, client_id):
        """
        Generates message to send to client when a player quits
        :param client_id: which player quit
        :return: quit message for client
        """
        other_player = 3 - client_id
        quit_str = "Player " + str(client_id) + " quit. Player " + str(other_player) + " wins!"
        return [QUIT_MESS, quit_str, self.board.get_grid()]

    def send_win(self, winner):
        win_str = "Player " + str(winner) + " wins!"
        return [WIN_MESS, win_str, self.board.get_grid()]

    def check_win(self, current_player):
        if current_player == self.player1.get_number():
            return self.move.check_for_win(self.player1)
        else:
            return self.move.check_for_win(self.player2)


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
