#This populate is before resumes implemented. More variety for testing though.
import shutil
from webserver.app import app, db, Recording, TextFile
import random
from datetime import datetime, timedelta

random.seed(0)

def random_time():
    # Generate a random time
    random_hour = random.randint(0, 23)
    random_minute = random.randint(0, 59)
    random_second = random.randint(0, 59)
    return datetime.now().replace(hour=random_hour, minute=random_minute, second=random_second)

with app.app_context():
    # Delete all existing recordings and text files entries
    Recording.query.delete()
    TextFile.query.delete()
    example_texts = ["example-aliens.txt", "example-text.txt", "example-apples.txt", "example-beaches.txt", "example-coconuts.txt", "example-rockets.txt"]


    start_date = datetime.now() - timedelta(days=30)  # Assuming last 30 days
    for day in range(30):  # For each day
        current_date = start_date + timedelta(days=day)
        for i in range(2, 4):  # Create 2 or 3 recordings for each day
            r = Recording()
            r.recording_filename = f"test_recording_{day}_{i}.wav"
            r.display_name = f"Test Recording {day} #{i}"
            r.associated_transcription_id = i + 1
            r.flag_transcribed = True
            r.created_at = current_date.replace(hour=random_time().hour, minute=random_time().minute, second=random_time().second)
            db.session.add(r)
            # Copy the example recording file
            try:
                shutil.copyfile("webserver/userdata/recordings/example-recording.wav", f"webserver/userdata/recordings/{r.recording_filename}")
            except IOError as e:
                print(f"Error copying file for recording {day}_{i}: {e}")
                pass

    # Create test text files (adjust as needed)
    for i in range(30):  # Adjust the range as needed
        t = TextFile()
        t.text_filename = f"test_text_{i}.txt"
        t.display_name = f"Test Text {i}"
        t.associated_recording_id = i + 1
        t.type = 0
        db.session.add(t)
        # Copy the example text file
        try:
            # Choose a random text file from example_texts
            random_text_file = random.choice(example_texts)

            # Assuming t.text_filename is some variable you have defined
            shutil.copyfile(f"webserver/userdata/texts/{random_text_file}", f"webserver/userdata/texts/{t.text_filename}")
        
        except IOError as e:
            print(f"Error copying file for text {i}: {e}")
            pass

    # Commit changes to the database
    db.session.commit()
