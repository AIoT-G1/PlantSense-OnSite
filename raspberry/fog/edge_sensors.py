# Based on Lect 7: src10.py

# Commands: python3 -m serial.tools.list_ports
# python3 edge_sensors.py

# For scheduling task execution (pip install schedule)
# https://stackoverflow.com/questions/22715086/scheduling-python-script-to-run-every-hour-accurately
import schedule

import socket
import _thread as thread
import serial
import time
import RPi.GPIO as GPIO


GPIO.setwarnings(False)

GPIO.setmode(GPIO.BCM)
GPIO.setup(5, GPIO.OUT)  # solenoid valve for ___
GPIO.setup(17, GPIO.OUT)  # solenoid valve for ___
GPIO.setup(18, GPIO.OUT)  # water pump


def sendCommand(command):

	command = command + '\n'
	ser.write(str.encode(command))


def waitResponse():

	response = ser.readline()
	response = response.decode('utf-8').strip()

	return response


def waterPlant(sensorValues):

	for reading in sensorValues:

		data = reading.split(":")

		node_id = data[5]
		soil_moisture = data[8]

		if soil_moisture < 690:

			if node_id == 18243620:
				print()
				pin = 17
			elif node_id == 1775143845:
				pin = 5

			GPIO.output(pin, 1)
			sleep(1)
			GPIO.output(18, 1)

			sleep(3)

			GPIO.output(18, 0)
			sleep(1)
			GPIO.output(pin, 0)


def automateCommandSensorDataCollection():
	# Automate Plant Sensor Data Collection (Send Commands)
	sendCommand('cmd:' + "sensor=")
	print('Sending Command to Plant Nodes for data collection.')
	print('Finished sending command to all micro:bit devices...')

	strSensorValues = ''

	while strSensorValues == None or len(strSensorValues) <= 0:

		# Take note that Microbits have max limit of 19 char (String); radio.sendString()

		# Format data
		# data = "'timestamp': ${input.runningTime}, 'type': 'plant_node_data', 'plant_node_id': ${control.deviceSerialNumber()}, 'readings': {'soil_moisture': ${sm_reading}, 'light_sensor': ${light_reading}, 'onboard_temperature': ${onboard_temp_reading}}}

		# Wait for Plant Node Microbits to respond with Sensor Data
		strSensorValues = waitResponse()
		time.sleep(0.1)

	listSensorValues = strSensorValues.split(',')

	print(listSensorValues)

	for sensorValue in listSensorValues:

		print(sensorValue)


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
	port = 8888 # Cloud Relay listen at port 8888

	socketClient = socket.socket()
	socketClient.connect((host, port))
	socketClient.send(data.encode('utf-8'))
 
	response = socketClient.recv(1024).decode('utf-8')
	print('Cloud relay -> ' + response)
	socketClient.close()
 

try:

	# Retrieve User's Settings: sensorInterval from DB
	sensorIntervals = 15

	# Change port name as required (Run in RPi terminal "python3 -m serial.tools.list_ports")
	print("Listening on /dev/ttyACM0... Press CTRL+C to exit")
	ser = serial.Serial(port='/dev/ttyACM0', baudrate=115200, timeout=1)

	# Handshaking
	sendCommand('handshake')

	strMicrobitDevices = ''

	while strMicrobitDevices == None or len(strMicrobitDevices) <= 0:

		strMicrobitDevices = waitResponse()
		time.sleep(0.1)

	strMicrobitDevices = strMicrobitDevices.split('=')

	if len(strMicrobitDevices[1]) > 0:

		listMicrobitDevices = strMicrobitDevices[1].split(',')

		if len(listMicrobitDevices) > 0:

			for mb in listMicrobitDevices:

				print('Connected to micro:bit device {}...'.format(mb))

			# Get sensorIntervals User Settings from DB (i.e. 30mins), and schedule accordingly
			schedule.every(sensorIntervals).minutes.do(
				automateCommandSensorDataCollection)

			# Run one-time command for retrieving sensor data
			automateCommandSensorDataCollection()

			while True:

				# Automatic Get Plant Node Sensor Readings (Automate Sending Command)
				schedule.run_pending()

				# Manual Commands
				txCommand = input(
					'Do you want to transmit command to micro:bit (Y/n) = ')

				if txCommand == 'Y':

					commandToTx = input('Enter command to send = ')
					sendCommand('cmd:' + commandToTx)
					print('Finished sending command to all micro:bit devices...')

					if commandToTx.startswith('sensor='):

						strSensorValues = ''

						while strSensorValues == None or len(strSensorValues) <= 0:

							strSensorValues = waitResponse()
							time.sleep(0.1)

						listSensorValues = strSensorValues.split(',')

						for sensorValue in listSensorValues:
							waterPlant(sensorValue)

							print(sensorValue)
       
						# Send data to cloud
						socketClient(strSensorValues)

		time.sleep(0.1)

except KeyboardInterrupt:

	if ser.is_open:
		ser.close()

	print("Program terminated!")
