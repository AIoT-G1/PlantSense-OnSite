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
    if (capacity > 1) {
        capacity = 1
    }
    if (capacity < 0) {
        capacity = 0
    }
    basic.showNumber(capacity)

    if (serial_connected == 1) {
        //serial.writeLine("water_tank=" + convertToText(capacity))
        serial.writeLine("water_tank=AAAAAAAAAAAAAAAAAAAAAAA")
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
    if (capacity > 1) {
        capacity = 1
    }
    if (capacity < 0) {
        capacity = 0
    }
    basic.showNumber(capacity)
})

input.onButtonPressed(Button.B, function() {
    if (serial_connected == 1) {
        basic.showNumber(1)
    } else {
        basic.showNumber(0) 
    }
})


