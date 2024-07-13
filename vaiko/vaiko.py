import os
import sys

import vosk
from yaml.scanner import ScannerError

from PyQt6.QtCore import QFileSystemWatcher
from PyQt6.QtGui import QFontDatabase
from PyQt6.QtWidgets import QApplication, QMessageBox

from window import Window
from word_dict import gen_word_dict, read_word_file
from word_recognizer import WordRecognizer

WORD_FILE_PATH = os.path.join(sys.path[0], 'words.yaml')

class Vaiko:
    
    def __init__(self):
        self.curr_word = ''
        self.word_history = []

        # Place this before everything else so that any error dialogs can be
        # parented to it, and so that the dialogs would show up over it.
        self.window = Window()
        self.window.show()

        self.word_dict = self.load_word_dict()

        self.word_file_observer = QFileSystemWatcher()
        self.word_file_observer.addPath(WORD_FILE_PATH)
        self.word_file_observer.fileChanged.connect(self.handle_word_file_change)

        self.word_recognizer = WordRecognizer(self.word_dict.keys())
        self.word_recognizer.recognized.connect(self.handle_word_recognized)

        self.update_words_loaded_display()
        self.word_recognizer.start()
    
    def handle_exit(self):
        self.word_recognizer.stop()

    def handle_word_file_change(self, file_path):
        self.word_dict = self.load_word_dict()
        self.word_recognizer.update_keywords(self.word_dict.keys())

        self.curr_word = ''
        self.word_history = []

        self.update_words_loaded_display()

    def handle_word_recognized(self, words):
        # Vosk may end up bundling words together even when said apart, so
        # it's assumed in processing that they were said at roughly the same
        # time.
        for word in words:
            assert word in self.word_dict

            self.curr_word = word
            self.word_history.append(word)

            keystroke = self.word_dict[word]
            keystroke.invoke()

            self.window.main_display.detection = self.curr_word
            self.window.main_display.keystroke_value = keystroke.input_code
            self.window.history_display.update_keywords(self.word_history)

    def load_word_dict(self):
        try:
            return gen_word_dict(read_word_file(WORD_FILE_PATH))
        except ValueError:
            QMessageBox.warning(self.window, 'Warning!', 'Invalid keystroke value.')
        except ScannerError:
            QMessageBox.warning(self.window, 'Warning!', 'Word file parse error.')

        return {}

    def update_words_loaded_display(self):
        self.window.status_bar.status_text = f'{len(self.word_dict)} Words Loaded'

def main():
    # Disable initial logs printed by Vosk
    vosk.SetLogLevel(-1)

    app = QApplication(sys.argv)
    QFontDatabase.addApplicationFont('assets/font.ttf')

    vaiko = Vaiko()
    app.aboutToQuit.connect(vaiko.handle_exit)

    sys.exit(app.exec())