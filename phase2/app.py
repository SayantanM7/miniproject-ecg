from flask import Flask, jsonify, render_template, request
import wfdb
import numpy as np
import tensorflow as tf
import os
import google.generativeai as genai
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


genai.configure(api_key="AIzaSyDZKA3DqTush7vqa4Kw-S4vDfbVGQXIbYk")  

app = Flask(__name__)

# Doctor's email and your SMTP credentials
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
SENDER_EMAIL = 'rick.mondal@gmail.com'
SENDER_PASSWORD = 'umqnharcxdvhdtbn'  # Use App Password, not real one
DOCTOR_EMAIL = 'drswapan1207@gmail.com'


@app.route('/')
def index():
    return render_template('index.html')
def send_alert_email(record_id):
    subject = f"⚠️ Arrhythmia Detected in Record {record_id}"
    body = f"""
Dear Doctor,

An abnormal ECG pattern (Arrhythmia) has been detected in record {record_id}.
Immediate attention is advised.

Please log in to the ECG monitoring system for details.

Regards,
ECG AI System
    """

    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = DOCTOR_EMAIL
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
        print("Alert email sent.")
    except Exception as e:
        print(f"Failed to send email: {e}")

@app.route('/data')
def get_data():
    record_id = request.args.get('record', '100')  # default = 100 if not specified
    record_path = f'mitbih/{record_id}'

    if not os.path.exists(record_path + '.dat') or not os.path.exists(record_path + '.hea'):
        return jsonify({'error': f'Record {record_id} not found'}), 404

    try:
        record = wfdb.rdrecord(record_path)
        signal = record.p_signal[:, 0]

        segment = None

        try:
            annotation = wfdb.rdann(record_path, 'atr')
            ann_samples = annotation.sample

            for sample in ann_samples:
                if sample - 90 < 0 or sample + 90 > len(signal):
                    continue
                segment = signal[sample - 90: sample + 90]
                break
        except:
            # No .atr file available – use center of signal
            mid = len(signal) // 2
            if mid - 90 >= 0 and mid + 90 <= len(signal):
                segment = signal[mid - 90: mid + 90]

        if segment is None:
            return jsonify({'error': 'No valid segment found'}), 500

        # Prediction using TensorFlow Lite model
        interpreter = tf.lite.Interpreter(model_path='model.tflite')
        interpreter.allocate_tensors()
        input_details = interpreter.get_input_details()
        output_details = interpreter.get_output_details()

        segment_input = np.array(segment, dtype=np.float32).reshape(1, 180, 1)
        interpreter.set_tensor(input_details[0]['index'], segment_input)
        interpreter.invoke()
        prediction = interpreter.get_tensor(output_details[0]['index'])[0][0]
        result = "Abnormal (Arrhythmia)\nYour Doctor has been notified via email." if prediction > 0.5 else "Normal"
        # Gemini AI call for explanation and precautions
        if result!= "Normal":
            send_alert_email(record_id)
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"ECG Segment analysis: The AI model predicted this as '{result}'. Based on this, what could be the probable cause and what precautions should the patient take? Give a short 2-3 line note."
        response = model.generate_content(prompt)
        note = response.text.strip()

        return jsonify({
            'segment': segment.tolist(),
            'prediction': result,
            'record_id': record_id,
            'note': note
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
