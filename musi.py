"""
program for capturing audio from a guitar,
doing a bit of DSP on it to determine notes
being played and then interfacing with a front-end
web application that provides feedback to the user
"""
import time
from firebase import get_firebase_ref
from AudioProcessor import AudioProcessor

FIREBASE_REF = get_firebase_ref()

def main():
    audio_processor = AudioProcessor(db=FIREBASE_REF)
    audio_processor.start_audio_capture()
    while True:
        time.sleep(0.1)
    audio_processor.stop_audio_capture()

if __name__ == '__main__': 
    main()
