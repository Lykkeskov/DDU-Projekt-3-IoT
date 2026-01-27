#include <Wire.h>
#include "rgb_lcd.h"

rgb_lcd lcd;

String message = "";
int scrollIndex = 0;
unsigned long lastScroll = 0;
const int scrollDelay = 300;  // ms

void setup() {
  lcd.begin(16, 2);
  lcd.setRGB(255, 255, 255);

  Serial.begin(9600);
  while (!Serial) {}

  // Static title (line 1)
  lcd.setCursor(0, 0);
  lcd.print("CO2e Forbrug");

  // Clear line 2
  lcd.setCursor(0, 1);
  lcd.print("                ");
}

void loop() {
  // Receive new message from Python
  if (Serial.available() > 0) {
    message = Serial.readStringUntil('\n');

    // Pad message for smooth scrolling
    message = "                " + message + "                ";
    scrollIndex = 0;
  }

  // Scroll text on line 2
  if (message.length() > 0) {
    if (millis() - lastScroll > scrollDelay) {
      lastScroll = millis();

      lcd.setCursor(0, 1);
      lcd.print(message.substring(scrollIndex, scrollIndex + 16));

      scrollIndex++;
      if (scrollIndex + 16 > message.length()) {
        scrollIndex = 0;
      }
    }
  }
}
