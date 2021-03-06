import logging
import os

from Crypto.Cipher.AES import MODE_CBC, MODE_ECB
from PyQt5.QtWidgets import QDialog, QFileDialog
from PyQt5.uic import loadUi

from App.Utils.message_receiver import UiMessageReceiver
from App.Utils.security_keys_handler import SecurityKeysHandler
from message_handler import MessageHandler

log = logging.getLogger(__name__)


class MainWindow(QDialog):

    def __init__(self) -> None:
        super(MainWindow, self).__init__()
        loadUi("main_window.ui", self)
        self.submit_button.clicked.connect(self.on_submit_button_click)
        self.connection_button.clicked.connect(self.on_connection_button_click)
        self.browse_button.clicked.connect(self.on_browse_button_click)
        self.id_button.clicked.connect(self.on_id_button_click)
        self.keys_button.clicked.connect(self.on_keys_button_click)
        self.password_button.clicked.connect(self.on_password_button_click)
        self.security_keys_handler = SecurityKeysHandler()
        self.message_handler = None
        self.message_receiver = None
        self.connected = False
        self.id = None
        self.password = None

    def on_id_button_click(self) -> None:
        self.id = self.id_line.text()
        log.info(f'Client set id to {self.id}')

    def on_submit_button_click(self) -> None:
        if self.connected:
            message = self.message_line.text()
            receiver_id = self.receiver_id.text()
            is_session_established = self.check_session(receiver_id)

            if not is_session_established:
                self.message_handler.send_public_key(self.security_keys_handler.public_key, receiver_id)
                return

            encryption_mode = MODE_CBC if self.cbc_radio_button.isChecked() else MODE_ECB
            self.message_handler.send_text(
                message,
                encryption_mode=encryption_mode,
                key=self.security_keys_handler.session_keys[receiver_id],
                receiver_id=receiver_id
            )
            self.add_message(message)

    def on_connection_button_click(self) -> None:
        if self.id:
            if not self.connected:
                log.info(f'Connecting to server')
                if not self.message_handler:
                    self.message_receiver = UiMessageReceiver(self.id, self.text_edit, self.security_keys_handler)
                    self.message_handler = MessageHandler(
                        id=self.id,
                        message_receiver=self.message_receiver,
                        progress_bar=self.progress_bar,
                    )
                self.message_handler.connect()
                self.connected = True
                self.ConnectionStatusLabel.setText('Connected')
            else:
                log.info(f'Disconnecting from server')
                self.message_handler.disconnect()
                self.connected = False
                self.ConnectionStatusLabel.setText('Disconnected')

    def add_message(self, message: str) -> None:
        self.text_edit.append(f'{self.id}: {message}')

    def on_browse_button_click(self) -> None:
        file_path = QFileDialog.getOpenFileName(self, 'Open file')[0]
        log.info(f'Sending file: {file_path}')
        receiver_id = self.receiver_id.text()
        if receiver_id:
            is_session_established = self.check_session(receiver_id)
            if not is_session_established:
                self.message_handler.send_public_key(self.security_keys_handler.public_key, receiver_id)
                return
            self.progress_bar.show()
            encryption_mode = MODE_CBC if self.cbc_radio_button.isChecked() else MODE_ECB
            self.message_handler.send_file(file_path, receiver_id, self.security_keys_handler.session_keys[receiver_id],
                                           encryption_mode)
            log.info(f'File sent')

    def on_keys_button_click(self) -> None:
        if self.password is None:
            log.warning('Password is not set')
            return
        selected_path = os.path.normpath(QFileDialog.getExistingDirectory(self, 'Select directory'))
        log.info(f'Selecting folder {selected_path}')
        self.security_keys_handler.load_rsa_keys(selected_path, self.password)

    def on_password_button_click(self) -> None:
        self.password = self.password_line.text()
        if len(self.password) < 3:
            log.warning('Password is to short')
            self.password = None
            return
        log.info('User set new password')

    def check_session(self, receiver_id):
        is_connection_established = receiver_id in self.security_keys_handler.session_keys
        if not is_connection_established:
            log.info('Session not established')
        return is_connection_established
