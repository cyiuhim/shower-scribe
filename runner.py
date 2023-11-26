import assemblyai
import multiprocessing as mp
import os
import RPi.GPIO as GPIO
import sys
import uuid

from assemblyai import Transcriber
from dotenv import load_dotenv
#from pynput import keyboard
from llm_services.cohere_interractions import full_resume_and_title
from multiprocessing import Process
from workers.recorder import Recorder
from sql_interface import *
from webserver.app import startup_webserver, user_settings

from datetime import datetime


class Conductor():

    recordings_directory = os.path.join(
        ".", "webserver", "userdata", "recordings")

    transcriptions_directory = os.path.join(
        ".", "webserver", "userdata", "texts")

    def __init__(self, BUTTON_PIN: int, LED_PIN: int):
        load_dotenv()
        assemblyai.settings.api_key = os.environ.get("ASSEMBLY_AI_KEY")


        self.worker_pool = mp.Pool()
        self.BUTTON_PIN = BUTTON_PIN
        self.LED_PIN = LED_PIN
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(self.LED_PIN, GPIO.OUT)

        self.flask_server = Process(target=startup_webserver)
        self.flask_server.start()
        self.recorder = Recorder(stereo=False)

        for recording_id in get_untranscribed_recordings():
            # run the transcription thing which should then auto call the ai thing
            status, text = get_recording_path(recording_id)
            if status:
                self.worker_pool.apply_async(Conductor.create_transcription_worker,
                                             args=(os.path.join(
                                                 Conductor.recordings_directory, text), recording_id),
                                             callback=self.transcription_callback,
                                             error_callback=self.transcription_error_callback
                                             )

        for recording_id in get_unresumed_recordings():
            # run the ai thing
            self.worker_pool.apply_async(Conductor.create_llm_worker,
                                         args=(recording_id))

    def listen_for_input(self):
        """
        Listen for keyboard input and orchestrate recording/transcription workers.

        """
        if len(sys.argv) > |1 and sys.argv[1] == "test":
            with keyboard.Events() as events:
                for event in events:
                    if event.key == keyboard.Key.space and not self.recorder.is_recording:
                        GPIO.output(self.LED_PIN, GPIO.HIGH)
                        self.recorder.start_recording()
                    if event.key == keyboard.Key.shift_l and self.recorder.is_recording:
                        GPIO.output(self.LED_PIN, GPIO.LOW)
                        self.create_new_recording()
        else:
            if GPIO.input(self.BUTTON_PIN) and not self.recorder.is_recording:
                GPIO.output(self.LED_PIN, GPIO.HIGH)
                self.recorder.start_recording()
            if GPIO.input(self.BUTTON_PIN) == 0 and self.recorder.is_recording:
                GPIO.output(self.LED_PIN, GPIO.LOW)
                self.create_new_recording()

    def create_new_recording(self) -> bool:
        """
        Creates a new recording and returns True upon successful execution.
        """
        filename = f"resume_{uuid.uuid4()}.wav"
        status = self.recorder.save_recording(
            Conductor.recordings_directory, filename)
        print(f"Recorder saved with status {status}.")
        if status == 0:
            recording_id = add_recording(filename)
            print("attempting transcription.")
            self.worker_pool.apply_async(Conductor.create_transcription_worker,
                                         args=(filename, recording_id),
                                         callback=self.transcription_callback,
                                         error_callback=self.transcription_error_callback
                                         )
        return not bool(status)

    @staticmethod
    def create_transcription_worker(audio_file: str, recording_id: int) -> tuple[str | None, int]:
        """
        Class method for creating transcriptions.
        """
        transcriber = Transcriber()
        transcript = transcriber.transcribe(os.path.join(Conductor.recordings_directory, audio_file))
        filename = audio_file.replace(".wav", ".txt")

        if transcript.text:
            print(transcript.text)
            with open(os.path.join(Conductor.transcriptions_directory, filename), "w") as f:
                f.write(transcript.text)
        return filename, recording_id

    @staticmethod
    def create_llm_worker(recording_id: int):
        full_resume_and_title(recording_id)

    def transcription_callback(self, data: tuple[str | None, int]):
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
        print(text_creation_dict)

        print(create_text_from_dict(text_creation_dict))
        print(update_recording_flag_transcribed(recording_id))
        Conductor.create_llm_worker(recording_id)

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
        GPIO.cleanup()
        self.flask_server.join()


if __name__ == "__main__":
    conductor = Conductor(11, 18)
    while True:
        try:
            conductor.listen_for_input()
        except KeyboardInterrupt:
            print("Exiting")
            conductor.clean()
            exit()
