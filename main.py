import sys
import psutil
import signal
import qasync
import asyncio

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import QIcon
import vlc
import yt_dlp

from widgets.LogWidget import CombinedErrorLog
from youtubefunc.youtubelogin import authrequest

import youtubefunc.ytdlpstuff
import resources

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Youtube Music At Home")

        self.instance = vlc.Instance()

        self.mediaplayer = self.instance.media_player_new()
        self.mediaplayer.audio_set_volume(50)

        
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
        self.songlistview.itemActivated.connect(self.songlistViewItemActivated)

        #placeholder for controlls
        # self.controllplaceholder = QTextEdit()
        # self.controllplaceholder.setMinimumHeight(50)
        # self.controllplaceholder.setMaximumHeight(70)
        # layout.addWidget(self.controllplaceholder)

        self.volumeSlider = QSlider()
        self.volumeSlider.setToolTip("Volume")
        self.volumeSlider.setMaximum(100)
        self.volumeSlider.setValue(self.mediaplayer.audio_get_volume())
        self.volumeSlider.sliderMoved.connect(self.setVolume)
        layout.addWidget(self.volumeSlider)
        
        # # Add the combined log widget
        # self.error_log = CombinedErrorLog()
        # self.error_log.setMaximumHeight(200)
        # self.error_log.setMinimumHeight(150)
        # #self.error_log.setMaximumWidth(400)
        # layout.addWidget(self.error_log, alignment=Qt.AlignmentFlag.AlignBottom)

        self.queueBox = QListWidget()
        self.queueBox.setMaximumHeight(200)
        self.queueBox.setMinimumHeight(100)
        self.queueBox.setMinimumWidth(350)
        layout.addWidget(self.queueBox, alignment=Qt.AlignmentFlag.AlignBottom)

        self.playlists = {}
        self.songlist = {}

        self.youtubeClient= authrequest()

        if not self.youtubeClient.makeAuthRequest():
            sys.exit()

        self.populatePlaylistdict()

    def setVolume(self, volume):
        self.mediaplayer.audio_set_volume(volume)

    def playlistBoxSelectionChange(self):
        if self.playlistcombobox.currentIndex() == -1:
            return
        print("Combo box selection changed")
        print(self.playlistcombobox.currentIndex())
        print(self.playlists[self.playlistcombobox.currentText()])
        asyncio.create_task(self.populateSongList())
    
    async def populateSongList(self):
        self.playlistcombobox.setEnabled(False)
        self.songlistview.setEnabled(False)
        #self.songlistview.setCurrentRow(-1)
        self.songlistview.clear()
        self.songlist.clear()
        
        if len(self.playlists[self.playlistcombobox.currentText()]['playlistCache']) == 0:
            
            print("populating song list")

            nextpagetoken=""
            while nextpagetoken != None:

                request = self.youtubeClient.youtube.playlistItems().list(
                    part="snippet",
                    maxResults=50,
                    playlistId=self.playlists[self.playlistcombobox.currentText()]['id'],
                    pageToken=nextpagetoken
                )
                print(self.playlists[self.playlistcombobox.currentText()])
                
                response = request.execute()

                print(response)

                for s in response["items"]:
                    if s['snippet']['title'].lower() in ['deleted video', 'private video']:
                        continue
                    self.songlist.update({s['snippet']['title']:s['snippet']['resourceId']['videoId']})
                    print(s['snippet']['title'])
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
        
    def songlistViewItemActivated(self):
        playlist = self.playlistcombobox.currentText()
        song = self.songlistview.currentItem().text()
        id = self.playlists[playlist]['playlistCache'][song]
        self.queueBox.addItem(id)
        try:
            songstream = youtubefunc.ytdlpstuff.getAudioStream(id)
        except Exception as e:
            # pixmapi = getattr(QStyle.StandardPixmap, 'SP_MessageBoxWarning')
            # icon = self.style().standardIcon(pixmapi)
            dlg = QMessageBox(self, "Error!", e, QMessageBox.standardButton())
            return

        media = self.instance.media_new(songstream)
        self.mediaplayer.set_media(media)
        self.mediaplayer.play()

    def songlistViewSelectionChanged(self):
        if self.songlistview.currentRow() == -1:
            return
        playlist = self.playlistcombobox.currentText()
        song = self.songlistview.currentItem().text()
        id = self.playlists[playlist]['playlistCache'][song]
        print(f"{id}")

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
        

    def __del__(self):
        del self.youtubeClient


async def main():
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(':/icons/icon.png'))
    window = MainWindow()
    window.show()
    

    app.aboutToQuit.connect(lambda: asyncio.get_running_loop().stop())

    await qasync.QEventLoop(app).run_forever()

def kill_all_children():
    current_process = psutil.Process()
    children = current_process.children(recursive=True)
    for child in children:
        child.send_signal(signal.SIGTERM)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except asyncio.exceptions.CancelledError:
        pass
    except TypeError:
        pass

    kill_all_children()

