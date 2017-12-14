"""Module for performing basic processing on a stream of
audio coming in
"""
import time
import numpy as np
import librosa as lr

from AudioSource import AudioSource

DEFAULT_SR = 44100
GUITAR_NOTES = lr.hz_to_note(lr.cqt_frequencies(49, fmin=lr.note_to_hz('E2')))
RECORD_LENGTH = 100
MAG_THRESHOLD = 500

class AudioProcessor(object):
    def __init__(self, db):
        self._data = []
        self._prev_chunk_magnitude = 0
        self._chunk_magnitudes = []
        self._curr_note_token = []
        self._current_note_name = None
        self._note_index = 0
        self._note_started = False
        self._audio_source = AudioSource(data_callback=self._process_data)
        self._db = db

    def start_audio_capture(self):
        """start audio capture"""
        self._start_time = time.time()
        if not self._audio_source.stream_is_open():
            self._audio_source.open_stream()
        self._audio_source.listen()

    def stop_audio_capture(self):
        """stop listening to input device"""
        self._audio_source.stop_listening()
        self._audio_source.close_stream()
        self._audio_source.terminate()

    def _process_data(self, data):
        # there is a spike when the mic turns on
        # that messes with audio normalization
        if time.time() - self._start_time < 0.5:
            return

        clean_data = np.nan_to_num(np.fromstring(data, np.int16))
        chunk_magnitude = np.mean(abs(clean_data))

        # check for onset of note
        if not self._note_started and (chunk_magnitude - self._prev_chunk_magnitude) > 300:
            self._note_started = True

        # capture frames into note token
        if self._note_started and chunk_magnitude > MAG_THRESHOLD:
            self._curr_note_token.append(clean_data)
        elif self._note_started and chunk_magnitude < MAG_THRESHOLD:
            if len(self._curr_note_token) > 0:
                # compute constant-Q transform of note token
                shaped_token = np.hstack(self._curr_note_token).astype(dtype='float32')
                cqt = self.cqt(shaped_token)
                self._current_note_name = self.get_note(cqt)
                self._db.update({"current_note": self._current_note_name})
            self._curr_note_token = []
            self._note_started = False

        self._prev_chunk_magnitude = chunk_magnitude

        # self._data.append(clean_data)
        # self._chunk_magnitudes.append(chunk_magnitude)

    def cqt(self, data):
        # 5 octaves starting @ E2 = 82.407 Hz
        return lr.core.cqt(data, sr=DEFAULT_SR, hop_length=2048, fmin=lr.note_to_hz('E2'), n_bins=49)

    def get_note(self, cqt_data):
        magnitudes = []
        for freq in cqt_data:
            magnitudes.append(np.mean(abs(freq)))

        max_index = np.argmax(magnitudes)
        return GUITAR_NOTES[max_index]

    def get_data(self):
        """returns horizontal stack of clean data"""
        return np.hstack(self._data)