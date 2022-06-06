import logging
import pickle
from socket import socket

from PyQt5.QtWidgets import QTextEdit

from App.Utils.message import Message, MessageTypes
from App.Utils.message_encryptor import Encryptions

log = logging.getLogger(__name__)


class MessageReceiver:
    HEADER_SIZE = 512
    FORMAT = 'utf-8'

    def __init__(self, id: str, session_key: bytes = None):
        self.id = id
        self.key = session_key

    def get_message(self, conn: socket) -> Message:
        msg_length = int(conn.recv(self.HEADER_SIZE).decode(self.FORMAT))
        if msg_length:
            msg = conn.recv(msg_length)
            msg = pickle.loads(msg)
            if msg.type not in [MessageTypes.CONNECT.value, MessageTypes.DISCONNECT.value] and self.id == msg.receiver_id:
                encryption_mode = msg.encryption_mode
                msg.msg = Encryptions.decrypt_message(self.key, encryption_mode, msg.msg)
                if msg.type == MessageTypes.TEXT.value:
                    msg.msg = msg.msg.decode(self.FORMAT)
            return msg


class UiMessageReceiver(MessageReceiver):
    def __init__(self, id: str, text_edit: QTextEdit):
        super().__init__(id)
        self.text_edit = text_edit

    def get_message(self, conn: socket) -> None:
        while conn:
            try:
                msg = super().get_message(conn)
                if msg.type == MessageTypes.TEXT.value:
                    self.text_edit.append(f'{msg.sender_id}: {msg.msg}')
                elif msg.type == MessageTypes.FILE.value:
                    self.download_file(msg, conn)
            except:
                pass

    def download_file(self, msg: Message, conn: socket) -> None:
        file_parts = int(msg.file_parts)
        extension = msg.extension
        log.info(f'Downloading file in {file_parts} parts | extension {extension}')
        with open(f'sent_file{extension}', 'w+b') as file:
            file.write(msg.msg)
            for i in range(file_parts - 1):
                log.info(f'Wrote part {i} of {file_parts}')
                msg = (super().get_message(conn).msg)
                file.write(msg)
