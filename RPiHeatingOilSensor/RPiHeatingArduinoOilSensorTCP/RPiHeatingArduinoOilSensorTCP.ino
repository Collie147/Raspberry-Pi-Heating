/*
 * ESP8266 ESP-07 Home Heating Oil sensor node
 * 
 *    ESP8266 ESP-07 Pinout
 * RST--------------------TXD
 * ADC--------------------RXD
 * CH_PD----------------GPIO4
 * GPIO16---------------GPIO5
 * GPIO14---------------GPIO0
 * GPIO12---------------GPIO2
 * GPIO13--------------GPIO15
 * VCC--------------------GND
 * 
 * Connections 
 * 
 * DS18B20
 * VCC----DATA----GND
 *  |      |       |
 *  +-4.7K-+       |
 *  |      |       |
 *  3.3v  GPIO5   GND
 *  
 * HC-SR04 
 * VCC----Trig----Echo----GND
 *  |       |      |       |
 *  5v    GPIO4  GPIO13   GND
 *  
 *  ESP8266
 *  GPIO16--> RST (jumper pins)
 *  
 *   Battery --> 100K --> ADC
 *   (>7v)        |
 *     |          |        
 *   5v Reg      6.8K
 *     |          |
 *   3.3v Reg    GND
 *    
 *                            
 */                     




#include <ESP8266WiFi.h>
#include <WiFiClient.h>
#include <Wire.h>
#include <SPI.h>
#include <OneWire.h>
#include <DallasTemperature.h>

#define ONE_WIRE_BUS 5  // DS18B20 pin on GPIO5
OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature DS18B20(&oneWire);

String tempString = ""; //string value of the temperature
float tempLong; //float value of the temperature

unsigned int distance; //int value for the distance reading of the HC-SR04
#define TriggerPin 4 //trigger pin on GPIO4
#define EchoPin 13 //echo pin on GPIO 13 - circuit has built in mosfet on GPIO13

//Insert your Tank Dimensions (only for horizontal cylindrical Tank) - calculations are approximate
double Length = 1750; //input the Oil tank dimensions here
double Height = 1000;
//standard definitions for calculations
float pi = 3.14159; //calculations for tank capacity and fill level
double radius = Height / 2;
double R2 = radius * radius;
double capacity = (((pi*R2) * Length) / 1000000);

//battery read definitions (resistors used 100K and 6.7K measured with Multimeter for more accuracy and divided by 1000
#define voltReadPin A0
float Resistor1 = 97;
float Resistor2 = 6.8;

//sleep definitions
#define sleepMinutes 1
long sleepSeconds = sleepMinutes * 60;

const char* ssid     = "SSIDNAME";//change to SSID name
const char* password = "SSIDPASS";//change to SSID password

//Static IP address Settings, client IP and port
IPAddress ip(192, 168, 1, 241); //static IP address
IPAddress gateway(192, 168, 1, 1); //gateway
IPAddress subnet(255, 255, 0, 0);//subnet
IPAddress HOST(192, 168, 1, 240); //client address to send data to
#define PORT 5005 //port to send client messages to
int status = WL_IDLE_STATUS;
String IP;

//function prototypes
void ScanAP();
void TempRead();
void DistanceRead();
void OilStateQuery();
double getVolume(double distance);
float getBatteryLevel();
void BatteryQuery();
void GoToSleep();

WiFiServer server(PORT);
void setup() {
  Serial.begin(9600);
  WiFi.begin(ssid, password);//begin connection to wifi access point/router
  WiFi.config(ip, gateway, subnet); //sets the connection to static
  while (WiFi.status() != WL_CONNECTED) // Wait for connection
  {
    Serial.print(".");//adds a dot for each half second that the connection is not established
    delay(100);
  }
  Serial.print("Connected to "); //sends serial information about the connection
  Serial.println(ssid);
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
  IPAddress localIP = WiFi.localIP();
  IP = String(localIP[0]);
  IP += ".";
  IP += String(localIP[1]);
  IP += ".";
  IP += String(localIP[2]);
  IP += ".";
  IP += String(localIP[3]);

  pinMode(TriggerPin, OUTPUT);
  pinMode(EchoPin, INPUT);
}

void loop() {
  if (ESP.getResetReason() == "Deep-Sleep Wake") {
    Serial.println("Waking Up from Sleep");
  }
  if (WiFi.status() != WL_CONNECTED)
  {
    ESP.reset();
  }
  ScanAP();
  TempRead();
  OilStateQuery();
  BatteryQuery();
  GoToSleep();
}

void sendClientMessage(String clientString) {
  
  WiFiClient client = server.available();
  if (!client.connect(HOST, PORT)) {
    Serial.println("connection failed");
  }
  else {
    Serial.print("sending clientString=");
    Serial.println(clientString);
    client.println(clientString);
    delay(250);
    client.stop();
  }
}

void ScanAP(void) {
  WiFi.mode(WIFI_STA);
  delay(100);
  int n = WiFi.scanNetworks();
  String clientString;
  String SSIDandRSSI;
  if (WiFi.status() != WL_CONNECTED) {
    WiFi.begin(ssid, password);
  }
  while (WiFi.status() != WL_CONNECTED) // Wait for connection
  {
    Serial.print(".");//adds a dot for each half second that the connection is not established
    delay(100);
  }
  Serial.println("scan done");
  if (n == 0)
    Serial.println("no networks found");
  else
  {
    Serial.print(n);
    Serial.println(" networks found");
    for (int i = 0; i < n; ++i)
    {
      // Print SSID and RSSI for each network found
      SSIDandRSSI = String(i + 1);
      SSIDandRSSI += ": ";
      SSIDandRSSI += String(WiFi.SSID(i));
      SSIDandRSSI += " (";
      SSIDandRSSI += String(WiFi.RSSI(i));
      SSIDandRSSI += "dB)";
      SSIDandRSSI += " Enc:";
      switch (WiFi.encryptionType(i)) {
        case (ENC_TYPE_NONE):
          SSIDandRSSI += "None";
          break;
        case (ENC_TYPE_WEP):
          SSIDandRSSI += "WEP";
          break;
        case (ENC_TYPE_TKIP):
          SSIDandRSSI += "WPA";
          break;
        case (ENC_TYPE_CCMP):
          SSIDandRSSI += "WPA2";
          break;
        case (ENC_TYPE_AUTO):
          SSIDandRSSI += "Auto";
          break;
        default:
          SSIDandRSSI += "N/A";
      }
      Serial.println(SSIDandRSSI);
      clientString += SSIDandRSSI;
      clientString += "\r\n";
     }
    sendClientMessage(clientString);
  }
}

void TempRead(void)
{
  // call DS18B20.requestTemperatures() to issue a global temperature
  // request to all devices on the bus
  float tmp = 0;//create a value to hold the temperature
  float TempTmp = 0;//create another value to get the average temperature over a number of readings
  float samples[10];//number of samples in an array
  char buffer[8];//buffer to convert the float to a string
  //Serial.print(F("Temperature is: "));
  DS18B20.requestTemperatures(); // Send the command to get temperatures
  for (int i = 0; i <= 9; i++) { //for loop to get the average temperature reading
    samples[i] = DS18B20.getTempCByIndex(0);//set the sample value to that of the reading
    TempTmp = TempTmp + samples[i];//add the sample values together
  }
  tmp = TempTmp / 10.0;//divide by the number of samples to get the average
  if (tmp == -127 || (tmp > 127 && tmp < 128))//if theres an error in communications with the DS18B20
  {
    Serial.println(F("Temp Read Error"));
  }
  if (tmp == 85)//another error handler
  {
    DS18B20.requestTemperatures();//retry without the average reading
    tmp = DS18B20.getTempCByIndex(0);
    if (tmp == 85)
    {
      Serial.println(F("Temperature is unavailable"));//if the error is the same
    }
  }
  if (tmp != 85)//if there is no error
  {
    tempLong = ((int)(tmp * 100)) / 100.0;//calculates the value of temp to one decimal place
    #ifdef DEBUG
      Serial.println(tmp);
      Serial.println(tempLong, 1);
    #endif
    tempString = dtostrf(tempLong, 4, 1, buffer);//convert it to a string
    Serial.print("Temp: ");//print the string
    Serial.println(tempString);
    String clientMessage = "Temp:";//add a prefix to the message so the receiver knows what the value refers to
    clientMessage += tempString;//adds the value to the string
    sendClientMessage(clientMessage);
  }
}
void DistanceRead(void)
{
  unsigned int SensorReading;//create an int to store the reading
  digitalWrite(TriggerPin, LOW);//make sure the trigger pin is low
  delayMicroseconds(2);//wait
  digitalWrite(TriggerPin, HIGH);//turn on the trigger pin
  delayMicroseconds(10);//wait
  digitalWrite(TriggerPin, LOW);//turn off the trigger pin
  SensorReading = pulseIn(EchoPin, HIGH);//listen for the echo
  //test distance = high level time * velocity (speed of sound ~340m/s) / 2
  distance = SensorReading / 58;//distance is set as the reading divided by 58 for CM or 148 for inch
  Serial.print(F("Distance = "));
  Serial.print(distance, DEC);
  Serial.println(F("CM"));
}
void OilStateQuery(void)
{
  DistanceRead();//Read the distance
  int Volume = getVolume(distance);//create an int to store the volume value
  String clientMessage = "OilLevel:";//add a prefix to the message so the receiver knows what the value refers to
  clientMessage += String(Volume);//adds the value to the string
  Serial.println(clientMessage);
  sendClientMessage(clientMessage);
}
double getVolume(double distance)
{
  double Level = Height - (distance * 10); //get the level (distance to the oil)
  //formula to calculate a horizontal cylinders volume using measurements at the start of the sketch
  double Volume = ((Length * ((R2 * acos(1 - 2 * (Level / Height))) - ((radius - Level) * sqrt(Level * (Height - Level))))) / 1000000);
  return Volume;
}
float getBatteryLevel() {
  int voltRead = (analogRead(voltReadPin));
  float roughVoltage = voltRead / 1024.0;
  float batteryVoltage = roughVoltage / (Resistor2 / (Resistor1 + Resistor2)); //sets the battery voltage as the voltage read minus the voltage divider circuit (as battery is more than 5v it would destroy the chip)
#ifdef DEBUG
  Serial.print("analogRead=");
  Serial.println(voltRead);
  Serial.print("Rough Voltage = ");
  Serial.println(roughVoltage);
  Serial.print("analogRead*voltage=");
  Serial.println(batteryVoltage);
#endif
  return batteryVoltage;
}

void BatteryQuery() {
  float batteryVoltage = getBatteryLevel();
  String TempMessage = "BatteryVoltage:";
  TempMessage += String(batteryVoltage);
  String clientMessage = "BattVolt:";
  clientMessage += String(batteryVoltage);
  sendClientMessage(clientMessage);
  Serial.print("Battery Voltage =");
  Serial.println(batteryVoltage);
}

void GoToSleep(){
  if (sleepSeconds / 60 >= 1) {
    Serial.print("Going to sleep for");
    Serial.print(sleepSeconds / 60);
    if (sleepSeconds / 60 == 1) {
      Serial.println(" Minute");
    }
    else {
      Serial.println(" Minutes");
    }
  }
  else {
    Serial.print("Going to sleep for ");
    Serial.print(sleepSeconds);
    if (sleepSeconds == 1) {
      Serial.println(" Second");
    }
    else {
      Serial.println(" Seconds");
    }
  }
  ESP.deepSleep(1000000 * sleepSeconds, RF_NO_CAL); //sleep * seconds(1000000*5=5seconds) - Options (WAKE_RF_DEFAULT, WAKE_RFCAL, WAKE_NO_RFCAL, WAKE_RF_DISABLED) GPIO16 --> RST
}

