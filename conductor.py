# A script that coordinates the execution of the entire showerscribe stack
# It provides a single point of entry, and manages the databases

import threading
from webserver.app import startup_webserver


def startup():
    # start the app on it's own thread, make sure to set it .daemon = True to avoid leaving hanging threads
    app_thread = threading.Thread(target=startup_webserver)
    app_thread.start()
    # app.run(host="0.0.0.0", debug=True, port=8000)
    print("App started.")


if __name__ == "__main__":
    startup()