import json
from queue import Queue

import sounddevice as sd
import vosk

from PyQt6.QtCore import pyqtSignal, pyqtSlot, QThread

def get_keyword_str(keywords):
    if len(keywords) == 0:
        return '[""]'

    keyword_str = '['

    for i, phrase in enumerate(keywords):
        if i < len(keywords) - 1:
            keyword_str += f'"{phrase}",'
        else:
            keyword_str += f'"{phrase}"]'

    return keyword_str

class WordRecognizer(QThread):

    # Pass in `object` to allow the spotted keywords array to be passed through the signal.
    recognized = pyqtSignal(object)

    def __init__(self, keywords):
        super().__init__()

        self.input_data = Queue()
        self.input_device = sd.default.device

        self.model = vosk.Model(lang="en-us")
        self.recognizer = vosk.KaldiRecognizer(self.model, self.sample_rate, get_keyword_str(keywords))

        # SetPartialWords() should break down the words in the partial result (
        # i.e. no more manual string processing) and provide more information on
        # each word. However, using it seems to stop detection altogether...
        #
        # self.recognizer.SetPartialWords(True)

        self.running = False
        self.prev_partial_res = ''

    @property
    def sample_rate(self):
        device_info = sd.query_devices(self.input_device, 'input')
        return int(device_info['default_samplerate'])

    def handle_input_data_received(self, indata, frames, time, status):
        self.input_data.put(bytes(indata))

    @pyqtSlot()
    def run(self):
        with sd.RawInputStream(
            device=self.input_device, 
            channels=1, 
            samplerate=self.sample_rate, 
            dtype='int16',
            callback=self.handle_input_data_received
        ):
            while self.running:
                # Explanation:
                #
                # Vosk works by feeding audio data to the recognizer until it is able to
                # finish processing it (finds its "endpoint"). Until then, it stores the
                # words it has recognized into the partial result string (all words in one
                # string). While the recognizer can be constrained on a set of keywords, 
                # Vosk does not inherently support keyword spotting.
                #
                # Attemping to obtain a result (i.e. via recognizer.Result()) without the 
                # recognizer saying that its processing is finished (i.e. 
                # recognizer.AcceptWaveform() has not returned True) to isolate each result
                # to a single keyword can produce false positives, at least for keyword 
                # spotting. So something like this can produce false results:
                #
                #   # Add waveform data to buffer
                #   recognizer.AcceptWaveform(data)
                #
                #   # Force a result even if no "endpoint" detected
                #   print(recognizer.Result())
                #
                # This is why keyword spotting needs to occur by looking at the partial
                # results (i.e. via recognizer.PartialResult()), as the proper Vosk flow
                # is followed. However, as the partial result can end up a phrase of words
                # if many words are said in quick succession, the partial results have to
                # be diffed to determine the latest said keyword.

                audio_data = self.input_data.get()

                # Add waveform data to recognizer's buffer. 
                # If the audio "endpoint" is found:
                if self.recognizer.AcceptWaveform(audio_data):
                    # Acknowledge the result and empty the recognizer's buffer so that the
                    # next set of words can be recognized properly.
                    #
                    # The result is an aggregate of the partial results (i.e. a phrase)
                    # returned at one time so this can't be used for realtime keyword 
                    # spotting.
                    self.recognizer.Result()
                    self.prev_partial_res = ''
                
                # Perform keyword spotting from the partial results:
                else:
                    # recognizer.PartialResult() returns a JSON string of the result.
                    # Just to be safe, let's use a JSON parser even if it's slower.
                    curr_partial_res = json.loads(self.recognizer.PartialResult())['partial']
                    
                    if len(curr_partial_res) == 0 or self.prev_partial_res == curr_partial_res: 
                        continue

                    # Vosk may end up changing the last word in the partial results if
                    # it felt that another word better fit the audio data. Since this happens
                    # only while the user is in the process of talking, assume it to be
                    # another detection. This means that the string diffing is based on the
                    # string length (i.e. content-based) rather than space count (delimiter
                    # -based).
                    slice_index = curr_partial_res.rfind(' ')

                    # Vosk bunches up keywords together if they are said in a fast enough
                    # succession. In such a case, consider all those keywords to have been
                    # said at the same time.
                    #
                    # The timestamp data for each word is seemingly stored by Vosk though
                    # when printing the result with recognizer.SetWords(True), so a fork
                    # of Vosk could be made to simplify this loop and isolate each word.
                    latest_words = curr_partial_res[slice_index + 1:].split(' ')
                    self.recognized.emit(latest_words)
                    
                    self.prev_partial_res = curr_partial_res

    def start(self, priority = QThread.Priority.InheritPriority):
        self.running = True
        super().start(priority)

    def stop(self):
        self.running = False

    def update_keywords(self, keywords):
        self.recognizer = vosk.KaldiRecognizer(self.model, self.sample_rate, get_keyword_str(keywords))