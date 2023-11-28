

import assemblyai
import multiprocessing as mp
import os
import sys
import uuid

GPIO_ON = True

# if test is in argv then set gpio to false
if len(sys.argv) > 1 and sys.argv[1] == "test":
    GPIO_ON = False

if GPIO_ON: 
    import RPi.GPIO as GPIO

from assemblyai import Transcriber
from dotenv import load_dotenv
from llm_services.cohere_interractions import full_resume_and_title
from multiprocessing import Process
from workers.recorder import Recorder
from sql_interface import *
from webserver.app import startup_webserver, user_settings
from vector_interface import add_vector_from_content

from datetime import datetime

class Conductor():

    recordings_directory = os.path.join(
        ".", "webserver", "userdata", "recordings")

    transcriptions_directory = os.path.join(
        ".", "webserver", "userdata", "texts")

    def __init__(self, BUTTON_PIN: int, LED_PIN: int):
        load_dotenv()
        # check that the api key is set
        if os.environ.get("ASSEMBLY_AI_KEY") == None:
            print("No AssemblyAI API key found. Please set the ASSEMBLY_AI_KEY environment variable.")
            exit()
        # check if cohere key is there
        if os.environ.get("COHERE_API_KEY") == None:
            print("No Cohere API key found. Please set the COHERE_API_KEY environment variable.")
            exit()
        
        assemblyai.settings.api_key = os.environ.get("ASSEMBLY_AI_KEY")

        self.worker_pool = mp.get_context("fork").Pool()
        self.BUTTON_PIN = BUTTON_PIN
        self.LED_PIN = LED_PIN
        if GPIO_ON:
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
                print(f"attempting to transcribe {recording_id}")
                self.worker_pool.apply_async(Conductor.create_transcription_worker,
                                             args=(text, recording_id),
                                             callback=self.transcription_callback,
                                             error_callback=self.transcription_error_callback
                                             )

        for recording_id in get_unresumed_recordings():
            print(f"attempting to resume {recording_id}")
            # run the ai thing
            if user_settings["resume"] == True:
                self.worker_pool.apply_async(Conductor.create_llm_worker,
                                            args=(recording_id))
                
        print("Shower Scribe is ready to go!")

    def listen_for_input(self):
        """
        Listen for keyboard input and orchestrate recording/transcription workers.

        """
        if not GPIO_ON:
            from pynput import keyboard
            with keyboard.Events() as events:
                for event in events:
                    if event.key == keyboard.Key.space and not self.recorder.is_recording:
                        self.recorder.start_recording()
                    if event.key == keyboard.Key.shift_l and self.recorder.is_recording:
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
        filename = f"recording_{uuid.uuid4()}.wav"
        status = self.recorder.save_recording(
            Conductor.recordings_directory, filename)
        print(f"Recorder saved with status {status}.")
        if status == 0:
            recording_id = add_recording(filename)
            if user_settings["transcription"] == True:
                print("attempting transcription.")
                self.worker_pool.apply_async(Conductor.create_transcription_worker,
                                            args=(filename, recording_id),
                                            callback=self.transcription_callback,
                                            error_callback=self.transcription_error_callback
                                            )
            else:
                print("transcription disabled")
            
        return not bool(status)

    @staticmethod
    def create_transcription_worker(audio_file: str, recording_id: int) -> tuple[str | None, int, str | None]:
        """
        Class method for creating transcriptions.
        """
        transcriber = Transcriber()
        transcription_audio_path = os.path.join(Conductor.recordings_directory, audio_file)
        transcript = transcriber.transcribe(transcription_audio_path)
        filename = f"transcription_{uuid.uuid4()}.txt"

        if transcript.text:
            with open(os.path.join(Conductor.transcriptions_directory, filename), "w") as f:
                f.write(transcript.text)
        return filename, recording_id, transcript.text

    @staticmethod
    def create_llm_worker(recording_id: int):
        full_resume_and_title(recording_id)

    def transcription_callback(self, data: tuple[str | None, int, str | None]):
        """
        Transcription callback.
        """
        filename, recording_id, transcript_text = data
        text_creation_dict = {
            "text_filename": filename,
            "display_name": f"Transcription of {recording_id}",
            "type": 0,
            "associated_recording_id": recording_id
        }
        print(f"Transcription received for recording {recording_id}")
        text_id = create_text_from_dict(text_creation_dict)
        if text_id is None:
            print("Error creating text")
            return
        update_recording_flag_transcribed(recording_id)
        add_vector_from_content(0, text_id, transcript_text)
        if user_settings["resume"] == True:
            Conductor.create_llm_worker(recording_id)
        else:
            print("Resume disabled")

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
    print("Starting Shower Scribe")
    conductor = Conductor(11, 18)
    while True:
        try:
            conductor.listen_for_input()
        except KeyboardInterrupt:
            print("Exiting...")
            conductor.clean()
            print("Shower Scribe has exited.")
            exit()
