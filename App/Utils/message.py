from enum import Enum
from typing import Union


class MessageTypes(Enum):
    CONNECT = 'CONNECT'
    DISCONNECT = 'DISCONNECT'
    TEXT = 'TEXT'
    FILE = 'FILE'


class Message:
    def __init__(self, id: str, type: str, receiver_id: str = None,  msg: Union[str, bytes, int] = None) -> None:
        self.sender_id = id
        self.receiver_id = receiver_id
        self.msg = msg
        self.type = type
