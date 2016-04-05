#!/usr/bin/python
# Raspberry Pi Heating system Written by Collie147
 

import pygame, sys, os, time, json, thread, datetime, select, socket, SocketServer, threading, pywapi, string, re
import xml.etree.cElementTree as XML
import pigpio
import piVirtualWire.piVirtualWire as piVirtualWire
from piVirtualWire.piVirtualWire import *
from pygame.locals import *
from time import sleep
import RPi.GPIO as GPIO
from threading import Timer
from threading import Thread
from evdev import InputDevice, list_devices

GPIO_RED_LED = *RED_LED_GPIO_PIN
GPIO_GREEN_LED = *GREEN_LED_GPIO_PIN
GPIO_RELAY = *RELAY_GPIO_PIN
GPIO_RX = *RX_433_GPIO_PIN
GPIO_TX = *TX_433_GPIO_PIN

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
OilLevel = 9
OilLevelText = "OilLevel = 999"
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
devices = map(InputDevice, list_devices())
eventX=""

for dev in devices:
	if dev.name == "*TOUCHSCREEN":
		eventX = dev.fn
print eventX

os.environ["SDL_FBDEV"] = "/dev/fb1"
os.environ["SDL_MOUSEDRV"] = "TSLIB"
os.environ["SDL_MOUSEDEV"] = eventX

pygame.init()

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
		OilLevel = str(root[9].text)
		OilLevelText = "OilLevel = "
		OilLevelText += OilLevel
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
	tree = XML.ElementTree(root)
	tree = XML.ElementTree(root)
	tree.write("/var/www/html/ButtonStatus.xml")
	Screen1Refresh()
	
def WeatherDisplay() :
	
	global WeatherCheck
	global WeatherDelay
	global WeatherCount
	WeatherCount = (time.time() - WeatherCheck)
	if WeatherCount > WeatherDelay :
		print "Getting Weather Info"
		try:
			global yahoo_result
			global SunRiseSet
			global Weather
			global RainHumid
			global Wind
			global WindSpeed
			u = u"\N{DEGREE SIGN}"
			a = u.encode('utf-8')
			weather_result = pywapi.get_weather_from_weather_com('EIXX0003')
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
			
			RainHumid = str("Humidity: " + (weather_result['forecasts'][0]['day']['humidity']) + "%" + "         Rain Chance: " + (weather_result['forecasts'][0]['day']['chance_precip']) + "%")
			yahoo_result = pywapi.get_weather_from_yahoo('EIXX0003', 'metric')
			SunRiseSet = str("Sunrise: " + (yahoo_result['astronomy']['sunrise']) + "   -   Sunset: " + (yahoo_result['astronomy']['sunset']))
			Weather = str((yahoo_result['condition']['text']) + " and " + (yahoo_result['condition']['temp']))
			Weather = Weather + u + "C"
			Wind = "Wind: " + WindDirection
			WindSpeed = WindSpd + " km/h"
			WeatherCheck = time.time()
		except Exception, e:
			print "Weather Error:", repr(e)
			RainHumid = ""
			yahoo_result = ""
			SunRiseSet = ""
			Weather = "       Weather Information Unavailable"
			Wind = ""
			WindSpeed = ""
			WeatherCheck = time.time()
		
# set up the window
screen = pygame.display.set_mode((*HORIZONTAL, *VERTICAL), 0, 32)
pygame.display.set_caption('Drawing')
pygame.mouse.set_visible(0)
# set up the colors
BLACK = (  0,   0,   0)
WHITE = (255, 255, 255)
RED   = (255,   0,   0)
GREEN = (  0, 255,   0)
BLUE  = (  0,   0, 255)
CYAN  = (  0, 255, 255)
MAGENTA=(255,   0, 255)
YELLOW =(255, 255,   0)
GREY   =(190, 190, 190)

# Fill background
background = pygame.Surface(screen.get_size())
background = background.convert()
background.fill(WHITE)
#Rectangles
box1 = pygame.draw.rect(background, RED,(0, 100, 100, 50))
box2 = pygame.draw.rect(background,  GREEN, (110, 100, 100, 50))
box3 = pygame.draw.rect(background, GREEN, (220, 100, 100, 50))
box4 = pygame.draw.rect(background,GREEN, (0, 180, 100, 50))
box5 = pygame.draw.rect(background, GREEN,   (110, 180, 100, 50))
box6 = pygame.draw.rect(background, GREEN  ,(220, 180, 100, 50))
box7 = pygame.draw.rect(background, YELLOW, (0, 20, 320, 80))
  
#Text
font = pygame.font.Font(None, 25)
#TextBox1
text1 = font.render("OFF", 1, (BLACK))
#text = pygame.transform.rotate(text,270) 
textpos1 = text1.get_rect(centerx=50,centery=125)
#TextBox2
text2 = font.render("Upstairs", 1, (BLACK))
textpos2 = text2.get_rect(centerx=160,centery=125)
#TextBox3
text3 = font.render("Downstairs", 1, (BLACK))
textpos3 = text3.get_rect(centerx=270,centery=125)
#TextBox4
text4 = font.render("1 Hour", 1, (BLACK))
textpos4 = text4.get_rect(centerx=50,centery=205)
#TextBox5
text5 = font.render("Timed", 1, (BLACK))
textpos5 = text5.get_rect(centerx=160,centery=205)
#TextBox6
text6 = font.render("Const.", 1, (BLACK))
textpos6 = text6.get_rect(centerx=270,centery=205)
#Draw
background.blit(text1, textpos1)
background.blit(text2, textpos2)
background.blit(text3, textpos3)
background.blit(text4, textpos4)
background.blit(text5, textpos5)
background.blit(text6, textpos6)
WeatherDisplay()
SunRiseSetText = font.render(SunRiseSet, 1, (BLACK), (YELLOW))
WeatherText = font.render(Weather, 1, (BLACK), (YELLOW))
RainText = font.render(RainHumid, 1, (BLACK), (YELLOW))
WindText = font.render(Wind, 1, (BLACK), (YELLOW))
WindSpeedText = font.render(WindSpeed, 1, (BLACK), (YELLOW))
background.blit(SunRiseSetText, (0, 20))
background.blit(WeatherText, (0, 40))
background.blit(RainText, (0, 60))
background.blit(WindText, (0, 80))
background.blit(WindSpeedText, (240, 80))
global theTime
theTime=time.strftime("%H:%M:%S", time.localtime())
timeText=font.render(str(theTime), 1, (BLACK), (GREEN))
timeTextPos = timeText.get_rect()
timeTextPos.right = background.get_rect().right
background.blit(timeText, timeTextPos)	
	
#Render and refresh
screen.blit(background, (0, 0))
pygame.display.flip()

ReadJSONFile()
Width = 26
Height = 30
	
def Screen1() : 

	# Fill background
	background = pygame.Surface(screen.get_size())
	background = background.convert()
	background.fill(WHITE)

	#Rectangles
	box1 = pygame.draw.rect(background, RED,(0, 100, 100, 50)) # Off Button
	box2 = pygame.draw.rect(background,  GREEN, (110, 100, 100, 50)) # Upstairs Button
	box3 = pygame.draw.rect(background, GREEN, (220, 100, 100, 50)) # Downstairs Button
	box4 = pygame.draw.rect(background,GREEN,(0, 180, 100, 50)) # Boost Button
	box5 = pygame.draw.rect(background, GREEN,   (110, 180, 100, 50)) # Timed Button
	box6 = pygame.draw.rect(background, GREEN  ,(220, 180, 100, 50)) # Const Button
	box7 = pygame.draw.rect(background, YELLOW, (0, 20, 320, 80)) # Weather Box
	#Text
	font = pygame.font.Font(None, 25)

	#TextBox1
	text1 = font.render("OFF", 1, (BLACK))
	#text = pygame.transform.rotate(text,270) 
	textpos1 = text1.get_rect(centerx=50,centery=125)
	#TextBox2
	text2 = font.render("Upstairs", 1, (BLACK))
	textpos2 = text2.get_rect(centerx=160,centery=125)
	#TextBox3
	text3 = font.render("Downstairs", 1, (BLACK))
	textpos3 = text3.get_rect(centerx=270,centery=125)
	#TextBox4
	text4 = font.render("1 Hour", 1, (BLACK))
	textpos4 = text4.get_rect(centerx=50,centery=205)
	#TextBox5
	text5 = font.render("Timed", 1, (BLACK))
	textpos5 = text5.get_rect(centerx=160,centery=205)
	#TextBox6
	text6 = font.render("Const.", 1, (BLACK))
	textpos6 = text6.get_rect(centerx=270,centery=205)
	#Draw
	background.blit(text1, textpos1)
	background.blit(text2, textpos2)
	background.blit(text3, textpos3)
	background.blit(text4, textpos4)
	background.blit(text5, textpos5)
	background.blit(text6, textpos6)
	
	WeatherDisplay()
	SunRiseSetText = font.render(SunRiseSet, 1, (BLACK), (YELLOW))
	WeatherText = font.render(Weather, 1, (BLACK), (YELLOW))
	RainText = font.render(RainHumid, 1, (BLACK), (YELLOW))
	WindText = font.render(Wind, 1, (BLACK), (YELLOW))
	WindSpeedText = font.render(WindSpeed, 1, (BLACK), (YELLOW))
	background.blit(SunRiseSetText, (0, 20))
	background.blit(WeatherText, (0, 40))
	background.blit(RainText, (0, 60))
	background.blit(WindText, (0, 80))
	background.blit(WindSpeedText, (240, 80))
	
	#Render and refresh
	screen.blit(background, (0, 0))
	pygame.display.flip()

def Screen1Refresh() :

	ReadXML()
	font = pygame.font.Font(None, 25)
	global Upstairs
	global Downstairs
	global SystemMode
	global OilLevel
	global OilLevelText
	if SystemMode != 1 :
		background.fill(WHITE)
			
	#Rectangles
	if SystemMode == 0 :
		box1 = pygame.draw.rect(background, RED,(0, 100, 100, 50))
	else :
		box1 = pygame.draw.rect(background, GREEN,(0, 100, 100, 50))
	if ESP8266Online == True :
		if (Upstairs == True) :
			box2 = pygame.draw.rect(background,  RED, (110, 100, 100, 50))
		elif Upstairs == False :
			box2 = pygame.draw.rect(background,  GREEN, (110, 100, 100, 50))
		if Downstairs == True :
			box3 = pygame.draw.rect(background, RED, (220, 100, 100, 50))
		elif Downstairs == False :
			box3 = pygame.draw.rect(background, GREEN, (220, 100, 100, 50))
	else:
		box2 = pygame.draw.rect(background,  GREY, (110, 100, 100, 50))
		box3 = pygame.draw.rect(background, GREY, (220, 100, 100, 50))
	if SystemMode == 1 :
		box4 = pygame.draw.rect(background,RED,(0, 180, 100, 50))
		text4 = font.render("Add 30 Min", 1, (BLUE))
		textpos4 = text4.get_rect(centerx=50, centery=205)
	else :
		box4 = pygame.draw.rect(background,GREEN,(0, 180, 100, 50))
		text4 = font.render("30 Mins", 1, (BLACK))
		textpos4 = text4.get_rect(centerx=50,centery=205)
	if SystemMode == 2 :
		box5 = pygame.draw.rect(background, RED,(110, 180, 100, 50))
	else :
		box5 = pygame.draw.rect(background, GREEN,   (110, 180, 100, 50))
	if SystemMode == 3 :
		box6 = pygame.draw.rect(background, RED  ,(220, 180, 100, 50))
	else :
		box6 = pygame.draw.rect(background, GREEN  ,(220, 180, 100, 50))
	box7 = pygame.draw.rect(background, YELLOW, (0, 20, 320, 80))
	
	#TextBox1
	text1 = font.render("OFF", 1, (BLACK))
	#text = pygame.transform.rotate(text,270) 
	textpos1 = text1.get_rect(centerx=50,centery=125)
	#TextBox5
	text5 = font.render("Timed", 1, (BLACK))
	textpos5 = text5.get_rect(centerx=160,centery=205)
	#TextBox6
	text6 = font.render("Const.", 1, (BLACK))
	textpos6 = text6.get_rect(centerx=270,centery=205)
	
	clock = pygame.time.Clock()
	clock.tick(20)	#Sets the refresh rate of the screen
	
	theTime=time.strftime("%H:%M:%S", time.localtime())
	timeText=font.render(str(theTime), 1, (BLACK), (GREEN))
	timeTextPos = timeText.get_rect()
	timeTextPos.right = background.get_rect().right
	background.blit(timeText, timeTextPos)
	
	if (OilLevel < 50) :
		OilLevelTextRender=font.render(str(OilLevelText), 1, (BLACK), (RED))
	if (OilLevel >= 50) and (OilLevel < 100):
		OilLevelTextRender=font.render(str(OilLevelText), 1, (BLACK), (YELLOW))
	if (OilLevel >= 100) :
		OilLevelTextRender=font.render(str(OilLevelText), 1, (BLACK), (GREEN))
	background.blit(OilLevelTextRender, (0, 0))
	
	global WeatherCheck
	global SunRiseSet
	global Weather
	u = u"\N{DEGREE SIGN}"
	
	WeatherDisplay()
	SunRiseSetText = font.render(SunRiseSet, 1, (BLACK), (YELLOW))
	WeatherText = font.render(Weather, 1, (BLACK), (YELLOW))
	RainText = font.render(RainHumid, 1, (BLACK), (YELLOW))
	WindText = font.render(Wind, 1, (BLACK), (YELLOW))
	WindSpeedText = font.render(WindSpeed, 1, (BLACK), (YELLOW))
	background.blit(SunRiseSetText, (0, 20))
	background.blit(WeatherText, (0, 40))
	background.blit(RainText, (0, 60))
	background.blit(WindText, (0, 80))
	background.blit(WindSpeedText, (240, 80))
	background.blit(text1, textpos1)
	background.blit(text2, textpos2)
	background.blit(text3, textpos3)
	background.blit(text4, textpos4)
	background.blit(text5, textpos5)
	background.blit(text6, textpos6)
	screen.blit(background, (0, 0))
	pygame.display.flip()
	
Screen1Refresh()	

def ClockTime() : # Updates the on-screen clock
	clock = pygame.time.Clock()
	clock.tick(20) #Sets the refresh rate of the screen
	theTime=time.strftime("%H:%M:%S", time.localtime())
	timeText=font.render(str(theTime), 1, (BLACK), (GREEN))
	timeTextPos = timeText.get_rect()
	timeTextPos.right = background.get_rect().right
	background.blit(timeText, timeTextPos)
	screen.blit(background, (0, 0))
	pygame.display.flip()	

def TimeScreen1():# Mark the populated time screen as either Red:selected or Blue:not selected
	ReadJSONFile()
	global timeboxstatus
	background = pygame.Surface(screen.get_size())
	background = background.convert()
	background.fill(WHITE)
	if timeboxstatus[1] :
		timebox[1] = pygame.draw.rect(background, RED,(8, 0, Width, Height))
	else :
		timebox[1] = pygame.draw.rect(background, BLUE,(8, 0, Width, Height))
	if timeboxstatus[2] :
		timebox[2] = pygame.draw.rect(background, RED,(8, Height, Width, Height))
	else :
		timebox[2] = pygame.draw.rect(background, BLUE,(8, Height, Width, Height))
	if timeboxstatus[3] :
		timebox[3] = pygame.draw.rect(background, RED,(8, Height*2, Width, Height))
	else :
		timebox[3] = pygame.draw.rect(background, BLUE,(8, Height*2, Width, Height))
	if timeboxstatus[4] :
		timebox[4] = pygame.draw.rect(background, RED,(8, Height*3, Width, Height))
	else :
		timebox[4] = pygame.draw.rect(background, BLUE,(8, Height*3, Width, Height))
	if timeboxstatus[5] :
		timebox[5] = pygame.draw.rect(background, RED,(8, Height*4, Width, Height))
	else :
		timebox[5] = pygame.draw.rect(background, BLUE,(8, Height*4, Width, Height))
	if timeboxstatus[6] :
		timebox[6] = pygame.draw.rect(background, RED,(8, Height*5, Width, Height))
	else : 
		timebox[6] = pygame.draw.rect(background, BLUE,(8, Height*5, Width, Height))
	if timeboxstatus[7] :
		timebox[7] = pygame.draw.rect(background, RED,(8, Height*6, Width, Height))
	else :
		timebox[7] = pygame.draw.rect(background, BLUE,(8, Height*6, Width, Height))
	if timeboxstatus[8] :
		timebox[8] = pygame.draw.rect(background, RED,(8, Height*7, Width, Height))
	else :
		timebox[8] = pygame.draw.rect(background, BLUE,(8, Height*7, Width, Height))
	if timeboxstatus[9] :
		timebox[9] = pygame.draw.rect(background, RED,(Width+8, 0, Width, Height))
	else :
		timebox[9] = pygame.draw.rect(background, BLUE,(Width+8, 0, Width, Height))
	if timeboxstatus[10] :
		timebox[10] = pygame.draw.rect(background, RED,(Width+8, Height, Width, Height))
	else :
		timebox[10] = pygame.draw.rect(background, BLUE,(Width+8, Height, Width, Height))
	if timeboxstatus[11] :
		timebox[11]= pygame.draw.rect(background, RED,(Width+8, Height*2, Width, Height))
	else :
		timebox[11]= pygame.draw.rect(background, BLUE,(Width+8, Height*2, Width, Height))
	if timeboxstatus[12] :
		timebox[12] = pygame.draw.rect(background, RED,(Width+8, Height*3, Width, Height))
	else :
		timebox[12] = pygame.draw.rect(background, BLUE,(Width+8, Height*3, Width, Height))
	if timeboxstatus[13] :
		timebox[13] = pygame.draw.rect(background, RED,(Width+8, Height*4, Width, Height))
	else :
		timebox[13] = pygame.draw.rect(background, BLUE,(Width+8, Height*4, Width, Height))
	if timeboxstatus[14] :
		timebox[14] = pygame.draw.rect(background, RED,(Width+8, Height*5, Width, Height))
	else :
		timebox[14] = pygame.draw.rect(background, BLUE,(Width+8, Height*5, Width, Height))
	if timeboxstatus[15] :
		timebox[15] = pygame.draw.rect(background, RED,(Width+8, Height*6, Width, Height))
	else :
		timebox[15] = pygame.draw.rect(background, BLUE,(Width+8, Height*6, Width, Height))
	if timeboxstatus[16] :
		timebox[16] = pygame.draw.rect(background, RED,(Width+8, Height*7, Width, Height))
	else:
		timebox[16] = pygame.draw.rect(background, BLUE,(Width+8, Height*7, Width, Height))
	if timeboxstatus[17] :
		timebox[17] = pygame.draw.rect(background, RED,(((Width*2)+8), 0, Width, Height))
	else :
		timebox[17] = pygame.draw.rect(background, BLUE,(((Width*2)+8), 0, Width, Height))
	if timeboxstatus[18] :
		timebox[18] = pygame.draw.rect(background, RED,(((Width*2)+8), Height, Width, Height))
	else :
		timebox[18] = pygame.draw.rect(background, BLUE,(((Width*2)+8), Height, Width, Height))
	if timeboxstatus[19] :
		timebox[19] = pygame.draw.rect(background, RED,(((Width*2)+8), Height*2, Width, Height))
	else :
		timebox[19] = pygame.draw.rect(background, BLUE,(((Width*2)+8), Height*2, Width, Height))
	if timeboxstatus[20] :
		timebox[20] = pygame.draw.rect(background, RED,(((Width*2)+8), Height*3, Width, Height))
	else :
		timebox[20] = pygame.draw.rect(background, BLUE,(((Width*2)+8), Height*3, Width, Height))
	if timeboxstatus[21] :
		timebox[21] = pygame.draw.rect(background, RED,(((Width*2)+8), Height*4, Width, Height))
	else :
		timebox[21] = pygame.draw.rect(background, BLUE,(((Width*2)+8), Height*4, Width, Height))
	if timeboxstatus[22] :
		timebox[22] = pygame.draw.rect(background, RED,(((Width*2)+8), Height*5, Width, Height))
	else :
		timebox[22] = pygame.draw.rect(background, BLUE,(((Width*2)+8), Height*5, Width, Height))
	if timeboxstatus[23] :
		timebox[23] = pygame.draw.rect(background, RED,(((Width*2)+8), Height*6, Width, Height))
	else :
		timebox[23] = pygame.draw.rect(background, BLUE,(((Width*2)+8), Height*6, Width, Height))
	if timeboxstatus[24] :
		timebox[24] = pygame.draw.rect(background, RED,(((Width*2)+8), Height*7, Width, Height))
	else :
		timebox[24] = pygame.draw.rect(background, BLUE,(((Width*2)+8), Height*7, Width, Height))
	if timeboxstatus[25] :
		timebox[25] = pygame.draw.rect(background, RED,(((Width*3)+8), 0, Width, Height))
	else :
		timebox[25] = pygame.draw.rect(background, BLUE,(((Width*3)+8), 0, Width, Height))
	if timeboxstatus[26] :
		timebox[26] = pygame.draw.rect(background, RED,(((Width*3)+8), Height, Width, Height))
	else :
		timebox[26] = pygame.draw.rect(background, BLUE,(((Width*3)+8), Height, Width, Height))
	if timeboxstatus[27] :
		timebox[27] = pygame.draw.rect(background, RED,(((Width*3)+8), Height*2, Width, Height))
	else :
		timebox[27] = pygame.draw.rect(background, BLUE,(((Width*3)+8), Height*2, Width, Height))
	if timeboxstatus[28] :
		timebox[28] = pygame.draw.rect(background, RED,(((Width*3)+8), Height*3, Width, Height))
	else :
		timebox[28] = pygame.draw.rect(background, BLUE,(((Width*3)+8), Height*3, Width, Height))
	if timeboxstatus[29] :
		timebox[29] = pygame.draw.rect(background, RED,(((Width*3)+8), Height*4, Width, Height))
	else :
		timebox[29] = pygame.draw.rect(background, BLUE,(((Width*3)+8), Height*4, Width, Height))
	if timeboxstatus[30] :
		timebox[30] = pygame.draw.rect(background, RED,(((Width*3)+8), Height*5, Width, Height))
	else :
		timebox[30] = pygame.draw.rect(background, BLUE,(((Width*3)+8), Height*5, Width, Height))
	if timeboxstatus[31] :
		timebox[31] = pygame.draw.rect(background, RED,(((Width*3)+8), Height*6, Width, Height))
	else :
		timebox[31] = pygame.draw.rect(background, BLUE,(((Width*3)+8), Height*6, Width, Height))
	if timeboxstatus[32] :
		timebox[32] = pygame.draw.rect(background, RED,(((Width*3)+8), Height*7, Width, Height))
	else :
		timebox[32] = pygame.draw.rect(background, BLUE,(((Width*3)+8), Height*7, Width, Height))
	if timeboxstatus[33] :
		timebox[33] = pygame.draw.rect(background, RED,(((Width*4)+8), 0, Width, Height))
	else :
		timebox[33] = pygame.draw.rect(background, BLUE,(((Width*4)+8), 0, Width, Height))
	if timeboxstatus[34] :
		timebox[34] = pygame.draw.rect(background, RED,(((Width*4)+8), Height, Width, Height))
	else :
		timebox[34] = pygame.draw.rect(background, BLUE,(((Width*4)+8), Height, Width, Height))
	if timeboxstatus[35] :
		timebox[35] = pygame.draw.rect(background, RED,(((Width*4)+8), Height*2, Width, Height))
	else :
		timebox[35] = pygame.draw.rect(background, BLUE,(((Width*4)+8), Height*2, Width, Height))
	if timeboxstatus[36] :
		timebox[36] = pygame.draw.rect(background, RED,(((Width*4)+8), Height*3, Width, Height))
	else :
		timebox[36] = pygame.draw.rect(background, BLUE,(((Width*4)+8), Height*3, Width, Height))
	if timeboxstatus[37] :
		timebox[37] = pygame.draw.rect(background, RED,(((Width*4)+8), Height*4, Width, Height))
	else :
		timebox[37] = pygame.draw.rect(background, BLUE,(((Width*4)+8), Height*4, Width, Height))
	if timeboxstatus[38] :
		timebox[38] = pygame.draw.rect(background, RED,(((Width*4)+8), Height*5, Width, Height))
	else :
		timebox[38] = pygame.draw.rect(background, BLUE,(((Width*4)+8), Height*5, Width, Height))
	if timeboxstatus[39] :
		timebox[39] = pygame.draw.rect(background, RED,(((Width*4)+8), Height*6, Width, Height))
	else :
		timebox[39] = pygame.draw.rect(background, BLUE,(((Width*4)+8), Height*6, Width, Height))
	if timeboxstatus[40] :
		timebox[40] = pygame.draw.rect(background, RED,(((Width*4)+8), Height*7, Width, Height))
	else :
		timebox[40] = pygame.draw.rect(background, BLUE,(((Width*4)+8), Height*7, Width, Height))
	if timeboxstatus[41] :
		timebox[41] = pygame.draw.rect(background, RED,(((Width*5)+8), 0, Width, Height))
	else :
		timebox[41] = pygame.draw.rect(background, BLUE,(((Width*5)+8), 0, Width, Height))
	if timeboxstatus[42] :
		timebox[42] = pygame.draw.rect(background, RED,(((Width*5)+8), Height, Width, Height))
	else :
		timebox[42] = pygame.draw.rect(background, BLUE,(((Width*5)+8), Height, Width, Height))
	if timeboxstatus[43] :
		timebox[43] = pygame.draw.rect(background, RED,(((Width*5)+8), Height*2, Width, Height))
	else :
		timebox[43] = pygame.draw.rect(background, BLUE,(((Width*5)+8), Height*2, Width, Height))
	if timeboxstatus[44] :
		timebox[44] = pygame.draw.rect(background, RED,(((Width*5)+8), Height*3, Width, Height))
	else :
		timebox[44] = pygame.draw.rect(background, BLUE,(((Width*5)+8), Height*3, Width, Height))
	if timeboxstatus[45] :
		timebox[45] = pygame.draw.rect(background, RED,(((Width*5)+8), Height*4, Width, Height))
	else :
		timebox[45] = pygame.draw.rect(background, BLUE,(((Width*5)+8), Height*4, Width, Height))
	if timeboxstatus[46] :
		timebox[46] = pygame.draw.rect(background, RED,(((Width*5)+8), Height*5, Width, Height))
	else :
		timebox[46] = pygame.draw.rect(background, BLUE,(((Width*5)+8), Height*5, Width, Height))
	if timeboxstatus[47] :
		timebox[47] = pygame.draw.rect(background, RED,(((Width*5)+8), Height*6, Width, Height))
	else :
		timebox[47] = pygame.draw.rect(background, BLUE,(((Width*5)+8), Height*6, Width, Height))
	if timeboxstatus[48] :
		timebox[48] = pygame.draw.rect(background, RED,(((Width*5)+8), Height*7, Width, Height))
	else :
		timebox[48] = pygame.draw.rect(background, BLUE,(((Width*5)+8), Height*7, Width, Height))
	if timeboxstatus[49] :
		timebox[49] = pygame.draw.rect(background, RED,(((Width*6)+8), 0, Width, Height))
	else :
		timebox[49] = pygame.draw.rect(background, BLUE,(((Width*6)+8), 0, Width, Height))
	if timeboxstatus[50] :
		timebox[50] = pygame.draw.rect(background, RED,(((Width*6)+8), Height, Width, Height))
	else :
		timebox[50] = pygame.draw.rect(background, BLUE,(((Width*6)+8), Height, Width, Height))
	if timeboxstatus[51] :
		timebox[51] = pygame.draw.rect(background, RED,(((Width*6)+8), Height*2, Width, Height))
	else :
		timebox[51] = pygame.draw.rect(background, BLUE,(((Width*6)+8), Height*2, Width, Height))
	if timeboxstatus[52] :
		timebox[52] = pygame.draw.rect(background, RED,(((Width*6)+8), Height*3, Width, Height))
	else :
		timebox[52] = pygame.draw.rect(background, BLUE,(((Width*6)+8), Height*3, Width, Height))
	if timeboxstatus[53] :
		timebox[53] = pygame.draw.rect(background, RED,(((Width*6)+8), Height*4, Width, Height))
	else :
		timebox[53] = pygame.draw.rect(background, BLUE,(((Width*6)+8), Height*4, Width, Height))
	if timeboxstatus[54] :
		timebox[54] = pygame.draw.rect(background, RED,(((Width*6)+8), Height*5, Width, Height))
	else :
		timebox[54] = pygame.draw.rect(background, BLUE,(((Width*6)+8), Height*5, Width, Height))
	if timeboxstatus[55] :
		timebox[55] = pygame.draw.rect(background, RED,(((Width*6)+8), Height*6, Width, Height))
	else :
		timebox[55] = pygame.draw.rect(background, BLUE,(((Width*6)+8), Height*6, Width, Height))
	if timeboxstatus[56] :
		timebox[56] = pygame.draw.rect(background, RED,(((Width*6)+8), Height*7, Width, Height))
	else :
		timebox[56] = pygame.draw.rect(background, BLUE,(((Width*6)+8), Height*7, Width, Height))
	if timeboxstatus[57] :
		timebox[57] = pygame.draw.rect(background, RED,(((Width*7)+8), 0, Width, Height))
	else :
		timebox[57] = pygame.draw.rect(background, BLUE,(((Width*7)+8), 0, Width, Height))
	if timeboxstatus[58] :
		timebox[58] = pygame.draw.rect(background, RED,(((Width*7)+8), Height, Width, Height))
	else :
		timebox[58] = pygame.draw.rect(background, BLUE,(((Width*7)+8), Height, Width, Height))
	if timeboxstatus[59] :
		timebox[59] = pygame.draw.rect(background, RED,(((Width*7)+8), Height*2, Width, Height))
	else :
		timebox[59] = pygame.draw.rect(background, BLUE,(((Width*7)+8), Height*2, Width, Height))
	if timeboxstatus[60] :
		timebox[60] = pygame.draw.rect(background, RED,(((Width*7)+8), Height*3, Width, Height))
	else :
		timebox[60] = pygame.draw.rect(background, BLUE,(((Width*7)+8), Height*3, Width, Height))
	if timeboxstatus[61] :
		timebox[61] = pygame.draw.rect(background, RED,(((Width*7)+8), Height*4, Width, Height))
	else :
		timebox[61] = pygame.draw.rect(background, BLUE,(((Width*7)+8), Height*4, Width, Height))
	if timeboxstatus[62] :
		timebox[62] = pygame.draw.rect(background, RED,(((Width*7)+8), Height*5, Width, Height))
	else :
		timebox[62] = pygame.draw.rect(background, BLUE,(((Width*7)+8), Height*5, Width, Height))
	if timeboxstatus[63] :
		timebox[63] = pygame.draw.rect(background, RED,(((Width*7)+8), Height*6, Width, Height))
	else :
		timebox[63] = pygame.draw.rect(background, BLUE,(((Width*7)+8), Height*6, Width, Height))
	if timeboxstatus[64] :
		timebox[64] = pygame.draw.rect(background, RED,(((Width*7)+8), Height*7, Width, Height))
	else :
		timebox[64] = pygame.draw.rect(background, BLUE,(((Width*7)+8), Height*7, Width, Height))
	if timeboxstatus[65] :
		timebox[65] = pygame.draw.rect(background, RED,(((Width*8)+8), 0, Width, Height))
	else :
		timebox[65] = pygame.draw.rect(background, BLUE,(((Width*8)+8), 0, Width, Height))
	if timeboxstatus[66] :
		timebox[66] = pygame.draw.rect(background, RED,(((Width*8)+8), Height, Width, Height))
	else :
		timebox[66] = pygame.draw.rect(background, BLUE,(((Width*8)+8), Height, Width, Height))
	if timeboxstatus[67] :
		timebox[67] = pygame.draw.rect(background, RED,(((Width*8)+8), Height*2, Width, Height))
	else :
		timebox[67] = pygame.draw.rect(background, BLUE,(((Width*8)+8), Height*2, Width, Height))
	if timeboxstatus[68] :
		timebox[68] = pygame.draw.rect(background, RED,(((Width*8)+8), Height*3, Width, Height))
	else :
		timebox[68] = pygame.draw.rect(background, BLUE,(((Width*8)+8), Height*3, Width, Height))
	if timeboxstatus[69] :
		timebox[69] = pygame.draw.rect(background, RED,(((Width*8)+8), Height*4, Width, Height))
	else :
		timebox[69] = pygame.draw.rect(background, BLUE,(((Width*8)+8), Height*4, Width, Height))
	if timeboxstatus[70] :
		timebox[70] = pygame.draw.rect(background, RED,(((Width*8)+8), Height*5, Width, Height))
	else :
		timebox[70] = pygame.draw.rect(background, BLUE,(((Width*8)+8), Height*5, Width, Height))
	if timeboxstatus[71] :
		timebox[71] = pygame.draw.rect(background, RED,(((Width*8)+8), Height*6, Width, Height))
	else :
		timebox[71] = pygame.draw.rect(background, BLUE,(((Width*8)+8), Height*6, Width, Height))
	if timeboxstatus[72] :
		timebox[72] = pygame.draw.rect(background, RED,(((Width*8)+8), Height*7, Width, Height))
	else :
		timebox[72] = pygame.draw.rect(background, BLUE,(((Width*8)+8), Height*7, Width, Height))
	if timeboxstatus[73] :
		timebox[73] = pygame.draw.rect(background, RED,(((Width*9)+8), 0, Width, Height))
	else :
		timebox[73] = pygame.draw.rect(background, BLUE,(((Width*9)+8), 0, Width, Height))
	if timeboxstatus[74] :
		timebox[74] = pygame.draw.rect(background, RED,(((Width*9)+8), Height, Width, Height))
	else :
		timebox[74] = pygame.draw.rect(background, BLUE,(((Width*9)+8), Height, Width, Height))
	if timeboxstatus[75] :
		timebox[75] = pygame.draw.rect(background, RED,(((Width*9)+8), Height*2, Width, Height))
	else :
		timebox[75] = pygame.draw.rect(background, BLUE,(((Width*9)+8), Height*2, Width, Height))
	if timeboxstatus[76] :
		timebox[76] = pygame.draw.rect(background, RED,(((Width*9)+8), Height*3, Width, Height))
	else :
		timebox[76] = pygame.draw.rect(background, BLUE,(((Width*9)+8), Height*3, Width, Height))
	if timeboxstatus[77] :
		timebox[77] = pygame.draw.rect(background, RED,(((Width*9)+8), Height*4, Width, Height))
	else :
		timebox[77] = pygame.draw.rect(background, BLUE,(((Width*9)+8), Height*4, Width, Height))
	if timeboxstatus[78] :
		timebox[78] = pygame.draw.rect(background, RED,(((Width*9)+8), Height*5, Width, Height))
	else :
		timebox[78] = pygame.draw.rect(background, BLUE,(((Width*9)+8), Height*5, Width, Height))
	if timeboxstatus[79] :
		timebox[79] = pygame.draw.rect(background, RED,(((Width*9)+8), Height*6, Width, Height))
	else :
		timebox[79] = pygame.draw.rect(background, BLUE,(((Width*9)+8), Height*6, Width, Height))
	if timeboxstatus[80] :
		timebox[80] = pygame.draw.rect(background, RED,(((Width*9)+8), Height*7, Width, Height))
	else :
		timebox[80] = pygame.draw.rect(background, BLUE,(((Width*9)+8), Height*7, Width, Height))
	if timeboxstatus[81] :
		timebox[81] = pygame.draw.rect(background, RED,(((Width*10)+8), 0, Width, Height))
	else :
		timebox[81] = pygame.draw.rect(background, BLUE,(((Width*10)+8), 0, Width, Height))
	if timeboxstatus[82] :
		timebox[82] = pygame.draw.rect(background, RED,(((Width*10)+8), Height, Width, Height))
	else :
		timebox[82] = pygame.draw.rect(background, BLUE,(((Width*10)+8), Height, Width, Height))
	if timeboxstatus[83] :
		timebox[83] = pygame.draw.rect(background, RED,(((Width*10)+8), Height*2, Width, Height))
	else :
		timebox[83] = pygame.draw.rect(background, BLUE,(((Width*10)+8), Height*2, Width, Height))
	if timeboxstatus[84] :
		timebox[84] = pygame.draw.rect(background, RED,(((Width*10)+8), Height*3, Width, Height))
	else :
		timebox[84] = pygame.draw.rect(background, BLUE,(((Width*10)+8), Height*3, Width, Height))
	if timeboxstatus[85] :
		timebox[85] = pygame.draw.rect(background, RED,(((Width*10)+8), Height*4, Width, Height))
	else :
		timebox[85] = pygame.draw.rect(background, BLUE,(((Width*10)+8), Height*4, Width, Height))
	if timeboxstatus[86] :
		timebox[86] = pygame.draw.rect(background, RED,(((Width*10)+8), Height*5, Width, Height))
	else :
		timebox[86] = pygame.draw.rect(background, BLUE,(((Width*10)+8), Height*5, Width, Height))
	if timeboxstatus[87] :
		timebox[87] = pygame.draw.rect(background, RED,(((Width*10)+8), Height*6, Width, Height))
	else :
		timebox[87] = pygame.draw.rect(background, BLUE,(((Width*10)+8), Height*6, Width, Height))
	if timeboxstatus[88] :
		timebox[88] = pygame.draw.rect(background, RED,(((Width*10)+8), Height*7, Width, Height))
	else :
		timebox[88] = pygame.draw.rect(background, BLUE,(((Width*10)+8), Height*7, Width, Height))
	if timeboxstatus[89] :
		timebox[89] = pygame.draw.rect(background, RED,(((Width*11)+8), 0, Width, Height))
	else :
		timebox[89] = pygame.draw.rect(background, BLUE,(((Width*11)+8), 0, Width, Height))
	if timeboxstatus[90] :
		timebox[90] = pygame.draw.rect(background, RED,(((Width*11)+8), Height, Width, Height))
	else :
		timebox[90] = pygame.draw.rect(background, BLUE,(((Width*11)+8), Height, Width, Height))
	if timeboxstatus[91] :
		timebox[91] = pygame.draw.rect(background, RED,(((Width*11)+8), Height*2, Width, Height))
	else :
		timebox[91] = pygame.draw.rect(background, BLUE,(((Width*11)+8), Height*2, Width, Height))
	if timeboxstatus[92] :
		timebox[92] = pygame.draw.rect(background, RED,(((Width*11)+8), Height*3, Width, Height))
	else :
		timebox[92] = pygame.draw.rect(background, BLUE,(((Width*11)+8), Height*3, Width, Height))
	if timeboxstatus[93] :
		timebox[93] = pygame.draw.rect(background, RED,(((Width*11)+8), Height*4, Width, Height))
	else :
		timebox[93] = pygame.draw.rect(background, BLUE,(((Width*11)+8), Height*4, Width, Height))
	if timeboxstatus[94] :
		timebox[94] = pygame.draw.rect(background, RED,(((Width*11)+8), Height*5, Width, Height))
	else :
		timebox[94] = pygame.draw.rect(background, BLUE,(((Width*11)+8), Height*5, Width, Height))
	if timeboxstatus[95] :
		timebox[95] = pygame.draw.rect(background, RED,(((Width*11)+8), Height*6, Width, Height))
	else :
		timebox[95] = pygame.draw.rect(background, BLUE,(((Width*11)+8), Height*6, Width, Height))
	if timeboxstatus[96] :
		timebox[96] = pygame.draw.rect(background, RED,(((Width*11)+8), Height*7, Width, Height))
	else :
		timebox[96] = pygame.draw.rect(background, BLUE,(((Width*11)+8), Height*7, Width, Height))
	
	font = pygame.font.Font(None, 14)
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
			
		timetext[w] = font.render(hrsString + ":" + minString, 1, (BLACK))
		timetextpos[w] = timebox[w].x+2, timebox[w].y+8
		background.blit(timetext[w], timetextpos[w])
		min = min + 15
	OKbox = pygame.draw.rect(background, GREEN, (0, 0, 8, 240))
	OKtext = font.render("OK    OK    OK    OK    OK    OK    OK    OK    OK", 1, (BLACK))
	OKtext = pygame.transform.rotate(OKtext,270)
	OKtextpos = OKbox.x-1, OKbox.y+8
	background.blit(OKtext, OKtextpos)
	screen.blit(background, (0, 0))
	pygame.display.flip()

def TimeSelect() :# Populate the time screen with blocks of 15 minutes
	global timeboxstatus
	clock = pygame.time.Clock()
	clock.tick(20)
	OKbox = pygame.draw.rect(background, GREEN, (0, 0, 8, 240))
	timeboxout[1] = pygame.draw.rect(background, BLUE,(8, 0, Width, Height))
	timeboxout[2] = pygame.draw.rect(background, BLACK,(8, Height, Width, Height),2)
	timeboxout[3] = pygame.draw.rect(background, BLACK,(8, Height*2, Width, Height),2)
	timeboxout[4] = pygame.draw.rect(background, BLACK,(8, Height*3, Width, Height),2)
	timeboxout[5] = pygame.draw.rect(background, BLACK,(8, Height*4, Width, Height),2)
	timeboxout[6] = pygame.draw.rect(background, BLACK,(8, Height*5, Width, Height),2)
	timeboxout[7] = pygame.draw.rect(background, BLACK,(8, Height*6, Width, Height),2)
	timeboxout[8] = pygame.draw.rect(background, BLACK,(8, Height*7, Width, Height),2)
	timeboxout[9] = pygame.draw.rect(background, BLACK,(Width+8, 0, Width, Height),2)
	timeboxout[10] = pygame.draw.rect(background, BLACK,(Width+8, Height, Width, Height),2)
	timeboxout[11] = pygame.draw.rect(background, BLACK,(Width+8, Height*2, Width, Height),2)
	timeboxout[12] = pygame.draw.rect(background, BLACK,(Width+8, Height*3, Width, Height),2)
	timeboxout[13] = pygame.draw.rect(background, BLACK,(Width+8, Height*4, Width, Height),2)
	timeboxout[14] = pygame.draw.rect(background, BLACK,(Width+8, Height*5, Width, Height),2)
	timeboxout[15] = pygame.draw.rect(background, BLACK,(Width+8, Height*6, Width, Height),2)
	timeboxout[16] = pygame.draw.rect(background, BLACK,(Width+8, Height*7, Width, Height),2)
	timeboxout[17] = pygame.draw.rect(background, BLACK,(((Width*2)+8), 0, Width, Height),2)
	timeboxout[18] = pygame.draw.rect(background, BLACK,(((Width*2)+8), Height, Width, Height),2)
	timeboxout[19] = pygame.draw.rect(background, BLACK,(((Width*2)+8), Height*2, Width, Height),2)
	timeboxout[20] = pygame.draw.rect(background, BLACK,(((Width*2)+8), Height*3, Width, Height),2)
	timeboxout[21] = pygame.draw.rect(background, BLACK,(((Width*2)+8), Height*4, Width, Height),2)
	timeboxout[22] = pygame.draw.rect(background, BLACK,(((Width*2)+8), Height*5, Width, Height),2)
	timeboxout[23] = pygame.draw.rect(background, BLACK,(((Width*2)+8), Height*6, Width, Height),2)
	timeboxout[24] = pygame.draw.rect(background, BLACK,(((Width*2)+8), Height*7, Width, Height),2)
	timeboxout[25] = pygame.draw.rect(background, BLACK,(((Width*3)+8), 0, Width, Height),2)
	timeboxout[26] = pygame.draw.rect(background, BLACK,(((Width*3)+8), Height, Width, Height),2)
	timeboxout[27] = pygame.draw.rect(background, BLACK,(((Width*3)+8), Height*2, Width, Height),2)
	timeboxout[28] = pygame.draw.rect(background, BLACK,(((Width*3)+8), Height*3, Width, Height),2)
	timeboxout[29] = pygame.draw.rect(background, BLACK,(((Width*3)+8), Height*4, Width, Height),2)
	timeboxout[30] = pygame.draw.rect(background, BLACK,(((Width*3)+8), Height*5, Width, Height),2)
	timeboxout[31] = pygame.draw.rect(background, BLACK,(((Width*3)+8), Height*6, Width, Height),2)
	timeboxout[32] = pygame.draw.rect(background, BLACK,(((Width*3)+8), Height*7, Width, Height),2)
	timeboxout[33] = pygame.draw.rect(background, BLACK,(((Width*4)+8), 0, Width, Height),2)
	timeboxout[34] = pygame.draw.rect(background, BLACK,(((Width*4)+8), Height, Width, Height),2)
	timeboxout[35] = pygame.draw.rect(background, BLACK,(((Width*4)+8), Height*2, Width, Height),2)
	timeboxout[36] = pygame.draw.rect(background, BLACK,(((Width*4)+8), Height*3, Width, Height),2)
	timeboxout[37] = pygame.draw.rect(background, BLACK,(((Width*4)+8), Height*4, Width, Height),2)
	timeboxout[38] = pygame.draw.rect(background, BLACK,(((Width*4)+8), Height*5, Width, Height),2)
	timeboxout[39] = pygame.draw.rect(background, BLACK,(((Width*4)+8), Height*6, Width, Height),2)
	timeboxout[40] = pygame.draw.rect(background, BLACK,(((Width*4)+8), Height*7, Width, Height),2)
	timeboxout[41] = pygame.draw.rect(background, BLACK,(((Width*5)+8), 0, Width, Height),2)
	timeboxout[42] = pygame.draw.rect(background, BLACK,(((Width*5)+8), Height, Width, Height),2)
	timeboxout[43] = pygame.draw.rect(background, BLACK,(((Width*5)+8), Height*2, Width, Height),2)
	timeboxout[44] = pygame.draw.rect(background, BLACK,(((Width*5)+8), Height*3, Width, Height),2)
	timeboxout[45] = pygame.draw.rect(background, BLACK,(((Width*5)+8), Height*4, Width, Height),2)
	timeboxout[46] = pygame.draw.rect(background, BLACK,(((Width*5)+8), Height*5, Width, Height),2)
	timeboxout[47] = pygame.draw.rect(background, BLACK,(((Width*5)+8), Height*6, Width, Height),2)
	timeboxout[48] = pygame.draw.rect(background, BLACK,(((Width*5)+8), Height*7, Width, Height),2)
	timeboxout[49] = pygame.draw.rect(background, BLACK,(((Width*6)+8), 0, Width, Height),2)
	timeboxout[50] = pygame.draw.rect(background, BLACK,(((Width*6)+8), Height, Width, Height),2)
	timeboxout[51] = pygame.draw.rect(background, BLACK,(((Width*6)+8), Height*2, Width, Height),2)
	timeboxout[52] = pygame.draw.rect(background, BLACK,(((Width*6)+8), Height*3, Width, Height),2)
	timeboxout[53] = pygame.draw.rect(background, BLACK,(((Width*6)+8), Height*4, Width, Height),2)
	timeboxout[54] = pygame.draw.rect(background, BLACK,(((Width*6)+8), Height*5, Width, Height),2)
	timeboxout[55] = pygame.draw.rect(background, BLACK,(((Width*6)+8), Height*6, Width, Height),2)
	timeboxout[56] = pygame.draw.rect(background, BLACK,(((Width*6)+8), Height*7, Width, Height),2)
	timeboxout[57] = pygame.draw.rect(background, BLACK,(((Width*7)+8), 0, Width, Height),2)
	timeboxout[58] = pygame.draw.rect(background, BLACK,(((Width*7)+8), Height, Width, Height),2)
	timeboxout[59] = pygame.draw.rect(background, BLACK,(((Width*7)+8), Height*2, Width, Height),2)
	timeboxout[60] = pygame.draw.rect(background, BLACK,(((Width*7)+8), Height*3, Width, Height),2)
	timeboxout[61] = pygame.draw.rect(background, BLACK,(((Width*7)+8), Height*4, Width, Height),2)
	timeboxout[62] = pygame.draw.rect(background, BLACK,(((Width*7)+8), Height*5, Width, Height),2)
	timeboxout[63] = pygame.draw.rect(background, BLACK,(((Width*7)+8), Height*6, Width, Height),2)
	timeboxout[64] = pygame.draw.rect(background, BLACK,(((Width*7)+8), Height*7, Width, Height),2)
	timeboxout[65] = pygame.draw.rect(background, BLACK,(((Width*8)+8), 0, Width, Height),2)
	timeboxout[66] = pygame.draw.rect(background, BLACK,(((Width*8)+8), Height, Width, Height),2)
	timeboxout[67] = pygame.draw.rect(background, BLACK,(((Width*8)+8), Height*2, Width, Height),2)
	timeboxout[68] = pygame.draw.rect(background, BLACK,(((Width*8)+8), Height*3, Width, Height),2)
	timeboxout[69] = pygame.draw.rect(background, BLACK,(((Width*8)+8), Height*4, Width, Height),2)
	timeboxout[70] = pygame.draw.rect(background, BLACK,(((Width*8)+8), Height*5, Width, Height),2)
	timeboxout[71] = pygame.draw.rect(background, BLACK,(((Width*8)+8), Height*6, Width, Height),2)
	timeboxout[72] = pygame.draw.rect(background, BLACK,(((Width*8)+8), Height*7, Width, Height),2)
	timeboxout[73] = pygame.draw.rect(background, BLACK,(((Width*9)+8), 0, Width, Height),2)
	timeboxout[74] = pygame.draw.rect(background, BLACK,(((Width*9)+8), Height, Width, Height),2)
	timeboxout[75] = pygame.draw.rect(background, BLACK,(((Width*9)+8), Height*2, Width, Height),2)
	timeboxout[76] = pygame.draw.rect(background, BLACK,(((Width*9)+8), Height*3, Width, Height),2)
	timeboxout[77] = pygame.draw.rect(background, BLACK,(((Width*9)+8), Height*4, Width, Height),2)
	timeboxout[78] = pygame.draw.rect(background, BLACK,(((Width*9)+8), Height*5, Width, Height),2)
	timeboxout[79] = pygame.draw.rect(background, BLACK,(((Width*9)+8), Height*6, Width, Height),2)
	timeboxout[80] = pygame.draw.rect(background, BLACK,(((Width*9)+8), Height*7, Width, Height),2)
	timeboxout[81] = pygame.draw.rect(background, BLACK,(((Width*10)+8), 0, Width, Height),2)
	timeboxout[82] = pygame.draw.rect(background, BLACK,(((Width*10)+8), Height, Width, Height),2)
	timeboxout[83] = pygame.draw.rect(background, BLACK,(((Width*10)+8), Height*2, Width, Height),2)
	timeboxout[84] = pygame.draw.rect(background, BLACK,(((Width*10)+8), Height*3, Width, Height),2)
	timeboxout[85] = pygame.draw.rect(background, BLACK,(((Width*10)+8), Height*4, Width, Height),2)
	timeboxout[86] = pygame.draw.rect(background, BLACK,(((Width*10)+8), Height*5, Width, Height),2)
	timeboxout[87] = pygame.draw.rect(background, BLACK,(((Width*10)+8), Height*6, Width, Height),2)
	timeboxout[88] = pygame.draw.rect(background, BLACK,(((Width*10)+8), Height*7, Width, Height),2)
	timeboxout[89] = pygame.draw.rect(background, BLACK,(((Width*11)+8), 0, Width, Height),2)
	timeboxout[90] = pygame.draw.rect(background, BLACK,(((Width*11)+8), Height, Width, Height),2)
	timeboxout[91] = pygame.draw.rect(background, BLACK,(((Width*11)+8), Height*2, Width, Height),2)
	timeboxout[92] = pygame.draw.rect(background, BLACK,(((Width*11)+8), Height*3, Width, Height),2)
	timeboxout[93] = pygame.draw.rect(background, BLACK,(((Width*11)+8), Height*4, Width, Height),2)
	timeboxout[94] = pygame.draw.rect(background, BLACK,(((Width*11)+8), Height*5, Width, Height),2)
	timeboxout[95] = pygame.draw.rect(background, BLACK,(((Width*11)+8), Height*6, Width, Height),2)
	timeboxout[96] = pygame.draw.rect(background, BLACK,(((Width*11)+8), Height*7, Width, Height),2)
	global selecting
	selecting = True
	TimeScreen1()
	# run the game loop
	while selecting:
		
		for event in pygame.event.get():
			if event.type == QUIT:
				pygame.quit()
				sys.exit()
				selecting = False  
			elif event.type == pygame.MOUSEBUTTONDOWN:
				for x in range (1, 97) :
					if timeboxout[x].collidepoint(pygame.mouse.get_pos()):
						if timeboxstatus[x] == True	:
							timeboxstatus[x] = False
							WriteJSONFile()
							TimeScreen1()
						else :
							timeboxstatus[x] = True
							WriteJSONFile()
							TimeScreen1()
					if OKbox.collidepoint(pygame.mouse.get_pos()):
						selecting = False
			elif event.type == KEYDOWN and event.key == K_ESCAPE:
				selecting = False
		
		pygame.display.update()

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
		timertext = font.render(BoostTimer, 1, (RED), (BLUE))
		background.blit(timertext, (0, 160))
		screen.blit(background, (0, 0))
		pygame.display.flip()
		if ((time.time() - XMLWriteTime) > XMLWriteDelay) :	
			print "Writing Time to XML"
			WriteXML()	
			XMLWriteTime = time.time()
	elif SystemMode == 1 and TIMER <= 0:
		print "TIMEROUT"
				
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
	if screenRefreshRequested == True :
		screenRefreshRequested = False
		Screen1Refresh()
	
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
			for event in pygame.event.get():
				if event.type == QUIT:
					pygame.quit()
					sys.exit()
					running = False
					listening = False
			
				elif event.type == pygame.MOUSEBUTTONDOWN:
					#print("Pos: %sx%s\n" % pygame.mouse.get_pos())
					if box1.collidepoint(pygame.mouse.get_pos()): # Off Button Pressed
						SystemMode = 0
						WriteXML()
						screenRefreshRequested = True
					
					elif box2.collidepoint(pygame.mouse.get_pos()):
						if Upstairs == True :
							Upstairs = False
						else :
							Upstairs = True
						zoneUpChange = True
						WriteXML()	
						screenRefreshRequested = True
					
					elif box3.collidepoint(pygame.mouse.get_pos()):
						Downstairs != Downstairs
						if Downstairs == True :
							Downstairs = False
						else :
							Downstairs = True
						zoneDownChange = True
						WriteXML()
						screenRefreshRequested = True
						
					elif box4.collidepoint(pygame.mouse.get_pos()):
						Screen1Refresh()
						if SystemMode != 1 :
							BoostDelay = 1800 # 30 mins 3600 for hour
							BoostCount = time.time()
							PreviousSystemModeBoost = SystemMode
							SystemMode = 1
						elif SystemMode == 1 :
							BoostDelay = BoostDelay + 1800
							if BoostDelay >= 18000 :
								BoostDelay = 18000
						WriteXML()
						screenRefreshRequested = True
						
					elif box5.collidepoint(pygame.mouse.get_pos()):
						SystemMode = 2
						TimeScreen1()
						TimeSelect()
						WriteXML()
						screenRefreshRequested = True
						
					elif box6.collidepoint(pygame.mouse.get_pos()):
						SystemMode = 3
						WriteXML()
						screenRefreshRequested = True
					
					if (SystemMode == 2) :
						ReadJSONFile()
				
				elif event.type == KEYDOWN and event.key == K_ESCAPE:
					running = False
					listening = False
			pygame.display.update()
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
			
def ListenSend433() :#Function to listen for OilLevel readings (over 433mhz) --- possibly outside temperature also at a later date
	global OilLevel
	global OilLevelText
	global listening
	#global Listen433Loops
	print ("Initialising PIGPIO daemon")
	os.system('sudo /home/pi/PIGPIO/pigpiod')
	pi = pigpio.pi()
	rx = piVirtualWire.rx(pi, GPIO_RX, 2000) # Set pigpio instance, TX module GPIO pin and baud rate
	data = ""
	while listening == True :
		try :
			#print "Listen433Loops"
			#Listen433Loops = Listen433Loops +1
			while rx.ready():
				msgRecv = rx.get()
				msgRecvLength = len(msgRecv)
				print(msgRecv)
				stringMsg = ""
				for x in range (0, msgRecvLength):
					stringMsg += (str(unichr(msgRecv[x])))
				print "433 Received: ", stringMsg
				data = stringMsg
				while data != "":
					if not data: break
					print "Received Data: ", data
					if (listening == False) :
						print "Listening", listening, "Exiting Thread"
						rx.cancel()
						pi.stop()
						thread.exit()
					elif (listening == True): 
						print "Listening", listening
					if data:
						if "OilLevel" in data :
							print "Arduino TCP Received", data
							try:
								OilLevelInt = int(re.search(r'\d+', data).group())
							except ValueError :
								OilLevel = "   "
							
							OilLevel = str(OilLevelInt)
							OilLevelText = "OilLevel = "
							OilLevelText += OilLevel
							XMLWriteRequest = True
							screenRefreshRequested = True
							data = ""
			time.sleep(0.5)
		except Exception, e:
			print "ListenSend433", repr(e)
			
	rx.cancel()
	pi.stop()	
	thread.exit()			

if __name__ == '__main__' :
	
	HOST, PORT = '', 8889
	server = SocketServer.TCPServer((HOST, PORT), MyTCPHandler)
	try:
		threading.Thread(target=ListenSend433).start()
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