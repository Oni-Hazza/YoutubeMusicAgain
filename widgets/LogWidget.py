from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt, QRegularExpression
from PyQt6.QtGui import (QTextCursor, QTextCharFormat, 
                        QSyntaxHighlighter, QTextDocument)
from datetime import datetime

class LogHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)
        self.highlighting_rules = []
        
        error_format = QTextCharFormat()
        error_format.setForeground(Qt.GlobalColor.red)
        self.highlighting_rules.append(
            (QRegularExpression(r"\[.*\] ERROR: .*"), error_format)
        )
        
        warning_format = QTextCharFormat()
        warning_format.setForeground(Qt.GlobalColor.yellow)
        self.highlighting_rules.append(
            (QRegularExpression(r"\[.*\] WARNING: .*"), warning_format)
        )
        
        debug_format = QTextCharFormat()
        debug_format.setForeground(Qt.GlobalColor.cyan)
        self.highlighting_rules.append(
            (QRegularExpression(r"\[.*\] DEBUG: .*"), debug_format)
        )
        
    def highlightBlock(self, text):
        for pattern, format in self.highlighting_rules:
            match_iterator = pattern.globalMatch(text)
            while match_iterator.hasNext():
                match = match_iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), format)

class ErrorLog(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.all_messages = []
        
    def setup_ui(self):
        self.setReadOnly(True)
        self.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        self.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                font-family: Consolas, monospace;
                font-size: 10pt;
                border: 1px solid #3c3c3c;
            }
        """)
        self.highlighter = LogHighlighter(self.document())
        
        # Default filter settings
        self.show_errors = True
        self.show_warnings = True
        self.show_info = True
        self.show_debug = False
        
    def append_message(self, message_type, message):
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        formatted_message = f"[{timestamp}] {message_type}: {message}"
        
        self.all_messages.append({
            'type': message_type,
            'text': message,
            'timestamp': timestamp,
            'formatted': formatted_message
        })
        
        self._apply_filters()
        
    def _apply_filters(self):
        self.clear()
        for msg in self.all_messages:
            if ((msg['type'] == "ERROR" and self.show_errors) or
                (msg['type'] == "WARNING" and self.show_warnings) or
                (msg['type'] == "INFO" and self.show_info) or
                (msg['type'] == "DEBUG" and self.show_debug)):
                
                color = {
                    "ERROR": Qt.GlobalColor.red,
                    "WARNING": Qt.GlobalColor.yellow,
                    "DEBUG": Qt.GlobalColor.cyan
                }.get(msg['type'], Qt.GlobalColor.white)
                
                self.setTextColor(color)
                self.append(msg['formatted'])
                
        self.ensureCursorVisible()
        
    def set_filters(self, errors=True, warnings=True, info=True, debug=False):
        self.show_errors = errors
        self.show_warnings = warnings
        self.show_info = info
        self.show_debug = debug
        self._apply_filters()
        
    def error(self, message): self.append_message("ERROR", message)
    def warning(self, message): self.append_message("WARNING", message)
    def info(self, message): self.append_message("INFO", message)
    def debug(self, message): self.append_message("DEBUG", message)

class LogControls(QWidget):
    def __init__(self, log_widget, parent=None):
        super().__init__(parent)
        self.log = log_widget
        self.setup_ui()
        
    def setup_ui(self):
        layout = QHBoxLayout()
        
        self.error_check = QCheckBox("Errors")
        self.error_check.setChecked(True)
        self.error_check.toggled.connect(lambda: self.update_filters())
        
        self.warning_check = QCheckBox("Warnings")
        self.warning_check.setChecked(True)
        self.warning_check.toggled.connect(lambda: self.update_filters())
        
        self.info_check = QCheckBox("Info")
        self.info_check.setChecked(True)
        self.info_check.toggled.connect(lambda: self.update_filters())
        
        self.debug_check = QCheckBox("Debug")
        self.debug_check.setChecked(False)
        self.debug_check.toggled.connect(lambda: self.update_filters())
        
        self.clear_btn = QPushButton("Clear Log")
        self.clear_btn.clicked.connect(self.log.clear)
        
        layout.addWidget(QLabel("Filter:"))
        layout.addWidget(self.error_check)
        layout.addWidget(self.warning_check)
        layout.addWidget(self.info_check)
        layout.addWidget(self.debug_check)
        layout.addStretch()
        layout.addWidget(self.clear_btn)
        
        self.setLayout(layout)
        
    def update_filters(self):
        self.log.set_filters(
            self.error_check.isChecked(),
            self.warning_check.isChecked(),
            self.info_check.isChecked(),
            self.debug_check.isChecked()
        )