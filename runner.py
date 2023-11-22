import assemblyai
import multiprocessing as mp

from assemblyai import Transcriber
from dotenv import load_dotenv
from pynput import keyboard 
from multiprocessing import Process
from workers.recorder import Recorder
from webserver.app import startup_webserver

from datetime import datetime
import sys
import os


class Conductor():
    def __init__(self):
        load_dotenv()
        assemblyai.settings.api_key = os.environ.get("ASSEMBLY_AI_KEY")

        self.recordings_directory = os.path.join(".","webserver","userdata","recordings")
        self.transcriptions_directory = os.path.join(".","webserver","userdata","texts")

        self.worker_pool = mp.Pool()
        
        self.flask_server = Process(target=startup_webserver)
        self.flask_server.start()


    def listen_for_input(self):
        recorder = Recorder(stereo=False)
        while True:
            with keyboard.Events() as events:
                for event in events:
                    if event.key == keyboard.Key.space and not recorder.is_recording:
                        recorder.start_recording()
                    if event.key == keyboard.Key.shift_l and recorder.is_recording:
                        filename = datetime.now().strftime("recording-%Y-%m-%d-%H-%M.wav")
                        status = recorder.save_recording(self.recordings_directory, filename)
                        print(f"Recorder saved with status {status}.")
                        if status == 0:
                            print("attempting transcription.")
                            self.worker_pool.apply_async(Conductor.create_transcription_worker,
                                                         args=(os.path.join(self.recordings_directory, filename),),
                                                         callback=self.transcription_callback,
                                                         error_callback=self.transcription_error_callback
                                                         )
    @staticmethod
    def create_transcription_worker(audio_file: str) -> str | None:
        with open("debug.txt", "w") as f:
            f.write("pissssss")
        transcriber = Transcriber()
        transcript = transcriber.transcribe(audio_file)
        filename = audio_file.replace(".wav",".txt").replace("recordings", "texts")
        if transcript.text:
            with open(filename, "w") as f:
                f.write(transcript.text)
        return transcript.text

    def transcription_callback(self, data):
        print(data)

    def transcription_error_callback(self, data):
        with open("debug.txt", "w") as f:
            f.write("BONGOBONGBOBGO")
            f.write(f"Test garbage: Unsuccessful execution of transcription function: {data}.")
        print(f"Test garbage: Unsuccessful execution of transcription function: {data}.")

    def clean(self):
        self.flask_server.join()



if __name__ == "__main__":
    conductor = Conductor()
    while True:
        try:
            conductor.listen_for_input()
        except KeyboardInterrupt:
            conductor.clean()
            exit()


