"""
Abstract server class

Starbuck Beagley
"""
import abc


class AbstractServer(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def initialize_client(self, client_id, game_id):
        """
        Generates initial message to send to client
        :param client_id: which client will receive message
        :param game_id: unique game id
        :return: initial message for client
        """
        pass

    @abc.abstractmethod
    def request_move(self, client_id):
        """
        Generates move-request message to send to client
        :param client_id: which client will receive message
        :return: move-request message for client
        """
        pass

    @abc.abstractmethod
    def evaluate_move(self, client_id, msg):
        """
        Evaluates move for server
        :param client_id: which client made the move
        :param msg: the most recent move
        :return: evaluation message for server
        """
        pass

    @abc.abstractmethod
    def send_move(self, client_id, msg):
        """
        Generates message informing client of most recent move
        :param client_id: who moved
        :param msg: the most recent move
        :return: recent-move message for client
        """
        pass

    @abc.abstractmethod
    def send_error(self, client_id, err_type):
        """
        Generates message to send to client when an error is caused
        by an invalid move or an unexpected disconnection
        :param client_id: which player made the invalid move
        :param err_type: string containing error
        :return: error message for client
        """
        pass

    @abc.abstractmethod
    def send_quit(self, client_id):
        """
        Generates message to send to client when a player quits
        :param client_id: which player quit
        :return: quit message for client
        """
        pass

    @abc.abstractmethod
    def send_win(self, client_id):
        """
        Generates message to send to client when a player wins
        :param client_id: which player won
        :return: win message for client
        """
        pass
