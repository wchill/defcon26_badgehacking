# Hardware Notes

This is a collection of one-off notes and useful things to know about the DC26 badge hardware-wise, most of which was reverse engineered from the firmware dump as well as board schematics and datasheets.

## ICs

The entire board runs at 3.3V.

The main microcontroller is a [PIC32MM0256GPM048](http://ww1.microchip.com/downloads/en/DeviceDoc/60001387c.pdf) with no code protection.

The U7 microcontroller is a [PIC12F508](http://ww1.microchip.com/downloads/en/DeviceDoc/41236E.pdf) in 8-pin SOIC package with code protection enabled; only something like the first 32 bytes are readable which makes firmware dumping useless.

The U4 microcontroller is a [PIC10F200](http://ww1.microchip.com/downloads/en/DeviceDoc/40001239F.pdf) in 6-pin SOT-23 package (likely with code protection enabled), masquerading as a 74LVC1G57 configurable multifunction logic gate. By default it is configured to operate as a 2 input AND gate, but by feeding it a hex string on GP0 (see below), it will swap modes to become a 2 input XOR gate until the next power cycle.

The LED controller is an [IS31FL3236](http://www.issi.com/WW/pdf/31FL3236.pdf) 36 channel I2C constant current LED sink driver.

## Hardware Puzzles

There are four hardware puzzles on the DEFCON26 badge. They correspond to the following:

1. Short the C11 capacitor on the PCB to stop the LED from blinking. Solves the E on human badges.

2. Feed 0xFEEDB0B0DEADBEEF to U4 LSB first, or desolder U7 and resolder it rotated 180 degrees (both of these will activate the LED next to U4). Currently this puzzle is not working correctly.

3. Use U7 as an LFSR somehow (currently unknown what needs to be done). Currently this puzzle is not working correctly.

4. Generate a magnetic field next to the hall effect sensor (location will vary based on badge type - on human badges it is behind the subway car on the bottom right). Changes some flavor text, unknown what else it does.

## Useful U4/U7/PIC32 pin mappings

The PIC32, U4 and U7 are all connected with SPI-like wiring. These are prime locations to attach a logic analyzer to analyze the data going in and out of the microcontrollers for LFSR analysis.

Note that for the PIC12F508 (U7), the pin assignments are when the chip is unflipped.

| Function           | PIC32MM0256GPM048 | PIC12F508 | PIC10F200 |
| ------------------ | ----------------- | --------- | --------- |
| RST                | RC4               | GP5       |           |
| CLK                | RB0               | GP1       | GP1       |
| MOSI (PIC32 -> U4) | RB1               |           | GP0       |
| MOSI (U7 -> U4)    | RC0               | GP0       | GP3       |
| MISO (U4 -> PIC32) | RC2               |           | GP2       |

Note that U4 has two inputs in XOR mode, one from the PIC32 (the bitstring to be decoded) and one from U7 (its LFSR output). U4 MISO is also connected to the LED next to U4 (the robot head on a human badge).

## Notes on U4/U7/PIC32 SPI

All microcontrollers run off of the same clock signal, which is generated in software by the PIC32.

Before any encoding/decoding operation is done, the PIC32 will hold RST high to reset U7 (note that this does not reset U4), then drive the clock once before it feeds U4 with input.

To make U4 switch to XOR mode, 0xFEEDB0B0DEADBEEF must be fed to U4 least significant bit first while driving the clock. This will look like you are feeding F77D B57B 0D0D B77F if interpreting as MSB first.

## Other useful PIC32 pins

RA4 and RA2 can control the C11 LED. Holding RA2 high (also known as CTRL1 in debug menu) will cause the LED to stop blinking, and holding RA4 high (CTRL0) will cause the LED to turn on.

RB1 (CTRL2) can be held high to toggle the U4 LED, which also seems to solve puzzle 2 (If it is working correctly).

Hall effect sensor (puzzle 4) is triggered by RD0 being pulled high.

## Other pin mappings

All following mappings are output channels on the LED controller (IS31FL3236).

Out16 corresponds to the middle blinking terminal on the human badge.

Out22 corresponds to the bottom blinking terminal on the human badge.

Out27/28/29 correspond to the RGB channels of the O on the human badge.

This will probably not be that useful except for when analyzing the firmware, to know the relative positions of the LED data in the I2C write buffer.