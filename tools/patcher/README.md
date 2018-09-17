# DEFCON 26 Badge Firmware Patcher

Patches a clean firmware dump from a DEFCON 26 badge. See help output for list of patches

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

Example usage: `python patcher.py --all_leds_on firmware.hex patched.hex`
