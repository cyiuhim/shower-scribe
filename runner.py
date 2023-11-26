import assemblyai
import multiprocessing as mp
import os

from assemblyai import Transcriber
from dotenv import load_dotenv
from pynput import keyboard 
from multiprocessing import Process
from workers.recorder import Recorder
from webserver.app import startup_webserver
import uuid
from sql_interface import add_recording, create_text_from_dict

from datetime import datetime


class Conductor():
    def __init__(self):
        load_dotenv()
        assemblyai.settings.api_key = os.environ.get("ASSEMBLY_AI_KEY")

        self.recordings_directory = os.path.join(".","webserver","userdata","recordings")
        self.transcriptions_directory = os.path.join(".","webserver","userdata","texts")

        self.worker_pool = mp.Pool()
        
        self.flask_server = Process(target=startup_webserver)
        self.flask_server.start()
        self.recorder = Recorder(stereo=False)


    def listen_for_input(self):
        """
        Listen for keyboard input and orchestrate recording/transcription workers.

        """
        with keyboard.Events() as events:
            for event in events:
                if event.key == keyboard.Key.space and not self.recorder.is_recording:
                    self.recorder.start_recording()
                if event.key == keyboard.Key.shift_l and self.recorder.is_recording:
                    filename = f"resume_{uuid.uuid4()}.wav"
                    status = self.recorder.save_recording(self.recordings_directory, filename)
                    print(f"Recorder saved with status {status}.")
                    if status == 0:
                        recording_id = add_recording(filename)
                        print("attempting transcription.")
                        self.worker_pool.apply_async(Conductor.create_transcription_worker,
                                                     args=(os.path.join(self.recordings_directory, filename), recording_id),
                                                     callback=self.transcription_callback,
                                                     error_callback=self.transcription_error_callback
                                                     )

    @staticmethod
    def create_transcription_worker(audio_file: str, recording_id: str) -> tuple[str | None, str]:
        """
        Class method for creating transcriptions.
        """
        transcriber = Transcriber()
        transcript = transcriber.transcribe(audio_file)
        filename = audio_file.replace(".wav",".txt").replace("recordings", "texts")
        if transcript.text:
            with open(filename, "w") as f:
                f.write(transcript.text)
        return filename, recording_id

    def transcription_callback(self, data: tuple[str | None, str]):
        """
        Transcription callback.
        """
        filename, recording_id = data
        text_creation_dict = {
                "text_filename": filename,
                "display_name": f"Transcription of {recording_id}",
                "type": 0,
                "associated_recording_id": recording_id
                }
        
        create_text_from_dict(text_creation_dict)

    def transcription_error_callback(self, data):
        """
        Runs upon transcription failure.
        """
        print("Transcription failure")

    def clean(self):
        """
        Runs upon conductor cleanup.
        """
        self.recorder.terminate_interface()
        self.flask_server.join()


if __name__ == "__main__":
    conductor = Conductor()
    while True:
        try:
            conductor.listen_for_input()
        except KeyboardInterrupt:
            print("Exiting")
            conductor.clean()
            exit()


