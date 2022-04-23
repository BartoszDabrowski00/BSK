import sys
from main_window import MainWindow
from PyQt5.QtWidgets import QApplication


def main() -> None:
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()

    try:
        sys.exit(app.exec_())
    except:
        print("Closing the application")

if __name__ == "__main__":
    main()