import assemblyai as aai
import base64
import os
import os.path
from pathlib import Path

# rate = 48000
# duration = 5 # the conductor will set the duration by button control

recordpath = "../webserver/userdata/recordings/example-prof2.wav" # use relative paths, not absolute paths, and use them through the os module. because this will only work on your machine. it would be something like "../webserver/userdata/recordings/test.wav"

# def recording():
#     testrecord = sd.rec(int(rate * duration), samplerate=rate, channels=2)
#     sd.wait()
#     write(recordpath, rate, testrecord)

transcriber = aai.Transcriber()
transcript = transcriber.transcribe(recordpath) #TODO: INSERT PATH FOR AUDIO FILE 

print(transcript.text)