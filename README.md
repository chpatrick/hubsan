Python A7105/Hubsan X4 library
======

Python 2 library for controlling a Hubsan X4 quadcopter, based on the [Deviation firmware](https://bitbucket.org/PhracturedBlue/deviation).

## Usage
* Get a [C232HM-DDHSL](http://www.ftdichip.com/Documents/DataSheets/Cables/DS_C232HM_MPSSE_CABLE.pdf) or equivalent MPSSE cable. Make sure you get one with a 3.3v VDD or you might fry your A7105.
* Attach the cable to your A7105 chip according to the instructions below.
* Install [libmpsse](https://code.google.com/p/libmpsse/).
* Enjoy!

### Wiring
![A7105 pinout](http://www.electrodragon.com/w/images/d/d8/A7105_pin_definition.png)

A7105 | wire | color
----- | ---- | -----
vdd   | VCC  | red
gnd (both pins)  | GND  | black
sdio  | DO   | yellow
sck   | SK   | orange
scs   | CS   | brown
gio1  | DI   | green
