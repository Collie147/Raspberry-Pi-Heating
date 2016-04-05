#include <EEPROM.h>

const int upstairs[4] = {2, 3, 4, 5};//set the output pins for stepper1 - this controls the upstairs valve
const int downstairs[4] = {6, 7, 8, 9};//set the output pins for stepper2 - this controls the downstairs valve
int powerTransistorUpstairs = 10;//this controls the power transistor to allow voltage to the stepper controller
int powerTransistorDownstairs = 11;//this controls the power transistor to allow voltage to the stepper controller
int upstairsPin = 12;//this pin is set by the ESP8266, the arduino reads this and if high sets upstairs valve to open else closed
int downstairsPin = A0;//this pin is set by the ESP8266, the arduino reads this and if high sets downstairs valve to open else closed
int upstairsConfirmPin = A2;//when the stepper has completed its 90 degree cycle the pin is set High when open and Low when closed
int downstairsConfirmPin = A1;//when the stepper has completed its 90 degree cycle the pin is set High when open and Low when closed
int WifiEnabledPin = A3;//this pin is set by the ESP8266 when it's ready to send instructions, the arduino will only react to pin reads when this is High
int Steps = 130;//amount of steps in 90 degrees
const int speedN = 8;//speed to turn (lower is faster, is a delay value between step cycle sequence)
boolean UpOn;//boolean to set upstairs as on(true) or off(false)
boolean DownOn;//boolean to set downstairs as on(true) or off(false)
byte UpAddress = 0;//the eeprom address the upstairs value is saved to (in case of power failure)
byte DownAddress = 1;//the eeprom address the downstairs value is saved to (in case of power failure)


void setup() {
  //set the pins as i/o
  pinMode(upstairs[0], OUTPUT);
  pinMode(upstairs[1], OUTPUT);
  pinMode(upstairs[2], OUTPUT);
  pinMode(upstairs[3], OUTPUT);
  pinMode(downstairs[0], OUTPUT);
  pinMode(downstairs[1], OUTPUT);
  pinMode(downstairs[2], OUTPUT);
  pinMode(downstairs[3], OUTPUT);
  pinMode(powerTransistorUpstairs, OUTPUT);
  pinMode(powerTransistorDownstairs, OUTPUT);
  pinMode (upstairsPin, INPUT);
  pinMode (downstairsPin, INPUT);
  pinMode (upstairsConfirmPin, OUTPUT);
  pinMode (downstairsConfirmPin, OUTPUT);
  Serial.begin(9600);
  Serial.println("start");

  //flash the upstairs/downstairs confirm pins (also connected to LEDs - will flash during boot to indicate startup)
  for (int x = 0; x < 6; x++)
  {
  digitalWrite(upstairsConfirmPin, HIGH);
  digitalWrite(downstairsConfirmPin, LOW);
  delay(100);
  digitalWrite(upstairsConfirmPin, LOW);
  digitalWrite(downstairsConfirmPin, HIGH);
  delay(100);
  }
  
  digitalWrite(upstairsConfirmPin, LOW);
  digitalWrite(downstairsConfirmPin, LOW);

  UpOn = EEPROM.read(UpAddress);//set the boolean to the state saved in the eeprom
  DownOn = EEPROM.read(DownAddress);//set the boolean to the state saved in the eeprom
  Serial.print("EEprom Up = ");
  Serial.print(EEPROM.read(UpAddress));
  Serial.print(" . UpOn = ");
  Serial.print(UpOn);
  Serial.print(" . Up Pin = ");
  Serial.println(digitalRead(upstairsPin));
  Serial.print("EEprom Down = ");
  Serial.print(EEPROM.read(DownAddress));
  Serial.print(" . DownOn = ");
  Serial.print(DownOn);
  Serial.print(" . Down Pin = ");
  Serial.println(digitalRead(downstairsPin));
  //write the confirm pins to the boolean values
  digitalWrite(upstairsConfirmPin, UpOn);
  digitalWrite(downstairsConfirmPin, DownOn);
  delay(6000);//wait 6 seconds for the esp8266 to receive the info and continue setup
}

void loop()
{
  if (digitalRead(WifiEnabledPin))//if the ESP is set up and ready
  {
  if ((digitalRead (upstairsPin) == HIGH) && (UpOn == false))//if the pin is signalling to open the valve and the valve is closed
    {
      ZoneStepper("Upstairs", true);//run the stepper function with the zone and value to set
      UpOn = true;//set the boolean
      digitalWrite(upstairsConfirmPin, HIGH);//send the confirm pin signal
      EEPROM.write(UpAddress, UpOn);//save the value to the eeprom
    }
    if ((digitalRead (upstairsPin) == LOW) && (UpOn == true))//if the pin is signalling to close the valve and the valve is open
    {
      ZoneStepper("Upstairs", false);//run the stepper function with the zone and value to set
      UpOn = false;//set the boolean
      digitalWrite(upstairsConfirmPin, LOW);//send the confirm pin signal
      EEPROM.write(UpAddress, UpOn);//save the value to the eeprom
    }
    if ((digitalRead (downstairsPin) == HIGH) && (DownOn == false))
    {
      ZoneStepper("Downstairs", true);
      DownOn = true;
      digitalWrite(downstairsConfirmPin, HIGH);
      EEPROM.write(DownAddress, DownOn);
    }
    if ((digitalRead (downstairsPin) == LOW) && (DownOn == true))
    {
      ZoneStepper("Downstairs", false);
      DownOn = false;
      digitalWrite(downstairsConfirmPin, LOW);
      EEPROM.write(DownAddress, DownOn);
    }
    Serial.print("UpstairsPin=");
    Serial.println(digitalRead(upstairsPin));
    Serial.print("DownstairsPin=");
    Serial.println(digitalRead(downstairsPin));
    delay(500);
  }
  else // if the ESP is not set up and ready
  {
    Serial.println("Wifi Module error");//print an error
    delay(500);//wait half a second and start again
  }
}
void ZoneStepper(String zone, boolean onOff)//zone stepper function - sets the string received as the zone to change and the boolean value as open or closed
{
  unsigned int stepN;//sets an int for the number of steps
  if (zone == "Upstairs")//if the zone is upstairs
  {
    if (onOff == true)//and the signal is set to open the valve
    {
      stepN = Steps;//sets the steps as the value set at startup
      Serial.println("clockwise Upstairs");
      Step_OFF_Upstairs();//runs the Step_OFF_Upstairs function (sets all the pins as LOW)
      while (stepN > 0) {//while there are still steps left to turn
        digitalWrite(powerTransistorUpstairs, HIGH);//give the stepper driver power
        if (stepN > 130)
        {
          digitalWrite(upstairsConfirmPin, LOW);//flash the confirm pin & LED to indicate motion
        }
        if ((stepN <= 120) && (stepN > 110))
        {
          digitalWrite(upstairsConfirmPin, HIGH);
        }
        if ((stepN <= 110) && (stepN > 100))
        {
          digitalWrite(upstairsConfirmPin, LOW);
        }
        if ((stepN <= 100) && (stepN > 90))
        {
          digitalWrite(upstairsConfirmPin, HIGH);
        }
        if ((stepN <= 90) && (stepN > 80))
        {
          digitalWrite(upstairsConfirmPin, LOW);
        }
        if ((stepN <= 80) && (stepN > 70))
        {
          digitalWrite(upstairsConfirmPin, HIGH);
        }
        if ((stepN <= 70) && (stepN > 60))
        {
          digitalWrite(upstairsConfirmPin, LOW);
        }
        if ((stepN <= 60) && (stepN > 50))
        {
          digitalWrite(upstairsConfirmPin, HIGH);
        }
        if ((stepN <= 50) && (stepN > 40))
        {
          digitalWrite(upstairsConfirmPin, LOW);
        }
        if ((stepN <= 40) && (stepN > 30))
        {
          digitalWrite(upstairsConfirmPin, HIGH);
        }
        if ((stepN <= 30) && (stepN > 20))
        {
          digitalWrite(upstairsConfirmPin, LOW);
        }
        if ((stepN <= 20) && (stepN > 10))
        {
          digitalWrite(upstairsConfirmPin, HIGH);
        }
        if (stepN <= 10)
        {
          digitalWrite(upstairsConfirmPin, LOW);
        }
        forward_Upstairs();//turns the stepper forward using the output pins
        stepN --;//reduce the steps by 1 each time
      }
      digitalWrite(powerTransistorUpstairs, LOW);//when finsihed turn off the power to the stepper controller
    }
    if (onOff == false)//if the signal is set to the closed value (all steps are same as above)
    {
      stepN = Steps;
      Serial.println("counterclockwiseUpstairs");
      Step_OFF_Upstairs();
      while (stepN > 0) {
        digitalWrite(powerTransistorUpstairs, HIGH);
        if (stepN > 130)
        {
          digitalWrite(upstairsConfirmPin, LOW);
        }
        if ((stepN <= 120) && (stepN > 110))
        {
          digitalWrite(upstairsConfirmPin, HIGH);
        }
        if ((stepN <= 110) && (stepN > 100))
        {
          digitalWrite(upstairsConfirmPin, LOW);
        }
        if ((stepN <= 100) && (stepN > 90))
        {
          digitalWrite(upstairsConfirmPin, HIGH);
        }
        if ((stepN <= 90) && (stepN > 80))
        {
          digitalWrite(upstairsConfirmPin, LOW);
        }
        if ((stepN <= 80) && (stepN > 70))
        {
          digitalWrite(upstairsConfirmPin, HIGH);
        }
        if ((stepN <= 70) && (stepN > 60))
        {
          digitalWrite(upstairsConfirmPin, LOW);
        }
        if ((stepN <= 60) && (stepN > 50))
        {
          digitalWrite(upstairsConfirmPin, HIGH);
        }
        if ((stepN <= 50) && (stepN > 40))
        {
          digitalWrite(upstairsConfirmPin, LOW);
        }
        if ((stepN <= 40) && (stepN > 30))
        {
          digitalWrite(upstairsConfirmPin, HIGH);
        }
        if ((stepN <= 30) && (stepN > 20))
        {
          digitalWrite(upstairsConfirmPin, LOW);
        }
        if ((stepN <= 20) && (stepN > 10))
        {
          digitalWrite(upstairsConfirmPin, HIGH);
        }
        if (stepN <= 10)
        {
          digitalWrite(upstairsConfirmPin, LOW);
        }
        backward_Upstairs();
        stepN --;
      }
      digitalWrite(powerTransistorUpstairs, LOW);
    }
  }
  if (zone == "Downstairs")
  {
    if (onOff == true)
    {
      stepN = Steps;
      Serial.println("clockwise Downstairs");
      Step_OFF_Downstairs();
      while (stepN > 0) {
        digitalWrite(powerTransistorDownstairs, HIGH);
        if (stepN > 130)
        {
          digitalWrite(downstairsConfirmPin, LOW);
        }
        if ((stepN <= 120) && (stepN > 110))
        {
          digitalWrite(downstairsConfirmPin, HIGH);
        }
        if ((stepN <= 110) && (stepN > 100))
        {
          digitalWrite(downstairsConfirmPin, LOW);
        }
        if ((stepN <= 100) && (stepN > 90))
        {
          digitalWrite(downstairsConfirmPin, HIGH);
        }
        if ((stepN <= 90) && (stepN > 80))
        {
          digitalWrite(downstairsConfirmPin, LOW);
        }
        if ((stepN <= 80) && (stepN > 70))
        {
          digitalWrite(downstairsConfirmPin, HIGH);
        }
        if ((stepN <= 70) && (stepN > 60))
        {
          digitalWrite(downstairsConfirmPin, LOW);
        }
        if ((stepN <= 60) && (stepN > 50))
        {
          digitalWrite(downstairsConfirmPin, HIGH);
        }
        if ((stepN <= 50) && (stepN > 40))
        {
          digitalWrite(downstairsConfirmPin, LOW);
        }
        if ((stepN <= 40) && (stepN > 30))
        {
          digitalWrite(downstairsConfirmPin, HIGH);
        }
        if ((stepN <= 30) && (stepN > 20))
        {
          digitalWrite(downstairsConfirmPin, LOW);
        }
        if ((stepN <= 20) && (stepN > 10))
        {
          digitalWrite(downstairsConfirmPin, HIGH);
        }
        if (stepN <= 10)
        {
          digitalWrite(downstairsConfirmPin, LOW);
        }
        forward_Downstairs();
        stepN --;
      }
      digitalWrite(powerTransistorDownstairs, LOW);
    }
    if (onOff == false)
    {
      stepN = Steps;
      Serial.println("counterclockwise Downstairs");
      Step_OFF_Downstairs();
      while (stepN > 0) {
        digitalWrite(powerTransistorDownstairs, HIGH);
        if (stepN > 130)
        {
          digitalWrite(downstairsConfirmPin, LOW);
        }
        if ((stepN <= 120) && (stepN > 110))
        {
          digitalWrite(downstairsConfirmPin, HIGH);
        }
        if ((stepN <= 110) && (stepN > 100))
        {
          digitalWrite(downstairsConfirmPin, LOW);
        }
        if ((stepN <= 100) && (stepN > 90))
        {
          digitalWrite(downstairsConfirmPin, HIGH);
        }
        if ((stepN <= 90) && (stepN > 80))
        {
          digitalWrite(downstairsConfirmPin, LOW);
        }
        if ((stepN <= 80) && (stepN > 70))
        {
          digitalWrite(downstairsConfirmPin, HIGH);
        }
        if ((stepN <= 70) && (stepN > 60))
        {
          digitalWrite(downstairsConfirmPin, LOW);
        }
        if ((stepN <= 60) && (stepN > 50))
        {
          digitalWrite(downstairsConfirmPin, HIGH);
        }
        if ((stepN <= 50) && (stepN > 40))
        {
          digitalWrite(downstairsConfirmPin, LOW);
        }
        if ((stepN <= 40) && (stepN > 30))
        {
          digitalWrite(downstairsConfirmPin, HIGH);
        }
        if ((stepN <= 30) && (stepN > 20))
        {
          digitalWrite(downstairsConfirmPin, LOW);
        }
        if ((stepN <= 20) && (stepN > 10))
        {
          digitalWrite(downstairsConfirmPin, HIGH);
        }
        if (stepN <= 10)
        {
          digitalWrite(downstairsConfirmPin, LOW);
        }
        backward_Downstairs();
        stepN --;
      }
      digitalWrite(powerTransistorDownstairs, LOW);
    }
  }





}
//Upstairs
void Step_A_Upstairs() {//this is the first in the sequence of steps - pull the first pin high to pull the motor toward that pole
  digitalWrite(upstairs[0], HIGH);
  digitalWrite(upstairs[1], LOW);
  digitalWrite(upstairs[2], LOW);
  digitalWrite(upstairs[3], LOW);
}
void Step_B_Upstairs() {//this is the second in the sequence of steps - pull the second pin high to pull the motor toward that pole
  digitalWrite(upstairs[0], LOW);
  digitalWrite(upstairs[1], HIGH);
  digitalWrite(upstairs[2], LOW);
  digitalWrite(upstairs[3], LOW);
}
void Step_C_Upstairs() {//this is the third in the sequence of steps - pull the third pin high to pull the motor toward that pole
  digitalWrite(upstairs[0], LOW);
  digitalWrite(upstairs[1], LOW);
  digitalWrite(upstairs[2], HIGH);
  digitalWrite(upstairs[3], LOW);
}
void Step_D_Upstairs() {//this is the fourth in the sequence of steps - pull the fourth pin high to pull the motor toward that pole
  digitalWrite(upstairs[0], LOW);
  digitalWrite(upstairs[1], LOW);
  digitalWrite(upstairs[2], LOW);
  digitalWrite(upstairs[3], HIGH);
}
void Step_OFF_Upstairs() {//this is the last after the sequence has finished - set all pins to low
  digitalWrite(upstairs[0], LOW);
  digitalWrite(upstairs[1], LOW);
  digitalWrite(upstairs[21], LOW);
  digitalWrite(upstairs[3], LOW);
}
void forward_Upstairs() {//run the sequence and delay by the speed set above in speedN
  Step_A_Upstairs();
  delay(speedN);
  Step_B_Upstairs();
  delay(speedN);
  Step_C_Upstairs();
  delay(speedN);
  Step_D_Upstairs();
  delay(speedN);
}
void backward_Upstairs() {
  Step_D_Upstairs();
  delay(speedN);
  Step_C_Upstairs();
  delay(speedN);
  Step_B_Upstairs();
  delay(speedN);
  Step_A_Upstairs();
  delay(speedN);
}
//Downstairs
void Step_A_Downstairs() {
  digitalWrite(downstairs[0], HIGH);
  digitalWrite(downstairs[1], LOW);
  digitalWrite(downstairs[2], LOW);
  digitalWrite(downstairs[3], LOW);
}
void Step_B_Downstairs() {
  digitalWrite(downstairs[0], LOW);
  digitalWrite(downstairs[1], HIGH);
  digitalWrite(downstairs[2], LOW);
  digitalWrite(downstairs[3], LOW);
}
void Step_C_Downstairs() {
  digitalWrite(downstairs[0], LOW);
  digitalWrite(downstairs[1], LOW);
  digitalWrite(downstairs[2], HIGH);
  digitalWrite(downstairs[3], LOW);
}
void Step_D_Downstairs() {
  digitalWrite(downstairs[0], LOW);
  digitalWrite(downstairs[1], LOW);
  digitalWrite(downstairs[2], LOW);
  digitalWrite(downstairs[3], HIGH);
}
void Step_OFF_Downstairs() {
  digitalWrite(downstairs[0], LOW);
  digitalWrite(downstairs[1], LOW);
  digitalWrite(downstairs[2], LOW);
  digitalWrite(downstairs[3], LOW);
}
void forward_Downstairs() {
  Step_A_Downstairs();
  delay(speedN);
  Step_B_Downstairs();
  delay(speedN);
  Step_C_Downstairs();
  delay(speedN);
  Step_D_Downstairs();
  delay(speedN);
}
void backward_Downstairs() {
  Step_D_Downstairs();
  delay(speedN);
  Step_C_Downstairs();
  delay(speedN);
  Step_B_Downstairs();
  delay(speedN);
  Step_A_Downstairs();
  delay(speedN);
}

