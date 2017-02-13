# Pi-Wakeup-Light
A wakeup light powered by a Raspberry Pi and white LED strip

---

## Prerequisites
This project is based off of the tutorial [here](http://dordnung.de/raspberrypi-ledstrip/) by [dordnung](https://github.com/dordnung). Following that guide will help a lot towards getting this going!

For the wakeup light I am using a white LED strip - this simplifies the tutorial above to just a single MOSFET circuit.

## Usage

`python ./wakeup.py 06:30`

## Buttons and LED

The LED will be lit when an alarm is set.

The button is programmed to disable the alarm on a quick press (the LED will go out). If the button is held for 1 second or more the light will come on - and off when held again.

## Circuit Diagram

![wakeup_bb](https://cloud.githubusercontent.com/assets/1861980/22898101/f6b78920-f21d-11e6-96cd-0ae462947c4d.png)
