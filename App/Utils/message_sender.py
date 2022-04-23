import pickle
from socket import socket

from App.Utils.message import Message


class MessageSender:
    HEADER_SIZE = 256
    FORMAT = 'utf-8'

    def __init__(self):
        pass

    def get_header_bytes(self, msg: bytes) -> bytes:
        send_length = str(len(msg)).encode(self.FORMAT)
        send_length += b' ' * (self.HEADER_SIZE - len(send_length))
        return send_length

    def send_message(self, connection: socket, msg: Message) -> None:
        msg = pickle.dumps(msg)
        msg_size = self.get_header_bytes(msg)
        connection.send(msg_size)
        connection.send(msg)
