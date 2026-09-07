#include <Arduino.h>
#include <math.h>
#include <Servo.h>

Servo base;
Servo hip;
Servo knee;
Servo gripper; 

const double xAxisOffset = -3.5; // 10.3
const double zAxisOffset = -6.2; // -7.2, or -5.2
const double yAxisOffset = 0; // 0
const int baseServoOffset = 90;
const double hipLength = 12.3;
const double kneeLength = 12;
const int reachLimit = hipLength + kneeLength;
const int minLength = 4;
const double minReach = 4.0; 
double planarLength;
double totalLength;
const double grabHeightOffset = 3;

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
  //return constrain(degrees(acos(((OppositeSide*OppositeSide) - (otherSideA*otherSideA) - (otherSideB*otherSideB))/(-2*otherSideA*otherSideB))), 0, 180);
}

void calculateIK(double x, double y, double z){
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

void closeGripper(){
  gripper.write(180);
}

void openGripper(){
  gripper.write(0);
}

void pickUp(double x, double y, double z){
  calculateIK(x, y, z + grabHeightOffset);
  delay(1000);
  openGripper();
  delay(1000);
  calculateIK(x, y, z);
  delay(1000);
  closeGripper();
  delay(1000);


}


void loop() {
  
  pickUp(12.2, -2.2, 0);
  calculateIK(4, 7, 3);
  delay(5000);
  openGripper();
  
}

