from flask import Flask, render_template, send_from_directory

app = Flask(__name__)

@app.route('/recordings/<path:path>')
def send_recording(path):
    return send_from_directory('recordings', path)


@app.route('/', methods=["GET", "POST"])
def show_main():
    return render_template('hello.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True,port=8000)
    
