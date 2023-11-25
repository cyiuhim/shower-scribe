import shutil
from app import app, db, Recording, TextFile
import random

random.seed(0)
example_texts = ["example-aliens.txt","example-text.txt","example-apples.txt","example-beaches.txt","example-coconuts.txt","example-rockets.txt"]

with app.app_context():
    # Delete all existing recordings and text files entries
    Recording.query.delete()
    TextFile.query.delete()

    # Create 5 new test recordings
    for i in range(5):
        r = Recording()
        r.recording_filename = f"test_recording_{i}.wav"
        r.display_name = f"Test Recording {i}"
        r.flag_transcribed = True
        db.session.add(r)
        # make copies of the example-recording.wav file to match the filename
        try:
            shutil.copyfile("userdata/recordings/example-recording.wav", f"userdata/recordings/{r.recording_filename}")
        except:
            print(f"Error copying example-recording.wav to test_recording_{i}.wav")
            pass

    # Create 5 new example transcription files
    for i in range(5):
        t = TextFile()
        t.text_filename = f"test_text_{i}.txt"
        t.display_name = f"Test Transcription {i}"
        t.associated_recording_id =  i+1 # associate with the recording with the same id
        t.type = 0 # transcription
        db.session.add(t)
        # make copies of the example-transcription.txt file to match the filename
        try:
            shutil.copyfile(f"userdata/texts/{example_texts[i]}", f"userdata/texts/{t.text_filename}")
        except:
            print(f"Error copying example-text.txt to test_text_{i}.txt")
            pass

        # associate the recording with the text file
        r = db.session.get(Recording,t.associated_recording_id)
        r.associated_transcription_id = t.id

    # Commit changes to database
    db.session.commit()
