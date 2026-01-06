void setup() {
  delay(2000);

  Serial.begin(19200);

  delay(500);

  // initialize printer
  Serial.write(0x1B);
  Serial.write('@');
  delay(100);

  Serial.println("HELLO WORLD");
  Serial.println("CSN-A2 PRINTER TEST");
  Serial.println("------------------");

  // Feed paper
  Serial.write(0x1B);
  Serial.write('d');
  Serial.write(3);

  Serial.flush();
}

void loop() {}
