import shutil
from app import app, db, Recording, TextFile

with app.app_context():
    # Delete all existing recordings and text files entries
    Recording.query.delete()
    TextFile.query.delete()

    # Create 5 new test recordings
    for i in range(5):
        r = Recording()
        r.recording_filename = f"test_recording_{i}.wav"
        db.session.add(r)
        # make copies of the example-recording.wav file to match the filename
        try:
            shutil.copyfile("userdata/recordings/example-recording.wav", f"userdata/recordings/{r.recording_filename}")
        except:
            print(f"Error copying example-recording.wav to test_recording_{i}.wav")
            pass

    # Create 5 new test text files
    for i in range(5):
        t = TextFile()
        t.text_filename = f"test_text_{i}.txt"
        t.type = 0 # transcription
        db.session.add(t)
        # make copies of the example-transcription.txt file to match the filename
        try:
            shutil.copyfile("userdata/texts/example-text.txt", f"userdata/texts/{t.text_filename}")
        except:
            print(f"Error copying example-text.txt to test_text_{i}.txt")
            pass

    # Commit changes to database
    db.session.commit()
