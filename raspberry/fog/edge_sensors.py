# Based on Lect 7: src10.py

import RPi.GPIO as GPIO
import serial
import time

GPIO.setwarnings(False)

GPIO.setmode(GPIO.BCM)
GPIO.setup(5, GPIO.OUT) # solenoid valve for ___
GPIO.setup(17, GPIO.OUT) # solenoid valve for ___
GPIO.setup(18, GPIO.OUT) # water pump


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


try:

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

            while True:

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

                time.sleep(0.1)

except KeyboardInterrupt:

    if ser.is_open:
        ser.close()

    print("Program terminated!")
