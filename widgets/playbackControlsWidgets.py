from PyQt6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QPushButton, 
                            QSlider, QLabel, QFileDialog)
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtCore import QUrl, Qt, QTimer
from PyQt6.QtGui import QIcon

class PlaybackControls(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        self.progress_slider = QSlider(Qt.Orientation.Horizontal)
        self.progress_slider.setRange(0, 100)
        self.progress_slider.setToolTip("Position")
        layout.addWidget(self.progress_slider)

        control_layout = QHBoxLayout()

        self.volume_slider = QSlider()
        self.volume_slider.setToolTip("Volume")
        self.volume_slider.setMinimumHeight(70)
        self.volume_slider.setMaximum(100)
        self.volume_slider.setValue(50)
        control_layout.addWidget(self.volume_slider)

        self.play_button = QPushButton()
        self.play_button.setToolTip("Play/Pause")
        self.play_button.setMaximumHeight(100)
        self.play_button.setIcon(QIcon.fromTheme("media-playback-start"))
        control_layout.addWidget(self.play_button)

        self.stop_button = QPushButton()
        self.stop_button.setToolTip("Stop playback")
        self.stop_button.setMaximumHeight(100)
        self.stop_button.setIcon(QIcon.fromTheme("media-playback-stop"))
        control_layout.addWidget(self.stop_button)

        self.skip_button = QPushButton()
        self.skip_button.setToolTip("Skip to next track")
        self.skip_button.setMaximumHeight(100)
        self.skip_button.setIcon(QIcon.fromTheme("media-seek-forward"))
        control_layout.addWidget(self.skip_button)

        layout.addLayout(control_layout)