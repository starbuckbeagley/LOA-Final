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
import ClientBadC
import ClientOkayC
import ClientF
import Display

INIT = 0
P1_MOVE_REQ = 1
P2_MOVE_REQ = 2
P1_MOVE_WAS = 3
P2_MOVE_WAS = 4
WIN_MESS = 5
ERR_MESS = 6
QUIT_MESS = 7

P1 = 1
P2 = 2
ROWS = 8
COLS = 8

BUFF_SIZE = 1024
CONT_IT = 0
NEXT_IT = 1
ORD_A = 65
PORT_NUM = 7667
TIME_DELAY = 0.5


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--bad_computer_opponent", help="bad computer opponent is desired", action="store_true")
    parser.add_argument("-o", "--okay_computer_opponent", help="okay computer opponent is desired", action="store_true")
    parser.add_argument("-r", "--remote_opponent", help="remote opponent is desired", action="store_true")
    parser.add_argument("-f", "--forgiving", help="warnings for invalid moves", action="store_true")
    args = parser.parse_args()

    display = Display.Display(ROWS, COLS)
    opponent_is_computer = False
    opponent_is_remote = False

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = socket.gethostname()
    port = PORT_NUM
    sock.connect((host, port))

    if args.bad_computer_opponent and args.okay_computer_opponent:
        print("Can only have one type of computer opponent!")
        sock.close()
        exit(0)
    elif args.bad_computer_opponent or args.okay_computer_opponent:
        opponent_is_computer = True
        if args.remote_opponent:
            print("Cannot have both computer and remote opponents!")
            sock.close()
            exit(0)

    if args.remote_opponent:
        resp = [INIT, True]
        opponent_is_remote = True
        print("Waiting for opponent...")
        print("")
    else:
        resp = [INIT, False]

    to_server(sock, resp, 0)

    msg_in = sock.recv(BUFF_SIZE)
    msg = pickle.loads(msg_in)
    game_id = msg[2]

    if msg[0] != 0:
        print("Received unexpected message from server. Quitting.")
        exit(0)
    elif args.forgiving:
        client1 = ClientF.ClientF(msg[1])
    else:
        client1 = ClientH.ClientH(msg[1])

    client1.initialize()

    if opponent_is_computer:
        if args.okay_computer_opponent:
            client2 = ClientOkayC.ClientOkayC(2)
        else:
            client2 = ClientBadC.ClientBadC(2)
        client2.initialize()
    elif not opponent_is_remote:
        client2 = ClientH.ClientH(2)
        client2.initialize()
    else:
        client2 = None

    single_local_player_number = print_welcome(client1, opponent_is_remote, display, game_id, msg)

    while 1:
        msg_in = sock.recv(BUFF_SIZE)
        msg = pickle.loads(msg_in)
        if msg[0] == P1_MOVE_REQ or msg[0] == P2_MOVE_REQ:
            if player_move_req(sock, client1, client2, opponent_is_computer, msg) == NEXT_IT:
                continue
        elif msg[0] == P1_MOVE_WAS or msg[0] == P2_MOVE_WAS:
            player_move_was(client1, client2, opponent_is_computer, opponent_is_remote,
                            single_local_player_number, display, msg)
        elif msg[0] == WIN_MESS or msg[0] == ERR_MESS or msg[0] == QUIT_MESS:
            if msg[0] == WIN_MESS:
                display.show_board(msg[2])
                print("")
            print(msg[1])
            break
        else:
            print("Received unexpected message from server. Quitting.")
            break

    sock.close()
    return 0


def to_server(sock, resp, pause):
    """
    Sends message to server
    :param sock: server socket
    :param resp: message to send
    :param pause: how long to pause (for smoothness of play)
    """
    time.sleep(pause)
    sock.sendall(pickle.dumps(resp))


def player_move_req(sock, client1, client2, opponent_is_computer, msg):
    """
    Handles requests for player moves from server
    :param sock: server socket
    :param client1: client1 socket
    :param client2: client2 socket
    :param opponent_is_computer: true if opponent is computer, false otherwise
    :param msg: message from server
    :return: NEXT_IT if continue needed in main while loop, CONT_IT otherwise
    """
    if msg[0] == P1_MOVE_REQ:
        print_move_req(P1, "x")
        l = client1.next_move()
        if check_quit(l, sock) == NEXT_IT:
            return NEXT_IT
        to_server(sock, [P1_MOVE_REQ, l], TIME_DELAY)
    elif msg[0] == P2_MOVE_REQ:
        if not opponent_is_computer:
            print_move_req(P2, "o")
        if client1.get_num() == 2:
            l = client1.next_move()
            if check_quit(l, sock) == NEXT_IT:
                return NEXT_IT
        else:
            if opponent_is_computer:
                to_server(sock, [P2_MOVE_REQ, client2.next_move()], TIME_DELAY)
                return NEXT_IT
            else:
                l = client2.next_move()
                if check_quit(l, sock) == NEXT_IT:
                    return NEXT_IT
        to_server(sock, [P2_MOVE_REQ, l], TIME_DELAY)
    return CONT_IT


def player_move_was(client1, client2, opponent_is_computer, opponent_is_remote,
                    single_local_player_number, display, msg):
    """
    Handles server responding with most recent move
    :param client1: client socket 1
    :param client2: client socket 2
    :param opponent_is_computer: true if opponent is computer, false otherwise
    :param opponent_is_remote: true if opponent is remote, false otherwise
    :param single_local_player_number: needed for player 2 using client_socket1
    :param display: display object for showing game board
    :param msg: most recent move
    """
    if msg[0] == P1_MOVE_WAS:
        client1.move_was(P1, msg[1])
        if not opponent_is_remote:
            client2.move_was(P1, msg[1])
        print_move(P1, untranslate(msg[1]), display, client1)
        if opponent_is_remote and single_local_player_number == 1:
            print("Waiting for Player 2's move...")
            print("")
    else:
        client1.move_was(P2, msg[1])
        if not opponent_is_remote:
            client2.move_was(P2, msg[1])
        if opponent_is_computer:
            p2_str = "Computer"
        else:
            p2_str = "Player 2"
        print_move(p2_str, untranslate(msg[1]), display, client1)
        if opponent_is_remote and single_local_player_number == 2:
            print("Waiting for Player 1's move...")
            print("")


def check_quit(l, sock):
    """
    Checks if player quit and sends message to server.
    :param l: player move
    :param sock: server socket
    :return: NEXT_IT if continue needed in main while loop, CONT_IT otherwise
    """
    if l[0].lower() == "q":
        to_server(sock, [QUIT_MESS], TIME_DELAY)
        return NEXT_IT
    return CONT_IT


def print_welcome(client1, opponent_is_remote, display, game_id, msg):
    """
    Prints welcome message to client 1.
    :param client1: socket for client 1
    :param opponent_is_remote: true if opponent is remote, false otherwise
    :param display: display object for showing game board
    :param game_id: unique game id
    :param msg: message from server (for player number)
    :return: player number (needed for player 2 using client_socket1)
    """
    print("Welcome to Game #" + str(game_id))
    if opponent_is_remote:
        slpn = msg[3]
        print("You are Player " + str(msg[3]))
    else:
        slpn = 0
    print("")
    display.show_board(client1.board.get_grid())
    print("")
    if opponent_is_remote and msg[1] == 2:
        print("Waiting for Player 1's move...")
        print("")
    return slpn


def print_move(player, move, display, client):
    """
    Displays game board and request for move.
    :param player: player who made most recent move
    :param move: most recent move
    :param display: display object for showing game board
    :param client: which client's board should be displayed
    """
    print("Player " + str(player) + "'s move: " + move)
    print("")
    display.show_board(client.board.get_grid())
    print("")


def print_move_req(player, piece):
    """
    Displays request for player move.
    :param player: player yet to move
    :param piece: piece of player
    """
    print("Player " + str(player) + "'s turn (" + piece + ").")
    print("Enter piece and destination coordinates, row before column, separated by a space: ")


def untranslate(a):
    """
    Returns row numbers to letters for readability
    :param a: list of number-only coordinates
    :return: coordinate string where rows are letters
    """
    return str(a[0]) + str(chr(ORD_A + a[1])) + " to " + str(a[2]) + str(chr(ORD_A + a[3]))


if __name__ == '__main__':
    main()
