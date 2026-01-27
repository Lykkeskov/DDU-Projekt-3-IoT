#include <WiFi.h>
#include <WebServer.h>
#include <HardwareSerial.h>

// -------- ACCESS POINT SETTINGS --------
const char* ap_ssid = "ESP32-PRINTER";
const char* ap_password = "print1234";

// -------- PRINTER UART --------
HardwareSerial Printer(2);
#define PRINTER_RX 27
#define PRINTER_TX 25

// -------- WEB SERVER --------
WebServer server(80);

void handlePrint() {
  Serial.println("PRINT REQUEST RECEIVED");

  if (!server.hasArg("plain")) {
    Serial.println("No body!");
    server.send(400, "text/plain", "No data received");
    return;
  }

  String text = server.arg("plain");
  Serial.println("Text:");
  Serial.println(text);

  Printer.write(0x1B);
  Printer.write('@');
  Printer.println(text);

  Printer.write(0x1B);
  Printer.write('d');
  Printer.write(3);

  server.send(200, "text/plain", "Printed OK");
}


void setup() {
  Serial.begin(115200);

  // Start printer UART
  Printer.begin(19200, SERIAL_8N1, PRINTER_RX, PRINTER_TX);
  delay(1000);

  // Start Access Point
  WiFi.softAP(ap_ssid, ap_password);

  IPAddress IP = WiFi.softAPIP();
  Serial.print("ESP32 AP IP: ");
  Serial.println(IP);

  // Start server
  server.on("/print", HTTP_POST, handlePrint);
  server.begin();
  Serial.println("HTTP server started");
}

void loop() {
  server.handleClient();
}
