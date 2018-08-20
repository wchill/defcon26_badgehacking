# DEFCON 26 Badge Firmware Patcher

Patches a clean firmware dump from a DEFCON 26 badge with one or more of the following patches:

	* Turn all LEDs on (the original "winning" patch)
	* Set your badge type to a different one (for example, change a human badge to a press badge)
	* Set which badges you have paired with
	* Set which badges that you've paired with have good karma (green N)
	* More to come

# Usage

You need Python 3 to run this patcher.

On MacOS/Linux, set up a clean virtualenv, then activate and install requirements:

```bash
python3 -m virtualenv env
env/bin/activate
pip install -r requirements.txt
```

If on Windows, the steps are similar - run the following in PowerShell:
```PowerShell
python -m virtualenv env
env/Scripts/activate
pip install -r requirements.txt
```

Then just run `patcher.py`. You can get usage information by running it with the `-h` switch.

Example usage: `python patcher.py --all_leds_on firmware.hex`

The patcher will backup your input file to a timestamped copy and then overwrite the original. There is no way to undo patches, so make sure you keep a copy of the original hex.
