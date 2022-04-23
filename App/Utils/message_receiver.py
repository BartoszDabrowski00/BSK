import pickle
from socket import socket

from PyQt5.QtWidgets import QTextEdit

from App.Utils.message import Message, MessageTypes


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
                    self.save_file(msg)
            except:
                pass

    def save_file(self, msg: Message) -> None:
        with open('sent_file', 'w') as file:
            file.write(msg.msg)