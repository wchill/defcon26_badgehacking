# Firmware Notes

This is a collection of one-off notes and useful things to know about the DC26 badge firmware-wise, most of which was reverse engineered from the firmware dump as well as board schematics and datasheets.

## Getting all green letters on the human badge

1. Flash the v2 firmware to your badge. v0 and v1 have bugs that prevent legitimate badge completion.

2. Pair with all 8 badge types, making sure they have green Ns (or patch your firmware before flashing). This turns the F green and O yellow (one but not all preconditions met).

3. Punch out in the starting room (if you're paired with all 8 badges with green karma, you will still be able to go down the elevator). This turns the D green.

4. Go to the ramen shop and order chef's choice. This turns the C yellow and also unlocks another precondition for the O.

5. Go to the console room with the ARC Networks terminal and download payment records. This turns the C green.

6. Enter 0xFEEDB0B0DEADBEEF in the console/arcade room using the -/+ buttons. **This must be fed LSB first (this is not the same thing as little endian).**

7. Turn on the "Communication panel" in the robot room. This turns the O green.

8. Short C11, the 2 lower left pins on U5, or patch the firmware to make the badge think this has been done. This turns the E green.

At this stage all letters will be green.

## Debug Menu

The debug menu can be accessed by using a USB-OTG adapter plus a USB A-A cable, or by shorting the USBID/sense pin through some other mechanism. The debug menu can then be accessed via serial console.

One of two specific baud rates must be used the first time. 1112223334 will unlock the debug menu for that session only. 88 will unlock the debug menu for use with any bitrate afterwards.

There are some useful menu options present, but they are currently insufficient to complete all the badge puzzles.

## Puzzle 1 (blinking terminal) check algorithm

At 0x9d009934 in the v0 firmware, there is a subroutine dedicated to checking whether puzzle 1 is solved or not.

It returns a 3-bit-wide bitfield corresponding to the following:

* Bit 2 - was RA2 latched high?
* Bit 1 - is the byte at 0x8000018c in RAM nonzero? 1 if nonzero, 0 otherwise
* Bit 0 - is RC3 currently reading as high?

If bit 2 is set, then the blink state is "not valid" and the puzzle is not considered solved. It is currently unknown how to latch RA2 high other than the debug menu, though there supposedly exists one other way.

If bit 1 is set, then blinking was detected. Likely the way this mechanism works is based on a hardware timer plus countdown to zero; if a state transition is detected on RC3, then the counter is reset. The counter is 100, so the timer must fire 100 times with no state transitions before this bit will be unset.

If bit 0 is set, then the C11 LED is on (whether it be by shorting C11 or latching RA4 high).

## Persistent storage

Currently there are 9 bytes of nonvolatile storage being used (only 3 of those bytes have been confirmed to have an actual purpose, though this is not 100%).

At 0x9d03f800, there are 2 dwords (8 bytes) that are loaded and saved. There is additionally one extra byte at 0x9d03fffb that is also used.

f800 is the pairing byte, which is a bitfield corresponding to which badge types have been paired with. If a bit is unset in this bitfield, then the corresponding badge type was paired with (presumably since going from 0->1 would require a block erase, but 1->0 does not). This determines whether flavor text will show up for rooms.

f801 is the karma byte, which is a bitfield corresponding to which badge types have "good karma" (green N). If a bit is unset, then the corresponding badge type has good karma. This will determine which flavor text to use for rooms corresponding to a paired badge. Note that this bitfield is separate from pairing.

fffb is the "debug menu unlock" byte. If the least significant bit is set, then the debug menu can be used at any bitrate.

The purpose of f802-f807 is currently unknown, or if they even have any purpose.

## U7 8-bit LFSR easter egg

In v2 firmware, if U7 has been flipped, you can use the -/= buttons in the arcade/control rooms to feed Bobo the bit sequence 0x2BFC8E2B3561C04FBBC73FA43D5D96540D0AA008B30924CE47DA0EC67530D3 (MSB first). This will cause the arcade to display the message "You've figured out the secret to life!"

The actual decoded message is "Tymkrs + Wire + Ninja wuz here!"

The seed for the 8-bit LFSR is 0x42. Taps can be bruteforced.

## U7 64-bit LFSR behavior

In v2 firmware, with U7 unflipped, feeding 0x536E65616B20466972737420466C6970205365636F6E64 MSB first ("Sneak first, flip second") will cause the item flag to go from 0xxxxxxx to 2xxxxxxx. The purpose of this is unknown.

Feeding 0x9E1CE2C2F6FBFE198637E6F10B957DDD50A7874177A51E seems to have no effect.

The seed for the 64-bit LFSR is 0x80. Taps are unknown.