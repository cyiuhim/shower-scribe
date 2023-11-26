# A module that handles all database interactions for the SQL database for external modules, 
# The slightly odd structure of this though is that the database is still owned by the flask server to keep all of the model interractions simple

from webserver.app import app, db, Recording, TextFile
import datetime

# Database methods

def add_recording(recording_filename)->int:
    with app.app_context():
        recording = Recording()
        recording.recording_filename = recording_filename
        recording.created_at = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-5)))
        db.session.add(recording)
        db.session.commit()
        recording.display_name = f"Shower Thoughts #{recording.id}"
        db.session.commit()
        return recording.id

def get_recording_path(recording_id) -> tuple[bool, str]:
    with app.app_context():
        recording = Recording.query.filter_by(id=recording_id).first()
        if recording:
            return True, recording.recording_filename
        else:
            return False, ""
        
def get_recording_as_dict(recording_id):
    with app.app_context():
        recording = Recording.query.filter_by(id=recording_id).first()
        if recording:
            return {
                "id": recording.id,
                "recording_filename": recording.recording_filename,
                "display_name": recording.display_name,
                "associated_transcription_id": recording.associated_transcription_id,
                "associated_resume_id": recording.associated_resume_id,
                "flag_transcribed": recording.flag_transcribed,
                "flag_resumed": recording.flag_resumed,
            }
        else:
            return None
        
def get_text_as_dict(text_id):
    with app.app_context():
        text = TextFile.query.filter_by(id=text_id).first()
        if text:
            return {
                "id": text.id,
                "text_filename": text.text_filename,
                "display_name": text.display_name,
                "type": text.type,
                "associated_recording_id": text.associated_recording_id
            }
        else:
            return None
        
def get_untranscribed_recordings():
    with app.app_context():
        recordings = Recording.query.filter_by(flag_transcribed=False).all()
        ids = [recording.id for recording in recordings]
        return ids

def get_unresumed_recordings():
    """Get the ids of all recordings that have been transcribed but not resumed. Ready to be AIed"""
    with app.app_context():
        recordings = Recording.query.filter_by(flag_resumed=False,flag_transcribed=True).all()
        ids = [recording.id for recording in recordings]
        return ids
        

def create_text_from_dict(text_dict):
    # check that there are the right feilds
    needed_keys = ["text_filename","display_name","type","associated_recording_id"]
    for key in needed_keys:
        if key not in text_dict:
            raise ValueError(f"Error, text_dict missing key {key}")
    try:
        with app.app_context():
            text = TextFile()
            text.text_filename = text_dict["text_filename"]
            text.display_name = text_dict["display_name"]
            text.type = text_dict["type"]
            text.associated_recording_id = text_dict["associated_recording_id"]
            db.session.add(text)
            db.session.commit()
            recording = Recording.query.filter_by(id=text_dict["associated_recording_id"]).first()
            if text_dict["type"] == 0 and recording:
                recording.associated_transcription_id = text.id
            if text_dict["type"] == 1 and recording:
                recording.associated_resume_id = text.id
            db.session.commit()
            return text.id
    except:
        return None

def update_recording_associated_resume(recording_id,new_resume_id):
    # update the associated resume for a recording
    with app.app_context():
        recording = Recording.query.filter_by(id=recording_id).first()
        if recording:
            recording.associated_resume_id = new_resume_id
            db.session.commit()
            return True
        else:
            return False
        
def update_recording_display_name(recording_id,new_display_name):
    # update the display name for a recording
    with app.app_context():
        recording = Recording.query.filter_by(id=recording_id).first()
        if recording:
            recording.display_name = new_display_name
            db.session.commit()
            return True
        else:
            return False
        
def update_recording_flag_transcribed(recording_id):
    with app.app_context():
        recording = Recording.query.filter_by(id=recording_id).first()
        if recording:
            recording.flag_transcribed = True
            db.session.commit()
            return True
        else:
            return False
        
def update_recording_flag_resumed(recording_id):
    with app.app_context():
        recording = Recording.query.filter_by(id=recording_id).first()
        if recording:
            recording.flag_resumed = True
            db.session.commit()
            return True
        else:
            return False
