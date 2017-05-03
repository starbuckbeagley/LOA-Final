"""
Lines of Action server
Starbuck Beagley

Socket messages sent to the client are lists with three
elements. The first element is a code. The second element is
a list of coordinates for a move, a message, or an empty string.
The third element is the board state.

Socket messages received by the client are lists with two elements.
The first element is a code. The second element is either a list
of coordinates for a move or an empty string.

Socket codes:
    0: Initialize (gets remote player if needed)
    1: Player 1 move request
    2: Player 2 move request
    3: Player 1 move was
    4: Player 2 move was
    5: Player win
    6: Error
    7: Quit

"""

import socket
import pickle
import Player
import Board
import Move
import time
import threading

INIT = 0
P1_MOVE_REQ = 1
P2_MOVE_REQ = 2
P1_MOVE_WAS = 3
P2_MOVE_WAS = 4
WIN_MESS = 5
ERR_MESS = 6
QUIT_MESS = 7


def main():

    needs_opponent = []
    game_id = 1
    threads = []

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = socket.gethostname()
    port = 7667
    server_socket.bind((host, port))
    server_socket.listen(100)

    while 1:
        print("Waiting for player")
        client_socket1, addr1 = server_socket.accept()
        print("Got connection from %s" % str(addr1))

        msg_in1 = client_socket1.recv(1024)
        msg = pickle.loads(msg_in1)

        if msg[0] == INIT:
            if msg[1]:
                if len(needs_opponent) != 0:
                    opp = needs_opponent.pop(0)
                    print("Game #" + str(opp[0]) + ": Got remote opponent. Starting thread.")
                    threads.append(LOAThread(opp[0], opp[1], client_socket1))
                    threads[len(threads) - 1].start()
                else:
                    print("Game #" + str(game_id) + ": Got player who needs remote opponent. Adding to queue.")
                    needs_opponent.append((game_id, client_socket1))
                    game_id += 1
            else:
                print("Game #" + str(game_id) + ": No remote player needed. Starting thread.")
                threads.append(LOAThread(game_id, client_socket1, None))
                threads[len(threads) - 1].start()
                game_id += 1
        else:
            err_msg = "Server needs to know if player 2 is remote. Passing."
            print(err_msg)
            client_socket1.sendall(pickle.dumps([ERR_MESS, err_msg]))


class LOAThread(threading.Thread):
    def __init__(self, game_id, client_socket1, client_socket2):
        """
        Constructor
        :param game_id: unique game identifier 
        :param client_socket1: socket object for client 1
        :param client_socket2: socket object for client 2 ("None" if local game)
        """
        threading.Thread.__init__(self)
        self.game_id = game_id
        self.client_socket1 = client_socket1
        self.client_socket2 = client_socket2

    def run(self):
        run_game(self.game_id, self.client_socket1, self.client_socket2)


def run_game(game_id, client_socket1, client_socket2):
    """
    Function to control game for each thread
    :param game_id: unique game identifier
    :param client_socket1: socket object for client 1
    :param client_socket2: socket object for client 2 ("None" if local game)
    """

    client_socket1.sendall(pickle.dumps([0, 1, game_id, 1]))

    if client_socket2 is None:
        remote_player = False
    else:
        remote_player = True
        client_socket2.sendall(pickle.dumps([0, 2, game_id, 2]))

    rows = 8
    cols = 8
    player1 = Player.Player(1)
    player2 = Player.Player(2)
    board = Board.Board(rows, cols, player1, player2)
    move = Move.Move(board, player1, player2)
    current_player = player1
    board.reset_board()

    print("Starting game #" + str(game_id))

    while 1:
        if current_player == player1:
            print("Game #" + str(game_id) + ": Current player is p1. Sending request for p1 move to client_socket1.")
            resp1 = [P1_MOVE_REQ, "", board.get_grid()]
            time.sleep(0.5)
            client_socket1.sendall(pickle.dumps(resp1))
            print("Game #" + str(game_id) + ": Waiting for response from client_socket1.")
            # timer = threading.Timer(5.0, thread_timeout, [threading.current_thread()])
            # timer.start()
            msg_in1 = client_socket1.recv(1024)
            msg1 = pickle.loads(msg_in1)
            print("Game #" + str(game_id) + ": Received response from client_socket1.")
            if msg1[0] == QUIT_MESS:
                print("Game #" + str(game_id) + ": Player 1 quit.")
                quit_str = "Player 1 quit. Player 2 wins!"
                resp = [QUIT_MESS, quit_str, board.get_grid()]
                time.sleep(0.1)
                client_socket1.sendall(pickle.dumps(resp))
                if remote_player:
                    time.sleep(0.1)
                    client_socket2.sendall(pickle.dumps(resp))
                break
            elif msg1[0] == P1_MOVE_REQ:
                if len(msg1[1]) == 4:
                    try_move = move.make_move(current_player, msg1[1][0], msg1[1][1], msg1[1][2], msg1[1][3])
                else:
                    try_move = [0, "Incorrect move format."]
                if try_move[0] == 0:
                    err_str = "Player 1 error: " + try_move[1] + "\nPlayer 1 is disqualified. Player 2 wins!"
                    resp = [ERR_MESS, err_str, board.get_grid()]
                    time.sleep(0.5)
                    client_socket1.sendall(pickle.dumps(resp))
                    if remote_player:
                        time.sleep(0.1)
                        client_socket2.sendall(pickle.dumps(resp))
                    print("Game #" + str(game_id) + ": Illegal move from player 1. Disconnecting.")
                    break
                else:
                    if move.check_for_win(current_player):
                        win_str = "Player " + str(current_player.get_number) + " wins!"
                        resp = [WIN_MESS, win_str, board.get_grid()]
                        time.sleep(0.5)
                        client_socket1.sendall(pickle.dumps(resp))
                        if remote_player:
                            time.sleep(0.1)
                            client_socket2.sendall(pickle.dumps(resp))
                        print("Game #" + str(game_id) + ": " + win_str)
                        break
                    else:
                        resp = [P1_MOVE_WAS, msg1[1], board.get_grid()]
                        time.sleep(0.5)
                        client_socket1.sendall(pickle.dumps(resp))
                        if remote_player:
                            client_socket2.sendall(pickle.dumps(resp))
            else:
                print("Game #" + str(game_id) + ": Got unexpected message from player 1. Disconnecting.")
                break

            current_player = player2

        else:
            print("Game #" + str(game_id) + ": Current player is p2.")
            resp2 = [P2_MOVE_REQ, "", board.get_grid()]

            if remote_player:
                print("Game #" + str(game_id) + ": Sending request for p2 move to client_socket2.")
                time.sleep(0.5)
                client_socket2.sendall(pickle.dumps(resp2))
                msg_in2 = client_socket2.recv(1024)
                print("Game #" + str(game_id) + ": Received response from client_socket2.")
            else:
                print("Game #" + str(game_id) + ": Sending request for p2 move to client_socket1.")
                time.sleep(0.5)
                client_socket1.sendall(pickle.dumps(resp2))
                msg_in2 = client_socket1.recv(1024)
                print("Game #" + str(game_id) + ": Received response from client_socket1.")

            msg2 = pickle.loads(msg_in2)

            if msg2[0] == QUIT_MESS:
                print("Game #" + str(game_id) + ": Player 2 quit.")
                quit_str = "Player 2 quit. Player 1 wins!"
                resp = [QUIT_MESS, quit_str, board.get_grid()]
                time.sleep(0.1)
                client_socket1.sendall(pickle.dumps(resp))
                if remote_player:
                    time.sleep(0.1)
                    client_socket2.sendall(pickle.dumps(resp))
                break
            elif msg2[0] == P2_MOVE_REQ:
                if len(msg2[1]) == 4:
                    try_move = move.make_move(current_player, msg2[1][0], msg2[1][1], msg2[1][2], msg2[1][3])
                else:
                    try_move = [0, "Incorrect move format."]
                if try_move[0] == 0:
                    err_str = "Player 2 error: " + try_move[1] + "\nPlayer 2 is disqualified. Player 1 wins!"
                    resp = [ERR_MESS, err_str, board.get_grid()]
                    time.sleep(0.5)
                    client_socket1.sendall(pickle.dumps(resp))
                    if remote_player:
                        time.sleep(0.1)
                        client_socket2.sendall(pickle.dumps(resp))
                    print("Game #" + str(game_id) + ": Illegal move from player 2. Disconnecting.")
                    break
                else:
                    if move.check_for_win(current_player):
                        win_str = "Player 2 wins!"
                        resp = [WIN_MESS, win_str, board.get_grid()]
                        time.sleep(0.5)
                        client_socket1.sendall(pickle.dumps(resp))
                        if remote_player:
                            time.sleep(0.1)
                            client_socket2.sendall(pickle.dumps(resp))
                        print("Game #" + str(game_id) + ": " + win_str)
                        break
                    else:
                        resp = [P2_MOVE_WAS, msg2[1], board.get_grid()]
                        time.sleep(0.5)
                        client_socket1.sendall(pickle.dumps(resp))
                        if remote_player:
                            time.sleep(0.1)
                            client_socket2.sendall(pickle.dumps(resp))
            else:
                print("Game #" + str(game_id) + ": Got unexpected message from player 2. Disconnecting.")
                break

            current_player = player1


def thread_timeout(a_thread):
    print("Killing thread.")
    a_thread.run().exit()

if __name__ == '__main__':
    main()
