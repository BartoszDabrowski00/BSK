import logging
import os

from socket_server import Server

PORT = int(os.getenv("SERVER_PORT", 12345))
SERVER_ADDRESS = os.getenv("SERVER_ADDRESS", 'localhost')


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    Server(PORT, SERVER_ADDRESS)
