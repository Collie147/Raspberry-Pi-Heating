import pywapi, string, sys, os

city = ""
country = ""
locations = ""
locationNum = 0
finalLocationCode = ""
locationCode = ""
def inputLocation():
	global city
	global country
	global locations
	global locationNum
	city = str(raw_input('\x1b[0;32mINSTALLER:\x1b[m Enter your nearest city or town: '))
	country = str(raw_input('\x1b[0;32mINSTALLER:\x1b[m Enter your country: '))
	locations = pywapi.get_location_ids( city+","+country )
	
	for index in range(len(locations)):
		print index+1, " ", locations.values()[index]
	print "\x1b[0;32mINSTALLER:\x1b[m input the number that corresponds to your nearest location"
	locationNum = int(raw_input("\x1b[0;32mINSTALLER:\x1b[m (enter '0' to search again: "))
def getLocationCode():
	global locationNum
	global locationCode
	global finalLocationCode
	locationNum = locationNum - 1
	locationName = locations.values()[locationNum]
	#print "you have selected ", locationName
	locationCode = locations.keys()[locationNum]
	#print "the key for this is ", locationCode
	
	finalLocationCode= locationCode
def main():
	if locationNum == 0:
		inputLocation()
	elif locationNum > 0:
		getLocationCode()
	else :
		exit()
while finalLocationCode == "":
	main()
os.system('sudo sed -i "s/*locationCode/'+finalLocationCode+'/g" /home/pi/RPiHeatingScreen.py	')