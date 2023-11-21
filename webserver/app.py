import os
from dotenv import load_dotenv
import json

from flask import Flask, render_template, send_from_directory, request, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
# from filesystem_interface import get_text_content

# App setup

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

@app.route('/get_recording/<path:path>')
def send_recording(path):
    return send_from_directory('userdata/recordings', path)

@app.route('/', methods=["GET", "POST"])
def show_main():
    return render_template('index.html')

@app.route('/texts', methods=["GET", "POST"])
def show_texts():
    texts = TextFile.query.all()
    return render_template('texts.html', texts=texts)

@app.route('/recordings', methods=["GET", "POST"])
def show_recordings():
    recordings = Recording.query.all()
    return render_template('recordings.html', recordings=recordings)

@app.route('/recordings/<int:recording_id>', methods=["GET", "POST"])
def show_recording(recording_id):
    recording = Recording.query.get_or_404(recording_id)
    return render_template('recording.html', recording=recording)

@app.route('/texts/<int:text_id>', methods=["GET", "POST"])
def show_text(text_id):
    text = TextFile.query.get_or_404(text_id)
    # safely get the content of the text file
    with open(os.path.join('userdata','texts',text.text_filename), "r") as f:
        content = f.read()
    return render_template('text.html', text=text, content=content) # we pass the text without any escaping, since it's been sanitized at ingest


# Run the app

def start_app():
    # print(f"To test that the OS keys are accessible: {os.getenv('COHERE_API_KEY')}")
    app.run(host='0.0.0.0', debug=True,port=8000)

if __name__ == "__main__":
    start_app()
    
