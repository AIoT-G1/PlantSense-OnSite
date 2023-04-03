let buf_us: string[] = []

radio.onReceivedString(function (receivedString) {
    // Receive signals from other MB
    if (receivedString.includes('notify=')) {
        buf_us = receivedString.split('=')
        // Receive arrival signal
        if (buf_us[1] == "arrival") {
            stop_buggy()
            take_pictures(radio.receivedPacket(RadioPacketProperty.SerialNumber))
        }
    }
})

radio.setGroup(8)
radio.setTransmitSerialNumber(true)
radio.setTransmitPower(8)
//serial.redirectToUSB()


// Code for buggy motion ¿¿?? <--------- Xueqi
function stop_buggy() {
    basic.showString("S")
    pause(6000)

    // Notify departure disease analysis
    radio.sendString("notify=departure") 
}

// Code for disease detection <--------- Rashini
function take_pictures(curr_plant_dn: number) {
    //serial.writeLine("cmd=take_picture:" + curr_plant_dn)
    basic.showString("P")
    pause(300)
    basic.showNumber(curr_plant_dn)
}


basic.forever(function () {
    // Code for buggy motion <--------- Xueqi
})
