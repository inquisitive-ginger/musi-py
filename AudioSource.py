"""This module provides a simple interface
to the PyAudio library.
"""
import pyaudio

DEFAULT_SAMPLE_RATE = 44100
DEFAULT_SAMPLE_WIDTH = 2
DEFAULT_CHUNK_SIZE = 4096
DEFAULT_INPUT_NAME = 'Built-in Microphone' #'Scarlett 2i2 USB'

class AudioSource(object):
    """A class for managing an audio stream
    from an input device
    """
    def __init__(self, data_callback, sample_rate=DEFAULT_SAMPLE_RATE,
                 frames_per_buffer=DEFAULT_CHUNK_SIZE, device_name=DEFAULT_INPUT_NAME,
                 sample_width=DEFAULT_SAMPLE_WIDTH):
        self._data_callback = data_callback
        self._pyaudio_object = pyaudio.PyAudio()
        self._sample_rate = sample_rate
        self._channels = 1
        self._sample_width = sample_width
        self._audio_format = self._pyaudio_object.get_format_from_width(self._sample_width)
        self._chunk_size = frames_per_buffer
        self._audio_stream = None
        self._input_device = self._get_index_by_name(device_name)
        self._listening = False

    def _get_available_devices(self):
        """list available input devices"""
        devices = []
        for index in range(0, self._pyaudio_object.get_device_count()):
            devices.append(self._pyaudio_object.get_device_info_by_index(index))

        return devices

    def _get_index_by_name(self, name):
        """find specific input device"""
        available_devices = self._get_available_devices()
        for index, device in enumerate(available_devices):
            if device['name'] == name:
                return index

        return -1

    def _handle_stream_data(self, in_data, frame_count, time_info, status_flags):
        """pass-through for data coming in from device"""
        self._data_callback(in_data)
        return (None, pyaudio.paContinue)

    def stream_is_open(self):
        """_audio_stream has been assigned"""
        return self._audio_stream is not None

    def open_stream(self):
        """open audio stream with given parameters"""
        print 'Opening stream...'
        self._audio_stream = self._pyaudio_object.open(rate=self._sample_rate,
                                                       channels=self._channels,
                                                       format=self._audio_format,
                                                       input=True,
                                                       output=False,
                                                       input_device_index=self._input_device,
                                                       frames_per_buffer=self._chunk_size,
                                                       stream_callback=self._handle_stream_data)

    def listen(self):
        """start the stream"""
        print 'Starting stream...'
        self._listening = True
        self._audio_stream.start_stream()

    def stop_listening(self):
        """stop the stream"""
        print 'Stopping stream...'
        self._listening = False
        self._audio_stream.stop_stream()

    def close_stream(self):
        """shut down stream, must call open_stream()
        to start it again.
        """
        print 'Closing stream...'
        if self._audio_stream is not None:
            self._audio_stream.close()
            self._audio_stream = None

    def terminate(self):
        self._pyaudio_object.terminate()
