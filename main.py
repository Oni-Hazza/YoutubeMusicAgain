import sys

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
import qasync
import asyncio

from widgets.LogWidget import CombinedErrorLog
from youtubefunc.youtubelogin import authrequest

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
        self.playlistcombobox = QComboBox()
        layout.addWidget(self.playlistcombobox)
        self.playlistcombobox.currentTextChanged.connect(self.playlistBoxSelectionChange)

        #song table view
        self.songlistview = QListWidget()
        self.songlistview.setMinimumHeight(300)
        layout.addWidget(self.songlistview)
        self.songlistview.itemClicked.connect(self.songlistViewSelectionChanged)

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

        self.playlists = {}
        self.songlist = {}

        self.youtubeClient= authrequest()

        if not self.youtubeClient.makeAuthRequest():
            sys.exit()

        self.populatePlaylistdict()

    def playlistBoxSelectionChange(self):
        if self.playlistcombobox.currentIndex() == -1:
            return
        self.error_log.debug("Combo box selection changed")
        self.error_log.debug(self.playlistcombobox.currentIndex())
        self.error_log.debug(self.playlists[self.playlistcombobox.currentText()])
        asyncio.create_task(self.populateSongList())
    
    async def populateSongList(self):
        self.playlistcombobox.setEnabled(False)
        self.songlistview.setEnabled(False)
        #self.songlistview.setCurrentRow(-1)
        self.songlistview.clear()
        self.songlist.clear()
        
        if len(self.playlists[self.playlistcombobox.currentText()]['playlistCache']) == 0:
            
            self.error_log.debug("populating song list")

            nextpagetoken=""
            while nextpagetoken != None:

                request = self.youtubeClient.youtube.playlistItems().list(
                    part="snippet",
                    maxResults=50,
                    playlistId=self.playlists[self.playlistcombobox.currentText()]['id'],
                    pageToken=nextpagetoken
                )
                self.error_log.debug(self.playlists[self.playlistcombobox.currentText()])
                
                response = request.execute()

                self.error_log.debug(response)

                for s in response["items"]:
                    if s['snippet']['title'].lower() in ['deleted video', 'private video']:
                        continue
                    self.songlist.update({s['snippet']['title']:s['snippet']['resourceId']['videoId']})
                    self.error_log.debug(s['snippet']['title'])
                    self.songlistview.addItem(s['snippet']['title'])
                    self.playlists[self.playlistcombobox.currentText()]['playlistCache'].update({s['snippet']['title']:s['snippet']['resourceId']['videoId']})
                
                self.songlistview.setCurrentRow(-1)
                
                self.songlistview.repaint()

                if "nextPageToken" in response:
                    nextpagetoken = response["nextPageToken"]
                else:
                    nextpagetoken = None
        else:
            self.songlistview.addItems(self.playlists[self.playlistcombobox.currentText()]['playlistCache'])
        
        self.songlistview.repaint()
        self.playlistcombobox.setEnabled(True)
        self.songlistview.setEnabled(True)
        
    
    def songlistViewSelectionChanged(self):
        if self.songlistview.currentRow() == -1:
            return
        playlist = self.playlistcombobox.currentText()
        song = self.songlistview.currentItem().text()
        id = self.playlists[playlist]['playlistCache'][song]
        self.error_log.info(f"{id}")

    def populatePlaylistdict(self):
        request = self.youtubeClient.youtube.playlists().list(
            part="snippet,contentDetails",
            maxResults=25,
            mine=True
        )

        response = request.execute()

        for x in response["items"]:
            self.playlists.update({x['snippet']['title']:{'id':x['id'], 'playlistCache':{}}})
        
        self.playlistcombobox.addItems(self.playlists)
        # for x in self.playlists:
        #     self.playlistcombobox.addItem(x)
        self.playlistcombobox.setCurrentIndex(-1)
        



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

    def __del__(self):
        del self.youtubeClient


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