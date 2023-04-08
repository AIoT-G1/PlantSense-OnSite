let serial_connected = 0
let ULTRASONIC_POSITION = 40 //cm
let MAX_TANK_HEIGHT = 30 //cm
let data = ""

serial.redirectToUSB()

basic.showIcon(IconNames.Yes)
basic.forever(function () {
    // Reads water level every 30s
    //get_water_level()
    //pause(30000)
    basic.showString("W")
})

function get_water_level(){
    let value = grove.measureInCentimetersV2(DigitalPin.P0)
    let capacity = (ULTRASONIC_POSITION - value) / MAX_TANK_HEIGHT
    basic.showNumber(capacity)

    if (serial_connected == 1) {
        data ='"' + convertToText(capacity) + '"'
        serial.writeLine('water_tank='+ data)
        basic.showString("T")
    }
}

serial.onDataReceived(serial.delimiters(Delimiters.NewLine), function () {
    data = serial.readLine()
    if (data == "handshake") {
        if (serial_connected == 0) {
            serial_connected = 1
            serial_("handshake")
            basic.showString("S")
        }
    }
    else {
        if (data.split(':')[1] == "water_tank") {
            get_water_level()
        }
    }
})
