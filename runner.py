from pynput import keyboard 
from multiprocessing import Process
from workers.recorder import Recorder

from datetime import datetime
import sys
import os

def listen_for_input():
    is_listening = False
    recorder = Recorder(stereo=False)
    while True:
        with keyboard.Events() as events:
            for event in events:
                if event.key == keyboard.Key.space and not is_listening:
                    recorder.start_recording()
                    is_listening = True
                if event.key == keyboard.Key.shift_l and is_listening:
                    status = recorder.save_recording("./webserver/userdata/recordings", datetime.now().strftime("recording-%Y-%m-%d-%H-%m-%s.wav"))
                    print(status)
                    is_listening = False
    
if __name__ == "__main__":
    p = Process(target=listen_for_input)
    p.start()
    p.join()

