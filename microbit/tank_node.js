let value = 0
let capacity = 0
let serial_connected = 0
let ULTRASONIC_POSITION = 40 //cm
let MAX_TANK_HEIGHT = 30 //cm
let data = ""

serial.redirectToUSB()

basic.showIcon(IconNames.Yes)
basic.forever(function () {
    // Reads water level every 30s
    get_water_level()
    pause(30000)   
})

function get_water_level(){
    value = grove.measureInCentimetersV2(DigitalPin.P0)
    capacity = (ULTRASONIC_POSITION - value) / MAX_TANK_HEIGHT
    basic.showNumber(capacity)

    if (connected == 1) {
        data = "{'timestamp': " + input.runningTime + "" +
            ", 'type': 'water_tank'" +
         ", 'device': " + control.deviceName() + "" +
            ", 'water_level': " + convertToText(capacity) + "}"
        serial.writeLine("collect="+ data)
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
})
