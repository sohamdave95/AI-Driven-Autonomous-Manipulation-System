#include <Arduino.h>
#include <math.h>
#include <Servo.h>

Servo base;
Servo hip;
Servo knee;
Servo gripper; 

const double xAxisOffset = -3.5; // 10.3
const double zAxisOffset = -7.2; // -7.2, or -5.2
const double yAxisOffset = -2.5; // 0
const int baseServoOffset = 90;
const double hipLength = 12.3;
const double kneeLength = 12;
const int reachLimit = hipLength + kneeLength;
const int minLength = 4;
const double minReach = 4.0; 
double planarLength;
double totalLength;


double baseAngle;
double hipAngle;
double kneeAngle;
double elevationAngle;

double x;
double y;
double z;

void setup() {
  Serial.begin(115200);
  delay(1000);
  base.attach(23);
  hip.attach(22);
  knee.attach(21);
  gripper.attach(19);

}

double findAngle(double OppositeSide, double otherSideA, double otherSideB){
  return degrees(acos(((OppositeSide*OppositeSide) - (otherSideA*otherSideA) - (otherSideB*otherSideB))/(-2*otherSideA*otherSideB)));
}

void move(double x, double y, double z){
  x += xAxisOffset;
  y += yAxisOffset;
  z += zAxisOffset;

  planarLength = sqrt(x*x + y*y);
  totalLength = sqrt(planarLength*planarLength + z*z);
  
  if (totalLength <= reachLimit && totalLength >= minReach && planarLength >= minLength){
  elevationAngle = degrees(atan2(z , planarLength));
  baseAngle = constrain(degrees(atan2(y,x)) + baseServoOffset, 0, 180);
  hipAngle = constrain(findAngle(kneeLength, hipLength, totalLength) + elevationAngle, 0, 180);
  kneeAngle = constrain((180 - findAngle(totalLength, kneeLength, hipLength)), 0, 180);

  base.write(baseAngle); 
  hip.write(hipAngle); 
  knee.write(kneeAngle);
}
else{
    Serial.println("Target too far or close.");
    delay(1000);
  }
}

void close(){
  gripper.write(180);
}

void open(){
  gripper.write(0);
}

void home(){
  move(0, 10, 0);
}

void loop() {
  if (Serial.available() > 0){
    String msg = Serial.readStringUntil('\n');
    msg.trim(); 
    
    int c1 = msg.indexOf(',');
    int c2 = msg.indexOf(',', c1 + 1);
    int c3 = msg.indexOf(',', c2 + 1);

    if (c1 != -1 && c2 != -1 && c3 != -1) {
      double targetX = msg.substring(0, c1).toDouble();
      double targetY = msg.substring(c1 + 1, c2).toDouble();
      double targetZ = msg.substring(c2 + 1, c3).toDouble();
      String cmd = msg.substring(c3 + 1);
      cmd.trim(); 

      if (cmd == "open"){
        open();
      }
      else if (cmd == "close"){
        close();
      }
      else if (cmd == "home"){
        home();
      }
      else if (cmd == "move"){
        move(targetX, targetY, targetZ);
      }
    }
    else {
      if (msg == "open"){
      open();
      }
      else if (msg == "close"){
      close();
      }
      else if (msg == "home"){ 
      home();
      }
    }
  }
}

