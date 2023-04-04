# Based on Lect 7: src10.py

import serial
import time


def sendCommand(command):

    command = command + '\n'
    ser.write(str.encode(command))


def waitResponse():

    response = ser.readline()
    response = response.decode('utf-8').strip()

    return response


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

                            print(sensorValue)

                time.sleep(0.1)

except KeyboardInterrupt:

    if ser.is_open:
        ser.close()

    print("Program terminated!")
