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
        self.message_receiver.client = self.client
        msg = Message(
            id=self.id,
            type=MessageTypes.CONNECT.value
        )
        self.message_sender.send_message(self.client, msg)
        self.receiving_thread = threading.Thread(target=self.message_receiver.get_message, args=[self.client])
        self.receiving_thread.start()
    def send_public_key(self, public_key: bytes, receiver_id: str):
        msg = Message(
            id=self.id,
            receiver_id=receiver_id,
            msg=public_key,
            type=MessageTypes.PUBLIC_KEY.value
        )
        self.message_sender.send_message(
            self.client,
            msg
        )
    def send_text(self, msg: str, receiver_id: str, encryption_mode: int = None, key: bytes = None) -> None:
        msg = Message(
            id=self.id,
            receiver_id=receiver_id,
            msg=msg,
            type=MessageTypes.TEXT.value
        )
        self.message_sender.send_message(
            self.client,
            msg,
            key=key,
            encryption_mode=encryption_mode
        )

    def send_file(self, file_path: str, receiver_id: str, key: bytes, encryption_mode: int) -> None:
        num_of_parts, extension = self.create_file_headers(file_path, receiver_id)
        with open(file_path, 'r+b') as source_file:
            idx = 0
            while True:
                data = source_file.read(self.MAX_MESSAGE_SIZE_BYTES)
                if data:
                    self.progress_bar.setValue((idx + 1) / num_of_parts * 100)
                    idx += 1
                    msg = Message(
                        id=self.id,
                        type=MessageTypes.FILE.value,
                        receiver_id=receiver_id,
                        msg=data,
                        file_parts=num_of_parts,
                        extension=extension,
                        file_part_position=idx
                    )
                    self.message_sender.send_message(
                        self.client,
                        msg,
                        key=key,
                        encryption_mode=encryption_mode
                    )
                    log.info(f'Send msg no {idx} of {num_of_parts}')
                else:
                    break

    def disconnect(self) -> None:
        msg = Message(
            id=self.id,
            type=MessageTypes.DISCONNECT.value
        )
        self.message_sender.send_message(self.client, msg)
        self.client.close()

    def create_file_headers(self, file_path: str, receiver_id: str) -> [Message]:
        extension = os.path.splitext(file_path)[1]
        file_parts = math.ceil(os.path.getsize(file_path) / self.MAX_MESSAGE_SIZE_BYTES)
        return file_parts, extension
