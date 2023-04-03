let buf_us:string[] = []
radio.onReceivedString(function (receivedString) {
    if (receivedString.includes('notify=')) {
        buf_us = receivedString.split('=')
        buf_us = buf_us[1].split(":")
        if (buf_us[0] == "arrival") {
            stop_buggy()
            take_pictures(buf_us[1]) //buf_us[1] includes device name
        }
    }
})

radio.setGroup(5)
radio.setTransmitSerialNumber(true)
radio.setTransmitPower(7)
//serial.redirectToUSB()

function stop_buggy() {
    basic.showString("A")
}

function take_pictures(curr_plant_dn:string) {
    //serial.writeLine("cmd=take_picture:" + control.deviceName())
    basic.showString("P")
    pause(300)
    basic.showString(curr_plant_dn)
}


basic.forever(function () {

})
