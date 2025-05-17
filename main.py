import sys

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
import qasync
import asyncio

from widgets.LogWidget import CombinedErrorLog

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Youtube Music At Home")
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        layout = QVBoxLayout(central_widget)
        
        # Main content area
        # self.testbutton = QPushButton("press")
        # self.testbutton.clicked.connect(lambda: self.buttonclick(self.testbutton))
        # layout.addWidget(self.testbutton, stretch=1)
        self.playlistbox = QComboBox()
        layout.addWidget(self.playlistbox)

        #song table view
        self.songtable = QTableView()
        self.songtable.setMinimumHeight(300)
        layout.addWidget(self.songtable)

        #placeholder for controlls
        self.controllplaceholder = QTextEdit()
        self.controllplaceholder.setMinimumHeight(50)
        self.controllplaceholder.setMaximumHeight(70)
        layout.addWidget(self.controllplaceholder)
        
        # Add the combined log widget
        self.error_log = CombinedErrorLog()
        self.error_log.setMaximumHeight(200)
        self.error_log.setMinimumHeight(150)
        #self.error_log.setMaximumWidth(400)
        layout.addWidget(self.error_log, alignment=Qt.AlignmentFlag.AlignBottom)

    def buttonclick(self, button:QPushButton):
        asyncio.create_task(self.on_async_button(button))
    
    async def on_async_button(self, button:QPushButton):
        if button == self.testbutton:
            try:
                
                button.setEnabled(False)
                self.error_log.info("Starting async operation")
                
                # Simulate async work
                await asyncio.sleep(1)
                self.error_log.warning("Still working...")
                
                await asyncio.sleep(1)
                self.error_log.info("Operation complete")
                
            except Exception as e:
                self.error_log.error(f"Async error: {str(e)}")
            finally:
                button.setEnabled(True)
        else:
            self.error_log.error(f"{button.text()} button was pressed with no valid functions")


async def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()

    app.aboutToQuit.connect(lambda: asyncio.get_running_loop().stop())

    await qasync.QEventLoop(app).run_forever()

    

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except asyncio.exceptions.CancelledError:
        pass