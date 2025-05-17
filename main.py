import sys

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *

from widgets.LogWidget import ErrorLog, LogControls
import LogManager

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setFixedSize(960, 540)
        self.setWindowTitle("Youtube Music")
        try:
            self.testbutton = QPushButton("test")
            self.testbutton.clicked.connect(self.testclicked)
            self.testbutton.move(10, 10)
            self.setCentralWidget(self.testbutton)
        except:
            print("something went wrong with button")

        self.setup_log_ui()
        
    def setup_log_ui(self):
        # Main content area
        # self.main_content = QTextEdit(self)
        # self.main_content.setGeometry(0, 0, 960, 540)
        
        # Error log in bottom-left corner
        self.error_log = ErrorLog(self)
        self.error_log.setGeometry(10, 540-190, 400, 180)  # x, y, w, h
        
        # Log controls
        self.log_controls = LogControls(self.error_log, self)
        self.log_controls.setGeometry(10, 540-230, 390, 50)

    def generate_test_messages(self):
        self.error_log.error("Global error message")
        self.error_log.info("Test button clicked")
        self.error_log.warning("Sample warning message")
        self.error_log.error("Sample error message")
        self.error_log.debug("Debug information")

    def testclicked(self):
        self.generate_test_messages()

    

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    app.exec()