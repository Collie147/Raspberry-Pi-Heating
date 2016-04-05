#!/bin/bash
echo -e "Select your touchscreen device"
SelectedDevice="None"
DEVICES="$(sudo python /home/pi/RPiHeatingInstall/listDevices.py)"
#echo DEVICES $DEVICES
eval set $DEVICES
select opt in "$@"; do
	#echo "$opt"
	SelectedDevice="$opt"
	echo "$SelectedDevice"
	sudo python /home/pi/RPiHeatingInstall/calibrateDevice.py "$SelectedDevice"
	break
done
