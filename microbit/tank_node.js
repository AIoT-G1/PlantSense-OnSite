let serial_connected = 0
let ULTRASONIC_POSITION = 40 //cm
let MAX_TANK_HEIGHT = 30 //cm
let data = ""

serial.redirectToUSB()

basic.showIcon(IconNames.Yes)
basic.forever(function () {
})

function get_water_level() {
    let value = grove.measureInCentimetersV2(DigitalPin.P0)
    let capacity = (ULTRASONIC_POSITION - value) / MAX_TANK_HEIGHT
    basic.showNumber(capacity)

    if (serial_connected == 1) {
        serial.writeLine('water_tank=' + convertToText(capacity))
        basic.showString("T")
    }
}

serial.onDataReceived(serial.delimiters(Delimiters.NewLine), function () {
    data = serial.readLine()
    if (data == "handshake") {
        if (serial_connected == 0) {
            serial_connected = 1
            serial.writeLine("handshake")
            basic.showString("S")
        }
    }
    else {
        if (data.split(':')[1] == "water_tank") {
            basic.showString("G")
            get_water_level()
        }
    }
})
input.onButtonPressed(Button.A, function() {
    let value = grove.measureInCentimetersV2(DigitalPin.P0)
    let capacity = (ULTRASONIC_POSITION - value) / MAX_TANK_HEIGHT
    basic.showNumber(capacity)
})
