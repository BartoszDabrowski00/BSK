import socket
import threading
import logging

from App.Utils.message import Message, MessageTypes
from App.Utils.message_receiver import MessageReceiver
from App.Utils.message_sender import MessageSender

log = logging.getLogger(__name__)


class Server:

    def __init__(self, port: int, address: str) -> None:
        self.id = 'SERVER'
        self.port = port
        self.address = address
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.address, self.port))
        self.connections = {}
        self.message_sender = MessageSender()
        self.message_receiver = MessageReceiver(self.id)
        self.wait_for_connection()

    def wait_for_connection(self) -> None:
        log.info('SERVER STARTING')
        self.server.listen()
        while True:
            conn, addr = self.server.accept()
            thread = threading.Thread(target=self.handle_connection, args=(conn, addr))
            thread.start()

    def handle_connection(self, conn: socket, addr: str) -> None:
        connection = True
        while connection:
            msg = self.message_receiver.get_message(conn)
            if msg:
                connection = self.handle_message(msg, addr, conn)

    def handle_message(self, msg: Message, addr: str, conn: socket) -> bool:
        if msg.type == MessageTypes.CONNECT.value:
            log.info(f'New connection from: {addr} | id {msg.sender_id}')
            self.connections.update({msg.sender_id: {"address": addr, "connection": conn}})
        elif msg.type == MessageTypes.DISCONNECT.value:
            log.info(f'Closing connection from: {addr}')
            conn.close()
            self.connections.pop(msg.sender_id)
            return False
        elif msg.type == MessageTypes.TEXT.value:
            log.info(f'Message from: {msg.sender_id} | Content: {msg.msg}')
            receiver_connection = self.get_receiver_connection(msg.receiver_id)
            if receiver_connection:
                self.message_sender.send_message(receiver_connection, msg)
        elif msg.type == MessageTypes.FILE.value:
            log.info(f'File from from: {msg.sender_id} to: {msg.receiver_id}')
            receiver_connection = self.get_receiver_connection(msg.receiver_id)
            if receiver_connection:
                self.message_sender.send_message(receiver_connection, msg)

        return True

    def get_receiver_connection(self, receiver_id: str) -> socket:
        return self.connections.get(receiver_id, {}).get("connection", None)

