#include <Servo.h>

Servo myservo;
int pos = 0;

void setup() {
  myservo.attach(9);
  Serial.begin(9600);
  Serial.println("Setup done");
}

void loop() {

  Serial.println("Rotating forward");

  for (pos = 0; pos <= 135; pos++) {
    myservo.write(pos);
    delay(1);
  }

  Serial.println("Rotating backward");
  delay(500);
  for (pos = 135; pos >= 0; pos--) {
    myservo.write(pos);
    delay(1);
  }

  delay(500);
}
