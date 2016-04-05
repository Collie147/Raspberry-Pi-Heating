import sys, os
from evdev import InputDevice, list_devices
devices = map(InputDevice, list_devices())

for dev in devices:
	if sys.argv[1] == dev.name:
		print dev.fn
		os.system("sudo TSLIB_FBDEVICE=/dev/fb1 TSLIB_TSDEVICE="+dev.fn+" ts_calibrate")
		

