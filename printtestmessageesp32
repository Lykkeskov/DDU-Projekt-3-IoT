#include <HardwareSerial.h>

// Sådan forbinder man printeren:
// GND -> GND
// Printer RX -> IO25
// Printer TX -> IO27
// Strøm sættes i stikkontakten indtil videre

HardwareSerial Printer(2);

void setup() {
  delay(2000);

  Printer.begin(19200, SERIAL_8N1, 27, 25); // RX, TX

  Printer.write(0x1B);
  Printer.write('@');

  Printer.println("HELLO FROM ESP32");
  Printer.println("THERMAL PRINTER OK");

  Printer.write(0x1B);
  Printer.write('d');
  Printer.write(3);
}

void loop() {}
