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
CONTINUE_GAME = 8
END_GAME = 9

P1 = 1
P2 = 2
ROWS = 8
COLS = 8

BUFF_SIZE = 1024
CONT_IT = 0
NEXT_IT = 1
ORD_A = 65
PORT_NUM = 7667
TIME_DELAY = 0.1


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--bad_computer_opponent", help="bad computer opponent is desired", action="store_true")
    parser.add_argument("-o", "--okay_computer_opponent", help="okay computer opponent is desired", action="store_true")
    parser.add_argument("-r", "--remote_opponent", help="remote opponent is desired", action="store_true")
    parser.add_argument("-f", "--forgiving", help="warnings for invalid moves", action="store_true")
    parser.add_argument("-a", "--ai_battle", help="computer plays against computer", action="store_true")
    args = parser.parse_args()

    display = Display.Display(ROWS, COLS)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = socket.gethostname()
    port = PORT_NUM
    try:
        sock.connect((host, port))
    except ConnectionRefusedError as err:
        print("Error: " + err.strerror)
        return 0

    check_input_args = check_args(args, sock)

    if check_input_args[0] is ERR_MESS:
        print("Error: " + check_input_args[1])
        sock.close()
        return 0
    else:
        opponent_is_computer = check_input_args[1]
        opponent_is_remote = check_input_args[2]

    msg = from_server(sock)

    set_user_clients = set_clients(msg, args)

    if set_user_clients[0] is ERR_MESS:
        print("Error: " + set_user_clients[1])
        sock.close()
        return 0
    else:
        client1 = set_user_clients[1]
        client2 = set_user_clients[2]
        game_id = set_user_clients[3]
        ai_battle = set_user_clients[4]

    single_local_player_number = print_welcome(client1, opponent_is_remote, display, game_id, msg, ai_battle)

    while 1:
        msg = from_server(sock)
        if msg[0] == P1_MOVE_REQ or msg[0] == P2_MOVE_REQ:
            if player_move_req(sock, client1, client2, opponent_is_computer, ai_battle, msg) == NEXT_IT:
                continue
        elif msg[0] == P1_MOVE_WAS or msg[0] == P2_MOVE_WAS:
            player_move_was(client1, client2, opponent_is_computer, opponent_is_remote,
                            single_local_player_number, display, msg, ai_battle)
        elif msg[0] == WIN_MESS or msg[0] == ERR_MESS or msg[0] == QUIT_MESS:
            if msg[0] == WIN_MESS:
                display.show_board(msg[2])
                print("")
                if ai_battle:
                    print("Computer ", end="")
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
    try:
        sock.sendall(pickle.dumps(resp))
        return [CONTINUE_GAME, ""]
    except OSError as err:
        try:
            sock.close()
        except OSError:
            pass
        return [ERR_MESS, "Error: " + err.strerror]


def from_server(sock):
    """
    Gets message from server
    :param sock: server socket
    :return: message from server
    """
    try:
        return pickle.loads(sock.recv(BUFF_SIZE))
    except OSError as err:
        try:
            sock.close()
        except OSError:
            pass
        return [ERR_MESS, "Error: " + err.strerror]


def player_move_req(sock, client1, client2, opponent_is_computer, ai_battle, msg):
    """
    Handles requests for player moves from server
    :param sock: server socket
    :param client1: client1 socket
    :param client2: client2 socket
    :param opponent_is_computer: true if opponent is computer, false otherwise
    :param ai_battle: true if both players are computers, false otherwise
    :param msg: message from server
    :return: NEXT_IT if continue needed in main while loop, CONT_IT otherwise
    """
    if msg[0] == P1_MOVE_REQ:
        print_move_req(P1, "x", ai_battle)
        l = client1.next_move()
        if not ai_battle:
            if check_quit(l, sock) == NEXT_IT:
                return NEXT_IT
        to_server(sock, [P1_MOVE_REQ, l], TIME_DELAY)
    elif msg[0] == P2_MOVE_REQ:
        if not opponent_is_computer:
            print_move_req(P2, "o", ai_battle)
        if client1.get_num() == 2:
            l = client1.next_move()
            if not ai_battle:
                if check_quit(l, sock) == NEXT_IT:
                    return NEXT_IT
        else:
            if opponent_is_computer:
                to_server(sock, [P2_MOVE_REQ, client2.next_move()], TIME_DELAY)
                return NEXT_IT
            else:
                l = client2.next_move()
                if not ai_battle:
                    if check_quit(l, sock) == NEXT_IT:
                        return NEXT_IT
        to_server(sock, [P2_MOVE_REQ, l], TIME_DELAY)
    return CONT_IT


def player_move_was(client1, client2, opponent_is_computer, opponent_is_remote,
                    single_local_player_number, display, msg, ai_battle):
    """
    Handles server responding with most recent move
    :param client1: client socket 1
    :param client2: client socket 2
    :param opponent_is_computer: true if opponent is computer, false otherwise
    :param opponent_is_remote: true if opponent is remote, false otherwise
    :param single_local_player_number: needed for player 2 using client_socket1
    :param display: display object for showing game board
    :param msg: most recent move
    :param ai_battle: true if both players are computers, false otherwise
    """
    if msg[0] == P1_MOVE_WAS:
        client1.move_was(P1, msg[1])
        if not opponent_is_remote:
            client2.move_was(P1, msg[1])
        print_move(P1, untranslate(msg[1]), display, client1, opponent_is_computer, ai_battle)
        if opponent_is_remote and single_local_player_number == 1:
            print("Waiting for Player 2's move...")
            print("")
    else:
        client1.move_was(P2, msg[1])
        if not opponent_is_remote:
            client2.move_was(P2, msg[1])
        print_move(P2, untranslate(msg[1]), display, client1, opponent_is_computer, ai_battle)
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


def check_args(args, sock):
    """
    Checks for incompatible arguments, sends initial message to server
    :param args: user-input arguments
    :param sock: server socket
    :return: list containing opponent variables or error message
    """
    opponent_is_computer = False
    opponent_is_remote = False
    if args.bad_computer_opponent and args.okay_computer_opponent:
        sock.close()
        return [ERR_MESS, "Can only have one type of computer opponent!"]
    elif args.bad_computer_opponent or args.okay_computer_opponent:
        if not args.ai_battle:
            opponent_is_computer = True
        if args.remote_opponent:
            sock.close()
            return [ERR_MESS, "Cannot have both computer and remote opponents!"]

    if args.remote_opponent:
        resp = [INIT, True]
        if not args.ai_battle:
            opponent_is_remote = True
        print("Waiting for opponent...")
        print("")
    else:
        resp = [INIT, False]

    check = to_server(sock, resp, 0)

    if check[0] is ERR_MESS:
        return [ERR_MESS, check[1]]

    return [CONTINUE_GAME, opponent_is_computer, opponent_is_remote]


def set_clients(msg, args):
    """
    Creates, initializes and returns player clients
    :param msg: message from server
    :param args: user-input arguments
    :return: 
    """
    ai_battle = False
    if msg[0] != 0:
        return [ERR_MESS, "Received unexpected message from server. Quitting."]
    elif args.ai_battle:
        client1 = ClientOkayC.ClientOkayC(1)
        ai_battle = True
    elif args.forgiving:
        client1 = ClientF.ClientF(msg[1])
    else:
        client1 = ClientH.ClientH(msg[1])

    game_id = msg[2]
    client1.initialize()

    if args.ai_battle:
        client2 = ClientOkayC.ClientOkayC(2)
        client2.initialize()
    elif args.okay_computer_opponent:
        client2 = ClientOkayC.ClientOkayC(2)
        client2.initialize()
    elif args.bad_computer_opponent:
        client2 = ClientBadC.ClientBadC(2)
        client2.initialize()
    elif not args.remote_opponent:
        client2 = ClientH.ClientH(2)
        client2.initialize()
    else:
        client2 = None

    return [CONTINUE_GAME, client1, client2, game_id, ai_battle]


def print_welcome(client1, opponent_is_remote, display, game_id, msg, ai_battle):
    """
    Prints welcome message to client 1.
    :param client1: socket for client 1
    :param opponent_is_remote: true if opponent is remote, false otherwise
    :param display: display object for showing game board
    :param game_id: unique game id
    :param msg: message from server (for player number)
    :param ai_battle: true if both players are computers, false otherwise
    :return: player number (needed for player 2 using client_socket1)
    """
    print("Welcome to Game #" + str(game_id))
    if ai_battle:
        print("Let the AI battle commence!")
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


def print_move(player, move, display, client, opponent_is_computer, ai_battle):
    """
    Displays game board and request for move.
    :param player: player who made most recent move
    :param move: most recent move
    :param display: display object for showing game board
    :param client: which client's board should be displayed
    :param opponent_is_computer: true if opponent is computer, false otherwise
    :param ai_battle: true if both players are computers, false otherwise
    """
    if ai_battle:
        print("Computer Player " + str(player) + "'s move: " + move)
    elif opponent_is_computer:
        print("Computer's move: " + move)
    else:
        print("Player " + str(player) + "'s move: " + move)
    print("")
    display.show_board(client.board.get_grid())
    print("")


def print_move_req(player, piece, ai_battle):
    """
    Displays request for player move.
    :param player: player yet to move
    :param piece: piece of player
    :param ai_battle: true if both players are computers, false otherwise
    """
    if ai_battle:
        print("Computer Player " + str(player) + "'s turn (" + piece + ").")
    else:
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
