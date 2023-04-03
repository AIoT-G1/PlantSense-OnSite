let distance = 0
let BUGGY_MIN_DISTANCE = 20
let BUGGY_MAX_DISTANCE = 80
let buggy_onMove = 1
let buggy_arrived = 0
let us_reading_interval_onMove = 500
let us_reading_baselineTime = 0
let buf_us:string[] = []


radio.setGroup(5)
radio.setTransmitSerialNumber(true)
radio.setTransmitPower(7)

let data = ""

basic.forever(function () {
    // Check ultrasonic reading interval
    if (buggy_onMove == 1 || buggy_arrived == 1) {
        if (input.runningTime() - us_reading_baselineTime >= us_reading_interval_onMove) {
            get_us_distance()
            us_reading_baselineTime = input.runningTime()
        }
    }
})

function get_us_distance() {
    distance = grove.measureInCentimetersV2(DigitalPin.P0)
    if (BUGGY_MIN_DISTANCE < distance && distance < BUGGY_MAX_DISTANCE) {
        radio.sendString("notify=arrival:" + control.deviceName())
        buggy_arrived = 1
        basic.showString("A")
        buggy_onMove = 0
    } else {
        radio.sendString("notify=departure:" + control.deviceName())
        //buggy_onMove = 0 -- No need to read if buggy departed from this station
        basic.showString("D")
        buggy_arrived = 0
    }
}

radio.onReceivedString(function (receivedString) {
    if (receivedString.includes('notify:')) {
        buf_us = receivedString.split('=')
        buf_us = buf_us[1].split(":")
        if (buf_us[0] == "arrival") {
            buggy_onMove = 0
        }
        if (buf_us[0] == "departure") {
            buggy_onMove = 1
        }
    }
})

