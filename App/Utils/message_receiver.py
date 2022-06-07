import logging
import pickle
from socket import socket

from PyQt5.QtWidgets import QTextEdit

from App.Utils.message import Message, MessageTypes
from App.Utils.message_encryptor import Encryptions
from App.Utils.security_keys_handler import SecurityKeysHandler
from App.Utils.message_sender import MessageSender
log = logging.getLogger(__name__)


class MessageReceiver:
    HEADER_SIZE = 512
    FORMAT = 'utf-8'

    def __init__(self, id: str, session_key: bytes = None, security_keys_handler: SecurityKeysHandler = None):
        self.id = id
        self.security_key_handler = security_keys_handler

    def get_message(self, conn: socket) -> Message:
        try:
            msg_length = []
            while len(b''.join(msg_length)) < self.HEADER_SIZE:
                msg_length.append(conn.recv(self.HEADER_SIZE))
            msg_length = int(b''.join(msg_length).decode(self.FORMAT))
            if msg_length:
                data = []
                while len(b''.join(data)) < msg_length:
                    data.append(conn.recv(msg_length))
                msg = pickle.loads(b''.join(data))
                if msg.type not in [MessageTypes.CONNECT.value,  MessageTypes.DISCONNECT.value,
                                    MessageTypes.PUBLIC_KEY.value, MessageTypes.SESSION_KEY.value]\
                                    and self.id == msg.receiver_id:
                    encryption_mode = msg.encryption_mode
                    key = self.security_key_handler.session_keys[msg.sender_id]
                    msg.msg = Encryptions.decrypt_message(key, encryption_mode, msg.msg)
                    if msg.type == MessageTypes.TEXT.value:
                        msg.msg = msg.msg.decode(self.FORMAT)
                return msg
        except Exception as e:
            pass


class UiMessageReceiver(MessageReceiver):
    def __init__(self, id: str, text_edit: QTextEdit, security_key_handler: SecurityKeysHandler):
        super().__init__(id, None, security_key_handler)
        self.text_edit = text_edit
        self.client = None

    def get_message(self, conn: socket) -> None:
        while conn:
            try:
                msg = super().get_message(conn)
                if msg.type == MessageTypes.TEXT.value:
                    self.text_edit.append(f'{msg.sender_id}: {msg.msg}')
                elif msg.type == MessageTypes.FILE.value:
                    self.download_file(msg, conn)
                elif msg.type == MessageTypes.PUBLIC_KEY.value:
                    self.start_session(msg)
                elif msg.type == MessageTypes.SESSION_KEY.value:
                    self.security_key_handler.load_session_key(msg)
            except:
                pass

    def download_file(self, msg: Message, conn: socket) -> None:
        file_parts = int(msg.file_parts)
        extension = msg.extension
        log.info(f'Downloading file in {file_parts} parts | extension {extension}')
        messages = [msg]
        while len(messages) != file_parts:
            msg = super().get_message(conn)
            log.info(f'Wrote part {msg.file_part_position} of {file_parts}')
            messages.append(msg)
        messages = list(map(lambda x: x.msg, sorted(messages, key=lambda x: x.file_part_position)))
        with open(f'sent_file{extension}', 'w+b') as file:
            file.write(b''.join(messages))

    def start_session(self, msg: Message):
        sender_public_key = msg.msg
        encrypted_session_key = self.security_key_handler.generate_session_key(msg.sender_id, sender_public_key)
        session_msg = Message(
            id=self.id,
            receiver_id=msg.sender_id,
            msg=encrypted_session_key,
            type=MessageTypes.SESSION_KEY.value
        )
        message_sender = MessageSender()
        message_sender.send_message(self.client, session_msg)







