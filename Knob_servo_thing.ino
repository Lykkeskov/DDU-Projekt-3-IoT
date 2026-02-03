/*
 Controlling a servo position using a potentiometer (variable resistor)
 by Michal Rinott <http://people.interaction-ivrea.it/m.rinott>
 modified on 8 Nov 2013 by Scott Fitzgerald
 http://www.arduino.cc/en/Tutorial/Knob
*/

#include <Servo.h>

Servo myservo;      // create Servo object to control a servo
int potpin = A0;    // analog pin used to connect the potentiometer
int in;             // variable to read the value from the analog pin
int out;            // variable to store the mapped servo value

void setup() {
  myservo.attach(9);      // attaches the servo on pin 9 to the Servo object
  Serial.begin(115200);
}

void loop() {
  in = analogRead(potpin);          // reads the potentiometer (0–1023)
  out = map(in, 0, 710, 0, 180);    // map to servo range
  myservo.write(out);               // move servo

  Serial.print(in);
  Serial.print(",");
  Serial.println(out);

  delay(15); // waits for the servo to get there
}

