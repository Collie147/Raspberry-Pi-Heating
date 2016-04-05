# Raspberry-Pi-Heating
Initial Beta Version
This is a project to create a customised home heating control on an oil fired heating system.  
The main controller is a Raspberry pi that controls a 5v Relay module.  
An SPI touchscreen provides the interface to control the system.
Nginx has been set up on the Raspberry pi also to allow control over web interface.
The Raspberry pi also communicates with an ESP8266-12E to control two valves in a two storey house - upstairs and downstairs.
The valves themselves are turned by stepper motors controlled by an arduino mini.  The ESP8266 pulls pins high to indicate with valve is open.
The arduino mini pulls pins high to let the ESP8266 know that the vales are now open and saves it to eeprom in case of power failure.

Valve conroller is optional.

To setup Raspberry Pi:
Set up Raspberry pi with Raspbian Jessue as per instructions for your touchscreen.
Copy RPiHeatingInstall.zip to /home/pi 

<code>sudo raspi-config</code>
Advanced --> Select A3 Memory Split --> 16
Advanced --> Select A5 Device Tree --> Yes
Finish
<code>sudo bash /home/pi/RPiHeatingInstall/setup.sh</code>
Follow instructions.

Take note of your pinout for your touchscreen as the default settings may conflict with that of your touchscreen.
Make changes as necessary
Assemble parts according to your pinout selected.

To setup valve controller:
Set up parts as shown in schematic.
Modify arduino sketches to match your wifi SSID and password
Upload code using Arduino IDE to ESP8266 and Arduino mini

