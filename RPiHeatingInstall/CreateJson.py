import pygame, sys, os, time, json
from pygame.locals import *
import socket
from time import sleep
import RPi.GPIO as GPIO
from threading import Timer
from threading import Thread
import time
import select
from evdev import InputDevice, list_devices
import datetime

timeboxstatus = range(97)
for x in range (1, 97) :
	timeboxstatus[x] = False
FileTimeSave = open('json.txt', 'w+')
	
json.dump(timeboxstatus, FileTimeSave)
os.system('sudo mv json.txt /var/www/html/json.txt')	
os.system('sudo chown "$user":www-data /var/www/html/json.txt')
os.system('sudo chmod 664 /var/www/html/json.txt')

