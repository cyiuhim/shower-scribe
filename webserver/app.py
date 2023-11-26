import os
from dotenv import load_dotenv
import json
import vector_interface

from flask import Flask, render_template, send_from_directory, request, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from vector_interface import get_n_closest_ids
# from filesystem_interface import get_text_content

# App setup

from flask import Flask, request, jsonify
from datetime import datetime
from collections import defaultdict
from collections import OrderedDict
from datetime import timedelta
from flask import request, jsonify


app = Flask(__name__)

# Settings setup
# This goes here instead of the data_interface because it's used by the flask app, not the data_interface, and this would lead to circular imports
current_dir = os.path.dirname(os.path.realpath(__file__))
user_settings_path = os.path.join(current_dir,'userdata','user_settings.json')
user_settings = {}
if os.path.exists(user_settings_path):
    with open(user_settings_path, 'r') as f:
        user_settings = json.load(f)
else:
    print(f"No settings file found {user_settings_path}. Using default settings.")

    user_settings = {
        "clustering_time_minutes" : 180,
        "transcription":True,
        "resume":True,
        "brainstorm":True,
    }
    try:
        with open(user_settings_path, 'w') as f:
            json.dump(user_settings, f)
    except:
        print(f"Error saving settings file {user_settings_path}")

# Database setup
current_dir = os.path.dirname(os.path.realpath(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(current_dir, 'userdata','database.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)



# Defined database models

class Recording(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime(timezone=True),
                           server_default=func.now())
    recording_filename = db.Column(db.Text)
    display_name = db.Column(db.Text)
    associated_transcription_id = db.Column(db.Integer, db.ForeignKey('text_file.id'))
    associated_resume_id = db.Column(db.Integer, db.ForeignKey('text_file.id'))
    flag_transcribed = db.Column(db.Boolean,default=False)
    flag_resumed = db.Column(db.Boolean,default=False)

    def __repr__(self):
        return f'<Recording {self.id} ({self.recording_filename})>'
    
class TextFile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime(timezone=True),
                           server_default=func.now())
    type = db.Column(db.Integer) # 0 = transcription, 1 = resume, 2 = brainstorm
    text_filename = db.Column(db.Text)
    display_name = db.Column(db.Text)
    associated_recording_id = db.Column(db.Integer, db.ForeignKey('recording.id'))

    def __repr__(self):
        return f'<TextFile {self.id} ({self.text_filename} type {self.type})>'
    


# Routes

@app.route('/')
def show_main():
    # Fetch and group the recordings by date
    grouped_recordings = get_grouped_recordings()

    # No need to convert dates here, as they are already formatted as strings in get_grouped_recordings
    return render_template('index.html', grouped_recordings=grouped_recordings)


@app.route('/recordings/<date>')
def recordings_on_date(date):
    try:
        date_obj = datetime.strptime(date, '%B %d, %Y')
        recordings = Recording.query.filter(
            func.date(Recording.created_at) == date_obj.date()
        ).all()
        grouped_sessions = group_recordings(recordings)
        return render_template('date_recordings.html', date=date_obj, grouped_sessions=grouped_sessions)
    except ValueError:
        # Handle the error if the date format is incorrect
        return "Invalid date format", 400


@app.route('/get_recording/<path:path>')
def send_recording(path):
    return send_from_directory('userdata/recordings', path)

@app.route('/recordings/<int:recording_id>', methods=["GET", "POST"])
def show_recording(recording_id):
    recording = Recording.query.get_or_404(recording_id)
    resume_text = "No resume available"

    # Fetch the associated transcript TextFile entry
    associated_resume = TextFile.query.get(recording.associated_resume_id)
    print(associated_resume)
    if associated_resume:
        # Assuming the text content is stored in a file
        try:
            with open(f"userdata/texts/{associated_resume.text_filename}", "r") as f:
                resume_text = f.read()
        except IOError:
            resume_text = "Error reading transcript file."

    return render_template('recording.html', recording=recording, resume_text=resume_text)


@app.route('/texts/<int:text_id>', methods=["GET", "POST"])
def show_text(text_id):
    text = TextFile.query.get_or_404(text_id)
    # safely get the content of the text file
    try:
        with open(os.path.join('webserver','userdata','texts',text.text_filename), "r") as f:
            content = f.read()
    except:
        content = "Error reading text file."
    return render_template('text.html', text=text, content=content) # we pass the text without any escaping
 
@app.route('/delete_recording/<int:recording_id>', methods=['POST']) #in progress. go through and kill all the children
def delete_recording(recording_id):
    recording = Recording.query.get(recording_id)
    if recording:
        db.session.delete(recording)
        db.session.commit()
        return jsonify({"success": True})
    else:
        return jsonify({"success": False}), 404
    
@app.route('/settings')
def show_settings():
    basedir = os.path.abspath(os.path.dirname(__file__))
    user_settings_path = os.path.join(basedir, 'userdata/user_settings.json')
    user_settings = {}
    if os.path.exists(user_settings_path):
        with open(user_settings_path, 'r') as f:
            user_settings = json.load(f)
    else:
        print(f"No settings file found {user_settings_path}. Using default settings.")
        # Define default settings here if needed

    return render_template('settings.html', user_settings=user_settings)

@app.route('/search')
def show_search():
    # This function simply renders the search.html template.
    # You can pass additional context or settings if required.
    return render_template('search.html')

@app.route('/search_results')
def search_results():
    query = request.args.get('query', '')  # Get the search query from URL parameters

    # Assuming get_n_closest_ids function returns a list of result IDs
    result_ids = get_n_closest_ids(1, query, 3)

    # Fetch the results from the database
    results = Recording.query.filter(Recording.id.in_(result_ids)).all()

    # Render a template with the search results and the original query
    return render_template('search_results.html', query=query, results=results)

#functions

def get_grouped_recordings():
    recordings = Recording.query.order_by(Recording.created_at.desc()).all()  # Sort by created_at in descending order
    grouped_recordings = defaultdict(list)
    for recording in recordings:
        date_key = recording.created_at.strftime('%B %d, %Y')
        grouped_recordings[date_key].append(recording)
    return dict(grouped_recordings)

def group_recordings(recordings):
    recordings.sort(key=lambda r: r.created_at)
    grouped_sessions = []
    session = []
    clustering_minutes = user_settings["clustering_time_minutes"]  # Directly use the setting

    for recording in recordings:
        if not session or recording.created_at - session[0].created_at <= timedelta(minutes=clustering_minutes):
            session.append(recording)
        else:
            grouped_sessions.append(session)
            session = [recording]

    if session:
        grouped_sessions.append(session)

    # Assign session titles
    for session in grouped_sessions:
        first_recording_time = session[0].created_at
        if first_recording_time.hour < 11 or (first_recording_time.hour == 11 and first_recording_time.minute <= 30): # Morning session if before 11:30
            session_title = "Morning Session"
        elif first_recording_time.hour < 17 or (first_recording_time.hour == 17 and first_recording_time.minute <= 30): # Afternoon session if before 17:30 (5:30pm)
            session_title = "Afternoon Session"
        else:
            session_title = "Evening Session" # Otherwise it's an evening session

        for recording in session:
            recording.session_title = session_title

    return grouped_sessions



# Run the app

def start_app():
    # print(f"To test that the OS keys are accessible: {os.getenv('COHERE_API_KEY')}")
    app.run(host='0.0.0.0', debug=True,port=8000)

if __name__ == "__main__":
    start_app()
    
