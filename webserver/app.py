import os

from flask import Flask, render_template, send_from_directory, request, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func

app = Flask(__name__)



# Database setup

basedir = os.path.abspath(os.path.dirname(__file__))

app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, 'userdata/database.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)



# Defined database models

class Recording(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime(timezone=True),
                           server_default=func.now())
    recording_filename = db.Column(db.Text)

    def __repr__(self):
        return f'<Recording {self.id} ({self.recording_filename})>'
    
class TextFile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime(timezone=True),
                           server_default=func.now())
    type = db.Column(db.Integer) # 0 = transcription, 1 = brainstorm
    text_filename = db.Column(db.Text)

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
    try:
        with open(f"userdata/texts/{text.text_filename}", "r") as f: # text_filename is generated by the code, so it's safe and can be served directly
            content = f.read()
    except:
        content = "Error reading text file."

    return render_template('text.html', text=text, content=content) # we pass the text without any escaping, since it's been sanitized at ingest


# Run the app

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True,port=8000)
    
