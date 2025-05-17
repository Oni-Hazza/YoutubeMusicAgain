from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QTextEdit, QHBoxLayout, 
                            QCheckBox, QPushButton, QLabel)
from PyQt6.QtCore import Qt, QRegularExpression
from PyQt6.QtGui import QTextCursor, QTextCharFormat, QSyntaxHighlighter
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

class CombinedErrorLog(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        
        # Control panel
        self.control_panel = QWidget()
        control_layout = QHBoxLayout(self.control_panel)
        control_layout.setContentsMargins(0, 0, 0, 0)
        
        # Filter controls
        control_layout.addWidget(QLabel("Filter:"))
        
        self.error_check = QCheckBox("Errors")
        self.error_check.setChecked(True)
        self.error_check.toggled.connect(self.update_filters)
        control_layout.addWidget(self.error_check)
        
        self.warning_check = QCheckBox("Warnings")
        self.warning_check.setChecked(True)
        self.warning_check.toggled.connect(self.update_filters)
        control_layout.addWidget(self.warning_check)
        
        self.info_check = QCheckBox("Info")
        self.info_check.setChecked(True)
        self.info_check.toggled.connect(self.update_filters)
        control_layout.addWidget(self.info_check)
        
        self.debug_check = QCheckBox("Debug")
        self.debug_check.setChecked(False)
        self.debug_check.toggled.connect(self.update_filters)
        control_layout.addWidget(self.debug_check)
        
        # Spacer and clear button
        control_layout.addStretch()
        
        self.clear_btn = QPushButton("Clear Log")
        self.clear_btn.clicked.connect(self.clear_log)
        control_layout.addWidget(self.clear_btn)
        
        # Log display
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        self.log_display.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                font-family: Consolas, monospace;
                font-size: 10pt;
                border: 1px solid #3c3c3c;
            }
        """)
        self.highlighter = LogHighlighter(self.log_display.document())
        
        # Add widgets to main layout
        layout.addWidget(self.control_panel)
        layout.addWidget(self.log_display)
        
        # Log storage and settings
        self.all_messages = []
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
        self.log_display.clear()
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
                
                self.log_display.setTextColor(color)
                self.log_display.append(msg['formatted'])
                
        self.log_display.ensureCursorVisible()
        
    def update_filters(self):
        self.show_errors = self.error_check.isChecked()
        self.show_warnings = self.warning_check.isChecked()
        self.show_info = self.info_check.isChecked()
        self.show_debug = self.debug_check.isChecked()
        self._apply_filters()
        
    def clear_log(self):
        self.all_messages = []
        self.log_display.clear()
        
    # Convenience methods
    def error(self, message): self.append_message("ERROR", message)
    def warning(self, message): self.append_message("WARNING", message)
    def info(self, message): self.append_message("INFO", message)
    def debug(self, message): self.append_message("DEBUG", message)