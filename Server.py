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

INIT = 0
P1_MOVE_REQ = 1
P2_MOVE_REQ = 2
P1_MOVE_WAS = 3
P2_MOVE_WAS = 4
WIN_MESS = 5
ERR_MESS = 6
QUIT_MESS = 7


def main():
    rows = 8
    cols = 8
    player1 = Player.Player(1)
    player2 = Player.Player(2)
    board = Board.Board(rows, cols, player1, player2)
    move = Move.Move(board, player1, player2)
    current_player = player1
    remote_player = False
    board.reset_board()

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = socket.gethostname()
    port = 7667
    server_socket.bind((host, port))
    server_socket.listen(2)

    print("**Waiting for remote player**")
    client_socket1, addr1 = server_socket.accept()
    print("**Got connection from %s**" % str(addr1))

    msg_in1 = client_socket1.recv(1024)
    msg = pickle.loads(msg_in1)

    if msg[0] == INIT:
        if msg[1]:      # Client wants remote opponent
            print("**Waiting for remote player**")
            client_socket2, addr2 = server_socket.accept()
            print("**Got connection from %s**" % str(addr2))

            # TODO handle when second player doesn't want remote opponent

            remote_player = True

            msg_in2 = client_socket2.recv(1024)
            msg2 = pickle.loads(msg_in2)        # check if client wants remote opponent

            resp1 = [0, 1, board.get_grid()]
            client_socket1.sendall(pickle.dumps(resp1))

            resp2 = [0, 2, board.get_grid()]
            client_socket2.sendall(pickle.dumps(resp2))
        else:           # Client is playing local or computer opponent
            # print("**No remote player. Sending message to client_socket1.**")
            resp1 = [0, 1, board.get_grid()]
            client_socket1.sendall(pickle.dumps(resp1))
    else:
        err_msg = "Server needs to know if player 2 is remote. Disconnecting."
        print(err_msg)
        client_socket1.sendall(pickle.dumps([ERR_MESS, err_msg, board.get_grid()]))
        exit(0)

    while 1:
        if current_player == player1:
            # print("**Current player is p1. Sending request for p1 move to client_socket1.**")
            resp1 = [P1_MOVE_REQ, "", board.get_grid()]
            time.sleep(1)
            client_socket1.sendall(pickle.dumps(resp1))
            # print("**Waiting for response from client_socket1.**")
            msg_in1 = client_socket1.recv(1024)
            msg1 = pickle.loads(msg_in1)
            # print("**Received response from client_socket1.**")
            if msg1[0] == P1_MOVE_REQ:
                if len(msg1[1]) == 4:
                    try_move = move.make_move(current_player, msg1[1][0], msg1[1][1], msg1[1][2], msg1[1][3])
                else:
                    try_move = [0, "Incorrect move format."]
                if try_move[0] == 0:
                    err_str = "Player 1 error: " + try_move[1] + "\nPlayer 1 is disqualified. Player 2 wins!"
                    resp = [ERR_MESS, err_str, board.get_grid()]
                    time.sleep(1)
                    client_socket1.sendall(pickle.dumps(resp))
                    if remote_player:
                        time.sleep(1)
                        client_socket2.sendall(pickle.dumps(resp))
                    print("Illegal move from player 1. Disconnecting.")
                    break
                else:
                    if move.check_for_win(current_player):
                        win_str = "Player " + str(current_player.get_number) + " wins!"
                        resp = [WIN_MESS, win_str, board.get_grid()]
                        time.sleep(1)
                        client_socket1.sendall(pickle.dumps(resp))
                        if remote_player:
                            time.sleep(1)
                            client_socket2.sendall(pickle.dumps(resp))
                        print(win_str)
                        break
                    else:
                        resp = [P1_MOVE_WAS, msg1[1], board.get_grid()]
                        time.sleep(1)
                        client_socket1.sendall(pickle.dumps(resp))
                        if remote_player:
                            client_socket2.sendall(pickle.dumps(resp))
            else:
                print("Got unexpected message from player 1. Disconnecting.")
                break

            current_player = player2

        else:
            # print("**Current player is p2.**")
            resp2 = [P2_MOVE_REQ, "", board.get_grid()]

            if remote_player:
                # print("**Sending request for p2 move to client_socket2.**")
                time.sleep(1)
                client_socket2.sendall(pickle.dumps(resp2))
                msg_in2 = client_socket2.recv(1024)
                # print("**Received response from client_socket2.**")
            else:
                # print("**Sending request for p2 move to client_socket1.**")
                time.sleep(1)
                client_socket1.sendall(pickle.dumps(resp2))
                msg_in2 = client_socket1.recv(1024)
                # print("**Received response from client_socket1.**")

            msg2 = pickle.loads(msg_in2)

            if msg2[0] == P2_MOVE_REQ:
                if len(msg2[1]) == 4:
                    try_move = move.make_move(current_player, msg2[1][0], msg2[1][1], msg2[1][2], msg2[1][3])
                else:
                    try_move = [0, "Incorrect move format."]
                if try_move[0] == 0:
                    err_str = "Player 2 error: " + try_move[1] + "\nPlayer 2 is disqualified. Player 1 wins!"
                    resp = [ERR_MESS, err_str, board.get_grid()]
                    time.sleep(1)
                    client_socket1.sendall(pickle.dumps(resp))
                    if remote_player:
                        time.sleep(1)
                        client_socket2.sendall(pickle.dumps(resp))
                    print("Illegal move from player 2. Disconnecting.")
                    break
                else:
                    if move.check_for_win(current_player):
                        win_str = "Player 2 wins!"
                        resp = [WIN_MESS, win_str, board.get_grid()]
                        time.sleep(1)
                        client_socket1.sendall(pickle.dumps(resp))
                        if remote_player:
                            time.sleep(1)
                            client_socket2.sendall(pickle.dumps(resp))
                        print(win_str)
                        break
                    else:
                        resp = [P2_MOVE_WAS, msg2[1], board.get_grid()]
                        time.sleep(1)
                        client_socket1.sendall(pickle.dumps(resp))
                        if remote_player:
                            time.sleep(1)
                            client_socket2.sendall(pickle.dumps(resp))
            else:
                print("Got unexpected message from player 2. Disconnecting.")
                break

            current_player = player1

    return 0

if __name__ == '__main__':
    main()
