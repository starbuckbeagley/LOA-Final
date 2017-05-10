"""
Generic game server

This server is designed to be used for games with two players
using threading and sockets. Specific server implementation
is controlled by the object represented by game_server, which
must extend abstract class AbstractServer.

Starbuck Beagley
"""

import socket
import pickle
import time
import threading
import LOAServer

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

BUFF_SIZE = 1024
SERVER_PORT = 7667
MAX_CLIENTS = 100
FIRST_GAME_ID = 1
TIME_DELAY = 0.5
MAX_MOVE_TIME = 30


def main():

    needs_opponent = []
    game_id = FIRST_GAME_ID
    threads = []

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = socket.gethostname()
    port = SERVER_PORT
    server_socket.bind((host, port))
    server_socket.listen(MAX_CLIENTS)

    while 1:
        print("Waiting for player")
        client_socket1, addr1 = server_socket.accept()
        print("Got connection from %s" % str(addr1))

        msg_in1 = client_socket1.recv(BUFF_SIZE)
        msg = pickle.loads(msg_in1)

        if msg[0] == INIT:
            if msg[1]:
                if len(needs_opponent) != 0:
                    opp = needs_opponent.pop(0)
                    print("Game #" + str(opp[0]) + ": Got remote opponent. Starting thread.")
                    threads.append(ClientThread(opp[0], opp[1], client_socket1))
                    threads[len(threads) - 1].start()
                else:
                    print("Game #" + str(game_id) + ": Got player who needs remote opponent. Adding to queue.")
                    needs_opponent.append((game_id, client_socket1))
                    game_id += 1
            else:
                print("Game #" + str(game_id) + ": No remote player needed. Starting thread.")
                threads.append(ClientThread(game_id, client_socket1, None))
                threads[len(threads) - 1].start()
                game_id += 1
        else:
            err_msg = "Server needs to know if player 2 is remote. Passing."
            print(err_msg)
            client_socket1.sendall(pickle.dumps([ERR_MESS, err_msg]))
            client_socket1.close()


class ClientThread(threading.Thread):
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
    print("Starting game #" + str(game_id))
    game_server = LOAServer.LOAServer()
    current_player = P1

    if client_socket2 is None:
        remote_player = False
    else:
        remote_player = True
        try:
            client_socket2.sendall(pickle.dumps(game_server.initialize_client(P2, game_id)))
        except OSError as err:
            game_error(game_server, client_socket1, client_socket2,
                       P2, err.strerror, remote_player, game_id)
    try:
        client_socket1.sendall(pickle.dumps(game_server.initialize_client(P1, game_id)))
    except OSError as err:
        game_error(game_server, client_socket1, client_socket2,
                   P1, err.strerror, remote_player, game_id)

    while 1:
        if current_player == P1:
            time.sleep(TIME_DELAY)
            msg1 = get_move(game_server, client_socket1, P1_MOVE_REQ, game_id)
            if msg1[0] == QUIT_MESS:
                client_quit(game_server, client_socket1, client_socket2, P1, game_id)
                break
            elif msg1[0] == P1_MOVE_REQ:
                check_move = player_turn(game_server, client_socket1, client_socket2,
                                         current_player, remote_player, game_id, msg1)
                if check_move == END_GAME:
                    break
                elif msg1[0] == ERR_MESS:
                    game_error(game_server, client_socket1, client_socket2,
                               current_player, msg1[1], remote_player, game_id)
                    break
            elif msg1[0] == ERR_MESS:
                game_error(game_server, client_socket1, client_socket2,
                           current_player, msg1[1], remote_player, game_id)
                break
            else:
                print("Game #" + str(game_id) + ": Got unexpected message from player 1. Disconnecting.")
                close_sockets(client_socket1, client_socket2)
                break
            current_player = P2
        else:
            if remote_player:
                time.sleep(TIME_DELAY)
                msg2 = get_move(game_server, client_socket2, P2_MOVE_REQ, game_id)
            else:
                time.sleep(TIME_DELAY)
                msg2 = get_move(game_server, client_socket1, P2_MOVE_REQ, game_id)

            if msg2[0] == QUIT_MESS:
                client_quit(game_server, client_socket1, client_socket2, P2, game_id)
                break
            elif msg2[0] == P2_MOVE_REQ:
                check_move = player_turn(game_server, client_socket1, client_socket2,
                                         current_player, remote_player, game_id, msg2)
                if check_move == END_GAME:
                    break
                elif msg2[0] == ERR_MESS:
                    game_error(game_server, client_socket1, client_socket2,
                               current_player, msg2[1], remote_player, game_id)
            elif msg2[0] == ERR_MESS:
                game_error(game_server, client_socket1, client_socket2,
                           current_player, msg2[1], remote_player, game_id)
                break
            else:
                print("Game #" + str(game_id) + ": Got unexpected message from player 2. Disconnecting.")
                close_sockets(client_socket1, client_socket2)
                break
            current_player = P1


def get_move(game_server, client_socket, client_id, game_id):
    """
    Sends message to socket requesting move
    :param game_server: game server object
    :param client_socket: client_socket1 or client_socket2
    :param client_id: identifies which client receives request
    :param game_id: unique game id (for server messages)
    :return: client move if successful, error message otherwise
    """
    print("Game #" + str(game_id) + ": Current player is Player " + str(client_id) + ". Sending request for move.")
    time.sleep(TIME_DELAY)
    try:
        client_socket.sendall(pickle.dumps(game_server.request_move(client_id)))
    except OSError as err:
        return [ERR_MESS, err.strerror]
    print("Game #" + str(game_id) + ": Waiting for response from Player " + str(client_id) + ".")
    try:
        start_time = time.time()
        msg_in = client_socket.recv(BUFF_SIZE)
        end_time = time.time()
        if (end_time - start_time) > MAX_MOVE_TIME:
            return [ERR_MESS, "Player " + str(client_id) + " timed out"]
    except OSError as err:
        return [ERR_MESS, err.strerror]
    print("Game #" + str(game_id) + ": Received response from Player " + str(client_id) + ".")
    return pickle.loads(msg_in)


def player_turn(game_server, client_socket1, client_socket2, current_player, remote_player, game_id, msg):
    """
    Evaluates player move and sends appropriate messages to clients
    :param game_server: game server object
    :param client_socket1: socket for client 1
    :param client_socket2: socket for client 2
    :param current_player: player who made most recent turn
    :param remote_player: true if players are on separate hosts, false otherwise
    :param game_id: unique game id (for server messages)
    :param msg: most recent move
    :return: CONTINUE_GAME, END_GAME, OR ERR_MESS
    """
    try_move = game_server.evaluate_move(current_player, msg)
    if try_move[0] == ERR_MESS:
        time.sleep(TIME_DELAY)
        try:
            client_socket1.sendall(pickle.dumps(game_server.send_error(current_player, try_move[1])))
        except OSError as err:
            return [ERR_MESS, err.strerror]
        if remote_player:
            time.sleep(0.1)
            try:
                client_socket2.sendall(pickle.dumps(game_server.send_error(current_player, try_move[1])))
            except OSError as err:
                return [ERR_MESS, err.strerror]
        print("Game #" + str(game_id) + ": Illegal move from player " + str(current_player) + ". Disconnecting.")
        close_sockets(client_socket1, client_socket2)
        return END_GAME
    else:
        if game_server.check_win(current_player):
            time.sleep(TIME_DELAY)
            try:
                client_socket1.sendall(pickle.dumps(game_server.send_win(current_player)))
            except OSError as err:
                return [ERR_MESS, err.strerror]
            if remote_player:
                time.sleep(0.1)
                try:
                    client_socket2.sendall(pickle.dumps(game_server.send_win(current_player)))
                except OSError as err:
                    return [ERR_MESS, err.strerror]
            print("Game #" + str(game_id) + ": " + "Player " + str(current_player) + " wins!")
            close_sockets(client_socket1, client_socket2)
            return END_GAME
        else:
            time.sleep(TIME_DELAY)
            if current_player == P1:
                move_was = P1_MOVE_WAS
            else:
                move_was = P2_MOVE_WAS
            try:
                client_socket1.sendall(pickle.dumps(game_server.send_move(move_was, msg)))
            except OSError as err:
                return [ERR_MESS, err.strerror]
            if remote_player:
                try:
                    client_socket2.sendall(pickle.dumps(game_server.send_move(move_was, msg)))
                except OSError as err:
                    return [ERR_MESS, err.strerror]
        return CONTINUE_GAME


def client_quit(game_server, client_socket1, client_socket2, client_id, game_id):
    """
    Sends message to opponent if client quits
    :param game_server: game server object
    :param client_socket1: socket for client 1
    :param client_socket2: socket for client 2
    :param client_id: player who quit
    :param game_id: unique game id (for server messages)
    """
    print("Game #" + str(game_id) + ": Player " + str(client_id) + " quit.")
    time.sleep(0.1)
    client_socket1.sendall(pickle.dumps(game_server.send_quit(client_id)))
    if client_socket2 is not None:
        client_socket2.sendall(pickle.dumps(game_server.send_quit(client_id)))
    close_sockets(client_socket1, client_socket2)


def player_timed_out():
    pass


def game_error(game_server, client_socket1, client_socket2, client_num, err_str, remote_player, game_id):
    """
    Sends message to client if error occurs, closes sockets
    :param game_server: game server object
    :param client_socket1: socket for client 1
    :param client_socket2: socket for client 2
    :param client_num: client who disconnected
    :param err_str: exception error string
    :param remote_player: true if players are on separate hosts, false otherwise
    :param game_id: unique game id (for server messages)
    """
    print("Game #" + str(game_id) + ": Error - " + err_str + ". Disconnecting.")
    try:
        client_socket1.sendall(pickle.dumps(game_server.send_error(client_num, err_str)))
    except OSError:
        pass
    if client_socket2 is not None:
        try:
            client_socket2.sendall(pickle.dumps(game_server.send_error(client_num, err_str)))
        except OSError:
            pass
    close_sockets(client_socket1, client_socket2)


def close_sockets(client_socket1, client_socket2):
    """
    Closes sockets
    :param client_socket1: socket for client 1
    :param client_socket2: socket for client 2
    """
    try:
        client_socket1.close()
    except OSError:
        pass
    if client_socket2 is not None:
        try:
            client_socket2.close()
        except OSError:
            pass


if __name__ == '__main__':
    main()