# SEP600_Project
AI-Powered Facial Recognition Software


First, The Keil Studio code is built and sent to the K64 board. \
Then the Arduino code for the ESP32 camera is run to connect it to either WIFI or Hotspot.\
Then the "Encode_Known_Faces.py" is run to encode the owner's uploaded photos so that the system can corroborate them with the feed that it is getting from the camera when the "Facial_Recognition_Software.py" is run.\
Lastly, the "Facial_Recognition_Software.py" is run to send commands to the K64 board based on the scanned face.
