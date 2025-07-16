from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins='*')

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('ecg_data')
def handle_ecg(data):
    print("Received ECG Data:", data)
    emit('ecg_data', data, broadcast=True)

if __name__ == '__main__':
    print("Starting Flask server...")
    socketio.run(app, host='0.0.0.0', port=5000)
