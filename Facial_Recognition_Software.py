import cv2
import face_recognition
import numpy as np
import pickle
import requests
import serial  # UART communication with K64F
import time
from mtcnn import MTCNN

# ESP32-CAM Stream URL (Replace with your ESP32 IP)
ESP32_STREAM_URL = "http://192.168.233.74/stream"

# UART Serial Communication Setup (Match COM port with Keil)
ser = serial.Serial("COM8", 115200, timeout=1)

# Load known faces and embeddings (if available)
try:
    with open("face_encodings.pkl", "rb") as f:
        known_face_encodings, known_face_names = pickle.load(f)
except FileNotFoundError:
    known_face_encodings = []
    known_face_names = []

# Initialize MTCNN detector
detector = MTCNN()

# Throttle settings: only send the same command if at least 5 seconds have passed.
THROTTLE_SECONDS = 8
last_sent = {"pass": 0, "failed": 0}

def send_command_to_k64f(command):
    """Send 'pass' or 'failed' command to the K64F via UART, throttled to once every 5 seconds."""
    current_time = time.time()
    lower_cmd = command.lower()
    if lower_cmd in last_sent:
        if current_time - last_sent[lower_cmd] < THROTTLE_SECONDS:
            return  # Too soon; skip sending
        last_sent[lower_cmd] = current_time
    try:
        ser.write((command + "\n").encode())  # Send command over UART
        print(f"Sent command: {command}")
    except Exception as e:
        print(f"Error sending command: {e}")

def recognize_face(frame):
    """Detects and recognizes faces using face_recognition."""
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Find face locations and encodings in the frame
    face_locations = face_recognition.face_locations(rgb_frame)
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
        name = "Unknown"
        color = (0, 0, 255)  # Red for unknown faces

        if True in matches:
            first_match_index = matches.index(True)
            name = known_face_names[first_match_index]
            color = (0, 255, 0)  # Green for recognized faces
            send_command_to_k64f("pass")
        else:
            send_command_to_k64f("failed")

        # Draw bounding box & label
        cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
        cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)

    return frame

def fetch_frames_from_esp32():
    """Fetches and processes frames from the ESP32-CAM stream."""
    session = requests.Session()
    stream = session.get(ESP32_STREAM_URL, stream=True)
    byte_stream = b""

    for chunk in stream.iter_content(chunk_size=1024):
        byte_stream += chunk
        a = byte_stream.find(b'\xff\xd8')  # JPEG start
        b = byte_stream.find(b'\xff\xd9')  # JPEG end

        if a != -1 and b != -1:
            jpg = byte_stream[a:b + 2]
            byte_stream = byte_stream[b + 2:]

            # Convert JPEG bytes to an OpenCV image
            img_np = np.frombuffer(jpg, dtype=np.uint8)
            frame = cv2.imdecode(img_np, cv2.IMREAD_COLOR)

            if frame is not None:
                frame = recognize_face(frame)
                cv2.imshow("ESP32-CAM Face Recognition", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

# Start processing the ESP32 camera stream
fetch_frames_from_esp32()

# Cleanup
ser.close()
cv2.destroyAllWindows()
