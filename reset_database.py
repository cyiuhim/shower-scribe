# THIS FILE SHOULD ONLY BE RUN BY HAND
import os

if __name__ == "__main__":
    # physically go find the database file and os remove it
    path = "webserver/userdata/database.db"
    os.remove(path)

    # itterate through all the recordings and texts in the recordings and texts directories without example- in them
    recordings_path = "webserver/userdata/recordings"
    texts_path = "webserver/userdata/texts"
    for filename in os.listdir(recordings_path):
        if "example-" not in filename and ".wav" in filename:
            os.remove(os.path.join(recordings_path, filename))

    for filename in os.listdir(texts_path):
        if "example-" not in filename and ".txt" in filename:
            os.remove(os.path.join(texts_path, filename))

    from webserver.app import *
    with app.app_context():
        db.create_all()

    import vector_interface
    vector_interface.reset_database()

    