from PyQt5.uic import loadUi
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog, QFileDialog


class MainWindow(QDialog):
    def __init__(self) -> None:
        super(MainWindow, self).__init__()
        loadUi("main_window.ui", self)
        self.submit_button.clicked.connect(self.on_submit_button_click)
        self.connection_button.clicked.connect(self.on_connection_button_click)
        self.browse_button.clicked.connect(self.on_browse_button_click)

    def on_submit_button_click(self) -> None:
        print("Print submit button clicked")

    def on_connection_button_click(self) -> None:
        print("Connection button clicked")

    def add_message(self, message: str) -> None:
        print("New message")
        self.text_edit.setText(message + self.text_edit.text())

    def on_browse_button_click(self) -> None:
        print("Browse file clicked")
        file_path = QFileDialog.getOpenFileName(self, 'Open file')[0]
        print(file_path)
        self.message_line.setText(file_path)
