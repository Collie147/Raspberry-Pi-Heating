from evdev import InputDevice, list_devices
devices = map(InputDevice, list_devices())
#print '"'
for dev in devices:
	print '"' + dev.name + '\"'
#print '"'
