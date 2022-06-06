import pickle
from socket import socket

from App.Utils.message import Message, MessageTypes
from App.Utils.message_encryptor import Encryptions


class MessageSender:
    HEADER_SIZE = 256
    FORMAT = 'utf-8'

    def __init__(self):
        pass

    def get_header_bytes(self, msg: bytes) -> bytes:
        send_length = str(len(msg)).encode(self.FORMAT)
        send_length += b' ' * (self.HEADER_SIZE - len(send_length))
        return send_length

    def send_message(self, connection: socket, msg: Message, key: bytes = None, encryption_mode: int = None) -> None:
        if key and encryption_mode and msg.type not in [MessageTypes.CONNECT.value, MessageTypes.DISCONNECT.value]:
            content = msg.msg
            if msg.type == MessageTypes.TEXT.value:
                content = content.encode(self.FORMAT)
            msg.msg = Encryptions.encrypt_message(key, encryption_mode, content)
            msg.encryption_mode = encryption_mode
        pickled_msg = pickle.dumps(msg)
        msg_size = self.get_header_bytes(pickled_msg)
        connection.send(msg_size)
        connection.send(pickled_msg)
