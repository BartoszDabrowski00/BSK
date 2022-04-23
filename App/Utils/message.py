from enum import Enum


class MessageTypes(Enum):
    CONNECT = 'CONNECT'
    DISCONNECT = 'DISCONNECT'
    TEXT = 'TEXT'
    FILE = 'FILE'


class Message:
    def __init__(self, id: str, type: str, receiver_id: str = None,  msg: str = None) -> None:
        self.sender_id = id
        self.receiver_id = receiver_id
        self.msg = msg
        self.type = type
