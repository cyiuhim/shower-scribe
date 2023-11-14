import assemblyai as aai
import base64
import os
import os.path
from pathlib import Path

rate = 48000
duration = 5

#aai.settings.api_key = f"91b2eda6b5b3474289b0649020d9245b" # make sure to not hard code environment variables, instead we're using a .env file that'll be managed by the director. for now this is fine but we'll have to reset the key

recordpath = "../webserver/userdata/recordings/talking_test.wav" # use relative paths, not absolute paths, and use them through the os module. because this will only work on your machine. it would be something like "../webserver/userdata/recordings/test.wav"

# def recording():
#     testrecord = sd.rec(int(rate * duration), samplerate=rate, channels=2)
#     sd.wait()
#     write(recordpath, rate, testrecord)

transcriber = aai.Transcriber()
transcript = transcriber.transcribe(recordpath) #TODO: INSERT PATH FOR AUDIO FILE 

print(transcript.text)