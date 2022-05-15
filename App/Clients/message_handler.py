import math
import os
import socket
import logging
import threading

from PyQt5.QtWidgets import QProgressBar

from App.Utils.message import Message, MessageTypes
from App.Utils.message_receiver import UiMessageReceiver
from App.Utils.message_sender import MessageSender

log = logging.getLogger(__name__)


class MessageHandler:
    PORT = int(os.getenv("SERVER_PORT", 12345))
    SERVER_ADDRESS = os.getenv("SERVER_ADDRESS", 'localhost')
    MAX_MESSAGE_SIZE_BYTES = 1024 * 1024

    def __init__(self, id: str, message_receiver: UiMessageReceiver, progress_bar: QProgressBar) -> None:
        self.client = None
        self.id = id
        self.message_sender = MessageSender()
        self.message_receiver = message_receiver
        self.receiving_thread = None
        self.progress_bar = progress_bar

    def connect(self) -> None:
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((self.SERVER_ADDRESS, self.PORT))
        msg = Message(
            id=self.id,
            type=MessageTypes.CONNECT.value
        )
        self.message_sender.send_message(self.client, msg)
        self.receiving_thread = threading.Thread(target=self.message_receiver.get_message, args=[self.client])
        self.receiving_thread.start()

    def send_text(self, msg: str, receiver_id: str) -> None:
        msg = Message(
            id=self.id,
            receiver_id=receiver_id,
            msg=msg,
            type=MessageTypes.TEXT.value
        )
        self.message_sender.send_message(self.client, msg)

    def send_file(self, file_path: str, receiver_id: str) -> None:
        messages = self.split_file(file_path, receiver_id)
        for idx, msg in enumerate(messages):
            self.progress_bar.setValue((idx+1)/len(messages)*100)
            self.message_sender.send_message(self.client, msg)

    def disconnect(self) -> None:
        msg = Message(
            id=self.id,
            type=MessageTypes.DISCONNECT.value
        )
        self.message_sender.send_message(self.client, msg)
        self.client.close()

    def split_file(self, file_path: str, receiver_id: str) -> [Message]:
        messages = self.create_file_headers(file_path, receiver_id)
        with open(file_path, 'r+b') as source_file:
            while True:
                data = source_file.read(self.MAX_MESSAGE_SIZE_BYTES)
                if data:
                    messages.append(Message(
                        id=self.id,
                        type=MessageTypes.FILE.value,
                        receiver_id=receiver_id,
                        msg=data
                    ))
                else:
                    break
        return messages

    def create_file_headers(self, file_path: str, receiver_id: str) -> [Message]:
        extension = os.path.splitext(file_path)[1]
        file_parts = math.ceil(os.path.getsize(file_path) / self.MAX_MESSAGE_SIZE_BYTES)
        return [Message(id=self.id, type=MessageTypes.FILE.value, receiver_id=receiver_id, msg=file_parts),
                Message(id=self.id, type=MessageTypes.FILE.value, receiver_id=receiver_id, msg=extension)]
