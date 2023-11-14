#code for test recordings 

import sounddevice as sd 
from scipy.io.wavfile import write
import base64
import os
import os.path
from pathlib import Path

recordpath = "../webserver/userdata/recordings/psych.wav"

rate = 48000
duration = 40

def recording():
    testrecord = sd.rec(int(rate * duration), samplerate=rate, channels=2)
    sd.wait()
    write(recordpath, rate, testrecord)

recording()