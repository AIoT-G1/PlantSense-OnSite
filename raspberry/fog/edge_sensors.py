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

# BME280
import smbus2
import bme280

port = 1
address = 0x77  # May differ. check with 'i2c -y 1'
bus = smbus2.SMBus(port)
bme280.load_calibration_params(bus, address)

GPIO.setwarnings(False)

# Pin Setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(5, GPIO.OUT)  # solenoid valve for ___
GPIO.setup(17, GPIO.OUT)  # solenoid valve for ___
GPIO.setup(18, GPIO.OUT)  # water pump

# Serial setup
hub_serial_port = '/dev/ttyACM0'
water_tank_serial_port = '/dev/ttyACM1'


# SerialHub (ttyACM0)
def serialCommand(receiver, command):
    try:
        # Open serial connection
        serial_conn = None
        
        # Change port name as required (Run in RPi terminal "python3 -m serial.tools.list_ports")
        print("Listening on /dev/ttyACM0... Press CTRL+C to exit")
        if receiver == "hub":
            serial_conn = serial.Serial(port=hub_serial_port, baudrate=115200, timeout=1)
        
        if receiver == "water_tank":
            serial_conn = serial.Serial(port=water_tank_serial_port, baudrate=115200, timeout=1)
            
        sendCommand(serial_conn, 'cmd:' + command)
        
        print("Sending command: " + command + " to " + receiver)

        response = ''

        while response == None or len(response) <= 0:
            # Wait for Plant Node Microbits to respond with Sensor Data
            response = waitResponse(serial_conn)

            time.sleep(0.1)
            
        print("Received from serial")
        print(response)
        serial_conn.close()
        return response
        
    except KeyboardInterrupt:

        if serial_conn.is_open:
            serial_conn.close()

    
def sendCommand(serial_conn, command):

    command = command + '\n'
    serial_conn.write(str.encode(command))


def waitResponse(serial_conn):

    response = serial_conn.readline()
    response = response.decode('utf-8').strip()

    return response

# Every 15 minutes (Default)
def automateCommandSensorDataCollection():
    # Automate Plant Sensor Data Collection (Send Commands)
    response = serialCommand("hub","sensor=")
        
    listSensorValues = response.split(',')

    print(listSensorValues)
    
    now = datetime.datetime.now()
    timestamp = str(now)
    timestamp_short = now.strftime("%Y%m%d %H%M%S")

    for sensorValue in listSensorValues:

        print(sensorValue)

        # Take note that Microbits have max limit of 19 char (String); radio.sendString()

        # Identified by 'col='
        # Sample incoming data format
        # c=${truncateSerialNumber};${sm_reading};${light_reading}

        # # Perform necessary changes to Data Format
        plantSensorValues = sensorValue.split('c=')

        # Get Serial Number + Soil Moisture + Light Sensor readings
        temp = plantSensorValues[1].split(';')

        detectedSerialNumber = temp[0]
        sm_reading = temp[1]
        light_reading = temp[2]

        print(detectedSerialNumber)
        print(sm_reading)
        print(light_reading)

        # Now Format into
        #  data = `{'timestamp': ${input.runningTime}, 'type': 'plant_node_data', 'plant_node_id': ${control.deviceSerialNumber()}, 'readings': { 'soil_moisture': ${sm_reading}, 'light_sensor': ${light_reading}, 'onboard_temperature': ${onboard_temp_reading}}}`;

        print(str(listMicrobitDevices))
        
        index = [idx for idx, s in enumerate(
            listMicrobitDevices) if detectedSerialNumber in s][0]
        
        print(str(index))
        
        fullSerialNumber = listMicrobitDevices[index]
        
        formattedPlantSensorData = "nusIS5451Plantsense-plant_sensor_data=" + str(json.dumps({"timestamp": timestamp, "timestamp_short": timestamp_short, "type": "plant_node_data", "plant_node_id": fullSerialNumber, "moisture": sm_reading, "light": light_reading}))

        
        # CLI
        print(formattedPlantSensorData)

        # Push to Cloud Database Server
        # nusIS5451Plantsense-plant_sensor_data
        socketClient(formattedPlantSensorData)
    
    # Get readings from BME280
    bme280Sensor = bme280.sample(bus, address)
    temp = str(bme280Sensor.temperature)
    humidity = str(bme280Sensor.humidity)
    
    formattedWeatherSensorData = "nusIS5451Plantsense-weather=" + str(json.dumps({"action": "add_weather_data", "timestamp": timestamp, "temp": temp, "humidity": humidity}))
    # formattedWaterTankData = "nusIS5451Plantsense-water_tank=" + str(json.dumps({"timestamp": timestamp, "water_level": str(1)}))
    
    print(formattedWeatherSensorData)
    # print(formattedWaterTankData)
    
    # nusIS5451Plantsense-system_sensor_data (temp, humidity)
    socketClient(formattedWeatherSensorData)
    # socketClient(formattedWaterTankData)
    
    # Request from Cloud to conduct Rain Predictions Algo. (Should return True/False)
    requestRainPredictionResultFromCloud(fullSerialNumber, sm_reading)

def requestRainPredictionResultFromCloud(fullSerialNumber, sm_reading):
    # Rain Prediction WILL NOT BE PERFORMED here, but on Cloud.py Server based on regular intervals (i.e. 30mins) which will determine where there is a need to water plant or not (based on Soil Moisture readings). Based on rain prediction (True/False or Yes/No), Cloud.py will send a command through CloudRelay.py > Edge_sensors.py: SendWaterCommand(). At any time, Edge Sensor can request rainPredictionOutput from Cloud.py 
    
    boolIsNotGoingToRain = True
    
    # If-Else Water Plant Algo: Check against Soil Moisture sensor readings.
    if (boolIsNotGoingToRain and int(sm_reading) < 500):
        waterPlant(fullSerialNumber)

def waterPlant(fullSerialNumber):

        node_id = fullSerialNumber
        
        pin = 17 # default

        if node_id == "-814970655": # microbit id: M1
            pin = 17 # Need to hardcode
        elif node_id == "-815128158": # microbit id: M2
            pin = 5 # Need to hardcode

        GPIO.output(pin, 1)
        time.sleep(1)
        GPIO.output(18, 1)

        time.sleep(3)

        GPIO.output(18, 0)
        time.sleep(1)
        GPIO.output(pin, 0)
        
        now = datetime.datetime.now()
        timestamp = str(now)
        timestamp_short = now.strftime("%Y%m%d %H%M%S")

        # Insert into "watering_history" of plant_data collection based on plant_node_id
        socketClient("nusIS5451Plantsense-plant_info=" +
                     str({"action": "update_last_watered", "plant_node_id": node_id, "timestamp": timestamp}))
        
def automateCommandWaterTank():

    response = serialCommand("water_tank", 'water_tank')
    
    now = datetime.datetime.now()
    timestamp = str(now)
    print(str(response))
    tank_level = response.split('=')[1]        
    formattedWaterTankData = "nusIS5451Plantsense-water_tank=" + str(json.dumps(
        {"timestamp": timestamp, 
         "tank_level": tank_level}))

    # nusIS5451Plantsense-system_sensor_data (water_level)
    socketClient(formattedWaterTankData)

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



## <<<<<<<------- MAIN PROGRAM ------->>>>>>>>

thread.start_new_thread(socketServer, ())

# Retrieve User's Settings: sensorInterval from DB
sensorIntervals = 15
tankSensorIntervals = 5

# Handshaking
strMicrobitDevices = serialCommand('hub','handshake')
serialCommand('water_tank','handshake')

strMicrobitDevices = strMicrobitDevices.split('=')

if len(strMicrobitDevices[1]) > 0:

    listMicrobitDevices = strMicrobitDevices[1].split(',')

    if len(listMicrobitDevices) > 0:

        for mb in listMicrobitDevices:

            print('Connected to micro:bit device {}...'.format(mb))

            # Add connected micro:bit device onto MongoDB (Online should check)
            socketClient("nusIS5451Plantsense-plant_info=" +
                            str(json.dumps({"action": "update_plant", "plant_node_id": mb, "name": "", "description": "",
                                "disease": "", "type": "", "photo_url": "", "water_history": []})))

        # Get sensorIntervals User Settings from DB (i.e. 15mins), and schedule accordingly
        # schedule.every(sensorIntervals).minutes.do(
        #     automateCommandSensorDataCollection)

        # # Run one-time command for retrieving sensor data (Initial Bootup)
        # automateCommandSensorDataCollection()
        
        schedule.every(sensorIntervals).minutes.do(
            automateCommandWaterTank)
        
        # Run one-time command for retrieving sensor data (Initial Bootup)
        automateCommandWaterTank()

        while True:

            # Automatic Get Plant Node Sensor Readings (Automate Sending Command)
            schedule.run_pending()

            # Manual Commands (Not for production, for developement ease)
            txCommand=input(
                'Do you want to transmit command to Hub micro:bit (Y/n) = ')

            if txCommand == 'Y':

                commandToTx=input('Enter command to send = ')
                # sendHubCommand('cmd:' + commandToTx)

                # Plant Node Sensors
                if commandToTx.startswith('sensor='):
                    # Run one-time command for retrieving sensor data
                    automateCommandSensorDataCollection()
                    
                    print('Finished sending hub command to all micro:bit devices...')

                # Water Tank node
                if commandToTx.startswith('tank='):
                    # Run one-time command for retrieving tank data
                    automateCommandWaterTank()
                    
                    print('Finished sending tank command...')

    time.sleep(0.1)
