#include <Arduino.h>
#include <math.h>
#include <Servo.h>

Servo base;
Servo hip;
Servo knee; 

const double xAxisOffset = 10.3; // 10.3
const double zAxisOffset = -7.2;
const double yAxisOffset = 0; // 0
const int baseServoOffset = 90;
const double hipLength = 12.3;
const double kneeLength = 12;
const int reachLimit = hipLength + kneeLength;
const int minLength = 8;
double planarLength;
double totalLength;

double baseAngle;
double hipAngle;
double kneeAngle;
double elevationAngle;

void setup() {
  Serial.begin(115200);
  delay(1000);
  base.attach(23);
  hip.attach(22);
  knee.attach(21);

}

double findAngle(double OppositeSide, double otherSideA, double otherSideB){
  return constrain(degrees(acos(((OppositeSide*OppositeSide) - (otherSideA*otherSideA) - (otherSideB*otherSideB))/(-2*otherSideA*otherSideB))), 0, 180);
}

void calculateIK(double x, double y, double z){
  x += xAxisOffset;
  y += yAxisOffset;
  z += zAxisOffset;

  planarLength = sqrt(x*x + y*y);
  totalLength = sqrt(planarLength*planarLength + z*z);
  
  if (totalLength <= reachLimit && planarLength >= minLength){
  elevationAngle = degrees(atan2(z , planarLength));
  baseAngle = constrain(degrees(atan2(y,x)) + baseServoOffset, 0, 180);
  hipAngle = constrain(findAngle(kneeLength, hipLength, totalLength) + elevationAngle, 0, 180);
  kneeAngle = constrain((180 - findAngle(totalLength, kneeLength, hipLength)), 0, 180);
  /* explain Knee Angle:
    180 - findAngle gets you the external angle of the joint (how much servo must rotate)
    that has to be added from the straight line of the arm, so from 90 deg which is the angle when the arm is straight
  */

  base.write(baseAngle);
  hip.write(hipAngle);
  knee.write(kneeAngle);

  Serial.println(elevationAngle);
  Serial.println(baseAngle);
  Serial.println(hipAngle);
  Serial.println(kneeAngle);
  delay(1000);

}
else{
    Serial.println("Target too far or close.");
    delay(1000);
  }
}

void loop() {
  calculateIK(10, 5, 0);
}



