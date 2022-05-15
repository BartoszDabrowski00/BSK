import logging

from PyQt5.QtWidgets import QDialog, QFileDialog
from PyQt5.uic import loadUi

from App.Utils.message_receiver import UiMessageReceiver
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
        self.message_handler = None
        self.connected = False
        self.id = None

    def on_id_button_click(self) -> None:
        self.id = self.id_line.text()
        log.info(f'Client set id to {self.id}')

    def on_submit_button_click(self) -> None:
        if self.connected:
            message = self.message_line.text()
            receiver_id = self.receiver_id.text()
            self.message_handler.send_text(message, receiver_id=receiver_id)
            self.add_message(message)

    def on_connection_button_click(self) -> None:
        if self.id:
            if not self.connected:
                log.info(f'Connecting to server')
                if not self.message_handler:
                    self.message_handler = MessageHandler(
                        id=self.id,
                        message_receiver=UiMessageReceiver(self.text_edit),
                        progress_bar=self.progress_bar
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
            self.progress_bar.show()
            self.message_handler.send_file(file_path, receiver_id)
            log.info(f'File sent')
