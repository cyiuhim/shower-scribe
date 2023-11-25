from recorder import Recorder
from time import sleep


def main():
    # initializes recorder
    recorder = Recorder(stereo=False)

    recorder.start_recording()
    sleep(2)  # when implementing this would be something like .on_button_press()
    # will save to ./recordings/test.wav
    recorder.save_recording("webserver/userdata/recordings", "test.wav")
    print("complete 1")

    # to demonstrate ability to do multiple recordings before resetting
    recorder.start_recording()
    sleep(3)
    recorder.save_recording("webserver/userdata/recordings", "test2.wav")
    print("complete 2")

    # to demonstrate what happens when you try to save without recording
    res = recorder.save_recording("webserver/userdata/recordings", "test3")
    print(f"fail 1: {res}")

    # closes the recorder
    recorder.terminate_interface()


if __name__ == "__main__":
    main()
