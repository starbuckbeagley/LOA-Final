"""
Lines of Action human client
Extends SuperClient

Starbuck Beagley
"""
from SuperClient import SuperClient


class ClientH(SuperClient):

    def __init__(self, num):
        """
        Constructor
        :param num: player number
        """
        SuperClient.__init__(self, num)

    def next_move(self):
        """
        Gets move from player
        :return: player move as list
        """
        return list("".join(input().split()))
