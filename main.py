import sys
import psutil
import signal
import qasync
import asyncio
import random
import webbrowser

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import QIcon
from PyQt6.QtGui import QCursor
import vlc
import yt_dlp

from widgets.LogWidget import CombinedErrorLog
from widgets.playbackControlsWidgets import PlaybackControls
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
        # self.events = self.mediaplayer.event_manager()
        # self.events.event_attach(vlc.EventType.MediaPlayerEndReached, self.mediaplayerended)
        

        
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
        self.songlistview.setMinimumHeight(250)
        layout.addWidget(self.songlistview)
        self.songlistview.itemClicked.connect(self.songlistViewSelectionChanged)
        self.songlistview.itemActivated.connect(self.songlistViewItemActivated)
        self.songlistview.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.songlistview.customContextMenuRequested.connect(self.songlistcontextmenuactivate)

        #songlist context menu
        self.songlistContextMenu = QMenu(self)
        shuffle = self.songlistContextMenu.addAction("Shuffle playlist into queue")
        addToQueue = self.songlistContextMenu.addAction("Add to queue")
        playNext = self.songlistContextMenu.addAction("Play next")
        openInYoutube = self.songlistContextMenu.addAction("Open in youtube")
        shuffle.triggered.connect(self.contextmenushuffletrigger)
        addToQueue.triggered.connect(self.contextmenuaddtoqueuetrigger)
        playNext.triggered.connect(self.contextmenuplaynexttrigger)
        openInYoutube.triggered.connect(self.contextmenuopeninyoutubetrigger)

        

        self.playbackcontrols = PlaybackControls(self)

        self.playbackcontrols.volume_slider.valueChanged.connect(self.setVolume)
        self.playbackcontrols.play_button.clicked.connect(self.playPauseClicked)
        self.playbackcontrols.stop_button.clicked.connect(self.stopButtonClicked)
        self.playbackcontrols.progress_slider.sliderMoved.connect(self.setPosition)
        self.playbackcontrols.skip_button.clicked.connect(self.skipButtonClicked)

        layout.addWidget(self.playbackcontrols)
        
        # # Add the combined log widget
        # self.error_log = CombinedErrorLog()
        # self.error_log.setMaximumHeight(200)
        # self.error_log.setMinimumHeight(150)
        # #self.error_log.setMaximumWidth(400)
        # layout.addWidget(self.error_log, alignment=Qt.AlignmentFlag.AlignBottom)

        self.queueboxMenu = QMenu(self)
        clearqueueaction = self.queueboxMenu.addAction("Clear Queue")
        clearqueueaction.triggered.connect(self.clearqueuepressed)
        removefromqueueaction = self.queueboxMenu.addAction("Remove item")
        removefromqueueaction.triggered.connect(self.removefromqueuepressed)
        self.queueBox = QListWidget()
        self.queueBox.setMaximumHeight(200)
        self.queueBox.setMinimumHeight(100)
        self.queueBox.setMinimumWidth(350)
        self.queueBox.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.queueBox.customContextMenuRequested.connect(self.queuecontextmenurequested)
        layout.addWidget(self.queueBox, alignment=Qt.AlignmentFlag.AlignBottom)

        self.playlists = {}
        self.songlist = {}
        self.queuelist = {}

        self.youtubeClient= authrequest()

        if not self.youtubeClient.makeAuthRequest():
            sys.exit()

        self.populatePlaylistdict()

        self.timer = QTimer(self)
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.timerTick)
        self.timer.start()
        
    def mediaplayerended(self, state): #out of order for now
        if self.queueBox.count() < 1:
            return
        if self.mediaplayer.get_state() != vlc.State.Ended:
            return
        items = []
        for i in range(self.queueBox.count()):
            items.append(self.queueBox.item(i).text())
        for item in items:
            nextToPlay = self.queuelist[item]
            try:
                songstream = youtubefunc.ytdlpstuff.getAudioStream(nextToPlay)
                self.queueBox.takeItem(0)
                self.queuelist.pop(item, None)
                break
            except:
                continue                

        self.queueBox.repaint()
        try:
            print(self.mediaplayer.will_play())
            media = self.instance.media_new(songstream)
            
            self.mediaplayer.set_media(media)
            if self.mediaplayer.play() == -1:
                print("something went wrong...") #TODO this still doesnt work and im going crazy
        except Exception as e:
            print(e)
        

    def clearqueuepressed(self):
        self.queuelist.clear()
        self.queueBox.clear()
        self.queueBox.repaint()
    def removefromqueuepressed(self):
        if self.queueBox.__len__() < 1:
            return
        index = self.queueBox.currentIndex()
        if index.row() >= 0:
            self.queueBox.takeItem(index.row())
    def queuecontextmenurequested(self, event):
        self.queueboxMenu.exec(QCursor.pos())

    def contextmenushuffletrigger(self):
        if self.songlist.__len__() < 1:
            return
        keys = list(self.songlist.keys())
        random.shuffle(keys)
        for key in keys:
            self.queuelist.update({key:self.songlist[key]})
            self.queueBox.addItem(key)
        self.queueBox.repaint()
    def contextmenuplaynexttrigger(self):
        if self.songlist.__len__() < 1:
            return
        playlist = self.playlistcombobox.currentText()
        song = self.songlistview.currentItem().text()
        id = self.playlists[playlist]['playlistCache'][song]
        
        self.queuelist.update({song:id})
        self.queueBox.insertItem(0, song)
        self.queueBox.repaint()
    def contextmenuaddtoqueuetrigger(self):
        if self.songlist.__len__() < 1:
            return
        playlist = self.playlistcombobox.currentText()
        song = self.songlistview.currentItem().text()
        id = self.playlists[playlist]['playlistCache'][song]
        self.queuelist.update({song:id})
        self.queueBox.addItem(song)
        self.queueBox.repaint()
    def songlistcontextmenuactivate(self, event:QPoint):
        self.songlistContextMenu.exec(QCursor.pos())
    def contextmenuopeninyoutubetrigger(self):
        playlist = self.playlistcombobox.currentText()
        song = self.songlistview.currentItem().text()
        id = self.playlists[playlist]['playlistCache'][song]
        link = f"https://youtu.be/{id}"
        webbrowser.open(link, new=0, autoraise=True)

    
    def timerTick(self):
        state = self.mediaplayer.get_state()
        if state == vlc.State.Playing or state == vlc.State.Paused:
            media_pos = int(self.mediaplayer.get_position() * 100)
            self.playbackcontrols.progress_slider.setValue(media_pos)
        elif state == vlc.State.Ended or state == vlc.State.Stopped:
            if self.queueBox.count() < 1:
                return
            items = []
            for i in range(self.queueBox.count()):
                items.append(self.queueBox.item(i).text())
            for item in items:
                nextToPlay = self.queuelist[item]
                try:
                    songstream = youtubefunc.ytdlpstuff.getAudioStream(nextToPlay)
                    self.queueBox.takeItem(0)
                    #self.queuelist.pop(item, None) #stopped coz realistically theres no reason to remove this
                    break
                except:
                    continue

            self.queueBox.repaint()
            try:
                print(self.mediaplayer.will_play())
                media = self.instance.media_new(songstream)
                
                self.mediaplayer.set_media(media)
                if self.mediaplayer.play() == -1:
                    print("something went wrong...") #TODO this still doesnt work and im going crazy
            except Exception as e:
                print(e)

    def playPauseClicked(self):
        state = self.mediaplayer.get_state()
        if state == vlc.State.Paused or state == vlc.State.Playing:
            self.mediaplayer.pause()
        else:
            pass
    def skipButtonClicked(self):
        self.mediaplayer.stop()
    def stopButtonClicked(self):
        state = self.mediaplayer.get_state()
        if state == vlc.State.Paused or state == vlc.State.Playing:
            self.queueBox.clear()
            self.queuelist.clear()
            self.mediaplayer.stop()        
        self.queueBox.repaint()
    def setVolume(self, volume):
        self.mediaplayer.audio_set_volume(volume)
    def setPosition(self, position):
        state = self.mediaplayer.get_state()
        if state == vlc.State.Playing:
            self.mediaplayer.set_position(position/100)

    def playlistBoxSelectionChange(self):
        if self.playlistcombobox.currentIndex() == -1:
            return
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
                
                response = request.execute()

                for s in response["items"]:
                    if s['snippet']['title'].lower() in ['deleted video', 'private video']:
                        continue
                    self.songlist.update({s['snippet']['title']:s['snippet']['resourceId']['videoId']})
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
        print(self.mediaplayer.get_state())
        print(self.mediaplayer.will_play())
        playlist = self.playlistcombobox.currentText()
        song = self.songlistview.currentItem().text()
        id = self.playlists[playlist]['playlistCache'][song]
        #self.queueBox.addItem(id)
        try:
            songstream = youtubefunc.ytdlpstuff.getAudioStream(id)
        except Exception as e:
            # pixmapi = getattr(QStyle.StandardPixmap, 'SP_MessageBoxWarning')
            # icon = self.style().standardIcon(pixmapi)
            print(e)
            #dlg = QMessageBox.warning(self, "Error!", e.__str__())
            return

        media = self.instance.media_new(songstream)
        self.mediaplayer.set_media(media)
        self.mediaplayer.play()

    def songlistViewSelectionChanged(self):
        pass
        # if self.songlistview.currentRow() == -1:
        #     return
        # playlist = self.playlistcombobox.currentText()
        # song = self.songlistview.currentItem().text()
        # id = self.playlists[playlist]['playlistCache'][song]
        # print(f"{id}")

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

