#!/bin/bash
cd /home/pi
echo -e "\x1b[0;32mINSTALLER:\x1b[m  Automatic Installation of Collie147s Raspberry Pi Heating System"
echo -e "\x1b[0;32mINSTALLER:\x1b[m  Updating Aptitude - Please Wait..."
echo
sudo aptitude update
echo -e "\x1b[0;32mINSTALLER:\x1b[m  installing evtest, xinput, python-dev, python-pip, pygame, php5, memcached and mcrypt"
echo
sudo aptitude install -y libts-bin evtest xinput python-dev python-pip python-software-properties python-pygame php5-fpm php5-suhosin php5-gd php-apc php5-mcrypt php5-cli php5-curl mcrypt memcached php5-memcache
echo -e "\x1b[0;32mINSTALLER:\x1b[m  installing evdev"
echo
sudo pip install evdev
echo -e "\x1b[0;32mINSTALLER:\x1b[m  installing nginx web hosting software"
echo
sudo aptitude install -y nginx
echo -e "\x1b[0;32mINSTALLER:\x1b[m  installing pywapi - Python Weather API"
echo
wget https://launchpad.net/python-weather-api/trunk/0.3.8/+download/pywapi-0.3.8.tar.gz
tar -zxvf pywapi-0.3.8.tar.gz
cd pywapi-0.3.8
sudo python setup.py build
sudo python setup.py install
cd /home/pi
echo -e "\x1b[0;32mINSTALLER:\x1b[m  installing PIGPIO (necessary for 433mhz communication)"
echo
wget abyz.co.uk/rpi/pigpio/pigpio.zip
unzip -o pigpio.zip
cd /home/pi/PIGPIO
sudo make
sudo make install
rm /home/pi/pigpio.zip
cd /home/pi
echo -e "\x1b[0;32mINSTALLER:\x1b[m  copying piVirtualWire"
echo
sudo cp -r /home/pi/RPiHeatingInstall/piVirtualWire /home/pi
echo -e "\x1b[0;32mINSTALLER:\x1b[m  copying config files for nginx"
echo
sudo cp -r /home/pi/RPiHeatingInstall/etc/* /etc
echo -e "\x1b[0;32mINSTALLER:\x1b[m  copying website files and changing permissions"
echo
echo -e "\x1b[0;32mINSTALLER:\x1b[m  Do you wish to use a touchscreen or web control only"
TOUCHSCREEN="YES"
OPTIONS="Touchscreen Web_Only"
select opt in $OPTIONS; do
	if [ "$opt" = "Touchscreen" ]; then
		TOUCHSCREEN="YES"
		break
	elif [ "$opt" = "Web_Only" ]; then
		TOUCHSCREEN="NO"
		break
	fi
done
echo -e "\x1b[0;32mINSTALLER:\x1b[m  Raspberry Pi configured on static IP address 192.168.1.240 on eth0"
echo -e "\x1b[0;32mINSTALLER:\x1b[m  Do you wish to reconfigure this address and/or interface?"
IPADDRESS="192.168.1.240"
ROUTERADDRESS="192.168.1.1"
DNSADDRESS=$ROUTERADDRESS
RESULT="No"
CONFIRM="No"
OPTIONS1="Yes No"
INTERFACE="eth0"
select opt in $OPTIONS1; do
	if [ "$opt" = "Yes" ]; then
		while [ "$CONFIRM" = "No" ]; do
			echo -e "\x1b[0;32mINSTALLER:\x1b[m  Select Interface for static connection"
			SUBOPTION1="$(ifconfig -a | sed 's/[ \t].*//;/^\(lo\|\)$/d')"
			select subopt1 in $SUBOPTION1; do
				INTERFACE=$subopt1
				break
			done
			echo -e "\x1b[0;32mINSTALLER:\x1b[m  Enter IP addresses below - DELETE DEFAULT INPUT first then Press [Enter]"
			read -p $'\e[32mINSTALLER:\e[0m  Enter new IP address for Raspberry Pi:-' -e -i 192.168.1.240 IPADDRESS
			read -p $'\e[32mINSTALLER:\e[0m  Enter Router IP Address:-' -e -i 192.168.1.1 ROUTERADDRESS
			read -p $'\e[32mINSTALLER:\e[0m  Enter DNS IP address:-' -e -i $ROUTERADDRESS DNSADDRESS
	  
			echo $IPADDRESS
			echo $ROUTERADDRESS
			echo $DNSADDRESS
			SUBOPTION2="Yes No"
			select subopt2 in $SUBOPTION2; do
				if [ "$subopt2" = "Yes" ]; then
					CONFIRM=$subopt2
					break
				elif [ "$subopt2" = "No" ]; then
					CONFIRM=$subopt2
					break
				else
					echo -e "\x1b[0;32mINSTALLER:\x1b[m  bad option enter 1 or 2"
					echo -e "\x1b[0;32mINSTALLER:\x1b[m  1. Yes"
					echo -e "\x1b[0;32mINSTALLER:\x1b[m  2. No"
				fi
			done
		done
		RESULT="YES"
		break
	elif [ "$opt" = "No" ]; then
		echo -e "\x1b[0;32mINSTALLER:\x1b[m  Excellent.  Moving on..."
		break
	else
		clear
		echo -e "\x1b[0;32mINSTALLER:\x1b[m  bad option enter 1 or 2"
		echo -e "\x1b[0;32mINSTALLER:\x1b[m  1. Yes"
		echo -e "\x1b[0;32mINSTALLER:\x1b[m  2. No"
	fi
done
sudo cp -r /home/pi/RPiHeatingInstall/html/* /var/www/html/
sudo chown -R root:root /var/www/html/*.*
sudo ln -s /etc/nginx/sites-available/www /etc/nginx/sites-enabled/www
sudo rm /etc/nginx/sites-enabled/default
sudo python /home/pi/RPiHeatingInstall/CreateJson.py
sudo rm /var/www/html/index.nginx-debian.html
echo -e "\x1b[0;32mINSTALLER:\x1b[m  Choose which version to run"
echo -e "\x1b[0;32mINSTALLER:\x1b[m  1. Oil unit using 433mhz communications"
echo -e "\x1b[0;32mINSTALLER:\x1b[m  2. Oil unit using wifi/TCP communications"
RED_LED_GPIO_PIN="24"
GREEN_LED_GPIO_PIN="23"
RELAY_GPIO_PIN="22"
OPTIONS2="433mhz Wifi/TCP"
select opt in $OPTIONS2; do
	if [ "$opt" = "433mhz" ]; then
	  echo -e "\x1b[0;32mINSTALLER:\x1b[m  433mhz Setup"
	  if [ "$TOUCHSCREEN" = "YES" ]; then
		sudo cp /home/pi/RPiHeatingInstall/RPiHeatingScreenOil433.py /home/pi/RPiHeatingScreen.py
	  else 
	    sudo cp /home/pi/RPiHeatingInstall/RPiHeatingScreenOil433NOSCREEN.py /home/pi/RPiHeatingScreen.py
	  fi
	  RX_433_GPIO_PIN="4"
	  TX_433_GPIO_PIN="3"
	  echo -e "\x1b[0;32mINSTALLER:\x1b[m  Do you want to Manually configure GPIO connections?"
	  echo -e "\x1b[0;32mINSTALLER:\x1b[0;33m  WARNING!!! This could conflict with your touchscreen\x1b[m"
	  echo -e "\x1b[0;32mINSTALLER:\x1b[0;33m  WARNING!!! Check your touchscreen datasheet first!\x1b[m"
	  echo -e "\x1b[0;32mINSTALLER:\x1b[0;33m  NB If your touchscreen uses PIN 5/7/15/16/18 (GPIO 3/4/22/23/24)\x1b[m"
	  echo -e "\x1b[0;32mINSTALLER:\x1b[0;33m              You will need to re-configure this!\x1b[m"
	  SUBOPTION3="Yes No"
	  select subopt3 in $SUBOPTION3; do
		if [ "$subopt3" = "Yes" ]; then
			read -p $'\e[32mINSTALLER:\e[0m  Enter GPIO Pin for \e[31mRED LED\e[0m:-' -e -i $RED_LED_GPIO_PIN RED_LED_GPIO_PIN
			read -p $'\e[32mINSTALLER:\e[0m  Enter GPIO Pin for \e[32mGREEN LED\e[0m:-' -e -i $GREEN_LED_GPIO_PIN GREEN_LED_GPIO_PIN
			read -p $'\e[32mINSTALLER:\e[0m  Enter GPIO Pin for \e[93mRELAY\e[0m:-' -e -i $RELAY_GPIO_PIN RELAY_GPIO_PIN
			read -p $'\e[32mINSTALLER:\e[0m  Enter GPIO Pin for \e[96m433Mhz RX <--\e[0m:-' -e -i $RX_433_GPIO_PIN RX_433_GPIO_PIN
			read -p $'\e[32mINSTALLER:\e[0m  Enter GPIO Pin for \e[95m433Mhz TX -->\e[0m:-' -e -i $TX_433_GPIO_PIN TX_433_GPIO_PIN
			break
		elif [ "$subopt3" = "No" ]; then
			break
		else
			clear
			echo -e "\x1b[0;32mINSTALLER:\x1b[m  bad option enter 1 or 2"
			echo -e "\x1b[0;32mINSTALLER:\x1b[m  1. Yes"
			echo -e "\x1b[0;32mINSTALLER:\x1b[m  2. No"
		fi
	  done
      sed -i "s/*RX_433_GPIO_PIN/$RX_433_GPIO_PIN/g" /home/pi/RPiHeatingScreen.py
	  sed -i "s/*TX_433_GPIO_PIN/$TX_433_GPIO_PIN/g" /home/pi/RPiHeatingScreen.py
	  break
	elif [ "$opt" = "Wifi/TCP" ]; then
	  echo -e "\x1b[0;32mINSTALLER:\x1b[m  Wifi/TCP"
	  if [ "$TOUCHSCREEN" = "YES" ]; then
		sudo cp /home/pi/RPiHeatingInstall/RPiHeatingScreenOilTCP.py /home/pi/RPiHeatingScreen.py
	  else
	    sudo cp /home/pi/RPiHeatingInstall/RPiHeatingScreenOilTCPNOSCREEN.py /home/pi/RPiHeatingScreen.py
	  fi
	  echo -e "\x1b[0;32mINSTALLER:\x1b[m  Do you want to Manually configure GPIO connections?"
	  echo -e "\x1b[0;32mINSTALLER:\x1b[0;33m  WARNING!!! This could conflict with your touchscreen\x1b[m"
	  echo -e "\x1b[0;32mINSTALLER:\x1b[0;33m  WARNING!!! Check your touchscreen datasheet first!\x1b[m"
	  echo -e "\x1b[0;32mINSTALLER:\x1b[0;33m  NB If your touchscreen uses PIN 15/16/18 (GPIO 22/23/24)\x1b[m"
	  echo -e "\x1b[0;32mINSTALLER:\x1b[0;33m            You will need to re-configure this!\x1b[m"
	  SUBOPTION3="Yes No"
	  select subopt3 in $SUBOPTION3; do
		if [ "$subopt3" = "Yes" ]; then
			read -p $'\e[32mINSTALLER:\e[0m  Enter GPIO Pin for \e[31mRED LED\e[0m:-' -e -i $RED_LED_GPIO_PIN RED_LED_GPIO_PIN
			read -p $'\e[32mINSTALLER:\e[0m  Enter GPIO Pin for \e[32mGREEN LED\e[0m:-' -e -i $GREEN_LED_GPIO_PIN GREEN_LED_GPIO_PIN
			read -p $'\e[32mINSTALLER:\e[0m  Enter GPIO Pin for \e[93mRELAY\e[0m:-' -e -i $RELAY_GPIO_PIN RELAY_GPIO_PIN
			break
		elif [ "$subopt3" = "No" ]; then
			break
		else
			clear
			echo -e "\x1b[0;32mINSTALLER:\x1b[m  bad option enter 1 or 2"
			echo -e "\x1b[0;32mINSTALLER:\x1b[m  1. Yes"
			echo -e "\x1b[0;32mINSTALLER:\x1b[m  2. No"
		fi
	  done
	  break
	else
	  clear
	  echo -e "\x1b[0;32mINSTALLER:\x1b[m  bad option enter 1 or 2"
	  echo -e "\x1b[0;32mINSTALLER:\x1b[m  1. Oil unit using 433mhz communications"
	  echo -e "\x1b[0;32mINSTALLER:\x1b[m  2. Oil unit using wifi/TCP communications"
	fi
done
sed -i "s/*RED_LED_GPIO_PIN/$RED_LED_GPIO_PIN/g" /home/pi/RPiHeatingScreen.py
sed -i "s/*GREEN_LED_GPIO_PIN/$GREEN_LED_GPIO_PIN/g" /home/pi/RPiHeatingScreen.py
sed -i "s/*RELAY_GPIO_PIN/$RELAY_GPIO_PIN/g" /home/pi/RPiHeatingScreen.py
sudo cp /home/pi/RPiHeatingInstall/rc.local /etc
CURRENTIPADDRESS="$(sudo hostname -I)"]
echo -e "\x1b[0;32mINSTALLER:\x1b[m  Writing IP address changes to files"
echo -e "\x1b[0;32mINSTALLER:\x1b[m  dhcpcd.conf"
sudo cp /home/pi/RPiHeatingInstall/etc/dhcpcd.conf /etc
sudo sed -i "s/*INTERFACE/$INTERFACE/g" /etc/dhcpcd.conf
sudo sed -i "s/*IPADDRESS/$IPADDRESS/g" /etc/dhcpcd.conf
sudo sed -i "s/*ROUTER/$ROUTERADDRESS/g" /etc/dhcpcd.conf
sudo sed -i "s/*DNS/$DNSADDRESS/g" /etc/dhcpcd.conf
echo -e "\x1b[0;32mINSTALLER:\x1b[m  RPiHeatingScreen.py"
sudo sed -i "s/*IPADDRESS/$IPADDRESS/g" /home/pi/RPiHeatingScreen.py
echo -e "\x1b[0;32mINSTALLER:\x1b[m  heating.php and heating2.php"
sudo sed -i "s/*IPADDRESS/$IPADDRESS/g" /var/www/html/heating.php
sudo sed -i "s/*IPADDRESS/$IPADDRESS/g" /var/www/html/heating2.php
if [ "$TOUCHSCREEN" = "YES" ]; then
	echo -e "\x1b[0;32mINSTALLER:\x1b[m  Select your touchscreen device"
	SelectedDevice="None"
	DEVICES="$(sudo python /home/pi/RPiHeatingInstall/listDevices.py)"
	#echo DEVICES $DEVICES
	eval set $DEVICES
	select opt in "$@"; do
		#echo "$opt"
		SelectedDevice="$opt"
		echo "$SelectedDevice"
		break
	done
	echo -e "\x1b[0;32mINSTALLER:\x1b[m  '"$SelectedDevice"' will be inserted into the python script"
	if [ "$SelectedDevice" != "None" ]; then
		sed -i "s/*TOUCHSCREEN/$SelectedDevice/g" /home/pi/RPiHeatingScreen.py
		sudo cp /home/pi/RPiHeatingInstall/testTouchScreen.py /home/pi
		sed -i "s/*TOUCHSCREEN/$SelectedDevice/g" /home/pi/testTouchScreen.py
	fi
	echo -e "\x1b[0;32mINSTALLER:\x1b[m  Screen resolution set at 320 x 240.  Do you want to change this?"
	OPTIONS3="Yes No"
	HORIZONTAL="320"
	VERTICAL="240"	
	select opt in $OPTIONS3; do
		if [ "$opt" = "Yes" ]; then
			read -p $'\e[32mINSTALLER:\e[0m  Enter Horizonal Number of Pixels:-' -e -i $HORIZONTAL HORIZONTAL
			read -p $'\e[32mINSTALLER:\e[0m  Enter Vertical Number of Pixels:-' -e -i $VERTICAL VERTICAL
			break
		elif [ "$opt" = "No" ]; then
			echo -e "\x1b[0;32mINSTALLER:\x1b[m  Excellent.  Moving on..."
			break
		else
			clear
			echo -e "\x1b[0;32mINSTALLER:\x1b[m  bad option enter 1 or 2"
			echo -e "\x1b[0;32mINSTALLER:\x1b[m  1. Yes"
			echo -e "\x1b[0;32mINSTALLER:\x1b[m  2. No"
		fi
	done
	sed -i "s/*HORIZONTAL/$HORIZONTAL/g" /home/pi/RPiHeatingScreen.py
	sed -i "s/*VERTICAL/$VERTICAL/g" /home/pi/RPiHeatingScreen.py
	sed -i "s/*HORIZONTAL/$HORIZONTAL/g" /home/pi/testTouchScreen.py
	sed -i "s/*VERTICAL/$VERTICAL/g" /home/pi/testTouchScreen.py
	echo -e "\x1b[0;32mINSTALLER:\x1b[m  Calibrating Touchscreen"
	sudo python /home/pi/RPiHeatingInstall/calibrateDevice.py "$SelectedDevice"
	echo -e "\x1b[0;32mINSTALLER:\x1b[m  Testing touchscreen - Test if mouse follows input before exit"
	echo -e "\x1b[0;32mINSTALLER:\x1b[m  NB If you cannot click HERE to exit press CTRL+C"
	sleep 1
	sudo python /home/pi/testTouchScreen.py
	echo -e "\x1b[0;32mINSTALLER:\x1b[m  Did the mouse follow inputs?"
	OPTIONS4="Yes No Error"
	select opt in $OPTIONS4; do
		if [ "$opt" = "Yes" ]; then
			echo -e "\x1b[0;32mINSTALLER:\x1b[m  Excellent. Moving on..."
			break
		elif [ "$opt" = "No" ]; then
			echo -e "\x1b[0;32mINSTALLER:\x1b[m  Applying Fix"
			sudo bash /home/pi/RPiHeatingInstall/installsd1.sh
			echo
			echo
			break
		elif [ "$opt" = "Error" ]; then
			echo -e "\x1b[0;32mINSTALLER:\x1b[m  There appears to be an issue with your screen"
			echo -e "\x1b[0;32mINSTALLER:\x1b[m  you can modify the testTouchScreen.py script"
			echo -e "\x1b[0;32mINSTALLER:\x1b[m  and change the resolution to match your screen"
			echo -e "\x1b[0;32mINSTALLER:\x1b[m  or there may be another issue"
			echo -e "\x1b[0;32mINSTALLER:\x1b[m  NB this is not tested on any other screens!"
			echo
			sleep 1
			break
		else
			clear
			echo -e "\x1b[0;32mINSTALLER:\x1b[m  bad option enter 1 or 2"
			echo -e "\x1b[0;32mINSTALLER:\x1b[m  1. Yes"
			echo -e "\x1b[0;32mINSTALLER:\x1b[m  2. No"
		fi
	done
fi
ESP8266ValveIPADDRESS="192.168.1.242"
read -p $'\e[32mINSTALLER:\e[0m  Enter IP address for the valve controller:-' -e -i $ESP8266ValveIPADDRESS ESP8266ValveIPADDRESS
while [ "$ESP8266ValveIPADDRESS" = "$IPADDRESS" ]; do
	echo -e "\x1b[0;32mINSTALLER:\x1b[m  IP Address for valve controller (ESP8266)"
	echo -e "\x1b[0;32mINSTALLER:\x1b[m  cannot be same as Raspberry Pi IP Address"
	read -p $'\e[32mINSTALLER:\e[0m  Enter a DIFFERENT IP address:-' -e -i $ESP8266ValveIPADDRESS ESP8266ValveIPADDRESS
done
echo -e "\x1b[0;32mINSTALLER:\x1b[m  Do you want access the web interface over the internet"
echo -e "\x1b[0;32mINSTALLER:\x1b[m  or restrict access only to local network addresses?"
OPTIONS5="Internet Local"
select opt in $OPTIONS5; do
	if [ "$opt" = "Local" ]; then
		IFS=. read ip1 ip2 ip3 ip4 <<< "$IPADDRESS"
		DOMAINADDRESS="$ip1.$ip2.$ip3.0"
		#echo -e "\x1b[0;32mINSTALLER:\x1b[m  DOMAINADDRESS="$DOMAINADDRESS
		sudo cp /home/pi/RPiHeatingInstall/etc/nginx/sites-available/www /etc/nginx/sites-available/
		sudo sed -i "s/#LOCKDOWNIPADDRESS/allow $DOMAINADDRESS/g" /etc/nginx/sites-available/www
		sudo sed -i "s/#LOCKDOWNLOCAL/allow 127.0.0.1/g" /etc/nginx/sites-available/www
		sudo sed -i "s/#LOCKDOWNALL/deny all/g" /etc/nginx/sites-available/www		
		break
	elif [ "$opt" = "Internet" ]; then
		echo -e "\x1b[0;32mINSTALLER:\x1b[m  You will need to set up port forwarding on your router for access"
		echo -e "\x1b[0;32mINSTALLER:\x1b[m  Ports 80 and 8889 will need to be forwarded to address $IPADDRESS"
		break
	else
		clear
		echo -e "\x1b[0;32mINSTALLER:\x1b[m  bad option enter 1 or 2"
		echo -e "\x1b[0;32mINSTALLER:\x1b[m  1. Internet"
		echo -e "\x1b[0;32mINSTALLER:\x1b[m  2. Local"
	fi
done
WebUSER="Heating"
WebPASS="Password123"
read -p $'\e[32mINSTALLER:\e[0m  Enter Username for the web admin:-' -e -i $WebUSER WebUSER
read -p $'\e[32mINSTALLER:\e[0m  Enter Password for the web admin:-' -e -i $WebPASS WebPASS
sudo sed -i "s/*WebUSER/$WebUSER/g" /var/www/html/login.php
sudo sed -i "s/*WebPASS/$WebPASS/g" /var/www/html/login.php
sed -i "s/*ESP8266ValveIPADDRESS/$ESP8266ValveIPADDRESS/g" /home/pi/RPiHeatingScreen.py	
echo -e "\x1b[0;32mINSTALLER:\x1b[m  Rebooting Now - NB Raspberry pi will be available @ "$IPADDRESS
sudo reboot
exit
