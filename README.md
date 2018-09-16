# defcon26_badgehacking
Notes and things regarding hacking DEFCON 26's badge

## Just want to turn all your letters green with the least effort possible and no hardware mods?

1. Use the patcher tool (see its README) on the v2 firmware in the `firmware` folder with the `--solve_p1`, `--pairing_byte 0`, and `--karma_byte 0` patches. (`python patcher.py --solve_p1 --pairing_byte 0 --karma_byte 0 v2_firmware.hex patched_v2_firmware.hex`)

2. Flash patched firmware to badge using a PIC programmer - [see Tymkrs' instructions here](https://github.com/Professor-plum/DefCon26_Badge_Solution/blob/master/resources/Reflashing_The_Badge.docx?raw=True). If you use a PICKit3 and don't solder headers, be warned that you'll have to keep good contact with the pads using your fingers for up to a minute.

3. Reset the badge so that you are in the starting room with no actions taken (just pull the power).

4. Connect to the badge via USB and a terminal emulator.

5. Paste the following string into the terminal (or enter the keys by hand): `>+<v>-<+v--++++-+++-+++++-++-++-+-+-++++-++----++-+----++-++-++-+++-+++++++>v+`

6. Congratulations, you now have a fully green badge!