

import face_recognition
import os
import pickle

KNOWN_FACES_DIR = "known_faces"
encoding_file = "face_encodings.pkl"

known_face_encodings = []
known_face_names = []

# Loop through all image files in the folder
for filename in os.listdir(KNOWN_FACES_DIR):
    if filename.endswith(".jpg") or filename.endswith(".png"):
        # Extract the person's name from the filename (removes extension)
        name = os.path.splitext(filename)[0]

        # Load the image
        img_path = os.path.join(KNOWN_FACES_DIR, filename)
        image = face_recognition.load_image_file(img_path)

        # Detect faces and encode
        encodings = face_recognition.face_encodings(image)

        if encodings:  # Only add if a face is found
            known_face_encodings.append(encodings[0])
            known_face_names.append(name)
            print(f"Encoded {name} successfully!")
        else:
            print(f"No face detected in {filename}. Skipping.")

# Save encodings
with open(encoding_file, "wb") as f:
    pickle.dump((known_face_encodings, known_face_names), f)

print("All face encodings saved successfully!")


with open("face_encodings.pkl", "rb") as f:
    known_face_encodings, known_face_names = pickle.load(f)

print("Loaded known faces:", known_face_names)
