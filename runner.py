from pynput import keyboard 
from multiprocessing import Process
from workers.recorder import Recorder
from webserver.app import startup_webserver

from datetime import datetime
import sys
import os


def listen_for_input():
    recorder = Recorder(stereo=False)
    while True:
        with keyboard.Events() as events:
            for event in events:
                if event.key == keyboard.Key.space and not recorder.is_recording:
                    recorder.start_recording()
                if event.key == keyboard.Key.shift_l and recorder.is_recording:
                    status = recorder.save_recording("./webserver/userdata/recordings", datetime.now().strftime("recording-%Y-%m-%d-%H-%m-%s.wav"))
                    print(status)
                    is_listening = False
    
if __name__ == "__main__":
    p = Process(target=listen_for_input)
    p.start()
    flask_server = Process(target=startup_webserver)
    flask_server.start()
    p.join()
    flask_server.join()

