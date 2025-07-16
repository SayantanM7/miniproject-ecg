import serial
import time
import struct
import os
import numpy as np
from scipy.signal import savgol_filter

# Configuration
PORT = '/dev/ttyACM0'  
BAUDRATE = 115200
SAMPLE_RATE = 360
RECORD_SECONDS = 5
RECORD_NAME = "500"

def main():
    try:
        ser = serial.Serial(PORT, BAUDRATE, timeout=1)
        print(f"Connected to {ser.name}")
    except serial.SerialException as e:
        print(f"Failed to connect: {e}")
        return

    while True:
        line = ser.readline().decode().strip()
        if line == "ECG_READY":
            break
        time.sleep(0.1)

    print(f"Recording {RECORD_SECONDS} seconds of ECG data...")
    
    samples = []
    annotations = []
    start_time = time.time()

    while (time.time() - start_time) < RECORD_SECONDS:
        try:
            line = ser.readline().decode().strip()
            if line:
                ecg_value = int(line)
                samples.append(ecg_value)

                if len(samples) % SAMPLE_RATE == SAMPLE_RATE // 2:
                    annotations.append((len(samples)-1, 'N'))
        except (ValueError, UnicodeDecodeError):
            continue

    ser.close()
    print(f"Captured {len(samples)} samples")

    # Normalize and smooth with Savitzky-Golay filter
    samples = np.array(samples, dtype=np.float32)
    normalized = (samples - np.mean(samples)) / np.std(samples)
    smoothed = savgol_filter(normalized, window_length=11, polyorder=2)

    # Convert to 12-bit range for MIT-BIH encoding
    scaled = np.clip((smoothed * 200) + 1024, 0, 4095).astype(np.uint16)

    # Generate MIT-BIH format files
    generate_dat_file(scaled)
    generate_hea_file(len(scaled))
    generate_atr_file(annotations)
    
    print("✅ .hea, .dat, and .atr files generated successfully!")

def generate_dat_file(samples):
    with open(f"{RECORD_NAME}.dat", 'wb') as f:
        for sample in samples:
            f.write(struct.pack('<H', sample))

def generate_hea_file(num_samples):
    with open(f"{RECORD_NAME}.hea", 'w') as f:
        f.write(f"{RECORD_NAME} 1 {SAMPLE_RATE} {num_samples}\n")
        f.write(f"{RECORD_NAME}.dat 16 200 12 0 0 0 0\n")
        f.write(f"{RECORD_NAME}.atr 16 200 0 0 0\n")
        f.write("# DIY ECG Recording with Savitzky–Golay filter\n")
        f.write("# Created using ESP32 + AD8232 + Python\n")

def generate_atr_file(annotations):
    with open(f"{RECORD_NAME}.atr", 'wb') as f:
        for sample_index, ann_type in annotations:
            code = 1 if ann_type == 'N' else 0
            f.write(struct.pack('<LHBB', sample_index, code, 0, 0))

if __name__ == "__main__":
    main()

