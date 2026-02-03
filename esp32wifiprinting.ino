#include <WiFi.h>
#include <WebServer.h>
#include <HardwareSerial.h>
#include <Wire.h>
#include "rgb_lcd.h"

// ===== ESP-IDF WPA2-Enterprise (NEW API) =====
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

// ===== WIFI (eduroam) =====
const char* ssid = "eduroam";
const char* identity = "INDSÆT SKOLE EMAIL";  // your school login
const char* password = "INDSÆT KODE TIL SKOLE EMAIL";

// ===== HTTP SERVER =====
WebServer server(80);

// ===== LCD SCROLL =====
String lcdMessage = "";
int scrollIndex = 0;
unsigned long lastScroll = 0;
const int scrollDelay = 300;

// ===== HTTP HANDLER =====
void handlePrint() {
  if (!server.hasArg("plain")) {
    server.send(400, "text/plain", "No data received");
    return;
  }

  String text = server.arg("plain");

  // --- Print to thermal printer ---
  Printer.write(0x1B); Printer.write('@');      // init
  Printer.println(text);
  Printer.write(0x1B); Printer.write('d'); Printer.write(3);

  // --- LCD CO2 text ---
  if (server.hasArg("co2")) {
    lcdMessage = server.arg("co2");
    lcdMessage = "                " + lcdMessage + "                ";
    scrollIndex = 0;
  }

  server.send(200, "text/plain", "Printed OK");
}

void setup() {
  Serial.begin(115200);
  delay(1000);

  // ===== PRINTER UART =====
  Printer.begin(19200, SERIAL_8N1, PRINTER_RX, PRINTER_TX);

  // ===== LCD INIT =====
  Wire.begin(LCD_SDA, LCD_SCL);
  lcd.begin(16, 2);
  lcd.setRGB(255, 255, 255);
  lcd.setCursor(0, 0);
  lcd.print("CO2e Forbrug");
  lcd.setCursor(0, 1);
  lcd.print("Starter...");

  // ===== WIFI WPA2-ENTERPRISE =====
  WiFi.disconnect(true);
  WiFi.mode(WIFI_STA);

  esp_wifi_sta_enterprise_enable();
  esp_eap_client_set_identity((uint8_t*)identity, strlen(identity));
  esp_eap_client_set_username((uint8_t*)identity, strlen(identity));
  esp_eap_client_set_password((uint8_t*)password, strlen(password));

  WiFi.begin(ssid);

  Serial.print("Connecting to eduroam");
  lcd.setCursor(0, 1);
  lcd.print("WiFi...");

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\nConnected!");
  Serial.print("IP: ");
  Serial.println(WiFi.localIP());

  lcd.setCursor(0, 1);
  lcd.print("IP OK        ");

  // ===== HTTP =====
  server.on("/print", HTTP_POST, handlePrint);
  server.begin();

  Serial.println("HTTP server started");
}

void loop() {
  server.handleClient();

  // ===== LCD SCROLL =====
  if (lcdMessage.length() > 0 && millis() - lastScroll > scrollDelay) {
    lastScroll = millis();
    lcd.setCursor(0, 1);
    lcd.print(lcdMessage.substring(scrollIndex, scrollIndex + 16));
    scrollIndex++;
    if (scrollIndex + 16 > lcdMessage.length()) scrollIndex = 0;
  }
}
