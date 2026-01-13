#define BUTTON_PIN 21
#define FIRE_PIN 18

void setup() {
  Serial.begin(115200);
  pinMode(BUTTON_PIN, INPUT_PULLUP);
  pinMode(FIRE_PIN, OUTPUT);
}

void loop() {
  bool state = digitalRead(BUTTON_PIN);
  Serial.println(state);
  digitalWrite(FIRE_PIN,!state);
  delay(20);
}
