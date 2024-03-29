let distance = 0;

let BUGGY_MIN_DISTANCE = 5;
let BUGGY_MAX_DISTANCE = 30;

let buggy_on_move = 1;
let buggy_is_here = 0;

let truncateSerialNumber = control.deviceSerialNumber().toString().slice(0, 7);

/**
 * External THREE SENSORS; Ultrasonic, Soil moisture, Light sensor
 * Onboard Microbit Sensor: Measures Ambient Temperature (We'll use both Onboard's & BME280's)
 * ONE SENSOR: BME280 (Temperature & Humidity) at RPi Edge Server
 */

// Ultra-sonic reading frequency
let us_reading_interval_onMove = 100;
let us_reading_baselineTime = 0;

// Ultra-sonic cooldown after departure
let us_cooldown_length = 30000; // 30 seconds
let us_cooldown_baselineTime = 0;
let us_cooldown = 0;

let buf_us: string[] = [];

// On-board Ambient Temperature
let onboard_temp_reading = 0;

/**
 * END
 */

let data = "";
/**
 * BASIC FOREVER LOOP
 */
basic.forever(function () {
    // ultrasonic reading
    f_ultrasonic();
});

input.onButtonPressed(Button.A, function () {
    basic.showString(control.deviceSerialNumber().toString());
})

/**
 * ULTRASONIC RANGER SENSOR (PIN 0)
 */
function f_ultrasonic() {
    if (buggy_on_move == 1 && us_cooldown == 0) {
        //starting state
        if (
            input.runningTime() - us_reading_baselineTime >=
            us_reading_interval_onMove
        ) {
            //more than 100 milliseconds have elapsed since power on
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
    // basic.showIcon(IconNames.Giraffe);

    if (BUGGY_MIN_DISTANCE < distance && distance < BUGGY_MAX_DISTANCE) {
        //distance measured by ultrasonic sensor is within 20 to 80 cm
        radio.sendString("notify=arrival");
        buggy_is_here = 1;
        buggy_on_move = 0;
        basic.showString("A");
    } else {
        basic.showString("");
    }
}

/**
 * RADIO COMMS WITH MICROBITS
 */
radio.setGroup(8);
radio.setTransmitSerialNumber(true);
radio.setTransmitPower(8);

radio.onReceivedString(function (receivedString) {
    // Hub handshake procedure
    if (receivedString.includes("handshake_plant")) {
        // Pauses during random interval to avoid collision
        randomWait();

        basic.showString("H")

        radio.sendString("enrol=" + control.deviceSerialNumber());
    }

    /**
     * COMMS between Microbits
     */
    // Plant Microbits (M1, M2, ...)
    if (receivedString.includes("sensor=")) {
        // Received command from Edge Server (RPi), get sensor readings and push northbound!
        f_send_sensor_data_to_hub();
    }

    // Buggy Microbit (notify)
    if (receivedString.includes("notify=")) {
        buf_us = receivedString.split("=");
        if (buf_us[1] == "departure") {
            if (buggy_is_here == 1) {
                // Sensor cooldown
                us_cooldown = 1;
                us_cooldown_baselineTime = input.runningTime();
                basic.showString("C");
                distance = 0;
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
            basic.showString("a");
        }
    }
});

function randomWait() {
  let rd_wait = Math.random() * 500;
  pause(rd_wait);
}

/**
 * UPLOAD/SEND SENSOR DATA TO MICROBIT HUB (By default, only do so when commanded from RPi/Fog/Edge server)
 */
function f_send_sensor_data_to_hub() {
    // data = `{'timestamp': ${input.runningTime}, 'type': 'plant_node_data', 'plant_node_id': ${control.deviceSerialNumber()}, 'readings': { 'soil_moisture': ${sm_reading}, 'light_sensor': ${light_reading}, 'onboard_temperature': ${onboard_temp_reading}}}`;

    // serial number: truncate to reduce

    //Total used 11 char (left 8)
    //include statement: 'col=': max 4 char
    //sm_reading: max 4 char
    //light_reading: max 3 char

    // analog pin P2 -> moisture, analog pin P1 -> light
    let moisture = pins.analogReadPin(AnalogPin.P2)
    let light = pins.analogReadPin(AnalogPin.P1)
    data = `${truncateSerialNumber};${moisture};${light}`;

    // Send data over Radio (Max 19 Chars per packet, so repeatedly send, RPi will accumulate).
    radio.sendString("c=" + data);

    basic.showString("S");
}
