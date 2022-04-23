import os
import socket
import logging
import threading

from App.Utils.message import Message, MessageTypes
from App.Utils.message_receiver import UiMessageReceiver
from App.Utils.message_sender import MessageSender

log = logging.getLogger(__name__)


class MessageHandler:
    PORT = int(os.getenv("SERVER_PORT", 12345))
    SERVER_ADDRESS = os.getenv("SERVER_ADDRESS", 'localhost')

    def __init__(self, id: str, message_receiver: UiMessageReceiver) -> None:
        self.client = None
        self.id = id
        self.message_sender = MessageSender()
        self.message_receiver = message_receiver
        self.receiving_thread = None

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

    def send_file(self, path: str, receiver_id: str) -> None:
        with open(path) as file:
            msg = Message(
                id=self.id,
                receiver_id=receiver_id,
                msg=file.read(),
                type=MessageTypes.FILE.value
            )
        self.message_sender.send_message(self.client, msg)

    def disconnect(self) -> None:
        msg = Message(
            id=self.id,
            type=MessageTypes.DISCONNECT.value
        )
        self.message_sender.send_message(self.client, msg)
        self.client.close()
