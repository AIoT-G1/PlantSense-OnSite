import time
import sqlite3
import serial
from predict_disease import predict
from picamera2 import Picamera2, Preview

PORT = "/dev/ttyACM0"
##
BAUD = 115200
s = serial.Serial(port='/dev/ttyACM0', baudrate=115200, timeout=1)


def captureAndpredict():
	picam = Picamera2()

	config = picam.create_preview_configuration()
	picam.configure(config)

	picam.start_preview(Preview.QTGL)

	picam.start()
	time.sleep(2)
	picam.capture_file("leaf.jpg")

	picam.close()

	disease = predict()
	
while True:
    
    #message = s.readline().decode().strip()
    
    message = s.readline()
    message = message.decode('utf-8').strip()
    #print(s.readline().decode('utf-8'))
    print("message:", message)
    if message == 'predict':
		
        # Call the on_microbit_message method with the received message
        captureAndpredict()
        response = 'move'
        s.write(str.encode(response))
        #s.write(response.encode('utf-8'))

s.close()
