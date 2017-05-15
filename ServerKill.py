"""
Remotely kills server

Starbuck Beagley
"""

import socket
import pickle

PORT_NUM = 7667
QUIT_MESS = 7


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = socket.gethostname()
    port = PORT_NUM
    sock.connect((host, port))
    sock.sendall(pickle.dumps([QUIT_MESS, ""]))
    return 0


if __name__ == '__main__':
    main()
