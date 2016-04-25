#!/usr/bin/python
# Raspberry Pi Heating system Written by Collie147
 

import pygame, sys, os, time, json, thread, datetime, select, socket, SocketServer, threading, pywapi, string, re
import xml.etree.cElementTree as XML
from time import sleep
import RPi.GPIO as GPIO
from threading import Timer
from threading import Thread

GPIO_RED_LED = *RED_LED_GPIO_PIN
GPIO_GREEN_LED = *GREEN_LED_GPIO_PIN
GPIO_RELAY = *RELAY_GPIO_PIN

newBoot = True
XMLWriteRequest = False
XMLWriteTime = 0
XMLWriteDelay = 5
Relay1DelayTime = 1
Relay2DelayTime = 2
Relay1Time = 0
Relay2Time = 0
Relay1Count = 0
Relay2Count = 0
Relay1Status = False
Relay2Status = False
PreviousUpstairs = False
PreviousDownstairs = False
ESP8266Online = False
ESP8266CheckDelay = 900
ESP8266PreviousCheck = 0
PreviousSystemMode = 0
PreviousSystemModeBoost = 0
BoostTimer = 0
BoostDelay = 0
BoostCount = 0
Upstairs = False
Downstairs = False	
listening = True
running = True
selecting = False
screenRefreshRequested = False
SystemMode = 0
OilLevel = 0
OilLevelText = "OilLevel = n/a"
OutsideTemp = 0
OutsideTempText = "n/a"
OutsideBatt = 0
MessageSent = False
RelayStatus = False
RelayChange = False
WeatherCheck = 0
WeatherDelay = 3600
WeatherCount = 0
SunRiseSet = ""
Weather = ""
TCP_IPReceive = "*IPADDRESS"
TCP_PORTReceive = 5005
BUFFER_SIZE = 256

GPIO.setmode(GPIO.BCM) # Set GPIO to Pin mode rather than GPIO mode
GPIO.setup(GPIO_RED_LED, GPIO.OUT) # Pin 18 or GPIO 24 | LED RED
GPIO.setup(GPIO_GREEN_LED, GPIO.OUT) # Pin 16 or GPIO 23 | LED GREEN
GPIO.setup(GPIO_RELAY, GPIO.OUT) # Pin 15 or GPIO 22 | Heating Relay
GPIO.output(GPIO_RED_LED, False)
GPIO.output(GPIO_GREEN_LED, False)
GPIO.output(GPIO_RELAY, False)

zoneUpChange = False
zoneDownChange = False

runningDelay = 10
runningCheck = 0
retryTimes = 0
#Listen433Loops = 0
def openSocket2():
	global socket2Open
	global sock2
	global ESP8266Online
	if os.system("ping -c 1 *ESP8266ValveIPADDRESS") == 0:
		try:
			TCP_IPSend = "*ESP8266ValveIPADDRESS"
			TCP_PORTSend = 81
			sock2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			sock2.connect((TCP_IPSend, TCP_PORTSend))
			sock2.settimeout(10)
			socket2Open = True
			ESP8266Online = True
			GPIO.output(GPIO_GREEN_LED, True)
		except socket.error:
			print "Cound not create socket to", TCP_IPSend, " ", TCP_PORTSend, socket.error
			socket2Open = False
			GPIO.output(GPIO_GREEN_LED, False)
			
	else :
		ESP8266Online = False
		socket2Open = False
		GPIO.output(GPIO_GREEN_LED, False)
		print "ESP8266 is not online" 
		
openSocket2()		

timeboxstatus = range(97)
timeboxout = range(97)
timebox = range(97)
timetext = range(97)
timetextpos = range(97)
for x in range (1, 97) :
	timeboxstatus[x] = False
	
def ReadJSONFile() :
	global timeboxstatus
	try:
		FileTimeRead = open('/var/www/html/json.txt', 'r')
		FileTimeRead.seek(0)
		print "Reading JSON File"
		timeboxstatus = json.load(FileTimeRead)
		FileTimeRead.close()
	except Exception, e:
		print "ReadJSONFile Error:", repr(e)
		print "Copying backup JSON"
		os.system('sudo cp /var/www/html/json.bak /var/www/html/json.txt')
		ReadXML()

def WriteJSONFile() :
	FileTimeSave = open('/var/www/html/json.txt', 'w+')
	print "Saving JSON file"
	json.dump(timeboxstatus, FileTimeSave)
	FileTimeSave.flush()
	FileTimeSave.close()

def ReadXML():
	global SystemMode
	global Downstairs
	global Upstairs
	global PreviousSystemMode
	global PreviousUpstairs
	global PreviousDownstairs
	global ESP8266Online
	global OilLevel
	global OutsideBatt
	global OutsideBattText
	global OutsideTemp
	global OutsideTempText
	global newBoot
	try:
		PreviousSystemMode = SystemMode
		PreviousUpstairs = Upstairs
		PreviousDownstairs  = Downstairs
		tree = XML.parse('/var/www/html/ButtonStatus.xml')
		root = tree.getroot()
		Off = root[0].text
		if (root[1].text == "True") :
			Upstairs = True
		elif (root[1].text == "False") :
			Upstairs = False
		if (root[2].text == "True") :
			Downstairs = True
		elif (root[2].text == "False") :
			Downstairs = False
	
		Timer = root[3].text
		Timed = root[5].text
		Constant = root[6].text
		if (Off == "True") :
			SystemMode = 0
		if (Timer == "True") :
			SystemMode = 1
		if (Timed == "True") :
			SystemMode = 2
		if (Constant == "True") :
			SystemMode = 3
		if (PreviousSystemMode != SystemMode):
			print "SystemMode changed to ", SystemMode
		
		if (PreviousUpstairs != Upstairs):
			print "Upstairs changed to ", Upstairs
		
		if (PreviousDownstairs != Downstairs) :
			print "Downstairs changed to ", Downstairs
		if root[7].text== "True" :
			ESP8266Online == True
			
		else :
			ESP8266Online == False
			
		if newBoot == True :
			newBoot = False
			print "New Boot"
			if SystemMode == 1 :
				print "SystemMode=",SystemMode
				SystemMode = 0
				print "SystemMode=",SystemMode
		OilLevel = str(root[9].text)
		OilLevelText = "OilLevel = "
		OilLevelText += OilLevel
		OutsideTemp = str(root[10].text)
		OutsideTempText = "Ground Temp = "
		OutsideTempText += OutsideTemp
		OutsideBatt = str(root[11].text)
		OutsideBattText = "Battery Vol = "
		OutsideTempText += OutsideTemp
	except Exception, e:
			print "ReadXML Error:", repr(e)
			print "Copying backup XML"
			os.system('sudo cp /var/www/html/ButtonStatus.bak /var/www/html/ButtonStatus.xml')
			ReadXML()

ReadXML()

def WriteXML():
	root = XML.Element("root")
	
	if (SystemMode == 0) :#1
		XML.SubElement(root, "field").text = "True"
	else :
		XML.SubElement(root, "field").text = "False"
	
	print "Upstairs value is ", Upstairs
	print "Downstairs value is ", Downstairs
	if 	(Upstairs == True) or (Upstairs == "True"):#2
		XML.SubElement(root, "field").text = "True"
		print "Upstairs Written as TRUE"
	elif (Upstairs == False) or (Upstairs == "False"):
		XML.SubElement(root, "field").text = "False"
		print "Upstairs Written as FALSE"
		
	if (Downstairs == True) or (Downstairs == "True"):#3
		XML.SubElement(root, "field").text = "True"
	elif (Downstairs == False) or (Downstairs == "False"):
		XML.SubElement(root, "field").text = "False"
		
	if (SystemMode == 1) :#4
		XML.SubElement(root, "field").text = "True"
		XML.SubElement(root, "field").text = BoostTimer
	else :
		XML.SubElement(root, "field").text = "False"
		XML.SubElement(root, "field").text = "  Boost   "
		
	if (SystemMode == 2) :#5
		XML.SubElement(root, "field").text = "True"
	else :
		XML.SubElement(root, "field").text = "False"
		
	if (SystemMode == 3) :#6

		XML.SubElement(root, "field").text = "True"
	else :
		XML.SubElement(root, "field").text = "False"
		
	if (ESP8266Online == True) :
		XML.SubElement(root, "field").text = "True"
	else :
		XML.SubElement(root, "field").text = "False"	
	if (RelayStatus == True) :
		XML.SubElement(root, "field").text = "True"
	else :
		XML.SubElement(root, "field").text = "False"
	XML.SubElement(root, "field").text = str(OilLevel)
	XML.SubElement(root, "field").text = str(OutsideTemp)
	XML.SubElement(root, "field").text = str(OutsideBatt)
	tree = XML.ElementTree(root)
	tree = XML.ElementTree(root)
	tree.write("/var/www/html/ButtonStatus.xml")
	

def WeatherDisplay() :
	
	global WeatherCheck
	global WeatherDelay
	global WeatherCount
	WeatherCount = (time.time() - WeatherCheck)
	if WeatherCount > WeatherDelay :
		print "Getting Weather Info"
		global yahoo_result
		global SunRiseSet
		global Weather
		global RainHumid
		global Wind
		global WindSpeed
		u = u"\N{DEGREE SIGN}"
		a = u.encode('utf-8')
		try:
			weather_result = pywapi.get_weather_from_weather_com('EIXX0003')
		except Exception, e:
			weather_result = "n/a"
			print "weather_result error", repr(e)
		try:
			WindSpd = str(weather_result['current_conditions']['wind']['speed'])
			WindDir = (weather_result['current_conditions']['wind']['direction'])
		
			if (WindDir >= 349) or (WindDir <= 11) :
				WindDirection = "NORTH"
			elif (WindDir >= 12) and (WindDir <= 33) :
				WindDirection = "North-North-East"
			elif (WindDir >= 34) and (WindDir <= 56) :
				WindDirection = "North-East"
			elif (WindDir >= 57) and (WindDir <= 78) :
				WindDirection = "East-North-East"
			elif (WindDir >= 79) and (WindDir <= 101) :
				WindDirection = "EAST"
			elif (WindDir >= 102) and (WindDir <= 123) :
				WindDirection = "East-South-East"
			elif (WindDir >= 124) and (WindDir <= 146) :
				WindDirection = "South-East"
			elif (WindDir >= 147) and (WindDir <= 168) :
				WindDirection = "South-South-East"
			elif (WindDir >= 169) and (WindDir <= 191) :
				WindDirection = "SOUTH"
			elif (WindDir >= 192) and (WindDir <= 213) :
				WindDirection = "South-South-West"
			elif (WindDir >= 214) and (WindDir <= 236) :
				WindDirection = "South-West"
			elif (WindDir >= 237) and (WindDir <= 258) :
				WindDirection = "West-South-West"
			elif (WindDir >= 259) and (WindDir <= 281) :
				WindDirection = "WEST"
			elif (WindDir >= 282) and (WindDir <= 303) :
				WindDirection = "West-North-West"
			elif (WindDir >= 304) and (WindDir <= 326) :
				WindDirection = "North-West"
			elif (WindDir >= 327) and (WindDir <= 348) :
				WindDirection = "North-North-West"
			Wind = "Wind: " + WindDirection
			WindSpeed = WindSpd + " km/h"
			
		except Exception, e:
			Wind = "n/a"
			WindSpeed = "n/a"
			print "Wind error", repr(e)
		
		try :
			RainHumid = str("Humidity: " + (weather_result['forecasts'][0]['day']['humidity']) + "%" + "         Rain Chance: " + (weather_result['forecasts'][0]['day']['chance_precip']) + "%")
		except Exception, e:
			RainHumid = "n/a"
			print "RainHumid error", repr(e)
		try:
			yahoo_result = pywapi.get_weather_from_yahoo('EIXX0003', 'metric')
		except Exception, e:
			yahoo_result = "n/a"
			print "yahoo_result", repr(e)
		try:
			SunRiseSet = str("Sunrise: " + (yahoo_result['astronomy']['sunrise']) + "   -   Sunset: " + (yahoo_result['astronomy']['sunset']))
		except Exception, e:
			SunRiseSet = "n/a"
			print "SunRiseSet error", repr(e)
		try:
			Weather = str((yahoo_result['condition']['text']) + " and " + (yahoo_result['condition']['temp']))
			Weather = Weather + u + "C"
		except Exception, e:
			Weather = "n/a"
			print "Weather error", repr(e)
		WeatherCheck = time.time()


global theTime
theTime=time.strftime("%H:%M:%S", time.localtime())

ReadJSONFile()
Width = 26
Height = 30
	
def ClockTime() : # Updates the on-screen clock
	theTime=time.strftime("%H:%M:%S", time.localtime())
	hrs = 0
	min = 0
	hrsString = ""
	minString = ""
	for w in range (1, 97) :
		if min == 60 :
			hrs = hrs + 1
			min = 0
		if min == 0 :
			minString = "0" + str(min)
		else :
			minString = str(min)
		if hrs > 23 :
			hrs = 0
		if hrs < 10 :
			hrsString = "0" + str(hrs)
		else :
			hrsString = str(hrs)
			
		
		min = min + 15


	

def XMLWriteRequestCheck() :# Checks if a the XML is to be written to and writes to it.  This avoids two processes writing at the same time
	global XMLWriteRequest
	if (XMLWriteRequest == True) :
		WriteXML()
		XMLWriteRequest = False

def RelayTimedMode() :# If the heating is in timed mode this checks the current time and if the slot is marked as true it turns on the relay
	jsonTimer = time.time()
	jsonTimerDelay = jsonTimer + 60
	global SystemMode
	if running == True:
		if SystemMode == 2 :
			timeNow = datetime.datetime.now()
			hrs = timeNow.hour
			min = timeNow.minute
			quarter1 = xrange(0,15)
			quarter2 = xrange(15,30)
			quarter3 = xrange(30,45)
			quarter4 = xrange(44,60)
			if (jsonTimerDelay < time.time()) :
				ReadJSONFile()
				jsonTimer = time.time()
				jsonTimerDelay = jsonTimer + 60
			if (hrs == 0) and (min in quarter1) and (timeboxstatus[1] == True) :
				TimedModeRelay = True
			elif (hrs == 0) and (min in quarter2) and (timeboxstatus[2] == True) :
				TimedModeRelay = True
			elif (hrs == 0) and (min in quarter3) and (timeboxstatus[3] == True) :
				TimedModeRelay = True
			elif (hrs == 0) and (min in quarter4) and (timeboxstatus[4] == True) :
				TimedModeRelay = True
			elif (hrs == 1) and (min in quarter1) and (timeboxstatus[5] == True) :
				TimedModeRelay = True
			elif (hrs == 1) and (min in quarter2) and (timeboxstatus[6] == True) :
				TimedModeRelay = True
			elif (hrs == 1) and (min in quarter3) and (timeboxstatus[7] == True) :
				TimedModeRelay = True
			elif (hrs == 1) and (min in quarter4) and (timeboxstatus[8] == True) :
				TimedModeRelay = True
			elif (hrs == 2) and (min in quarter1) and (timeboxstatus[9] == True) :
				TimedModeRelay = True
			elif (hrs == 2) and (min in quarter2) and (timeboxstatus[10] == True) :
				TimedModeRelay = True
			elif (hrs == 2) and (min in quarter3) and (timeboxstatus[11] == True) :
				TimedModeRelay = True
			elif (hrs == 2) and (min in quarter4) and (timeboxstatus[12] == True) :
				TimedModeRelay = True
			elif (hrs == 3) and (min in quarter1) and (timeboxstatus[13] == True) :
				TimedModeRelay = True
			elif (hrs == 3) and (min in quarter2) and (timeboxstatus[14] == True) :
				TimedModeRelay = True
			elif (hrs == 3) and (min in quarter3) and (timeboxstatus[15] == True) :
				TimedModeRelay = True
			elif (hrs == 3) and (min in quarter4) and (timeboxstatus[16] == True) :
				TimedModeRelay = True
			elif (hrs == 4) and (min in quarter1) and (timeboxstatus[17] == True) :
				TimedModeRelay = True
			elif (hrs == 4) and (min in quarter2) and (timeboxstatus[18] == True) :
				TimedModeRelay = True
			elif (hrs == 4) and (min in quarter3) and (timeboxstatus[19] == True) :
				TimedModeRelay = True
			elif (hrs == 4) and (min in quarter4) and (timeboxstatus[20] == True) :
				TimedModeRelay = True
			elif (hrs == 5) and (min in quarter1) and (timeboxstatus[21] == True) :
				TimedModeRelay = True
			elif (hrs == 5) and (min in quarter2) and (timeboxstatus[22] == True) :
				TimedModeRelay = True
			elif (hrs == 5) and (min in quarter3) and (timeboxstatus[23] == True) :
				TimedModeRelay = True
			elif (hrs == 5) and (min in quarter4) and (timeboxstatus[24] == True) :
				TimedModeRelay = True
			elif (hrs == 6) and (min in quarter1) and (timeboxstatus[25] == True) :
				TimedModeRelay = True
			elif (hrs == 6) and (min in quarter2) and (timeboxstatus[26] == True) :
				TimedModeRelay = True
			elif (hrs == 6) and (min in quarter3) and (timeboxstatus[27] == True) :
				TimedModeRelay = True
			elif (hrs == 6) and (min in quarter4) and (timeboxstatus[28] == True) :
				TimedModeRelay = True
			elif (hrs == 7) and (min in quarter1) and (timeboxstatus[29] == True) :
				TimedModeRelay = True
			elif (hrs == 7) and (min in quarter2) and (timeboxstatus[30] == True) :
				TimedModeRelay = True
			elif (hrs == 7) and (min in quarter3) and (timeboxstatus[31] == True) :
				TimedModeRelay = True
			elif (hrs == 7) and (min in quarter4) and (timeboxstatus[32] == True) :
				TimedModeRelay = True
			elif (hrs == 8) and (min in quarter1) and (timeboxstatus[33] == True) :
				TimedModeRelay = True
			elif (hrs == 8) and (min in quarter2) and (timeboxstatus[34] == True) :
				TimedModeRelay = True
			elif (hrs == 8) and (min in quarter3) and (timeboxstatus[35] == True) :
				TimedModeRelay = True
			elif (hrs == 8) and (min in quarter4) and (timeboxstatus[36] == True) :
				TimedModeRelay = True
			elif (hrs == 9) and (min in quarter1) and (timeboxstatus[37] == True) :
				TimedModeRelay = True
			elif (hrs == 9) and (min in quarter2) and (timeboxstatus[38] == True) :
				TimedModeRelay = True
			elif (hrs == 9) and (min in quarter3) and (timeboxstatus[39] == True) :
				TimedModeRelay = True
			elif (hrs == 9) and (min in quarter4) and (timeboxstatus[40] == True) :
				TimedModeRelay = True
			elif (hrs == 10) and (min in quarter1) and (timeboxstatus[41] == True) :
				TimedModeRelay = True
			elif (hrs == 10) and (min in quarter2) and (timeboxstatus[42] == True) :
				TimedModeRelay = True
			elif (hrs == 10) and (min in quarter3) and (timeboxstatus[43] == True) :
				TimedModeRelay = True
			elif (hrs == 10) and (min in quarter4) and (timeboxstatus[44] == True) :
				TimedModeRelay = True
			elif (hrs == 11) and (min in quarter1) and (timeboxstatus[45] == True) :
				TimedModeRelay = True
			elif (hrs == 11) and (min in quarter2) and (timeboxstatus[46] == True) :
				TimedModeRelay = True
			elif (hrs == 11) and (min in quarter3) and (timeboxstatus[47] == True) :
				TimedModeRelay = True
			elif (hrs == 11) and (min in quarter4) and (timeboxstatus[48] == True) :
				TimedModeRelay = True
			elif (hrs == 12) and (min in quarter1) and (timeboxstatus[49] == True) :
				TimedModeRelay = True
			elif (hrs == 12) and (min in quarter2) and (timeboxstatus[50] == True) :
				TimedModeRelay = True
			elif (hrs == 12) and (min in quarter3) and (timeboxstatus[51] == True) :
				TimedModeRelay = True
			elif (hrs == 12) and (min in quarter4) and (timeboxstatus[52] == True) :
				TimedModeRelay = True
			elif (hrs == 13) and (min in quarter1) and (timeboxstatus[53] == True) :
				TimedModeRelay = True
			elif (hrs == 13) and (min in quarter2) and (timeboxstatus[54] == True) :
				TimedModeRelay = True
			elif (hrs == 13) and (min in quarter3) and (timeboxstatus[55] == True) :
				TimedModeRelay = True
			elif (hrs == 13) and (min in quarter4) and (timeboxstatus[56] == True) :
				TimedModeRelay = True
			elif (hrs == 14) and (min in quarter1) and (timeboxstatus[57] == True) :
				TimedModeRelay = True
			elif (hrs == 14) and (min in quarter2) and (timeboxstatus[58] == True) :
				TimedModeRelay = True
			elif (hrs == 14) and (min in quarter3) and (timeboxstatus[59] == True) :
				TimedModeRelay = True
			elif (hrs == 14) and (min in quarter4) and (timeboxstatus[60] == True) :
				TimedModeRelay = True
			elif (hrs == 15) and (min in quarter1) and (timeboxstatus[61] == True) :
				TimedModeRelay = True
			elif (hrs == 15) and (min in quarter2) and (timeboxstatus[62] == True) :
				TimedModeRelay = True
			elif (hrs == 15) and (min in quarter3) and (timeboxstatus[63] == True) :
				TimedModeRelay = True
			elif (hrs == 15) and (min in quarter4) and (timeboxstatus[64] == True) :
				TimedModeRelay = True
			elif (hrs == 16) and (min in quarter1) and (timeboxstatus[65] == True) :
				TimedModeRelay = True
			elif (hrs == 16) and (min in quarter2) and (timeboxstatus[66] == True) :
				TimedModeRelay = True
			elif (hrs == 16) and (min in quarter3) and (timeboxstatus[67] == True) :
				TimedModeRelay = True
			elif (hrs == 16) and (min in quarter4) and (timeboxstatus[68] == True) :
				TimedModeRelay = True
			elif (hrs == 17) and (min in quarter1) and (timeboxstatus[69] == True) :
				TimedModeRelay = True
			elif (hrs == 17) and (min in quarter2) and (timeboxstatus[70] == True) :
				TimedModeRelay = True
			elif (hrs == 17) and (min in quarter3) and (timeboxstatus[71] == True) :
				TimedModeRelay = True
			elif (hrs == 17) and (min in quarter4) and (timeboxstatus[72] == True) :
				TimedModeRelay = True
			elif (hrs == 18) and (min in quarter1) and (timeboxstatus[73] == True) :
				TimedModeRelay = True
			elif (hrs == 18) and (min in quarter2) and (timeboxstatus[74] == True) :
				TimedModeRelay = True
			elif (hrs == 18) and (min in quarter3) and (timeboxstatus[75] == True) :
				TimedModeRelay = True
			elif (hrs == 18) and (min in quarter4) and (timeboxstatus[76] == True) :
				TimedModeRelay = True
			elif (hrs == 19) and (min in quarter1) and (timeboxstatus[77] == True) :
				TimedModeRelay = True
			elif (hrs == 19) and (min in quarter2) and (timeboxstatus[78] == True) :
				TimedModeRelay = True
			elif (hrs == 19) and (min in quarter3) and (timeboxstatus[79] == True) :
				TimedModeRelay = True
			elif (hrs == 19) and (min in quarter4) and (timeboxstatus[80] == True) :
				TimedModeRelay = True
			elif (hrs == 20) and (min in quarter1) and (timeboxstatus[81] == True) :
				TimedModeRelay = True
			elif (hrs == 20) and (min in quarter2) and (timeboxstatus[82] == True) :
				TimedModeRelay = True
			elif (hrs == 20) and (min in quarter3) and (timeboxstatus[83] == True) :
				TimedModeRelay = True
			elif (hrs == 20) and (min in quarter4) and (timeboxstatus[84] == True) :
				TimedModeRelay = True
			elif (hrs == 21) and (min in quarter1) and (timeboxstatus[85] == True) :
				TimedModeRelay = True
			elif (hrs == 21) and (min in quarter2) and (timeboxstatus[86] == True) :
				TimedModeRelay = True
			elif (hrs == 21) and (min in quarter3) and (timeboxstatus[87] == True) :
				TimedModeRelay = True
			elif (hrs == 21) and (min in quarter4) and (timeboxstatus[88] == True) :
				TimedModeRelay = True
			elif (hrs == 22) and (min in quarter1) and (timeboxstatus[89] == True) :
				TimedModeRelay = True
			elif (hrs == 22) and (min in quarter2) and (timeboxstatus[90] == True) :
				TimedModeRelay = True
			elif (hrs == 22) and (min in quarter3) and (timeboxstatus[91] == True) :
				TimedModeRelay = True
			elif (hrs == 22) and (min in quarter4) and (timeboxstatus[92] == True) :
				TimedModeRelay = True
			elif (hrs == 23) and (min in quarter1) and (timeboxstatus[93] == True) :
				TimedModeRelay = True
			elif (hrs == 23) and (min in quarter2) and (timeboxstatus[94] == True) :
				TimedModeRelay = True
			elif (hrs == 23) and (min in quarter3) and (timeboxstatus[95] == True) :
				TimedModeRelay = True
			elif (hrs == 23) and (min in quarter4) and (timeboxstatus[96] == True) :
				TimedModeRelay = True
			else :
				TimedModeRelay = False
			global RelayStatus
			global XMLWriteRequest
			global RelayChange
			if (TimedModeRelay == True) :
				if GPIO.input(GPIO_RELAY) == False :
					global RelayChange
					GPIO.output(GPIO_RELAY, True)
					GPIO.output(GPIO_RED_LED, True)
					RelayStatus = True
					XMLWriteRequest = True
			else :
				if GPIO.input(GPIO_RELAY) == True :
					GPIO.output(GPIO_RELAY, False)
					GPIO.output(GPIO_RED_LED, False)
					RelayStatus = False
					XMLWriteRequest = True
	
def TimerBox():# This function runs the Boost mode, counts down the timer, changes it to hrs+mins and displays it on screen and once the mode is active and the timer is greater than 0, it turns on the relay.
	global SystemMode
	global BoostDelay
	global BoostCount
	global BoostTimer
	global XMLWriteRequest
	global XMLWriteTime
	global XMLWriteDelay
	global RelayStatus
	global PreviousSystemModeBoost
	global screenRefreshRequested
	#print "BoostDelay: ", BoostDelay, "BoostCount: ", BoostCount
	
	TIMER = int(BoostDelay - (time.time() - BoostCount))
	#print "TIMER:", TIMER
	if SystemMode == 1 and TIMER > 0:
		Secs = int("%.0f" %(BoostDelay - (time.time() - BoostCount)))
		BoostTimer = "0"
		BoostTimer += str(datetime.timedelta(seconds = Secs))
		if GPIO.input(GPIO_RELAY) == False :
			print "Turning On"
			GPIO.output(GPIO_RELAY, True)
			GPIO.output(GPIO_RED_LED, True)
			RelayStatus = True
			XMLWriteRequest = True
		if ((time.time() - XMLWriteTime) > XMLWriteDelay) :	
			print "Writing Time to XML"
			WriteXML()	
			XMLWriteTime = time.time()
	elif SystemMode == 1 and TIMER <= 0:
		#print "TIMEROUT"
				
		if GPIO.input(GPIO_RELAY) == True :
			print "Turning Off", "PreviousSystem = ", PreviousSystemModeBoost
			GPIO.output(GPIO_RELAY, False)
			GPIO.output(GPIO_RED_LED, False)
			BoostTimer = "0:00:00"
			if PreviousSystemModeBoost == 1 :
				PreviousSystemModeBoost = 0
			SystemMode = PreviousSystemModeBoost
			screenRefreshRequested = True
			RelayStatus = False
			WriteXML()	
		
def TCPClientSend(data) :# Sends TCP instructions to the valve controller (if it's on and available) and waits for response.  
	global retryTimes
	global Upstairs
	global Downstairs
	global XMLWriteRequest
	global socket2Open
	global ESP8266Online
	global MessageSent
	if (socket2Open) :
		try: 
			sock2.sendall(data)
			response = sock2.recv(BUFFER_SIZE)
			print "Received: {}".format(response)
			if (data != "status") :
									
				if (response == "confirmed") :
					retryTimes = retryTimes + 1
					ESP8266Online = True
					XMLWriteRequest = True
					MessageSent = True
					GPIO.output(GPIO_GREEN_LED, True)
					print "MessageSent1 = ", MessageSent
				else :
					print "Send Failure"
					
			else :
				print response[9:10], response[22:23]
					
				if  (response[0:8] == "upstairs"):
					if (response[9:10] == "0") :
						Upstairs = False
						print "upstairs", Upstairs
						XMLWriteRequest = True
						zoneUpChange = True
					elif (response[9:10] == "1") :
						Upstairs = True
						print "upstairs", Upstairs
						XMLWriteRequest = True
						zoneUpChange = True
					if (response[22:23] == "0") :
						Downstairs = False
						print "downstairs", Downstairs
						XMLWriteRequest = True
						zoneDownChange = True
					elif (response[22:23] == "1") :
						Downstairs = True
						print "downstairs", Downstairs
						XMLWriteRequest = True
						zoneDownChange = True
					MessageSent = True
					print "MessageSent2 = ", MessageSent
					ESP8266Online = True
					XMLWriteRequest = True
		except Exception, e:
			print "TCPClientSend", repr(e)
			print "Sending data to Zone Controller timed out on message ", data
			if os.system("ping -c 1 *ESP8266ValveIPADDRESS") == 0:
				print "*ESP8266ValveIPADDRESS appears to be up"
				openSocket2()
				ESP8266Online = True
										
			else :
				print "*ESP8266ValveIPADDRESS appears to be down"
				socket2Open = False
				ESP8266Online = False
				GPIO.output(GPIO_GREEN_LED, False)
			XMLWriteRequest = True
	else :
		print "TCPClientSend socket closed"
		openSocket2()
	
	if MessageSent == True:
		print "MessageSent3 = ", MessageSent
		MessageSent = False
		print "MessageSent4= ", MessageSent
		return True
	elif MessageSent == False:
		print "MessageSent5 = ", MessageSent
		return False
		
def SystemModeCheck():# This checks the current system mode and initiates changes based on that variable including Downstairs and Upstairs valve changes.  This avoids two processes writing at the same time
	global zoneUpChange
	global zoneDownChange
	global screenRefreshRequested
	global Upstairs
	global Downstairs
	global XMLWriteRequest
	global RelayStatus
	global retryTimes
	global ESP8266PreviousCheck
	if (Upstairs == False) and (zoneUpChange == True):
		while retryTimes < 2 :
			if TCPClientSend("upstairs0") :
				print "TCPClientSendStatus = True"
				Upstairs = False
			else :
				print "TCPClientSendStatus = False"
				Upstairs = True
				retryTimes = retryTimes +1
		XMLWriteRequest = True
		zoneUpChange = False
		retryTimes = 0
		
	if (Upstairs == True) and (zoneUpChange == True) :
		while retryTimes < 2 :
			if TCPClientSend("upstairs1") :
				print "TCPClientSendStatus = True"
				Upstairs = True
			else :
				print "TCPClientSendStatus = False"
				Upstairs = False
				retryTimes = retryTimes + 1
		XMLWriteRequest = True
		zoneUpChange = False
		retryTimes = 0
		
	if (Downstairs == False) and (zoneDownChange == True):
		while retryTimes < 2 :
			if TCPClientSend("downstairs0") :
				Downstairs = False
			else:
				Downstairs = True
				retryTimes = retryTimes + 1
		XMLWriteRequest = True
		zoneDownChange = False
		retryTimes = 0
		
	if (Downstairs == True) and (zoneDownChange == True):
		while retryTimes < 2 :
			if TCPClientSend("downstairs1") :
				Downstairs = True
			else :
				Downstairs = False
				retryTimes = retryTimes + 1
		XMLWriteRequest = True
		zoneDownChange = False
		retryTimes = 0
		
	if (SystemMode == 1) :
		TimerBox()
	elif (SystemMode == 2) :
		RelayTimedMode()
	elif (SystemMode == 3) :
		if GPIO.input(GPIO_RELAY) == False :
			GPIO.output(GPIO_RELAY, True)
			GPIO.output(GPIO_RED_LED, True)
			RelayStatus = True
			XMLWriteRequest = True
	elif (SystemMode == 0) :
		if GPIO.input(GPIO_RELAY) == True :
			GPIO.output(GPIO_RELAY, False)
			GPIO.output(GPIO_RED_LED, False)
			RelayStatus = False
			XMLWriteRequest = True
	
	if (time.time() - ESP8266PreviousCheck) > ESP8266CheckDelay :
		TCPClientSend("status")
		ESP8266PreviousCheck = time.time()
		
def main():#The main functions of the program and handles the touchscreen
	
	clock = pygame.time.Clock()
	clock.tick(20)#Sets the refresh rate
	global Upstairs
	global Downstairs
	global runningCheck
	global SystemMode
	global BoostDelay
	global BoostCount
	global running
	global listening
	global XMLWriteRequest
	global zoneUpChange
	global zoneDownChange
	global PreviousSystemModeBoost
	while running == True:
		try:
			ClockTime()
			SystemModeCheck()
			XMLWriteRequestCheck()
			if ((time.time() - runningCheck) > runningDelay) :
				print "Running"
				print "Active Threads = ", threading.activeCount();
				#print "Listen433Loops = ", Listen433Loops
				runningCheck = time.time()
			
				if (SystemMode == 2) :
					ReadJSONFile()
				
		except Exception, e:
			print "main", repr(e)
				
class MyTCPHandler(SocketServer.BaseRequestHandler):#A class to handle the TCP instructions from the website
	def handle(self):
		global SystemMode
		global Downstairs
		global Upstairs
		global BoostDelay
		global BoostCount
		global BoostTimer
		global listening
		global XMLWriteRequest
		global zoneUpChange
		global zoneDownChange
		self.data = self.request.recv(1024).strip()
		print "{} wrote:".format(self.client_address[0])
		print self.data
		self.request.sendall(self.data.upper())
		
		if ((self.data) == "Off") :
			SystemMode = 0
			XMLWriteRequest = True
		if ((self.data) == "Timer") :
			
			if SystemMode != 1 :
				BoostDelay = 1800 # 30 mins 3600 for hour
				BoostCount = time.time()
				SystemMode = 1
			elif SystemMode == 1 :
				BoostDelay = BoostDelay + 1800
				if BoostDelay >= 18000 :
					BoostDelay = 18000
			XMLWriteRequest = True
			
		if ((self.data) == "Timed") :
			SystemMode = 2
			
			XMLWriteRequest = True
		if ((self.data) == "Constant") :
			SystemMode = 3
			XMLWriteRequest = True
		if ((self.data) == "Upstairs") :
			print "Upstairs: " , Upstairs
			print "Got Upstairs"
			if (Upstairs == False) or (Upstairs == "False"):
				Upstairs = True
			else :
				Upstairs = False
			zoneUpChange = True
			XMLWriteRequest = True
		if ((self.data) == "Downstairs") :
			print "Got Downstairs"
			if (Downstairs == False) or (Downstairs =="False") :
				Downstairs = True
			else :
				Downstairs = False
			zoneDownChange = True
			XMLWriteRequest = True
		if ((self.data) == "XMLUpdate") :
			XMLWriteRequest = True
			screenRefreshRequested = True
			ReadJSONFile()
			print "GOT XMLUPDATE"
		if listening == False :
			print "Shutdown Server"
			server.server_close()
			server.shutdown()

def TCPListen() :#Function to start listening for instructions from the website
	HOST, PORT = '', 8889
	server = SocketServer.TCPServer((HOST, PORT), MyTCPHandler)
	if (listening == True) :
		server.serve_forever()
	else :
		server.server_close()
		server.shutdown()
		
def TCPListen2() :#Function to listen for OilLevel readings (over TCP) --- possibly outside temperature also at a later date 
	global OilLevel
	global OilLevelText
	global OutsideTemp
	global OutsideTempText
	global OutsideBatt
	global OutsideBattText
	global listening
	global XMLWriteRequestCheck
	#global TCPListen2Loops
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.bind((TCP_IPReceive, TCP_PORTReceive))
	sock.settimeout(10)
	while listening == True :
		try :
			if (listening == False) :
				print "Listening", listening, "Exiting Thread"
				thread.exit()
			elif (listening == True): 
				print "Listening", listening
			#print "TCPListen2Loop"
			#TCPListen2Loops = TCPListen2Loops +1
			sock.listen(1)
			conn, addr = sock.accept()
			print 'Connection address:', addr
			data = ""
			while data != "\n":
				data = conn.recv(BUFFER_SIZE)
				if not data: break
				print "Received Data: ", data
				if data:
					if "OilLevel" in data :
						print "Arduino TCP Received", data
						try:
							OilLevelInt = int(re.search(r'\d+', data).group())
							OilLevel = str(OilLevelInt)
							OilLevelText = "OilLevel = "
							OilLevelText += OilLevel
							XMLWriteRequest = True
							
						except ValueError :
							OilLevel = "   "
							OilLevelText = "OilLevel = N/A"
					if "Temp" in data :
							print "Arduino 433 Received", data
							try :
								TempString = data.strip('Temp')
								TempFloat = float(TempString)
								OutsideTemp = str(TempFloat)
								OutsideTempText = "Ground Temp = "
								OutsideTempText += OutsideTemp
								print "Outside Temperature = ",OutsideTempText
								XMLWriteRequest = True
							except ValueError :
								OutsideTemp = "   "
								OutsideTempText = "Group Temp = N/A"	
					if "BattVolt" in data :
							print "Arduino TCP Received", data
							try :
								BattString = data.strip('BattVolt')
								BattFloat = float(BattString)
								OutsideBatt = str(BattFloat)
								OutsideBattText = "Battery Voltage = "
								OutsideBattText += OutsideBatt
								print "Outside Battery Voltage = ",OutsideBattText
								XMLWriteRequest = True
							except ValueError :
								OutsideTemp = "   "
								OutsideTempText = "Group Temp = N/A"	
						
					
			conn.close()
		except Exception, e:
			print "TCPListen2", repr(e)
		
	thread.exit()			

if __name__ == '__main__' :
	global listening
	global selecting
	HOST, PORT = '', 8889
	server = SocketServer.TCPServer((HOST, PORT), MyTCPHandler)
	try:
		threading.Thread(target=TCPListen2).start()
		threading.Thread(target=main).start()
		server.serve_forever()
		sleep(1)
	except KeyboardInterrupt :
		print "Running 1", running, ". Listening ", listening
		print "Exiting"
		running = False
		listening = False
		selecting = False
		SystemMode = 0
		server.server_close()
		server.shutdown()
		GPIO.cleanup()
		sys.exit
	while threading.active_count() > 0 :
		try :
			print "Active Threads = ", threading.enumerate()
			sleep(1)
		except KeyboardInterrupt :
			print "Exiting Threads"
			running = False
			listening = False
			selecting = False
			SystemMode = 0
			print "Running 2", running, ". Listening ", listening
			server.server_close()
			server.shutdown()
			GPIO.cleanup()
			sys.exit()