// LEGENDS
// STATE 1 = Handshake
// STATE 2 = Idle
// STATE 3 = Received Command

/**
 * RPI<->HUB: RECEIVED FROM SERIAL COMMS (RASPBERRY PI - EDGE SERVER)
 */
serial.onDataReceived(serial.delimiters(Delimiters.NewLine), function () {
  data = serial.readLine();
  if (data == "handshake") {
    if (state == 0) {
      // 1: HANDSHAKE
      state = 1;
      radio.sendString("handshake_plant");
      handshakeStartTime = input.runningTime();
    }
  } else if (data.includes("cmd:")) {
    if (state == 2) {
      if (data.includes("cmd:sensor=")) {
        // 3: IN COMMAND PROCESS
        state = 3;
        commandStartTime = input.runningTime();
        sensorValues = [];
      }

      if (data.includes("cmd:water_tank")) {
        state = 3;
        commandStartTime = input.runningTime();
        waterLevel = "";
      }
      buffer = data.split(":");
      radio.sendString("" + buffer[1]);
    }
  }
});

/**
 * HUB<->Microbit: RECEIVED FROM RADIO COMMS (PLANT MICROBITS)
 */
radio.onReceivedString(function (receivedString) {
  // Handshake procedure with other microbits
  if (receivedString.includes("enrol=")) {
    if (state == 1) {
      buffer = receivedString.split("=");
      microbitDevices.push(buffer[1]);
    }
  }
  // Data collection
  if (receivedString.includes("collect=")) {
    if (state == 3) {
      sensorValues.push(receivedString);
    }
  }

  // from Plant Nodes (c for collection)
  if (receivedString.includes("c=")) {
    // if (state == 3) {
      sensorValues.push(receivedString);
      basic.showString("R")
    // }
  }
});

let response = "";
let microbitDevices: string[] = [];
let sensorValues: string[] = [];
let waterLevel = ""
let state = 0;
let commandStartTime = 0;
let handshakeStartTime = 0;
let data = "";
let buffer: string[] = [];
handshakeStartTime = 0;
commandStartTime = 0;
radio.setGroup(8);
radio.setTransmitSerialNumber(true);
radio.setTransmitPower(7);
serial.redirectToUSB();
basic.showIcon(IconNames.Yes);

/**
 * BASIC FOREVER LOOP
 */
basic.forever(function () {
  f_show_state();

  if (state == 1) {
    if (input.runningTime() - handshakeStartTime > 10 * 1000) {
      // 2: IDLE MODE
      state = 2;
      response = "";
      for (let microbitDevice of microbitDevices) {
        if (response.length > 0) {
          response = "" + response + "," + microbitDevice;
        } else {
          response = microbitDevice;
        }
      }
      serial.writeLine("enrol=" + response);
    }
  } else if (state == 3) {
    if (input.runningTime() - commandStartTime > 10 * 1000) {
      response = "";
      for (let sensorValue of sensorValues) {
        if (response.length > 0) {
          response = "" + response + "," + sensorValue;
        } else {
          response = sensorValue;
        }
      }

      basic.showString("" + response);
      serial.writeLine("" + response);
      state = 2
    }
  }
});

function f_show_serial_number() {
  //Testing
  if (input.buttonIsPressed(Button.A)) {
    basic.showString(control.deviceSerialNumber().toString());
  }
}

function f_show_state() {
  //Default
  // if (input.buttonIsPressed(Button.B)) {
  basic.showNumber(state);
  // }
}
