import socket
import _thread as thread
from paho.mqtt import client as mqttClient
import ssl
import datetime


mqtt = None


def onConnect(client, userdata, flags, rc):
    # MQTT topics to subscribe
    # mqtt.subscribe("nus_IS5451_Plantsense_global_sensor_data")
    # mqtt.subscribe("nus_IS5451_Plantsense_plant_disease")
    # mqtt.subscribe("nus_IS5451_Plantsense_buggy_state")

    print("Connection ACK: " + str(rc))


def onMessage(client, userdata, msg):
    socketClient(msg)


def forwardEdgeSensorsData(data):
    # Forwards data from rhub to cloud
    print('From Edge Sensors -> {}'.format(data))

    r = mqtt.publish(data.split('=')[0], data.split('=')[1])

    if r[0] == 0:
        print("Message sent successfully")
    else:
        print("Failed to send message")


def serviceClient(clientSocket, address):

    print("Connection from: " + str(address))

    while True:
        data = clientSocket.recv(1024).decode('utf-8')
        if not data:
            break
        forwardEdgeSensorsData(data)
        data = 'ACK'
        clientSocket.send(data.encode('utf-8'))

    clientSocket.close()


def socketServer():
    host = socket.gethostname()
    port = 8888

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
    port = 8889  # Edge_sensors listen at port 8889

    socketClient = socket.socket()
    socketClient.connect((host, port))
    socketClient.send(data.encode('utf-8'))

    response = socketClient.recv(1024).decode('utf-8')
    print('Edge -> ' + response)
    socketClient.close()


if __name__ == '__main__':
    # Initialise MQTT connection
    mqtt = mqttClient.Client()
    mqtt.on_connect = onConnect
    mqtt.on_message = onMessage

    mqtt.tls_set(ca_certs="certs/mosquitto.org.crt", certfile="certs/client.crt", keyfile="certs/client.key", tls_version=ssl.PROTOCOL_TLSv1_2)
    mqtt.connect("test.mosquitto.org", 8883)
    mqtt.loop_start()

    # Socket connection
    socketServer()
