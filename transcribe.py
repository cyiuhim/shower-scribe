import assemblyai as aai
import sounddevice as sd
from scipy.io.wavfile import write
import base64
import os
import os.path
from pathlib import Path

rate = 48000
duration = 5

aai.settings.api_key = f"91b2eda6b5b3474289b0649020d9245b"

recordpath = "D:/coding/showerscribe/recordings/test.wav"

def recording():
    
    testrecord = sd.rec(int(rate * duration), samplerate=rate, channels=2)
    sd.wait()
    write(recordpath, rate, testrecord)

transcriber = aai.Transcriber()
transcript = transcriber.transcribe(recordpath) #TODO: INSERT PATH FOR AUDIO FILE 

print(transcript.text)