let distance = 0;
let BUGGY_MIN_DISTANCE = 20;
let BUGGY_MAX_DISTANCE = 80;
let buggy_on_move = 1;
let buggy_is_here = 0;

// Ultra-sonic reading frequency
let us_reading_interval_onMove = 100;
let us_reading_baselineTime = 0;

// Ultra-sonic cooldown after departure
let us_cooldown_length = 30000; // 30 seconds
let us_cooldown_baselineTime = 0;
let us_cooldown = 0;

/// Soil Moisture (sm) reading
let sm_reading = 0;

let buf_us: string[] = [];

radio.setGroup(8);
radio.setTransmitSerialNumber(true);
radio.setTransmitPower(8);

let data = "";
basic.showNumber(control.deviceSerialNumber());

/**
 * BASIC FOREVER LOOP
 */
basic.forever(function () {
  // ultrasonic reading
  f_ultrasonic();

  // soil moisture reading
  f_soil_moisture();

  // Other readings <--------- Dan
});

/**
 * SOIL MOISTURE
 */
function f_soil_moisture() {
  sm_reading = pins.analogReadPin(AnalogPin.P0);
  led.plotBarGraph(sm_reading, 1023);
  if (input.buttonIsPressed(Button.A)) {
    basic.showString("" + sm_reading);
  }
}

/**
 * ULTRA SONIC
 */
function f_ultrasonic() {
  if (buggy_on_move == 1 && us_cooldown == 0) {
    if (
      input.runningTime() - us_reading_baselineTime >=
      us_reading_interval_onMove
    ) {
      measure_distance();
      us_reading_baselineTime = input.runningTime();
    }
  }
  if (buggy_on_move == 1 && us_cooldown == 1) {
    if (input.runningTime() - us_cooldown_baselineTime >= us_cooldown_length) {
      us_cooldown = 0;
      basic.showString("D");
    }
  }
}

function measure_distance() {
  distance = grove.measureInCentimetersV2(DigitalPin.P0);
  if (BUGGY_MIN_DISTANCE < distance && distance < BUGGY_MAX_DISTANCE) {
    radio.sendString("notify=arrival");
    buggy_is_here = 1;
    buggy_on_move = 0;
    basic.showString("A");
  }
}
/**
 * ENDS
 */

radio.onReceivedString(function (receivedString) {
  // Communication between MicroBits (notify)
  if (receivedString.includes("notify=")) {
    buf_us = receivedString.split("=");
    if (buf_us[1] == "departure") {
      if (buggy_is_here == 1) {
        // Sensor cooldown
        us_cooldown = 1;
        us_cooldown_baselineTime = input.runningTime();
        basic.showString("C");
      }
      if (buggy_is_here == 0) {
        basic.showString("D");
      }
      buggy_is_here = 0;
      buggy_on_move = 1;
    }
    if (buf_us[1] == "arrival") {
      buggy_on_move = 0;
      buggy_is_here = 0;
      basic.showString("A");
    }
  }
});
