import pyaudio
import wave
import threading
from os import path


class Recorder:
    def __init__(self, chunk_size=1024, stereo=True, sample_rate=44100) -> None:
        """
            @brief Recorder is responsible for recoding audio from the microphone and
            saves the recorded audio to a .wav file.

            recorder is initialized with:

            @param chunk_size
            The size of recorded audio chunks in bytes. Chunks are spliced together
            when the file is being saved.
            Default to 1024 bytes.

            @param stereo
            When True, the recording will treat the volume of left and right channels
            Independantly. Otherwise the channels will be at the same volume(Mono).
            Default to True.

            @param sample_rate
            The sample rate of the recording in Hz
        """
        self.chunk_size: int = chunk_size
        self.audio_format: int = pyaudio.paInt16
        self.channels: int = 2 if stereo else 1  # number of output channels
        self.sample_rate: int = sample_rate
        self.__interface: pyaudio.PyAudio = pyaudio.PyAudio()  # PyAudio Interface
        self.sample_width = self.__interface.get_sample_size(self.audio_format)
        # List where chunks of audio are stored
        self.__frames: list[bytes] = []
        self.is_recording: bool = False  # Recording status
        self.recorder_thread = None # thread for recording, used to kill thread
        self.recording_stream = None # stream for recording, used to kill stream

    def start_recording(self) -> None:
        """
            @brief start_recording creates a thread for
            __start_recording_logic and calls the function
            check description of __start_recording_logic
            to learn more about it's purpose.
        """
        self.recorder_thread = threading.Thread(
            target=self.__start_recording_logic, name="Recorder")
        self.recorder_thread.start()

    def __start_recording_logic(self) -> None:
        """
            @brief start_recording_logic creates a pyaudio stream and starts sending 
            data to the stream. Once chunk is full it is added to frames.
            is_recording is set to True when called.
        """
        self.is_recording = True
        self.recording_stream = self.__interface.open(format=self.audio_format,
                                       channels=self.channels,
                                       rate=self.sample_rate,
                                       input=True,
                                       frames_per_buffer=self.chunk_size)

        # Recording the audio
        try:
            while self.is_recording:
                data: bytes = self.recording_stream.read(self.chunk_size)
                self.__frames.append(data)
        except Exception as e:
            print("Something has gone wrong")
            print(str(e))
            
        self.recording_stream.stop_stream()
        self.recording_stream.close()
        

    def save_recording(self, directory: str, filename: str) -> int:
        """
            @brief save_recording stops the recording stared by
            start_recording and saves to a file

            @param directory, the folder where the user
            wants to save the audio too. Also accepts subfolders
            ex. directory="folder/subfolder"

            @param filename, the name of the file the user
            want to save the audio too. Must end in .wav

            @return 0 if file is saved properly;
            1 if audio could not be saved to file;
            -1 if the program isn't recording
        """
        if not self.is_recording:
            return -1

        # checks if file has correct file extention
        if filename[-4:] != ".wav":
            print(f"Incorrect or missing file extention for {filename}, make sure to end with .wav")
            return 1
        
        self.is_recording = False  # tells the thread to stop recording
        self.recorder_thread.join()  # waits for thread to finish by itself

        # creates a path to a file in the form ../$directory/$filename
        path_home: str = "./"
        file_path: str = path.join(path_home, directory, filename)

        # configuring the file
        try:
            with wave.open(file_path, "wb") as wave_file:
                wave_file.setnchannels(self.channels)
                wave_file.setsampwidth(self.sample_width)
                wave_file.setframerate(self.sample_rate)
                # writing to the file
                wave_file.writeframes(b''.join(self.__frames))
        
        except Exception as e:
            print(f"Can't create file: {filename}, make sure the path exists")
            print(e)
            return 1

        self.__frames = []  # reseting frames

        return 0

    def terminate_interface(self):
        """
            @brief to be called one recorder has served it's purpose
        """
        self.__interface.terminate()
