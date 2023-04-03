let distance = 0
let BUGGY_MIN_DISTANCE = 20
let BUGGY_MAX_DISTANCE = 80
let buggy_onMove = 1
let buggy_is_here = 0

// Ultra-sonic reading frequency
let us_reading_interval_onMove = 100
let us_reading_baselineTime = 0

// Ultra-sonic cooldown after departure
let us_cooldown_length = 30000 // 30 seconds
let us_cooldown_baselineTime = 0
let us_cooldown = 0

let buf_us: string[] = []


radio.setGroup(8)
radio.setTransmitSerialNumber(true)
radio.setTransmitPower(8)

let data = ""
basic.showNumber(control.deviceSerialNumber())
basic.forever(function () {
    // Check ultrasonic reading interval
    f_ultrasonic()

    // Other readings (Dan)
})

function f_ultrasonic() {
  if (buggy_onMove == 1 && us_cooldown == 0) {
    if (input.runningTime() - us_reading_baselineTime >= us_reading_interval_onMove) {
      measure_distance()
      us_reading_baselineTime = input.runningTime()
    }
  }
  if (buggy_onMove == 1 && us_cooldown == 1) {
    if (input.runningTime() - us_cooldown_baselineTime >= us_cooldown_length) {
      us_cooldown = 0
      basic.showString("D")
    }
  }
}

function measure_distance() {
    distance = grove.measureInCentimetersV2(DigitalPin.P0)
    if (BUGGY_MIN_DISTANCE < distance && distance < BUGGY_MAX_DISTANCE) {
        radio.sendString("notify=arrival")
        buggy_is_here = 1
        buggy_onMove = 0
        basic.showString("A")
    }
}

radio.onReceivedString(function (receivedString) {
    if (receivedString.includes('notify=')) {
        buf_us = receivedString.split('=')
      if (buf_us[1] == "departure") {
        if (buggy_is_here == 1) {
          // Sensor cooldown
          us_cooldown = 1
          us_cooldown_baselineTime = input.runningTime()
          basic.showString("C")
        }
        if (buggy_is_here == 0) {
          basic.showString("D")
        }
        buggy_is_here = 0
        buggy_onMove = 1
      }
      if (buf_us[1] == "arrival") {
        buggy_onMove = 0
        buggy_is_here = 0
        basic.showString("A")
      }
    }
})

