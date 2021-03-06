from enum import Enum
from typing import Union


class MessageTypes(Enum):
    CONNECT = 'CONNECT'
    DISCONNECT = 'DISCONNECT'
    TEXT = 'TEXT'
    FILE = 'FILE'
    PUBLIC_KEY = 'PUBLIC_KEY'
    SESSION_KEY = 'SESSION_KEY'


class Message:
    def __init__(self, id: str, type: str, receiver_id: str = None,  msg: Union[str, bytes, int] = None,
                 encryption_mode: int = None, file_parts: int = None, extension: str = None, file_part_position: int = None) -> None:
        self.sender_id = id
        self.receiver_id = receiver_id
        self.msg = msg
        self.type = type
        self.encryption_mode = encryption_mode
        self.file_parts = file_parts
        self.extension = extension
        self.file_part_position = file_part_position
