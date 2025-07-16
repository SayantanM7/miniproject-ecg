# AI-Based ECG Monitoring and Arrhythmia Detection using ESP32, AD8232 & CNN

## 📋 Overview

This project presents an **end-to-end AI + IoT system** for real-time **ECG monitoring** and **arrhythmia detection**, combining **ESP32 microcontroller**, **AD8232 ECG sensor**, **Python/Flask backend**, and a **CNN-based deep learning model** trained on the MIT-BIH dataset.

The system is divided into three key development phases:

---

## 📡 Phase 1 – Real-Time ECG Web Visualization (No AI)

- **Hardware Used**: ESP32 + AD8232 ECG Sensor + Electrode Patches  
- **Goal**: Stream ECG data in real-time from ESP32 to a web browser.
- **Method**:
  1. The ESP32 starts a local Wi-Fi Access Point (`ESP32-ECG`) and hosts a basic HTTP server.
  2. An HTML/JavaScript page (using Chart.js) fetches ECG readings from the `/ecg` endpoint and plots the waveform.
  3. The system operates without any Python or backend server.

✅ **Outcome**: A working, low-cost IoT system for live ECG display in the browser.

---

## 🧠 Phase 2 – Model Training and Web-Based AI Prediction

- **Goal**: Train a Convolutional Neural Network (CNN) to classify heartbeats (Normal or Abnormal) using the **MIT-BIH Arrhythmia Database**.

- **Steps**:
  1. Data preprocessing: Each beat is extracted as a 180-sample segment.
  2. Binary labeling: 'N' as Normal (0), all others as Abnormal (1).
  3. Model training using TensorFlow + Keras + KerasTuner + MLflow for hyperparameter tuning.
  4. Best model converted to `.tflite` for lightweight deployment.

- **Frontend**:
  - A Flask server serves a webpage (`index.html`) with ECG waveform and classification output.
  - Doctors are alerted by **automated email** when abnormal beats are detected.
  - Gemini AI API is integrated to provide explanations and precautionary advice.

✅ **Outcome**: A web interface that loads MIT-BIH samples and uses the trained model to classify beats in real-time.

---

## 🫀 Phase 3 – Real-Time ECG Capture and Prediction from a Live Patient

- **Goal**: Record actual ECG data from a human using AD8232 sensor and ESP32, then classify the signal using the trained model.

- **Steps**:
  1. Arduino sends ECG samples via Serial using 360 Hz sampling (same as MIT-BIH).
  2. A Python script reads the serial data, applies **Savitzky-Golay filtering**, and saves `.hea`, `.dat`, and `.atr` files using `wfdb`.
  3. These files are placed in the `mitbih/` folder used in Phase 2.
  4. Flask frontend is reused: now it loads the patient's data (e.g., record `500`) and shows prediction.

⚠️ **Disclaimer**:  
This system uses a **clinical-grade dataset** for training but **consumer-grade hardware** (AD8232) for real-time testing. Due to noise, drift, and signal mismatch, this is **not for diagnostic use**, but it showcases the feasibility of low-cost health AI systems.

---

