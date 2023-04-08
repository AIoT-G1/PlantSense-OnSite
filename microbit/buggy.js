// Initialize UART let uart = serial;
// uart.setup(115200);
radio.onReceivedString(function (receivedString) {
    // Receive signals from other MB
    if (receivedString.includes("notify=")) {
        buf_us = receivedString.split("=");
        // Receive arrival signal
        if (buf_us[1] == "arrival") {
            stop_buggy()
            take_pictures(radio.receivedPacket(RadioPacketProperty.SerialNumber))
            continue_driving = true
        }
    }
})
function driveForward(distance: number) {
    timeToWait2 = distance * MICROSEC_IN_A_SEC / DISTANCE_PER_SEC
    pins.servoWritePin(AnalogPin.P1, 0)
    pins.servoWritePin(AnalogPin.P2, 180)
    control.waitMicros(timeToWait2)
    pins.servoWritePin(AnalogPin.P1, 90)
    pins.servoWritePin(AnalogPin.P2, 90)
}
// serial.redirectToUSB()
function stop_buggy() {
    basic.showString("S")
    continue_driving = false
    basic.pause(300)
}
// Code for disease detection <--------- Rashini
function take_pictures(curr_plant_dn: number) {
    // serial.writeLine("cmd=take_picture:" +
    // curr_plant_dn)
    basic.showString("P")
    basic.pause(300)
    // basic.showNumber(curr_plant_dn)
    serial.writeString("predict")
    basic.pause(300)

    serial.onDataReceived(serial.delimiters(Delimiters.NewLine), function () {
        // serial_response = serial.readString()
        serial_response = serial.readUntil(serial.delimiters(Delimiters.NewLine))
        basic.showString("1")
        if (serial_response == "move") {
            gotData = true
            radio.sendString("notify=departure")
        }
    })

    //gotData = true

}
function turnLeft(degrees: number) {
    timeToWait = degrees * MICROSEC_IN_A_SEC / DEGREES_PER_SEC
    pins.servoWritePin(AnalogPin.P1, 45)
    pins.servoWritePin(AnalogPin.P2, 45)
    control.waitMicros(timeToWait)
    pins.servoWritePin(AnalogPin.P1, 90)
    pins.servoWritePin(AnalogPin.P2, 90)
}
let timeToWait = 0
let gotData = false
let serial_response = ""
let timeToWait2 = 0
let DEGREES_PER_SEC = 0
let DISTANCE_PER_SEC = 0
let MICROSEC_IN_A_SEC = 0
let buf_us: string[] = []
let continue_driving = false
MICROSEC_IN_A_SEC = 1000000
DISTANCE_PER_SEC = 100
DEGREES_PER_SEC = 165
let radioChannel = 7
let uartBaudRate = 115200
radio.setGroup(8)
radio.setTransmitSerialNumber(true)
radio.setTransmitPower(8)
serial.redirectToUSB()
basic.forever(function () {
    if (gotData) {
        driveForward(350);
        turnLeft(90);
    }

    input.onButtonPressed(Button.A, function () {
        continue_driving = true;
        while (continue_driving) {
            basic.pause(500); //pauses buggy to move hand
            driveForward(350);
            turnLeft(90);
        }
    });
    input.onButtonPressed(Button.B, function () {
        continue_driving = false;
    });
})
