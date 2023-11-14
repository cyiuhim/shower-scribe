from pynput import keyboard 
from multiprocessing import Process
from workers.recorder import Recorder

import datetime
import sys
import os

print(Recorder)
def listen_for_input():
    while True:
        with keyboard.Events() as events:
            for event in events:
                if event.key == keyboard.Key.space:
                    print(event.key)
    
if __name__ == "__main__":
    p = Process(target=listen_for_input)
    p.start()
    p.join()

