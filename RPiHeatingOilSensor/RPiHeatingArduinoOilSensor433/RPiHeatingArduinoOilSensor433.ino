#include <VirtualWire.h>
#include <SPI.h>
#include <OneWire.h>
#include <DallasTemperature.h>
#include <Wire.h>
//sets up sleep mode
#include <avr/sleep.h>
#include <Sleep_n0m1.h>
#include <PinChangeInt.h>
#include <PinChangeIntConfig.h>
//library for ZS-042
#include "Sodaq_DS3231.h"

Sleep sleep;

#define rxPin 3 // 433mhz receive pin
#define txPin 4 // 433mhz send pin
#define ONE_WIRE_BUS 10 //one wire bus for DS18B20 thermometer
#define EchoPin 8 //Echo pin for HC-SR04
#define TriggerPin 9 //Trigger pin for HC-SR04
#define LightPin1 13 //LED to blink when data transmitted/received
#define retryTimes 5 //number of times to retry sending
#define voltReadPin A0 //pin for reading voltage from the battery

float Resistor1 = 100.0; //Resistor 1 value in KOhm
float Resistor2 = 47.0; //Resistor 2 value in KOhm
float voltage; //float to store the voltage value

OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature sensors(&oneWire);

String tempString = ""; //string value of the temperature
float tempLong; //float value of the temperature

int minutes = 0; //int value for the current minutes
int hours = 0; //int value for the current hours
unsigned int distance; //int value for the distance reading of the HC-SR04
const char *msg; //char value to store the sent message
String MessageReturn = "";//string value to store a message to send
String Message = "";//string value to store a message received

//Tank Dimensions
double Length = 1750; //input the Oil tank dimensions here
double Height = 1000; 

float pi = 3.14159; //calculations for tank capacity and fill level
double radius = Height/2;
double R2 = radius*radius;
double capacity = (((pi*R2)*Length)/1000000);

int retry = 0; //an int to store the current retry time count
float batteryVoltage; //float to store the battery voltage

void setup()
{
  //setup the Serial port
  Serial.begin(9600);       
  Serial.println(F("Ready"));
  //set up the pin modes
  pinMode(rxPin, OUTPUT);
  pinMode(TriggerPin, OUTPUT);
  pinMode(EchoPin, INPUT);
  pinMode(LightPin1, OUTPUT);
  pinMode(voltReadPin, INPUT);
  Serial.flush();
  //set up the pins for sending and receiving in virtualwire
  vw_set_tx_pin(txPin);    //set transmit pin as pin 3
  vw_set_rx_pin(rxPin);    //set receive pin as pin 4
  vw_set_ptt_inverted(true); // Required for DR3100
  vw_setup(2000);	 // baud rate for sending 433mhz
  vw_rx_start(); //start receiving

  //set up the real time clock and sleep interrupts
  PORTD |= 0x04;
  DDRD &= ~ 0x04;
  Wire.begin();
  rtc.begin();
  sensors.begin();
  rtc.enableInterrupts(EveryMinute); //interrupt at  EverySecond, EveryMinute, EveryHour
}

void loop()
{
  DateTime now = rtc.now(); //get the current date-time
  delay(1000);
  retry = 0;//set retry as 0
  while (retry < retryTimes)
  {
    OilStateQuery();//run the query to check the oil and send the fill level
    ReceiveInstruction(Message);//wait to receive a response
    if (Message.indexOf("ACK") > 0){ //if the response is not ACK ( > 0 as reply can also be NACK when data not received correctly)
      break; //exit the while loop
    }
    retry ++;//add another count to the retry times
  }
  //assuming that the data has been received or retry timeout move on
  retry = 0; //reset retry count
  Message = "";//reset message received
  delay(1000);//wait one second
  while (retry < retryTimes)
  {
    TempRead();//run the query to read the temperature and send the value
    ReceiveInstruction(Message);//wait to receive a response
    if (Message.indexOf("ACK") > 0) {//if the response is not ACK ( > 0 as reply can also be NACK when data not received correctly)
      break; //exit the while loop
    }
    retry ++; //add another count to the retry times
  }
  //assynubg that the data has been receuved or retry timeout move on
  retry = 0;//reset retry count
  Message = "";//reset message received
  delay(1000);//wait a second
  while (retry < retryTimes)
  {
    readBattery();//read the battery voltage level and send the value
    ReceiveInstruction(Message);//wait to receive a response
    if (Message.indexOf("ACK") > 0) {//if the response is not ACK ( > 0 as reply can also be NACK when data not received correctly)
      break;//exit the while loop
    }
    retry ++; //add another count to the retry times
  }
  
  Message = "";//reset the message received
  delay(1000);//wait a second
  setWakeTimer(now);//set the wake timer as the time set at the start of the loop
  delay(100);//wait
  goToSleep();//go to sleep for the hour set at the start of the loop
}

void ReceiveInstruction(String &data)
{
  uint8_t buf[VW_MAX_MESSAGE_LEN];//create a buffer value
  uint8_t buflen = VW_MAX_MESSAGE_LEN;//create a value of the size of the buffer
  if (vw_wait_rx_max(60000))//receive for 60 seconds
  {
    if (vw_get_message(buf, &buflen)) // if a message is received
    {
      data = "";//set the received string as blank
      //Serial.println(F("Receiving Instuction"));//left in for debugging
      digitalWrite(LightPin1, HIGH);//turn on the receive LED
      for (int i = 0; i < buflen; i++)
      {
        data += (char)buf[i]; //data value is the buffer of each char (removing char gives the uint8_t value)
        Serial.print(F("Instruction Received: "));
        Serial.println(data);
      }
      digitalWrite(LightPin1, LOW);// turns off the receive LED
    }
  }
}

void SendData(void)
{
  //Serial.println(MessageReturn);//left in for debugging
  msg = MessageReturn.c_str();//the message to send is converted from string to const char
  Serial.print("Sending data ");
  Serial.println(msg);
  delay(100);
  digitalWrite(LightPin1, HIGH);//turn on the Send LED
  vw_send((uint8_t *)msg, strlen(msg));//send the characters
  vw_wait_tx();//wait for transmission
  digitalWrite(LightPin1, LOW);//turn off the Send LED
  Serial.println("Data Sent");
  MessageReturn = "";//clear the string value
}

void TempRead(void)
{
  // call sensors.requestTemperatures() to issue a global temperature
  // request to all devices on the bus
  float tmp = 0;//create a value to hold the temperature
  float TempTmp = 0;//create another value to get the average temperature over a number of readings
  float samples[10];//number of samples in an array
  char buffer[8];//buffer to convert the float to a string 
  Serial.print(F("Temperature is: "));
  sensors.requestTemperatures(); // Send the command to get temperatures
  for (int i = 0; i <= 9; i++) { //for loop to get the average temperature reading
    samples[i] = sensors.getTempCByIndex(0);//set the sample value to that of the reading
    TempTmp = TempTmp + samples[i];//add the sample values together
  }
  tmp = TempTmp / 10.0;//divide by the number of samples to get the average
  if (tmp == -127 || (tmp > 127 && tmp < 128))//if theres an error in communications with the DS18B20
  {
    Serial.println(F("Error"));
  }
  if (tmp == 85)//another error handler
  {
    sensors.requestTemperatures();//retry without the average reading
    tmp = sensors.getTempCByIndex(0);
    if (tmp == 85)
    {
      Serial.println(F("Temperature is unavailable"));//if the error is the same
    }
  }
  if (tmp != 85)//if there is no error
  {
    //Serial.println(tmp);//left in for debug
    tempLong = ((int)(tmp * 100)) / 100.0;//calculates the value of temp to one decimal place
    //Serial.println(tempLong, 1);left in for debug
    tempString = dtostrf(tempLong, 4, 1, buffer);//convert it to a string
    Serial.print("Temp: ");//print the string
    Serial.println(tempString);
    MessageReturn = "T";//add a prefix to the message so the receiver knows what the value refers to
    MessageReturn += tempString;//adds the value to the string
    SendData();//sends the value
    MessageReturn = "";//clears the string
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
  MessageReturn = "OL";//add a prefix to the message so the receiver knows what the value refers to
  MessageReturn += String(Volume);//adds the value to the string
  Serial.println(MessageReturn);
  SendData();//send it
  MessageReturn = "";
}
double getVolume(double distance)
{
  double Level = Height-(distance*10);//get the level (distance to the oil)
  //formula to calculate a horizontal cylinders volume using measurements at the start of the sketch
  double Volume = ((Length*((R2*acos(1-2*(Level/Height)))-((radius-Level)*sqrt(Level*(Height-Level)))))/1000000);
  return Volume;
}
void goToSleep()
{
  Serial.println("Going to Sleep");
  delay(250);
  //rtc.enableInterrupts(EveryMinute);
  rtc.enableInterrupts(hours, minutes, 0);  // interrupt at (h,m,s)
  sleep.pwrDownMode();//enter power down mode
  sleep.sleepInterrupt(0, FALLING);//set to sleep and wake when the interrupt drops from High to Low (kept high by RTC)
  //device in sleep mode now waiting for RTC to wake on interrupt
  //
  //device in wake mode
  Serial.println("Waking Up");//
  delay(100);
}
void setWakeTimer(DateTime now)
{
  minutes = int(now.minute());//set the minute value as the now time read at the start of the loop
  hours = int(now.hour());//sets the hour value as the now time read at the start of the loop
  Serial.print("Time now: ");
  Serial.print(hours);
  Serial.print(":");
  Serial.println(minutes);
  minutes = minutes + 58;//add 58 to the minute value to wake 2 minutes early
  if (minutes >= 60)// if clock is more than 2 minutes calculate new time to wake
  {
    minutes = minutes - 60;
    hours = hours + 1;
  }
  if (hours >= 24)//make sure the wake time is an actual time
  {
    hours = 0;
  }
  Serial.print("Time to wakeup: ");
  Serial.print(hours);
  Serial.print(":");
  Serial.println(minutes);
  rtc.clearINTStatus();//clear the interrupt status
}
void readBattery()
{
  readVoltage();//read the voltage the device is running on from internal circutry
  float voltageRead = (analogRead(voltReadPin) * voltage) / 1024.0;//sets a float value to the reading of the pin multiplied by the running voltage
  Serial.println(voltageRead);
  batteryVoltage = voltageRead / (Resistor2/(Resistor1+Resistor2));//sets the battery voltage as the voltage read minus the voltage divider circuit (as battery is more than 5v it would destroy the chip)
  MessageReturn = "BV";//add a prefix to the message so the receiver knows what the value refers to
  MessageReturn += String(batteryVoltage);//add the value
  Serial.println(MessageReturn);
  SendData();//send it
  MessageReturn = "";//clear the string
}
long readVcc() {//function to read the internal voltage
  // Read 1.1V reference against AVcc
  // set the reference to Vcc and the measurement to the internal 1.1V reference
#if defined(__AVR_ATmega32U4__) || defined(__AVR_ATmega1280__) || defined(__AVR_ATmega2560__)
  ADMUX = _BV(REFS0) | _BV(MUX4) | _BV(MUX3) | _BV(MUX2) | _BV(MUX1);
#elif defined (__AVR_ATtiny24__) || defined(__AVR_ATtiny44__) || defined(__AVR_ATtiny84__)
  ADMUX = _BV(MUX5) | _BV(MUX0);
#elif defined (__AVR_ATtiny25__) || defined(__AVR_ATtiny45__) || defined(__AVR_ATtiny85__)
  ADMUX = _BV(MUX3) | _BV(MUX2);
#else
  ADMUX = _BV(REFS0) | _BV(MUX3) | _BV(MUX2) | _BV(MUX1);
#endif

  delay(2); // Wait for Vref to settle
  ADCSRA |= _BV(ADSC); // Start conversion
  while (bit_is_set(ADCSRA, ADSC)); // measuring
  uint8_t low  = ADCL; // must read ADCL first - it then locks ADCH
  uint8_t high = ADCH; // unlocks both
  long result = (high << 8) | low;
  result = 1125300L / result; // Calculate Vcc (in mV); 1125300 = 1.1*1023*1000
  return result; // Vcc in millivolts
}
void readVoltage()
{
  voltage = readVcc();//saves the value from the function
  double decimalVoltage = doubleMap(double(voltage), 0, 6000, 0, 6);//converts it to a mapped decimal value
  voltage = decimalVoltage;//resaves it as the new value
  Serial.print("voltage: ");
  Serial.print(voltage);
  Serial.print( " | ");
  Serial.println(decimalVoltage);
}
double doubleMap(double x, double in_min, double in_max, double out_min, double out_max)
{
  return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min;//return the calculated value
}
