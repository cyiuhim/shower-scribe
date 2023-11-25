from recorder import Recorder
from button_handler import ButtonHandler


def main():
    # initializes recorder
    recorder = Recorder(stereo=False)
    button_handler = ButtonHandler(0)

    try:
        while True:
            # starts recording when button is pressed
            if button_handler.is_pressed and not recorder.is_recording:
                recorder.start_recording()

            # stops recording when button is released
            if not button_handler.is_pressed and recorder.is_recording:
                recorder.save_recording("workers", "test.wav")

    except KeyboardInterrupt:
        recorder.terminate_interface()
        button_handler.terminate_interface()


if __name__ == "__main__":
    main()
