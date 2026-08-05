#include <Arduino.h>
#include <Servo.h>
#include <math.h>


Servo base;
Servo hip;
Servo knee;
Servo grabber;

const int lengthOffset = 3;
const double hl = 12;
const double kl = 12.3;
double tl;

double bsa;
double hsa;
double ksa;




void returnBaseAngle(double x, double y){
  bsa = atan2(y,x);
  bsa = degrees(bsa) - 90;
}

void returnTotalLength(double x, double y){
  tl = sqrt(x*x + y*y);
}

void returnHipServoAngle(double x, double y){
  if (tl < (hl + kl + lengthOffset)){
    hsa = acos((kl*kl - hl*hl - tl*tl)/(-2*kl*hl));
    hsa = degrees(hsa) - 90;
  }
}

void returnKneeServoAngle(double x, double y){
  if (tl < (hl + kl + lengthOffset)){
    ksa = acos((tl*tl - hl*hl - kl*kl)/(-2*tl*hl));
    ksa = degrees(ksa) - 90;
  }
}


void computeIK(double x, double y) {
  returnBaseAngle(x, y);
  returnTotalLength(x, y);
  returnHipServoAngle(x, y);
  returnKneeServoAngle(x, y);

  base.write((int)bsa);
  hip.write((int)hsa);
  knee.write((int)ksa);
}

void setup() {
  // put your setup code here, to run once:
  base.attach(23);
  hip.attach(22);
  knee.attach(21);
  grabber.attach(19);
  
  //base.write(90);
  //hip.write(90);
  //knee.write(90);
  //grabber.write(90);

  computeIK(10, 0);
}

void loop(){

}