import time
import sqlite3
import serial
import sys
import os
from predict_disease import predict
#from fog.edge_sensor import sendPlantImage

from picamera2 import Picamera2, Preview
#path = os.path.abspath("/home/pi/Desktop/PlantSense-OnSite/raspberry/fog")
#sys.path.append(path)
from edge_sensors import sendPlantDisease
#from req import upload_image
sys.path.insert(0, '/home/pi/Desktop/PlantSense-OnSite/raspberry/fog')


PORT = "/dev/ttyACM0"

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
    if message != "":
	    message,number = message.split("=")
	    number = int(number)
   
    if message == 'predict':
	
        # Call the on_microbit_message method with the received message
        disease = captureAndpredict()
        response = 'move'
        response = response + '\n'
        sent = 0
        
        s.write(str.encode(response))

        sendPlantDisease(number,disease)

		
s.close()
