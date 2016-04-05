
#include <ESP8266WiFi.h>
#include <WiFiClient.h>
#include <ESP8266WebServer.h>
#include <SPI.h>

#define webEnable //enable over Web
#define tcpEnable //enable over TCP comment out if you have a preference.  Both will work at the start but once used will take priority

#define webserver 80
#define tcpserver 81
#define DEBUG //enable debug mode (serial out enabled on specific functions)
#define upstairsConfirmPin 12 //pin to confirm whether the valve is open or closed, once the arduino is finished it writes this as High
#define downstairsConfirmPin 13  //pin to confirm whether the valve is open or closed, once the arduino is finished it writes this as High
#define upstairsPin 16 //pin to send the instruction to open/close the upstairs valve to the arduino
#define downstairsPin 14 //pin to send the instruction to open/close the downstairs valve to the arduino
#define connectedLED 4 //LED to indicate whether connected to WiFi
#define connectedOutPin 15 //pin to signal to the arduino when the ESP is set up and connected to wifi.

const char* ssid     = "SSID";// Enter your Wifi name here
const char* password = "PASSWORD"; // Enter your Wifi Password Here
IPAddress ip(192, 168, 1, 242); //static IP address
IPAddress gateway(192, 168, 1, 1); //gateway
IPAddress subnet(255, 255, 0, 0);//subnet

boolean zones[2] = {false, false};
boolean alreadyConnected = false;
int status = WL_IDLE_STATUS;

const char* html = // this is the webpage served to the client

  "<!DOCTYPE html><html><head><meta http-equiv='X-UA-Compatible' content='IE=Edge'><meta charset='utf-8'><meta http-equiv='refresh' content='5'><title>Home Heating Zones</title>"
  "<script>function ResetWebpage(){if (window.location.href != 'http://#IPADDRESS/'){window.open ('http://#IPADDRESS/','_self',true)}};function setColor(buttonid, buttoncolor) {var property = document.getElementById(buttonid);if (count == 0) {property.style.backgroundColor = 'buttoncolor';}}</script>"
  "<style>#upon {height:200px; width:200px; font-size: 200%; text-align: center;color: #uponValue;background-color:grey;} #upoff {height:200px; width:200px; font-size: 200%; text-align: center;color: #upoffValue;background-color:grey;}#downon {height:200px; width:200px; font-size: 200%; text-align: center;color: #downonValue;background-color:grey;}#downoff {height:200px; width:200px; font-size: 200%; text-align: center;color: #downoffValue;background-color:grey;}</style>"
  "<body onload='ResetWebpage()'>"
  "<input type='button' id='upon' onclick=location.href='/upstairs1' value='Upstairs &#13;&#10; On' />"
  "<input type='button' id='upoff' onclick=location.href='/upstairs0' value='Upstairs &#13;&#10; Off' /></br>"
  "<input type='button' id='downon' onclick=location.href='/downstairs1' value='Downstairs &#13;&#10; On' />"
  "<input type='button' id='downoff' onclick=location.href='/downstairs0' value='Downstairs &#13;&#10; Off' />"
  "</body></html>";
ESP8266WebServer server(webserver);
WiFiServer server2(tcpserver);
long previousMillis = 0; // a long value to store the millis()
String IP; //IP address converted from type IPAddress to String to replace in HTML

void setup() 
{
  Serial.begin(9600); //starts up Serial
  Serial.print("\n\r \n\rWorking to connect");
  pinMode(upstairsPin, OUTPUT);
  pinMode(downstairsPin, OUTPUT);
  pinMode(upstairsConfirmPin, INPUT);
  pinMode(downstairsConfirmPin, INPUT);
  pinMode(connectedLED, OUTPUT);
  pinMode(connectedOutPin, OUTPUT);
  WiFi.begin(ssid, password);//begin connection to wifi access point/router
  WiFi.config(ip, gateway, subnet); //sets the connection to static
  while (WiFi.status() != WL_CONNECTED) // Wait for connection
  {
    digitalWrite(connectedLED, HIGH);//blink the LED while connecting
    delay(100);//sets a delay to wait for the access point to create the connection
    Serial.print(".");//adds a dot for each half second that the connection is not established
    digitalWrite(connectedLED, LOW);
    delay(100);
  }
  digitalWrite(connectedLED, HIGH);
  //outputs the connection details to Serial
  Serial.print("Connected to "); //sends serial information about the connection
  Serial.println(ssid);
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
  //confirms the IP address and saves it to a string to sub into the HTML
  IPAddress localIP = WiFi.localIP();
  IP = String(localIP[0]);
  IP += ".";
  IP += String(localIP[1]);
  IP += ".";
  IP += String(localIP[2]);
  IP += ".";
  IP += String(localIP[3]);

#if defined DEBUG
  Serial.print("IP as String: ");
  Serial.println(IP);
#endif

  server.on("/", handle_root); //when the page returned is "/" run the function 'handle_root()'
  server.on("/generate_204", handle_root);  //Android captive portal
  server.on("/upstairs0", handle_upstairsOff); //when the page requested is "upstairs0" run the function 'handle_upstairsOff'
  server.on("/upstairs1", handle_upstairsOn); //when the page requested is "upstairs1" run the function 'handle_upstairsOn'
  server.on("/downstairs0", handle_downstairsOff); //when the page requested is "downstairs0" run the function 'handle_downstairsOff'
  server.on("/downstairs1", handle_downstairsOn); //when the page requested is "downstairs1" run the function 'handle_downstairsOn'
  server.on("/status", handle_statusRequest); // when page "status" is requested run the function 'handle_statusRequest'

  server.onNotFound(handleNotFound); //when page not found
  server.begin();//begin the HTML server
  server2.begin();//begin the TCP server
  Serial.println("HTTP server started");
  delay(2000);
  zones[0] = digitalRead(upstairsConfirmPin);//read the confirm pin to find out if the valve is already open and save it to a boolean
  zones[1] = digitalRead(downstairsConfirmPin);//read the confirm pin to find out if the valve is already open and save it to a boolean
  digitalWrite(connectedOutPin, HIGH); //set the connected (and set up) pin high so the Arduino knows its good to go
  digitalWrite(upstairsPin, digitalRead(upstairsConfirmPin)); //write the pins to their current states
  digitalWrite(downstairsPin, digitalRead(downstairsConfirmPin)); //write the pins to their current states
  delay(2000);

}

void loop() {
  if (WiFi.status() != WL_CONNECTED) // if wifi is not connected at any point 
  {
    digitalWrite(connectedLED, LOW); // turn off the Wifi Connected LED
    digitalWrite(connectedOutPin, LOW); // turn off the connected pin (let the arduino know we're not ready to go)
    ESP.reset();//reset and start again
  }
  
#if defined webEnable
  server.handleClient(); //handle the webpage
#endif
  zones[0] = digitalRead(upstairsConfirmPin);//set the boolean to the pin status for the webpage/status request
  zones[1] = digitalRead(downstairsConfirmPin);//set the boolean to the pin status for the webpage/status request
#if defined tcpEnable
  WifiTCPClientCheck();//TCP listen loop
#endif
}

void handle_root() {

#if defined DEBUG //if debug has been uncommented at the start of the script display the readouts below
  Serial.print("Args: "); //the number arguments in the webpage address
  Serial.println(server.args());
  Serial.print("ArgName1: ");//the name of the argument in the address
  Serial.println(server.argName(0));
  Serial.print("Arg1: "); //argument1
  Serial.println(server.arg(0));
  Serial.print("Arg2: ");//argument2
  Serial.println(server.arg(1));
  Serial.print("uri: ");//the webpage address
  Serial.println(server.uri());
  Serial.println("method");//the method - Post/Get
  Serial.println(server.method());
#endif

#if defined DEBUG
  Serial.println("Page served");
#endif
  String toSend = html;

  toSend.replace("#IPADDRESS", IP); //replace the "#IPADDRESS" in the HTML above with the string IP
  toSend.replace("#uponValue", zones[0] ? "red" : "black"); //replace the style code "#uponValue" with either red or black to indicate which status
  toSend.replace("#downonValue", zones[1] ? "red" : "black"); //same as above etc.
  toSend.replace("#upoffValue", zones[0] ? "black" : "red");
  toSend.replace("#downoffValue", zones[1] ? "black" : "red");

  server.send(200, "text/html", toSend); //send the html code to the client
  delay(500);//wait half a second after sending the data
}

void handleNotFound()
{
  Serial.print("\t\t\t\t URI Not Found: ");
  Serial.println(server.uri());
  server.send ( 200, "text/plain", "URI Not Found" );//send not found message

}

void handle_downstairsOff() {
  digitalWrite(downstairsPin, LOW);//turn the pin to low, the arduino will read this and turn the stepper accordingly
  zones[1] = false;//set the boolean to false
  Serial.println("GotDownstairsOff");
  handle_root();//handle root again to send the html with changes
}

void handle_downstairsOn() {
  digitalWrite(downstairsPin, HIGH);//turn the pin to high, the arduino will read this and turn the stepper accordingly
  zones[1] = true;//sets the boolean to true
  Serial.println("GotDownstairsOn");
  handle_root();//handle root again to send the html with changes
}

void handle_upstairsOff() {
  digitalWrite(upstairsPin, LOW);
  zones[0] = false;
  Serial.println("GotUpstairsOff");
  handle_root();//handle root again to send the html with changes
}
void handle_upstairsOn() {
  digitalWrite(upstairsPin, HIGH);
  zones[0] = true;
  Serial.println("GotUpstairsOn");
  handle_root();//handle root again to send the html with changes
}
void handle_statusRequest() {
  WiFiClient client = server2.available();//open up a new client (for TCP messages) on server2
  if (client.available())
  {
    String reply = "upstairs=";
    reply += String(digitalRead(upstairsConfirmPin));
    reply += " downstairs=";
    reply += String(digitalRead(downstairsConfirmPin));
    client.print(reply);//send the reply e.g. "upstairs=true downstairs=false"
  }

}
void WifiTCPClientCheck()
{
  WiFiClient client = server2.available();//open up a client for TCP messages on server2

  if (client) { //if there is a client
    if (!alreadyConnected) { // and if they are not already connected
      client.flush();//clear the client
      alreadyConnected = true; //set the client as already connected
    }
    while (client.connected()) {//while connected and available
      while (client.available()) {
        String req = client.readStringUntil('\r');//read until end of line
        Serial.println(req);//print the string that was received
        // client.flush();
        int val;//set up an integer to read a value
        if (req.indexOf("status") != -1)//if "status" is in the message
        {
          String reply = "upstairs=";
          reply += String(digitalRead(upstairsConfirmPin));
          reply += " downstairs=";
          reply += String(digitalRead(downstairsConfirmPin));
          client.print(reply);//send the status e.g. "upstairs=true downstairs=false"
        }
        else if (req.indexOf("upstairs1") != -1)//else if upstairs1 is in the message
        {
          digitalWrite(upstairsPin, HIGH);//write the pin as high for the arduino to read
          client.print("confirmed");//reply back that the instruction has been carried out
        }
        else if (req.indexOf("upstairs0") != -1)//else if upstairs0 is in the message
        {
          digitalWrite(upstairsPin, LOW);//write the pin as low for the arduino to read
          client.print("confirmed");//reply back that the instruction has been carried out
        }
        else if (req.indexOf("downstairs1") != -1)//same as above
        {
          digitalWrite(downstairsPin, HIGH);
          client.print("confirmed");
        }
        else if (req.indexOf("downstairs0") != -1)
        {
          digitalWrite(downstairsPin, LOW);
          client.print("confirmed");
        }
        else if (req.indexOf("HELLO WORLD") != -1)//test string (left in for a laugh)
        {
          client.println("Hello Back");
        }
        else {
          Serial.println("invalid request");//else stop
          client.stop();
          return;
        }
      }
    }
    client.flush();//clear the client
    delay(10);
    client.stop();//stop the client
    delay(10);
    


  }
}
