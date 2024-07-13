from PyQt6.QtCore import Qt, QPropertyAnimation
from PyQt6.QtWidgets import (
    QGraphicsOpacityEffect, 
    QHBoxLayout,
    QLabel, 
    QMainWindow, 
    QStatusBar, 
    QVBoxLayout,
    QWidget
)

# Will place styles here for now to make life easier
STYLESHEET = """
    QLabel {
        color: white;
        font-family: "Wix Madefor Display", sans-serif;
        font-size: 14px;
    }

    /* For pop-up dialogs */
    QMessageBox QLabel {
        color: black;
    }

    QMainWindow {
        background-color: qradialgradient(
            cx: 0.5, cy: 0.5, radius: 0.5, fx: 0.5, fy: 0.5, 
            stop: 0 #201330, stop: 1 #070813);
    }

    QStatusBar {
        background-color: #4D4D4D;
        min-height: 0;
        margin: 0;
        padding: 0;
    }

    QStatusBar::item {
        /* Remove the divider after the status_label. */
        border: None;
    }

    .detected_word {
        font-size: 42px;
        font-weight: bold;
    }

    .history_word {
        font-weight: bold;
    }

    .keystroke_heading {
        font-size: 18px;
    }

    .keystroke_label {
        font-size: 18px;
        font-weight: bold;

        padding: 1px 5px;
        background-color: #4D4D4D; 
        border-radius: 3px; 
    }

    .status_label {
        font-size: 10px;
    }
"""

class Window(QMainWindow):

    def __init__(self):
        super().__init__()

        self.closeEvent

        self.setFixedSize(340, 240)
        self.setWindowTitle('vaiko')
        self.setStyleSheet(STYLESHEET)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        layout.setSpacing(30)

        self.main_cont = QWidget()
        self.main_cont.setLayout(layout)
        self.setCentralWidget(self.main_cont)

        self.main_display = MainDisplay()
        layout.addWidget(self.main_display, alignment=Qt.AlignmentFlag.AlignCenter)

        self.history_display = HistoryDisplay()
        layout.addWidget(self.history_display, alignment=Qt.AlignmentFlag.AlignCenter)

        self.status_bar = StatusBar()
        self.setStatusBar(self.status_bar)

class MainDisplay(QWidget):

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        layout.setSpacing(10)
        self.setLayout(layout)

        self.latest_detection = DetectionDisplay()
        layout.addWidget(self.latest_detection)

        self.latest_keystroke = KeystrokeDisplay()
        layout.addWidget(self.latest_keystroke)

    @property
    def detection(self):
        return self.latest_detection.word
    
    @detection.setter
    def detection(self, v):
        self.latest_detection.word = v
        
    @property
    def keystroke_value(self):
        return self.latest_keystroke.keystroke_value

    @keystroke_value.setter
    def keystroke_value(self, v):
        self.latest_keystroke.keystroke_value = v

class DetectionDisplay(QWidget):

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setLayout(layout)

        self.heading = QLabel('Latest Detected Word')
        layout.addWidget(self.heading, alignment=Qt.AlignmentFlag.AlignCenter)

        self.word_label = QLabel('')
        self.word_label.setProperty('class', 'detected_word')
        layout.addWidget(self.word_label, alignment=Qt.AlignmentFlag.AlignCenter)

        self.word_label_opacity = QGraphicsOpacityEffect()
        self.word_label.setGraphicsEffect(self.word_label_opacity)

        self.word_label_fade = QPropertyAnimation(self.word_label_opacity, b'opacity')
        self.word_label_fade.setStartValue(0)
        self.word_label_fade.setEndValue(1)
        self.word_label_fade.setDuration(100)

    @property
    def word(self):
        return self.word_label.text()
    
    @word.setter
    def word(self, v):
        self.word_label.setText(v)
        self.word_label_fade.start()

class KeystrokeDisplay(QWidget):

    def __init__(self):
        super().__init__()

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(10)
        self.setLayout(layout)

        self.heading = QLabel('Keystroke:')
        self.heading.setProperty('class', 'keystroke_heading')
        layout.addWidget(self.heading)

        self.keystroke_label = QLabel('')
        self.keystroke_label.setProperty('class', 'keystroke_label')
        self.keystroke_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.keystroke_label)

        self.keystroke_label_opacity = QGraphicsOpacityEffect(opacity = 0)
        self.keystroke_label.setGraphicsEffect(self.keystroke_label_opacity)

        self.keystroke_label_fade = QPropertyAnimation(self.keystroke_label_opacity, b'opacity')
        self.keystroke_label_fade.setStartValue(0)
        self.keystroke_label_fade.setEndValue(1)
        self.keystroke_label_fade.setDuration(100)

    @property
    def keystroke_value(self):
        return self.keystroke_label.text()
    
    @keystroke_value.setter
    def keystroke_value(self, v):
        self.keystroke_label.setText(v)
        self.keystroke_label_fade.start()

class HistoryDisplay(QWidget):

    def __init__(self):
        super().__init__()

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        self.setLayout(layout)

        self.heading = QLabel('History:')
        layout.addWidget(self.heading)

        self.keyword_labels = [
            QLabel(''),
            QLabel(''),
            QLabel(''),
            QLabel('')
        ]

        for label in self.keyword_labels:
            label.setProperty('class', 'history_word')
            layout.addWidget(label)

    def update_keywords(self, keywords):
        to_display = keywords[-len(self.keyword_labels):]

        for i, label in enumerate(self.keyword_labels):
            text = to_display[i] if i < len(to_display) else ''
            label.setText(text)

class StatusBar(QStatusBar):

    def __init__(self):
        super().__init__()

        # Note that QStatusBar has some default, unremovable margin.
        self.setContentsMargins(15, 0, 15, 0)
        self.setGraphicsEffect(QGraphicsOpacityEffect(opacity=0.5))
        self.setSizeGripEnabled(False)

        self.status_label = QLabel('')
        self.status_label.setProperty('class', 'status_label')
        self.addWidget(self.status_label)

    @property
    def status_text(self):
        return self.status_label.text()
    
    @status_text.setter
    def status_text(self, v):
        self.status_label.setText(v)