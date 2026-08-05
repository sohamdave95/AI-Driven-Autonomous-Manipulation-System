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
    
    if (totalLength <= reachLimit){

    elevationAngle = constrain(degrees(atan2(z , planarLength)), 0, 180);
    baseAngle = constrain(degrees(atan2(y,x)) + baseServoOffset, 0, 180);
    hipAngle = constrain(findAngle(kneeLength, hipLength, totalLength) + elevationAngle, 0, 180);
    kneeAngle = constrain(findAngle(totalLength, kneeLength, hipLength) + hipAngle, 0, 180);

    base.write(baseAngle);
    hip.write(hipAngle);
    knee.write(kneeAngle);

      Serial.println(baseAngle);
      Serial.println(hipAngle);
      Serial.println(kneeAngle);
      delay(1000);

    }
    else{
      Serial.println("Target too far.");
      delay(1000);
    }

}

void loop() {
  calculateIK(5, 5, 3);
}




