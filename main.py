import sys

from PyQt6.QtWidgets import *

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__(parent=None)

        self.setWindowTitle("Youtube Music")
        self.setFixedSize(960, 540)
        self.setStyleSheet("background-color: #3f3f3f")
        
        self.outputlog()


    def outputlog(self):
        self.outputbox = QLabel(self)
        self.outputbox.setFrameStyle(QFrame.Shape.Panel | QFrame.Shadow.Sunken)
        self.outputbox.setFixedSize(400, 160)
        self.outputbox.move(10, 370)
        self.outputbox.setStyleSheet("background-color: #9c9c9c")
    

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    app.exec()