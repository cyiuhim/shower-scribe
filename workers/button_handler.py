import RPi.GPIO as GPIO


class ButtonHandler:
    def __init__(self, button_pin):
        """
            @brief ButtonHandler keeps track of the state of a button and makes it
            accessible for the rest of the program

            ButtonHandler is initialized with:

            @param button_pin
            The GPIO pin on the RaspberryPI where the button is connected

            The state of the button is accesed throught the is_pressed attribute
        """

        self.button_pin: int = button_pin
        self.is_pressed: bool = False  # state of the button

        # Setup GPIO
        GPIO.setmode(GPIO.Board)
        GPIO.setup(self.button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        # Add event detection for button press and release
        GPIO.add_event_detect(self.button_pin, GPIO.FALLING,
                              callback=self.on_button_press, bouncetime=300)
        
    def on_button_press(self, channel):
        """
            @brief Updates the button's state when pressed

            @param channel
            Channel is to handle multiple pins
        """
        print("Button pressed")
        self.is_pressed = not self.is_pressed  # update button state

    def terminate_interface(self):
        """
            @brief Call when finished to clean up GPIO interface
        """
        GPIO.cleanup()
