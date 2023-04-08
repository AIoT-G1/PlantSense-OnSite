let buf_us: string[] = [];
let MICROSEC_IN_A_SEC = 1000000;
let DISTANCE_PER_SEC = 100;
let DEGREES_PER_SEC = 165;
let continue_driving = false;
let radioChannel = 7;
let uartBaudRate = 115200;

// Initialize UART
// let uart = serial;
// uart.setup(115200);

radio.onReceivedString(function (receivedString) {
    // Receive signals from other MB
    if (receivedString.includes("notify=")) {
        buf_us = receivedString.split("=");
        // Receive arrival signal
        if (buf_us[1] == "arrival") {
            stop_buggy();
            take_pictures(radio.receivedPacket(RadioPacketProperty.SerialNumber));
        }
    }
});

radio.setGroup(8);
radio.setTransmitSerialNumber(true);
radio.setTransmitPower(8);
//serial.redirectToUSB()

function stop_buggy() {
    basic.showString("S");
    continue_driving = false;
    basic.pause(300); //in milliseconds, pause for 10 minutes
    // Notify departure disease analysis

}

// Code for disease detection <--------- Rashini
function take_pictures(curr_plant_dn: number) {
    //serial.writeLine("cmd=take_picture:" + curr_plant_dn)
    basic.showString("P");
    basic.pause(300);
    basic.showNumber(curr_plant_dn);
    serial.writeString("predict")
    serial.onDataReceived("move", function () {
        continue_driving = true
    })
    // basic.uart.writeString('predict')
    radio.sendString("notify=departure");
}

function turnLeft(degrees: number): void {
    let timeToWait = (degrees * MICROSEC_IN_A_SEC) / DEGREES_PER_SEC;
    pins.servoWritePin(AnalogPin.P1, 45);
    pins.servoWritePin(AnalogPin.P2, 45);
    control.waitMicros(timeToWait);
    pins.servoWritePin(AnalogPin.P1, 90);
    pins.servoWritePin(AnalogPin.P2, 90);
}

function driveForward(distance: number): void {
    let timeToWait2 = (distance * MICROSEC_IN_A_SEC) / DISTANCE_PER_SEC;
    pins.servoWritePin(AnalogPin.P1, 0);
    pins.servoWritePin(AnalogPin.P2, 180);
    control.waitMicros(timeToWait2);
    pins.servoWritePin(AnalogPin.P1, 90);
    pins.servoWritePin(AnalogPin.P2, 90);
}

basic.forever(function () {
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
});
