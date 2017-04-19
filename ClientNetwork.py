"""
Lines of Action client network
Starbuck Beagley

Socket messages sent to the server are lists with two elements.
The first element is a code. The second element is either a list
of coordinates for a move or an empty string.

Socket messages received from the server are lists with three
elements. The first element is a code. The second element is
a list of coordinates for a move, a message, or an empty string.
The third element is the board state.

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
import argparse
import pickle
import time
import ClientH
import ClientC
import Display

INIT = 0
P1_MOVE_REQ = 1
P2_MOVE_REQ = 2
P1_MOVE_WAS = 3
P2_MOVE_WAS = 4
WIN_MESS = 5
ERR_MESS = 6
QUIT_MESS = 7


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--computer_opponent", help="computer opponent is desired", action="store_true")
    parser.add_argument("-r", "--remote_opponent", help="remote opponent is desired", action="store_true")
    args = parser.parse_args()

    opponent_is_computer = False

    if args.computer_opponent:
        opponent_is_computer = True

    rows = 8
    cols = 8
    display = Display.Display(rows, cols)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = socket.gethostname()
    port = 7667
    sock.connect((host, port))

    opponent_is_remote = False

    if args.remote_opponent:
        resp = [INIT, True]
        opponent_is_remote = True
    else:
        resp = [INIT, False]

    sock.sendall(pickle.dumps(resp))

    msg_in = sock.recv(1024)
    msg = pickle.loads(msg_in)

    if msg[0] != 0:
        print("Received unexpected message from server. Quitting.")
        exit(0)
    else:
        client1 = ClientH.ClientH(msg[1])
        client1.initialize()

    if opponent_is_computer:
        client2 = ClientC.ClientC(2)
        client2.initialize()
    elif not opponent_is_remote:
        client2 = ClientH.ClientH(2)
        client2.initialize()

    display.show_board(client1.board.get_grid())
    print("")

    while 1:
        # print("**Waiting for server message**")
        msg_in = sock.recv(1024)
        msg = pickle.loads(msg_in)
        # print("**Received server message**")
        if msg[0] == P1_MOVE_REQ:
            print("Player 1's turn.")
            print("Enter piece and destination coordinates, row before column, separated by a space: ")
            l = client1.next_move()
            a = []
            translate(l, a, cols)
            resp = [P1_MOVE_REQ, a]
            time.sleep(1)
            sock.sendall(pickle.dumps(resp))
        elif msg[0] == P2_MOVE_REQ:
            # print("**Received request for p2 move**")
            if not opponent_is_computer:
                print("Player 2's turn.")
                print("Enter piece and destination coordinates, row before column, separated by a space: ")
            a = []
            if client1.get_num() == 2:
                l = client1.next_move()
            else:
                if opponent_is_computer:
                    resp = [P2_MOVE_REQ, client2.next_move()]
                    time.sleep(1)
                    sock.sendall(pickle.dumps(resp))
                    continue
                else:
                    l = client2.next_move()
            translate(l, a, cols)
            resp = [P2_MOVE_REQ, a]
            time.sleep(1)
            sock.sendall(pickle.dumps(resp))
        elif msg[0] == P1_MOVE_WAS:
            client1.move_was(1, msg[1])
            if not opponent_is_remote:
                client2.move_was(1, msg[1])
            p1_move = untranslate(msg[1])
            print("Player 1's move: " + p1_move)
            print("")
            display.show_board(client1.board.get_grid())
            print("")
        elif msg[0] == P2_MOVE_WAS:
            client1.move_was(2, msg[1])
            if not opponent_is_remote:
                client2.move_was(2, msg[1])
            if opponent_is_computer:
                p2_str = "Computer"
            else:
                p2_str = "Player 2"
            p2_move = untranslate(msg[1])
            print(p2_str + "'s move: " + p2_move)
            print("")
            display.show_board(client1.board.get_grid())
            print("")
        elif msg[0] == WIN_MESS or msg[0] == ERR_MESS or msg[0] == QUIT_MESS:
            # TODO show final move and updated board if win
            print(msg[1])
            break
        else:
            print("Received unexpected message from server. Quitting.")
            break
    return 0


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
    for j in range(97, 97 + c):
        if l[1].lower() == chr(j):
            a.append(j - 97)
            break
        elif j == (97 + c):
            return False
    try:
        i = int(l[2])
        a.append(i)
    except ValueError:
        return False
    for j in range(97, 97 + c):
        if l[3].lower() == chr(j):
            a.append(j - 97)
            break
        elif j == (97 + c):
            return False
    return True


def untranslate(a):
    return str(a[0]) + str(chr(65 + a[1])) + " to " + str(a[2]) + str(chr(65 + a[3]))


if __name__ == '__main__':
    main()
