// Provided by https://gist.github.com/Robotto
// Copypastey mashup from the following sources:
// https://wiki.dfrobot.com/RS485_Soil_Sensor_N_P_K_SKU_SEN0605
// https://randomnerdtutorials.com/esp32-uart-communication-serial-arduino/
// RS485 <-> UART conversion using: https://wiki.seeedstudio.com/Grove-RS485/

uint8_t Com[8] = { 0x01, 0x03, 0x00, 0x1E, 0x00, 0x01, 0xE4, 0x0C };   //N
uint8_t Com1[8] = { 0x01, 0x03, 0x00, 0x1F, 0x00, 0x01, 0xB5, 0xCC };  //P
uint8_t Com2[8] = { 0x01, 0x03, 0x00, 0x20, 0x00, 0x01, 0x85, 0xC0 };  //K
int N, P, K;

HardwareSerial NPK(2); //using uart 2

char val;

void setup() {
  Serial.begin(115200);  
  NPK.begin(9600, SERIAL_8N1, 34, 35); //RX pin is 34, TX pin is 35
}
void loop() {
  int N = readN();
  Serial.print("N = ");
  Serial.print(N);
  Serial.print(" mg/kg  ");
  int P = readP();
  Serial.print("P = ");
  Serial.print(P);
  Serial.print(" mg/kg  ");
  int k = readK();
  Serial.print("K = ");
  Serial.print(K);
  Serial.println(" mg/kg  ");
  delay(1000);
}

int readN(void) {
  uint8_t Data[10] = { 0 };
  uint8_t ch = 0;
  bool flag = 1;
  while (flag) {
    delay(100);
    NPK.write(Com, 8);
    delay(10);
    if (readN(&ch, 1) == 1) {
      if (ch == 0x01) {
        Data[0] = ch;
        if (readN(&ch, 1) == 1) {
          if (ch == 0x03) {
            Data[1] = ch;
            if (readN(&ch, 1) == 1) {
              if (ch == 0x02) {
                Data[2] = ch;
                if (readN(&Data[3], 4) == 4) {
                  if (CRC16_2(Data, 5) == (Data[5] * 256 + Data[6])) {
                    N = Data[3] * 256 + Data[4];
                    flag = 0;
                  }
                }
              }
            }
          }
        }
      }
    }
    NPK.flush();
  }
  return N;
}

int readP(void) {
  uint8_t Data1[10] = { 0 };
  uint8_t ch1 = 0;
  bool flag1 = 1;
  while (flag1) {
    delay(100);
    NPK.write(Com1, 8);
    delay(10);
    if (readN(&ch1, 1) == 1) {
      if (ch1 == 0x01) {
        Data1[0] = ch1;
        if (readN(&ch1, 1) == 1) {
          if (ch1 == 0x03) {
            Data1[1] = ch1;
            if (readN(&ch1, 1) == 1) {
              if (ch1 == 0x02) {
                Data1[2] = ch1;
                if (readN(&Data1[3], 4) == 4) {
                  if (CRC16_2(Data1, 5) == (Data1[5] * 256 + Data1[6])) {
                    P = Data1[3] * 256 + Data1[4];
                    flag1 = 0;
                  }
                }
              }
            }
          }
        }
      }
    }
    NPK.flush();
  }
  return P;
}

int readK(void) {
  uint8_t Data2[10] = { 0 };
  uint8_t ch2 = 0;
  bool flag2 = 1;
  while (flag2) {
    delay(100);
    NPK.write(Com2, 8);
    delay(10);
    if (readN(&ch2, 1) == 1) {
      if (ch2 == 0x01) {
        Data2[0] = ch2;
        if (readN(&ch2, 1) == 1) {
          if (ch2 == 0x03) {
            Data2[1] = ch2;
            if (readN(&ch2, 1) == 1) {
              if (ch2 == 0x02) {
                Data2[2] = ch2;
                if (readN(&Data2[3], 4) == 4) {
                  if (CRC16_2(Data2, 5) == (Data2[5] * 256 + Data2[6])) {
                    K = Data2[3] * 256 + Data2[4];
                    flag2 = 0;
                  }
                }
              }
            }
          }
        }
      }
    }
    NPK.flush();
  }
  return K;
}


uint8_t readN(uint8_t *buf, size_t len) {
  size_t offset = 0, left = len;
  int16_t Tineout = 500;
  uint8_t *buffer = buf;
  long curr = millis();
  while (left) {
    if (NPK.available()) {
      buffer[offset] = NPK.read();
      offset++;
      left--;
    }
    if (millis() - curr > Tineout) {
      break;
    }
  }
  return offset;
}

unsigned int CRC16_2(unsigned char *buf, int len) {
  unsigned int crc = 0xFFFF;
  for (int pos = 0; pos < len; pos++) {
    crc ^= (unsigned int)buf[pos];
    for (int i = 8; i != 0; i--) {
      if ((crc & 0x0001) != 0) {
        crc >>= 1;
        crc ^= 0xA001;
      } else {
        crc >>= 1;
      }
    }
  }

  crc = ((crc & 0x00ff) << 8) | ((crc & 0xff00) >> 8);
  return crc;
}

