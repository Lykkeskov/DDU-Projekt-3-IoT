#include <WiFi.h>
#include <WebServer.h>
#include <HardwareSerial.h>
#include <Wire.h>
#include "rgb_lcd.h"
#include <ESP32Servo.h>

// ===== WPA2 Enterprise =====
#include "esp_wifi.h"
#include "esp_eap_client.h"

// ===== PRINTER =====
HardwareSerial Printer(2);
#define PRINTER_RX 27
#define PRINTER_TX 25

// ===== LCD =====
rgb_lcd lcd;
#define LCD_SDA 21
#define LCD_SCL 22

// ===== SERVO =====
Servo piston;
#define SERVO_PIN 2
#define SERVO_EXTENDED 180
#define SERVO_RETRACTED 0

// ===== BUTTON + RELAY =====
#define BUTTON_PIN 26
#define RELAY_PIN 18

// ===== STATE =====
bool pistonIsExtended = true;   // <-- assume piston starts extended
bool lastButton = HIGH;

// ===== LIGHTER TIMING =====
bool lighterArmed = false;
bool lighterOn = false;
unsigned long lighterDelayStart = 0;
unsigned long lighterOnStart = 0;

const unsigned long LIGHTER_DELAY = 10000; // wait 10s after extend
const unsigned long LIGHTER_TIME  = 10000; // lighter on 10s

// ===== WIFI =====
const char* ssid = "eduroam";
const char* identity = "INDSÆT SKOLE EMAIL";
const char* password = "INDSÆT SKOLE EMAIL PASSWORD";

// ===== SERVER =====
WebServer server(80);

// ===== LCD SCROLL =====
String lcdMessage = "";
int scrollIndex = 0;
unsigned long lastScroll = 0;
const int scrollDelay = 300;

// ===== HTTP PRINT =====
void handlePrint() {
  if (!server.hasArg("plain")) {
    server.send(400, "text/plain", "No data");
    return;
  }

  Printer.write(0x1B); Printer.write('@');
  Printer.println(server.arg("plain"));
  Printer.write(0x1B); Printer.write('d'); Printer.write(3);

  if (server.hasArg("co2")) {
    lcdMessage = "                " + server.arg("co2") + "                ";
    scrollIndex = 0;
  }

  server.send(200, "text/plain", "OK");
}

void setup() {
  Serial.begin(115200);

  // ===== IO =====
  pinMode(BUTTON_PIN, INPUT_PULLUP);
  pinMode(RELAY_PIN, OUTPUT);
  digitalWrite(RELAY_PIN, LOW);

  // ===== SERVO =====
 // piston.setPeriodHertz(50);
 // piston.attach(SERVO_PIN, 500, 2400);
  piston.attach(SERVO_PIN);
  piston.write(SERVO_EXTENDED); // assume starting extended

  // ===== PRINTER =====
  Printer.begin(19200, SERIAL_8N1, PRINTER_RX, PRINTER_TX);

  // ===== LCD =====
  Wire.begin(LCD_SDA, LCD_SCL);
  lcd.begin(16, 2);
  lcd.setRGB(255, 255, 255);
  lcd.setCursor(0,0);
  lcd.print("CO2e Forbrug");
  lcd.setCursor(0,1);
  lcd.print("Starter...");

  // ===== WIFI =====
  WiFi.disconnect(true);
  WiFi.mode(WIFI_STA);

  esp_wifi_sta_enterprise_enable();
  esp_eap_client_set_identity((uint8_t*)identity, strlen(identity));
  esp_eap_client_set_username((uint8_t*)identity, strlen(identity));
  esp_eap_client_set_password((uint8_t*)password, strlen(password));

  WiFi.begin(ssid);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\nWiFi connected");
  Serial.println(WiFi.localIP());

  lcd.setCursor(0,1);
  lcd.print("WiFi OK        ");

  // ===== SERVER =====
  server.on("/print", HTTP_POST, handlePrint);
  server.begin();
}

void loop() {
  server.handleClient();

  // ===== BUTTON EDGE =====
  bool current = digitalRead(BUTTON_PIN);

  if (lastButton == HIGH && current == LOW) {
    delay(20);
    Serial.println("Button pressed");

    if (pistonIsExtended) {
      // RETRACT
      piston.write(SERVO_RETRACTED);
      pistonIsExtended = false;
          Serial.println("piston is extended, retracting");

    } else {
      // EXTEND + ARM LIGHTER
      piston.write(SERVO_EXTENDED);
      pistonIsExtended = true;
      lighterArmed = true;
      lighterDelayStart = millis();
          Serial.println("Lighter ON");
          Serial.println("piston is retracted, extending");
  
    }
  }
  lastButton = current;

  // ===== LIGHTER LOGIC =====
  if (lighterArmed && !lighterOn && millis() - lighterDelayStart >= LIGHTER_DELAY) {
    digitalWrite(RELAY_PIN, HIGH);
    lighterOn = true;
    lighterOnStart = millis();
    Serial.println("Lighter ON");
  }

  if (lighterOn && millis() - lighterOnStart >= LIGHTER_TIME) {
    digitalWrite(RELAY_PIN, LOW);
    lighterOn = false;
    lighterArmed = false;
    Serial.println("Lighter OFF");
  }

  // ===== LCD SCROLL =====
  if (lcdMessage.length() > 0 && millis() - lastScroll > scrollDelay) {
    lastScroll = millis();
    lcd.setCursor(0,1);
    lcd.print(lcdMessage.substring(scrollIndex, scrollIndex + 16));
    scrollIndex++;
    if (scrollIndex + 16 > lcdMessage.length()) scrollIndex = 0;
  }
}
