# Based on Lect 7: src10.py

# Commands: python3 -m serial.tools.list_ports
# python3 edge_sensors.py

# For scheduling task execution (pip install schedule)
# https://stackoverflow.com/questions/22715086/scheduling-python-script-to-run-every-hour-accurately
import schedule
import datetime
import json

import socket
import _thread as thread
import serial
import time
import RPi.GPIO as GPIO
import requests


# Image
import base64



def sendPlantImage(detectedSerialNumber,disease):
        node_id = detectedSerialNumber
        with open("leaf.jpg", "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read())

            part1 = encoded_string[:len(encoded_string)//3]
            part2 = encoded_string[len(encoded_string)//3:2*len(encoded_string)//3]
            part3 = encoded_string[2*len(encoded_string)//3:]

            # encode each part to base64
            encoded_part1 = str(base64.b64encode(part1).decode())
            encoded_part2 = str(base64.b64encode(part2).decode())
            encoded_part3 = str(base64.b64encode(part3).decode())

            formattedImageData1 = "nusIS5451Plantsense-plant_info="+str(json.dumps({"action": "update_last_image_1", "plant_node_id": node_id, "photo_url": encoded_part1,"disease":disease}))
            formattedImageData2 = "nusIS5451Plantsense-plant_info="+str(json.dumps({"action": "update_last_image_2", "plant_node_id": node_id, "photo_url": encoded_part2,"disease":disease}))
            formattedImageData3 = "nusIS5451Plantsense-plant_info="+str(json.dumps({"action": "update_last_image_3", "plant_node_id": node_id, "photo_url": encoded_part3,"disease":disease}))
        
            socketClient(formattedImageData1)
            socketClient(formattedImageData2)
            socketClient(formattedImageData3)



def serviceClient(clientSocket, address):

    print("Connection from: " + str(address))

    while True:
        data = clientSocket.recv(1024).decode('utf-8')
        if not data:
            break

        # Do whatever with data
        print(str(data))

        data = 'ACK'
        clientSocket.send(data.encode('utf-8'))

    clientSocket.close()


def socketServer():
    host = socket.gethostname()
    port = 8889

    socketServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socketServer.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    socketServer.bind((host, port))

    while True:
        print("Listening to new connections...")
        socketServer.listen()
        clientSocket, address = socketServer.accept()
        # s.setblocking(False)
        thread.start_new_thread(serviceClient, (clientSocket, address))


def socketClient(data):
    host = socket.gethostname()
    port = 8888  # Cloud Relay listen at port 8888

    socketClient = socket.socket()
    socketClient.connect((host, port))
    socketClient.send(data.encode('utf-8'))

    response = socketClient.recv(1024).decode('utf-8')
    print('Cloud relay -> ' + response)
    socketClient.close()


