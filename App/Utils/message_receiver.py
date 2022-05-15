import logging
import pickle
from socket import socket

from PyQt5.QtWidgets import QTextEdit

from App.Utils.message import Message, MessageTypes

log = logging.getLogger(__name__)


class MessageReceiver:
    HEADER_SIZE = 256
    FORMAT = 'utf-8'

    def __init__(self):
        pass

    def get_message(self, conn: socket) -> Message:
        msg_length = int(conn.recv(self.HEADER_SIZE).decode(self.FORMAT))
        if msg_length:
            msg = pickle.loads(conn.recv(msg_length))
            return msg


class UiMessageReceiver(MessageReceiver):
    def __init__(self, text_edit: QTextEdit):
        super().__init__()
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
        messages = []
        file_parts = int(msg.msg)
        extension = super().get_message(conn).msg
        log.info(f'Downloading file in {file_parts} parts | extension {extension}')
        for i in range(file_parts):
            messages.append(super().get_message(conn).msg)
        with open(f'sent_file{extension}', 'w+b') as file:
            file.write(b''.join(messages))
