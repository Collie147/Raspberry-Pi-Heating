# Raspberry-Pi-Heating
<h3>Initial Beta Version</h3>
This is a project to create a customised home heating control on an oil fired heating system.  <br />
The main controller is a Raspberry pi running a python script that controls a 5v Relay module<br />
An SPI touchscreen provides the interface to control the system.<br />
Nginx has been set up on the Raspberry pi also to allow control over web interface.

The Raspberry pi also communicates with an ESP8266-12E to control two valves in a two storey house - upstairs and downstairs.
The valves themselves are turned by stepper motors controlled by an arduino mini.  The ESP8266 pulls pins high to indicate with valve is open. The arduino mini pulls pins high to let the ESP8266 know that the vales are now open and saves it to eeprom in case of power failure.

<i>Valve controller is optional.</i>

<h3>To setup Raspberry Pi:</h3>
Set up Raspberry pi with Raspbian Jessue as per instructions for your touchscreen.<br />
Copy RPiHeatingInstall.zip to /home/pi <br />

<code>sudo raspi-config</code><br />
Advanced --> Select A3 Memory Split --> 16<br />
Advanced --> Select A5 Device Tree --> Yes<br />
Finish<br />
<code>sudo bash /home/pi/RPiHeatingInstall/setup.sh</code><br />
Follow instructions.

Take note of your pinout for your touchscreen as the default settings may conflict with that of your touchscreen.<br />
Make changes as necessary<br />
Assemble parts according to your pinout selected.<br />

<h3>To setup valve controller:</h3>
Set up parts as shown in schematic.<br />
Modify arduino sketches to match your wifi SSID and password<br />
Upload code using Arduino IDE to ESP8266 and Arduino mini

<i>Next version should contain oil tank level meter already in Raspberry pi python script</i>
